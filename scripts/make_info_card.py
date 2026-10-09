import os

def main():
    static = os.environ.get("STATIC", "0") == "1"
    width = 490
    height = 315

    # Neofetch data customized for Fikri Bintang
    info = [
        ("title", "isagi@archlinux", "------------------"),
        ("OS", "Arch Linux x86_64"),
        ("Host", "Realme & ThinkPad Workspace"),
        ("Kernel", "7.2.6-arch2-1"),
        ("Uptime", "Semester 4 (CS Undergrad)"),
        ("Shell", "zsh / bash"),
        ("Role", "Frontend Dev & Automation Enthusiast"),
        ("Stack", "React, Next.js, Flutter, Python, TS"),
        ("Editor", "Neovim / VS Code"),
        ("Focus", "Clean Minimalist UI & System Craft"),
        ("Status", "Building & shipping side projects"),
    ]

    svg = []
    svg.append(f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">')
    
    # CSS Styles & Animations
    anim_css = "" if static else """
        .line {
            opacity: 1;
            animation: fadeInSlide 0.45s ease-out forwards;
        }
        @keyframes fadeInSlide {
            from {
                opacity: 0;
                transform: translateY(6px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    """
    
    svg.append('<style>')
    svg.append(f'''
        .terminal-bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 8; ry: 8; }}
        .title-bar {{ fill: #161b22; }}
        .title-text {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; fill: #8b949e; font-weight: 500; }}
        .btn-red {{ fill: #ff5f56; }}
        .btn-yellow {{ fill: #ffbd2e; }}
        .btn-green {{ fill: #27c93f; }}
        .key {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; fill: #58a6ff; font-weight: 600; }}
        .val {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; fill: #c9d1d9; }}
        .hl {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; font-weight: 700; fill: #58a6ff; }}
        .sep {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; fill: #30363d; }}
        {anim_css}
    ''')
    svg.append('</style>')

    # Terminal Window Container
    svg.append(f'<rect width="{width}" height="{height}" class="terminal-bg" />')
    
    # Window Header
    svg.append(f'<path d="M0 8a8 8 0 0 1 8-8h{width-16}a8 8 0 0 1 8 8v24H0z" class="title-bar" />')
    svg.append('<circle cx="18" cy="16" r="5" class="btn-red" />')
    svg.append('<circle cx="34" cy="16" r="5" class="btn-yellow" />')
    svg.append('<circle cx="50" cy="16" r="5" class="btn-green" />')
    svg.append(f'<text x="{width // 2}" y="20" text-anchor="middle" class="title-text">fikri@archlinux: ~</text>')

    # Content
    start_y = 52
    line_h = 19
    delay_step = 0.06

    current_line = 0
    for item in info:
        delay = current_line * delay_step
        style_attr = "" if static else f'style="animation-delay: {delay:.2f}s"'
        y = start_y + (current_line * line_h)

        if item[0] == "title":
            svg.append(f'<g class="line" {style_attr}>')
            svg.append(f'  <text x="22" y="{y}" class="hl">{item[1]}</text>')
            svg.append(f'  <text x="22" y="{y + 12}" class="sep">{item[2]}</text>')
            svg.append('</g>')
            current_line += 1
        else:
            key, val = item
            svg.append(f'<g class="line" {style_attr}>')
            svg.append(f'  <text x="22" y="{y}" class="key">{key}:</text>')
            svg.append(f'  <text x="100" y="{y}" class="val">{val}</text>')
            svg.append('</g>')
        current_line += 1

    # Neofetch color palette blocks
    palette_colors = ["#484f58", "#ff7b72", "#7ee787", "#f2cc60", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"]
    delay = current_line * delay_step
    style_attr = "" if static else f'style="animation-delay: {delay:.2f}s"'
    block_y = start_y + (current_line * line_h) + 6
    block_size = 12
    block_gap = 6

    svg.append(f'<g class="line" {style_attr}>')
    for idx, c in enumerate(palette_colors):
        bx = 22 + idx * (block_size + block_gap)
        svg.append(f'  <rect x="{bx}" y="{block_y}" width="{block_size}" height="{block_size}" rx="2" fill="{c}" />')
    svg.append('</g>')

    svg.append('</svg>')

    with open("info-card.svg", "w") as f:
        f.write("\n".join(svg))
    print(f"Generated info-card.svg ({width}x{height})")

if __name__ == "__main__":
    main()
