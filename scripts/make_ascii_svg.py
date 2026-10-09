import os
import sys
import html
from PIL import Image

RAMP = " .`:-=+*cs#%@"

def image_to_ascii(image_path, width=70):
    if not os.path.exists(image_path):
        # Create a simple default placeholder if image doesn't exist yet
        img = Image.new("L", (100, 100), color=255)
    else:
        img = Image.open(image_path).convert("L")
    
    # Font aspect ratio is roughly 0.55 width/height
    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.55)
    
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    pixels = img.load()
    if pixels is None:
        return []
    rows = []
    for y in range(height):
        row_chars = []
        for x in range(width):
            val = pixels[x, y]
            brightness = int(val) if isinstance(val, (int, float)) else int(val[0])
            # 255 -> 0 (space), 0 -> len(RAMP)-1
            ramp_idx = int((255 - brightness) / 255.0 * (len(RAMP) - 1))
            row_chars.append(RAMP[ramp_idx])
        rows.append("".join(row_chars))
    return rows

def generate_svg(rows, output_path="fikri-ascii.svg"):
    # Calculate SVG dimensions
    char_w = 4.8
    char_h = 7.5
    num_cols = max(len(r) for r in rows) if rows else 70
    num_rows = len(rows)
    
    svg_w = int(num_cols * char_w + 20)
    svg_h = int(num_rows * char_h + 30)
    
    svg = []
    svg.append(f'<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg">')
    svg.append('<style>')
    svg.append('''
        .ascii-text {
            font-family: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Monaco, Consolas, "Courier New", monospace;
            font-size: 8px;
            fill: #c9d1d9;
            white-space: pre;
            opacity: 1;
        }
    ''')
    svg.append('</style>')
    
    # Background container matching info-card
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" rx="8" ry="8" fill="#0d1117" stroke="#30363d" stroke-width="1" />')
    
    # Render rows without clip-paths (100% static & reliable)
    for i, row in enumerate(rows):
        y_pos = int((i + 1) * char_h + 10)
        escaped_row = html.escape(row)
        
        # Text row
        svg.append(f'<text x="10" y="{y_pos}" class="ascii-text">{escaped_row}</text>')
        
    svg.append('</svg>')
    
    with open(output_path, "w") as f:
        f.write("\n".join(svg))
    print(f"Generated {output_path} ({svg_w}x{svg_h})")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "fikri-ascii.svg"
    rows = image_to_ascii(src)
    generate_svg(rows, out)
