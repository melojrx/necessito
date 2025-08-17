#!/usr/bin/env python3
"""
Generate simple SVG icons for PWA
"""

import os

def create_icon_svg(size, output_path):
    """Create a simple SVG icon"""
    svg_content = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d6efd;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0056b3;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="{size}" height="{size}" rx="{size//8}" fill="url(#grad)"/>
  <text x="{size//2}" y="{size//2 + size//8}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{size//4}" font-weight="bold" fill="white">I</text>
</svg>'''
    
    with open(output_path, 'w') as f:
        f.write(svg_content)

# Icon sizes for PWA
sizes = [72, 96, 128, 144, 152, 192, 384, 512]
icons_dir = '/app/static/img/icons'

# Create icons directory if it doesn't exist
os.makedirs(icons_dir, exist_ok=True)

# Generate icons
for size in sizes:
    icon_path = os.path.join(icons_dir, f'icon-{size}x{size}.svg')
    create_icon_svg(size, icon_path)
    print(f'Created {icon_path}')

print(f'Generated {len(sizes)} SVG icons')