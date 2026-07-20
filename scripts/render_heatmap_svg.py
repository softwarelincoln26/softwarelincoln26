#!/usr/bin/env python3
"""
Render GitHub contribution heatmap as SVG.
Reads data/contributions.json and creates contrib-heatmap.svg.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def load_contributions(data_path):
    with open(data_path) as f:
        return json.loads(f.read())


def get_weeks(days):
    if not days:
        return []
    start_date = datetime.strptime(days[0]['date'], '%Y-%m-%d')
    day_map = {d['date']: d['count'] for d in days}
    weeks = []
    current_week = []
    current_date = start_date
    for _ in range(371):
        date_str = current_date.strftime('%Y-%m-%d')
        count = day_map.get(date_str, 0)
        current_week.append({'date': date_str, 'count': count})
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
        current_date += timedelta(days=1)
    if current_week:
        weeks.append(current_week)
    return weeks


def render_heatmap_svg(data_path=None, output_path=None):
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
        return None

    data = load_contributions(data_path)
    days = data.get('days', [])
    total = data.get('total_contributions', 0)

    weeks = get_weeks(days)
    cell = 11
    gap = 3
    step = cell + gap
    left_margin = 40
    top_margin = 25

    svg_w = left_margin + 53 * step + 20
    svg_h = top_margin + 7 * step + 80

    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    parts.append(f'<rect width="100%" height="100%" fill="#0d1117"/>')

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months_seen = set()
    for wi, week in enumerate(weeks):
        if week:
            m = datetime.strptime(week[0]['date'], '%Y-%m-%d').strftime('%b')
            if m not in months_seen and wi < 52:
                months_seen.add(m)
                x = left_margin + wi * step
                parts.append(f'<text x="{x}" y="16" font-family="monospace" font-size="10" fill="#8b949e">{m}</text>')

    day_names = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    for name, pos in day_names:
        y = top_margin + pos * step + 9
        parts.append(f'<text x="5" y="{y}" font-family="monospace" font-size="9" fill="#8b949e">{name}</text>')

    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = left_margin + wi * step
            y = top_margin + di * step
            count = day['count']
            level = min(count, 4) if count > 0 else 0
            color = PALETTE[level]
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}" rx="2"/>')

    legend_y = top_margin + 7 * step + 20
    parts.append(f'<text x="{svg_w - 200}" y="{legend_y - 5}" font-family="monospace" font-size="10" fill="#8b949e">Less</text>')
    for i, color in enumerate(PALETTE):
        lx = svg_w - 200 + i * (cell + gap + 5) + 40
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{cell}" height="{cell}" fill="{color}" rx="2"/>')
    parts.append(f'<text x="{svg_w - 200 + 5 * (cell + gap + 5) + 40}" y="{legend_y - 5}" font-family="monospace" font-size="10" fill="#8b949e">More</text>')

    stats_y = legend_y + 30
    parts.append(f'<text x="15" y="{stats_y}" font-family="monospace" font-size="11" fill="#8b949e">{total:,} contributions in the last year</text>')

    parts.append('</svg>')

    svg = '\n'.join(parts)
    Path(output_path).write_text(svg)
    print(f"Heatmap saved to {output_path}")
    print(f"Total contributions: {total:,}")
    return output_path


if __name__ == "__main__":
    data_file = sys.argv[1] if len(sys.argv) > 1 else None
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    render_heatmap_svg(data_file, output_file)
