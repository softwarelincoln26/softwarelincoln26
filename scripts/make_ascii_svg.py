#!/usr/bin/env python3
"""
Convert a prepped photo to a self-typing monochrome ASCII SVG.
Each row animates left-to-right with a cursor effect.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pillow', 'numpy'], check=True)
    from PIL import Image
    import numpy as np

# ASCII density ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"
WIDTH = 100
HEIGHT = 53


def image_to_ascii_grid(image_path):
    """Convert image to character grid based on brightness"""
    img = Image.open(image_path).convert('L')
    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    pixels = np.array(img)

    grid = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            brightness = pixels[y, x]
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            idx = max(0, min(idx, len(RAMP) - 1))
            char = RAMP[idx]
            if char == ' ':
                row.append('&nbsp;')
            elif char == '<':
                row.append('&lt;')
            elif char == '>':
                row.append('&gt;')
            elif char == '&':
                row.append('&amp;')
            else:
                row.append(char)
        grid.append(''.join(row))
    return grid


def create_ascii_svg(grid, output_path, color='#c0c0c0', animate=True):
    """Create SVG with optional typing animation"""
    char_width = 10
    char_height = 12
    svg_width = WIDTH * char_width
    svg_height = HEIGHT * char_height

    if animate:
        anim_rows = []
        for y, row in enumerate(grid):
            delay = y * 0.05
            anim_rows.append(f'''
            <g>
                <animateTransform attributeName="transform" type="translate"
                    from="{svg_width} 0" to="0 0" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>
                <clipPath id="row-{y}">
                    <animateTransform attributeName="transform" type="translate"
                        from="{svg_width} 0" to="0 0" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>
                    <rect x="0" y="{y * char_height}" width="{svg_width}" height="{char_height}"/>
                </clipPath>
                <text x="5" y="{(y + 1) * char_height - 2}" 
                    font-family="monospace" font-size="12" fill="{color}"
                    clip-path="url(#row-{y})">{row}</text>
            </g>''')
        content = '\n'.join(anim_rows)
    else:
        lines = []
        for y, row in enumerate(grid):
            lines.append(f'<text x="5" y="{(y + 1) * char_height - 2}" '
                        f'font-family="monospace" font-size="12" fill="{color}">{row}</text>')
        content = '\n'.join(lines)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" 
     width="{svg_width}" height="{svg_height}">
    <rect width="100%" height="100%" fill="#0d1117"/>
    {content}
</svg>'''

    Path(output_path).write_text(svg)
    print(f"ASCII SVG saved to {output_path}")
    return output_path


def make_ascii_svg(input_path=None, output_path=None):
    """Main function to create ASCII portrait SVG"""
    if input_path is None:
        script_dir = Path(__file__).parent.parent
        # Try common naming patterns
        candidates = [
            script_dir / "data" / "source-prepped.png",
            script_dir / "data" / "source-photo-prepped.png",
            script_dir / "data" / "source-photo.jpg",
        ]
        input_path = None
        for c in candidates:
            if c.exists():
                input_path = c
                break
        if input_path is None:
            input_path = script_dir / "data" / "source-prepped.png"
    else:
        input_path = Path(input_path)

    if output_path is None:
        script_dir = Path(__file__).parent.parent
        output_path = script_dir / "ascii-portrait.svg"
    else:
        output_path = Path(output_path)

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("Run prep_photo.py first to prepare your photo")
        return None

    print(f"Converting {input_path.name} to ASCII...")
    grid = image_to_ascii_grid(input_path)
    create_ascii_svg(grid, output_path)
    return output_path


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    make_ascii_svg(input_file, output_file)
