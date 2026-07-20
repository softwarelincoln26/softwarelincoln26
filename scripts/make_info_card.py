#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG.
Shows role, stack, and highlights with fade-in animation.
"""

import sys
from pathlib import Path

# Customize these for your profile
PROFILE_CONFIG = {
    'name': 'softwarelincoln26',
    'role': 'Cybersecurity Student and Hardware Hacker',
    'stack': 'Python, C/C++, JavaScript, Linux',
    'highlights': [
        'ESP32 Security Projects',
        'AI Voice Assistant (Jarvis)',
        'Network Security Tools',
    ],
    'location': 'Learning and Building',
    'status': 'Online',
}


def create_info_card_svg(config=None, output_path=None, static=False):
    """Create neofetch-style info card SVG"""
    if config is None:
        config = PROFILE_CONFIG

    if output_path is None:
        script_dir = Path(__file__).parent.parent
        output_path = script_dir / "info-card.svg"
    else:
        output_path = Path(output_path)

    svg_width = 490
    svg_height = 300

    colors = {
        'title': '#58a6ff',
        'label': '#7ee787',
        'value': '#c9d1d9',
        'highlight': '#f0883e',
        'border': '#30363d',
        'bg': '#0d1117'
    }

    lines = []
    y_pos = 30
    line_height = 35

    lines.append(f'''    <rect x="0" y="0" width="{svg_width}" height="{svg_height}" 
        fill="{colors['bg']}" rx="8"/>''')

    lines.append(f'''    <rect x="0" y="0" width="{svg_width}" height="30" 
        fill="{colors['border']}" rx="8"/>
    <rect x="0" y="15" width="{svg_width}" height="15" 
        fill="{colors['border']}"/>''')

    title_y = 20
    lines.append(f'''    <text x="15" y="{title_y}" font-family="monospace" font-size="14" 
        fill="{colors['title']}">&gt; {config['name']}@github</text>''')

    y_pos = 55
    card_lines = [
        ('role', 'Role', config['role']),
        ('stack', 'Stack', config['stack']),
        ('location', 'Location', config['location']),
        ('status', 'Status', config['status']),
    ]

    for key, label, value in card_lines:
        anim_delay = 0.3
        if not static:
            lines.append(f'''    <g opacity="0">
        <animate attributeName="opacity" from="0" to="1" 
            dur="0.3s" begin="{anim_delay:.1f}s" fill="freeze"/>
        <text x="15" y="{y_pos}" font-family="monospace" font-size="12" 
            fill="{colors['label']}">{label}:</text>
        <text x="90" y="{y_pos}" font-family="monospace" font-size="12" 
            fill="{colors['value']}">{value}</text>
    </g>''')
        else:
            lines.append(f'''    <text x="15" y="{y_pos}" font-family="monospace" font-size="12" 
        fill="{colors['label']}">{label}:</text>
    <text x="90" y="{y_pos}" font-family="monospace" font-size="12" 
        fill="{colors['value']}">{value}</text>''')
        y_pos += line_height
        anim_delay += 0.2

    y_pos += 10
    lines.append(f'''    <line x1="15" y1="{y_pos - 10}" x2="{svg_width - 15}" y2="{y_pos - 10}" 
        stroke="{colors['border']}" stroke-width="1"/>''')

    for i, highlight in enumerate(config['highlights']):
        anim_delay = 1.0 + i * 0.2
        if not static:
            lines.append(f'''    <g opacity="0">
        <animate attributeName="opacity" from="0" to="1" 
            dur="0.3s" begin="{anim_delay:.1f}s" fill="freeze"/>
        <text x="15" y="{y_pos}" font-family="monospace" font-size="12" 
            fill="{colors['highlight']}">★ {highlight}</text>
    </g>''')
        else:
            lines.append(f'''    <text x="15" y="{y_pos}" font-family="monospace" font-size="12" 
        fill="{colors['highlight']}">★ {highlight}</text>''')
        y_pos += line_height

    content = '\n'.join(lines)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}"
     width="{svg_width}" height="{svg_height}">
{content}
</svg>'''

    Path(output_path).write_text(svg)
    print(f"Info card saved to {output_path}")
    return output_path


if __name__ == "__main__":
    static_mode = '--static' in sys.argv
    output_file = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            output_file = arg
    create_info_card_svg(output_path=output_file, static=static_mode)
