#!/usr/bin/env python3
"""
Render GitHub contribution heatmap as animated SVG.
Reads data/contributions.json and creates contrib-heatmap.svg.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# GitHub-style green palette
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def load_contributions(data_path):
    """Load contribution data from JSON"""
    with open(data_path) as f:
        return json.loads(f.read())


def get_weeks(days):
    """Organize days into weeks (7 days each)"""
    if not days:
        return []

    start_date = datetime.strptime(days[0]['date'], '%Y-%m-%d')
    end_date = datetime.strptime(days[-1]['date'], '%Y-%m-%d')

    day_map = {d['date']: d['count'] for d in days}

    weeks = []
    current_week = []

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        count = day_map.get(date_str, 0)
        current_week.append({
            'date': date_str,
            'count': count
        })

        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []

        current_date += timedelta(days=1)

    if current_week:
        weeks.append(current_week)

    return weeks


def render_heatmap_svg(data_path=None, output_path=None):
    """Render contribution heatmap as animated SVG"""
    if data_path is None:
        script_dir = Path(__file__).parent.parent
        data_path = script_dir / "data" / "contributions.json"
    else:
        data_path = Path(data_path)

    if output_path is None:
        script_dir = Path(__file__).parent.parent
        output_path = script_dir / "contrib-heatmap.svg"
    else:
        output_path = Path(output_path)

    if not data_path.exists():
        print(f"Error: {data_path} not found")
        print("Run fetch_contributions.py first")
        return None

    data = load_contributions(data_path)
    days = data.get('days', [])
    stats = data.get('stats', {})
    total = data.get('total_contributions', 0)

    weeks = get_weeks(days)
    num_weeks = len(weeks)

    cell_size = 11
    cell_gap = 3
    day_height = cell_size + cell_gap
    week_width = cell_size + cell_gap
    header_height = 25
    legend_height = 30
    stats_height = 30

    svg_width = 53 * week_width + 60
    svg_height = header_height + 7 * day_height + legend_height + stats_height + 20

    cells = []
    for week_idx, week in enumerate(weeks):
        for day_idx, day in enumerate(week):
            x = 40 + week_idx * week_width
            y = header_height + day_idx * day_height

            count = day['count']
            level = min(count, 4) if count > 0 else 0
            color = PALETTE[level]

            delay = week_idx * 0.03 + day_idx * 0.02
            opacity = 0 if count == 0 else 1

            cells.append(f'''
            <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" 
                fill="{color}" rx="2" opacity="0">
                <animate attributeName="opacity" from="0" to="{opacity}" 
                    dur="0.2s" begin="{delay:.2f}s" fill="freeze"/>
            </rect>''')

    month_labels = []
    months_seen = set()
    for week_idx, week in enumerate(weeks):
        if week:
            first_day = week[0]
            month = datetime.strptime(first_day['date'], '%Y-%m-%d').strftime('%b')
            if month not in months_seen:
                months_seen.add(month)
                x = 40 + week_idx * week_width
                month_labels.append(f'''
                <text x="{x}" y="15" font-family="monospace" font-size="10" 
                    fill="#8b949e">{month}</text>''')

    day_labels = ['Mon', 'Wed', 'Fri']
    day_positions = [1, 3, 5]
    for label, pos in zip(day_labels, day_positions):
        y = header_height + pos * day_height + 8
        day_labels_svg = f'''
        <text x="5" y="{y}" font-family="monospace" font-size="9" 
            fill="#8b949e">{label}</text>'''

    legend_y = header_height + 7 * day_height + 20
    legend_items = []
    for i, color in enumerate(PALETTE):
        x = svg_width - 200 + i * (cell_size + cell_gap + 5)
        legend_items.append(f'''
        <rect x="{x}" y="{legend_y}" width="{cell_size}" height="{cell_size}" 
            fill="{color}" rx="2"/>
        <text x="{x + cell_size + 3}" y="{legend_y + 9}" font-family="monospace" 
            font-size="9" fill="#8b949e">{'Less' if i == 0 else 'More' if i == len(PALETTE)-1 else ''}</text>''')

    stats_y = legend_y + legend_height + 5
    best_day = stats.get('best_day', {})
    best_day_str = best_day.get('date', 'N/A')
    if best_day_str != 'N/A':
        best_day_obj = datetime.strptime(best_day_str, '%Y-%m-%d')
        best_day_display = best_day_obj.strftime('%b %d, %Y')
    else:
        best_day_display = 'N/A'

    stats_text = f'''{total:,} contributions in the last year'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}"
     width="{svg_width}" height="{svg_height}">
    <rect width="100%" height="100%" fill="#0d1117"/>
    
    {chr(10).join(month_labels)}
    {chr(10).join(day_labels_svg if isinstance(day_labels_svg, str) else [day_labels_svg])}
    
    {chr(10).join(cells)}
    
    {chr(10).join(legend_items)}
    
    <text x="15" y="{stats_y}" font-family="monospace" font-size="11" 
        fill="#8b949e">{stats_text}</text>
</svg>'''

    Path(output_path).write_text(svg)
    print(f"Heatmap saved to {output_path}")
    print(f"Total contributions: {total:,}")
    return output_path


if __name__ == "__main__":
    data_file = sys.argv[1] if len(sys.argv) > 1 else None
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    render_heatmap_svg(data_file, output_file)
