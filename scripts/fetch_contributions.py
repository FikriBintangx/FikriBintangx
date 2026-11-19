#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint (the same fragment the profile page itself uses) and
write data/contributions.json with the raw days plus derived stats.

Supports standard library fallback (urllib + re) if bs4/requests are not installed.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

USERNAME = os.environ.get("GH_PROFILE_USER", "FikriBintangx")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    # Map tool-tips for counts
    tooltips = {}
    for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>', html, re.S):
        tid, txt = m.group(1), m.group(2)
        match_count = re.search(r'(\d+)\s+contribution', txt)
        tooltips[tid] = int(match_count.group(1)) if match_count else 0

    # Parse td.ContributionCalendar-day cells
    days = []
    cell_pattern = re.finditer(
        r'<td[^>]*\bclass="[^"]*ContributionCalendar-day[^"]*"[^>]*>',
        html
    )
    for m in cell_pattern:
        tag = m.group(0)
        date_m = re.search(r'\bdata-date="([^"]+)"', tag)
        if not date_m:
            continue
        date = date_m.group(1)
        level_m = re.search(r'\bdata-level="([^"]+)"', tag)
        level = int(level_m.group(1)) if level_m else 0
        id_m = re.search(r'\bid="([^"]+)"', tag)
        tid = id_m.group(1) if id_m else None
        count = tooltips.get(tid, 0) if tid else 0
        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_current_streak(days):
    if not days:
        return 0, None, None
    idx = len(days) - 1
    if days[idx]["count"] == 0:
        idx -= 1  # today isn't over yet
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "2026-01-08", "count": 40}
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]} if days else {},
        "total_contributions": total,
        "total": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


if __name__ == "__main__":
    try:
        days = fetch_days()
        if not days:
            raise ValueError("No calendar cells parsed from GitHub")
        data = build_data(days)
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"wrote {OUT_PATH}: {data['total_contributions']} contributions, "
              f"current streak {data['current_streak']['length']}, "
              f"longest streak {data['longest_streak']['length']}")
    except Exception as e:
        print(f"fetch_contributions error: {e}, keeping existing data/contributions.json if present")
