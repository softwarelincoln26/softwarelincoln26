#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion using only PIL.
Converts to grayscale and boosts contrast.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--break-system-packages', 'pillow'], check=True)
    from PIL import Image, ImageEnhance, ImageFilter


def prep_photo(input_path, output_path=None):
    """Prep photo for ASCII art conversion"""
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return None

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}-prepped.png"
    else:
        output_path = Path(output_path)

    print(f"Processing {input_path.name}...")

    img = Image.open(input_path)

    # Remove alpha channel and put on white background
    if img.mode == 'RGBA':
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(background, img)

    # Convert to grayscale
    img = img.convert('L')

    # Resize to manageable size while keeping aspect ratio
    max_size = 800
    ratio = min(max_size / img.width, max_size / img.height)
    if ratio < 1:
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Boost contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # Boost sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.2)

    # Save
    img.save(output_path)
    print(f"Saved to {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <input.jpg> [output.png]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    prep_photo(input_file, output_file)
