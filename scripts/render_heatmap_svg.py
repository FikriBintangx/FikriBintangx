import json
import math

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

def main():
    with open("data/contributions.json", "r") as f:
        data = json.load(f)

    days = data["days"]
    total = data["total"]
    
    # Grid dimensions
    box_size = 11
    gap = 4
    weeks = 53
    days_in_week = 7
    
    # Calculate offset to align days correctly (Sunday=0, Monday=1, etc.)
    # In GitHub, the grid starts on a Sunday. The first day in our data is a Sunday usually,
    # but let's just flow them into weeks of 7.
    # The data from GitHub is already column-major (weeks, then days).
    # Wait, in our parsing, the days are just in order.
    # GitHub's HTML is row-major by day-of-week, then column-major by week!
    # Ah! In fetch_contributions.py, `days` list is sorted by date.
    # Let's map date to column/row.
    from datetime import datetime
    
    # Figure out the exact day of week of the first date
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    start_dow = first_date.weekday() # Monday is 0, Sunday is 6
    # GitHub grid starts on Sunday. So Sunday=0, Monday=1...
    start_dow = (start_dow + 1) % 7
    
    # Create an SVG
    width = 860
    height = 200
    
    svg = []
    svg.append(f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">')
    svg.append('<style>')
    svg.append('''
        .day {
            rx: 2;
            ry: 2;
            animation: slideDown 0.8s ease-out forwards;
            opacity: 0;
            transform: translateY(-10px);
        }
        @keyframes slideDown {
            to { opacity: 1; transform: translateY(0); }
        }
        .text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 12px; fill: #8b949e; }
        .text-bold { font-weight: 600; fill: #c9d1d9; }
    ''')
    svg.append('</style>')
    
    # Draw background for a neat look
    # svg.append(f'<rect width="{width}" height="{height}" fill="#0d1117" rx="6" ry="6"/>')
    
    grid_x = 40
    grid_y = 30
    
    # Draw boxes
    for i, d in enumerate(days):
        # index with padding for start day of week
        idx = i + start_dow
        col = idx // days_in_week
        row = idx % days_in_week
        
        x = grid_x + col * (box_size + gap)
        y = grid_y + row * (box_size + gap)
        
        level = min(d["level"], len(PALETTE) - 1)
        color = PALETTE[level]
        
        # Diagonal stagger delay
        delay = (col * 0.015) + (row * 0.015)
        
        svg.append(f'<rect class="day" x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="{color}" style="animation-delay: {delay:.3f}s"/>')
        
    # Legend
    legend_x = grid_x + (weeks - 5) * (box_size + gap)
    legend_y = grid_y + 7 * (box_size + gap) + 15
    svg.append(f'<text x="{legend_x - 30}" y="{legend_y + 9}" class="text">Less</text>')
    for i, color in enumerate(PALETTE[:5]):
        svg.append(f'<rect x="{legend_x + i * (box_size + gap)}" y="{legend_y}" width="{box_size}" height="{box_size}" rx="2" ry="2" fill="{color}"/>')
    svg.append(f'<text x="{legend_x + 5 * (box_size + gap) + 5}" y="{legend_y + 9}" class="text">More</text>')
    
    # Stats footer
    stats_y = legend_y + 9
    svg.append(f'<text x="{grid_x}" y="{stats_y}" class="text"><tspan class="text-bold">{total:,}</tspan> contributions in the last year</text>')
    
    svg.append('</svg>')
    
    with open("contrib-heatmap.svg", "w") as f:
        f.write("\n".join(svg))

if __name__ == "__main__":
    main()
