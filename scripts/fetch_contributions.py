import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

USERNAME = "FikriBintangx"

def main():
    url = f"https://github.com/users/{USERNAME}/contributions"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    tooltips = {}
    for tt in soup.find_all('tool-tip'):
        target_id = tt.get('for')
        if target_id:
            text = tt.get_text()
            m = re.search(r'(\d+)\s+contribution', text)
            count = int(m.group(1)) if m else 0
            tooltips[target_id] = count

    days = []
    for td in soup.find_all('td', class_='ContributionCalendar-day'):
        date = td.get('data-date')
        level = int(td.get('data-level', 0))
        td_id = td.get('id')
        if not date:
            continue
        count = tooltips.get(td_id, 0)
        days.append({
            'date': date,
            'count': count,
            'level': level
        })

    # Sort days by date (usually already sorted, but to be sure)
    days.sort(key=lambda x: x['date'])
    
    # Calculate streaks & stats
    current_streak = 0
    longest_streak = 0
    best_day_count = 0
    best_day_date = ""
    total = sum(d['count'] for d in days)
    
    for d in days:
        if d['count'] > best_day_count:
            best_day_count = d['count']
            best_day_date = d['date']
            
        if d['count'] > 0:
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
        else:
            current_streak = 0

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    data = {
        "username": USERNAME,
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best_day_date, "count": best_day_count},
        "days": days
    }
    
    with open("data/contributions.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
