#!/bin/bash
# Setup script for GitHub Profile README
# Run this to initialize the project

echo "=== GitHub Profile Setup ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    sudo apt install -y python3 python3-pip
fi

echo "1. Installing Python dependencies..."
cd scripts
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
cd ..

echo ""
echo "2. Creating data directory..."
mkdir -p data

echo ""
echo "3. Testing contribution fetch..."
python3 scripts/fetch_contributions.py softwarelincoln26

echo ""
echo "4. Rendering heatmap..."
python3 scripts/render_heatmap_svg.py

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Add your photo: cp ~/your-photo.jpg data/source-photo.jpg"
echo "  2. Prep photo: python3 scripts/prep_photo.py data/source-photo.jpg"
echo "  3. Generate ASCII art: python3 scripts/make_ascii_svg.py"
echo "  4. Create repo on GitHub: gh repo create softwarelincoln26 --public"
echo "  5. Push to GitHub"
echo ""
