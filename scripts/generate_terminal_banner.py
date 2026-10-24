from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import html

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "github_profile_card_jihad (1).png"
ASSETS = ROOT / "assets"
W, H = 1180, 610

THEMES = {
    "dark": {
        "bg": "#0A101F", "panel": "#0D1628", "panel2": "#101B30",
        "line": "#25344C", "muted": "#8291A8", "text": "#DDE7F5",
        "portrait": "#22D3EE", "chrome": "#22D3EE", "accent": "#00FF9C",
        "shadow": "#02050B",
    },
    "light": {
        "bg": "#F6F8FA", "panel": "#FFFFFF", "panel2": "#EDF3F7",
        "line": "#CBD7E1", "muted": "#64748B", "text": "#172033",
        "portrait": "#0E7490", "chrome": "#0891B2", "accent": "#059669",
        "shadow": "#AAB7C4",
    },
}

ROWS = [
    ("Subject", "Jihad Tiazziti"),
    ("Role", "Mobile Application Developer"),
    ("Location", "Morocco"),
    ("Status", "Open to internships + junior roles"),
    ("Focus", "Android · Mobile Apps"),
    ("Core.Lang", "Kotlin · Dart"),
    ("Core.Mobile", "Android SDK · Flutter"),
    ("Core.Data", "Firebase · Room · SQLite · SQL"),
    ("Core.API", "REST APIs"),
    ("ToolChain", "Git · GitHub · Figma · VS Code"),
    ("Current", "J-Shop · G-Stock"),
    ("Grid.LinkedIn", "/in/jihad-tiazziti"),
    ("Grid.Instagram", "@ry_vnn17"),
]


def fit_crop(im, size, top_bias=0.08):
    tw, th = size
    ratio = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * ratio), round(im.height * ratio)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    max_top = max(0, nh - th)
    top = int(max_top * max(0.0, min(1.0, top_bias)))
    return im.crop((left, top, left + tw, top + th))


def portrait_points(theme: str):
    source = Image.open(SOURCE).convert("RGB")
    # Existing source card contains the portrait on the left side.
    crop = source.crop((0, 0, min(500, source.width), source.height))
    crop = fit_crop(crop, (300, 340), top_bias=0.04)
    gray = ImageOps.grayscale(crop)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.6, percent=180, threshold=2))

    # 1-bit Floyd-Steinberg gives the same crisp terminal-map feel.
    bits = gray.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    px = bits.load()
    pts = []
    for y in range(bits.height):
        for x in range(bits.width):
            lit = px[x, y] != 0
            if (theme == "dark" and lit) or (theme == "light" and not lit):
                # Sample every second point in dense zones for a cleaner face silhouette.
                if ((x + y) % 2 == 0) or (60 < x < 240 and 35 < y < 255):
                    pts.append((74 + x, 154 + y))
    return pts[:19000]


def points_path(points):
    # Compact SVG path: one 1.25px square per active dither pixel.
    return "".join(f"M{x} {y}h1.25v1.25h-1.25Z" for x, y in points)


def esc(s):
    return html.escape(s, quote=True)


def render(theme_name: str):
    t = THEMES[theme_name]
    pts = portrait_points(theme_name)
    portrait = points_path(pts)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">',
        '<title>Jihad Tiazziti live terminal profile</title>',
        '<defs>',
        f'<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="{t["shadow"]}" flood-opacity=".28"/></filter>',
        f'<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.3" result="b"/><feFlood flood-color="{t["chrome"]}" flood-opacity=".32"/><feComposite in2="b" operator="in"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<clipPath id="visualClip"><rect x="49" y="124" width="390" height="414" rx="3"/></clipPath>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>',
        f'<rect x="13" y="13" width="1154" height="584" rx="13" fill="{t["panel"]}" stroke="{t["line"]}" filter="url(#shadow)"/>',
        f'<path d="M13 62H1167" stroke="{t["line"]}"/>',
        '<circle cx="38" cy="38" r="6" fill="#FF5F57"/><circle cx="59" cy="38" r="6" fill="#FEBC2E"/><circle cx="80" cy="38" r="6" fill="#28C840"/>',
        f'<text x="110" y="44" fill="{t["accent"]}" font-family="monospace" font-size="16">jihad@dev:~/profile</text>',
        f'<text x="885" y="44" fill="{t["muted"]}" font-family="monospace" font-size="13">profile.sh --live</text>',
        # left panel
        f'<rect x="35" y="89" width="420" height="468" rx="8" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<text x="51" y="115" fill="{t["chrome"]}" font-family="monospace" font-size="16" font-weight="700">VISUAL.MAP</text>',
        f'<text x="334" y="115" fill="{t["muted"]}" font-family="monospace" font-size="11">DITHER_STREAM</text>',
        f'<rect x="49" y="124" width="390" height="414" rx="3" fill="{t["bg"]}" stroke="{t["line"]}"/>',
        f'<g clip-path="url(#visualClip)" fill="{t["portrait"]}" opacity=".88"><path d="{portrait}"/></g>',
        # subtle scan line animation
        f'<g clip-path="url(#visualClip)"><rect x="49" y="128" width="390" height="2" fill="#FFFFFF" opacity=".72" filter="url(#glow)"><animate attributeName="y" values="128;532;128" dur="6s" repeatCount="indefinite"/></rect></g>',
        # pulse frame
        f'<rect x="70" y="145" width="285" height="360" rx="2" fill="none" stroke="{t["chrome"]}" opacity=".45"><animate attributeName="opacity" values=".18;.55;.18" dur="3.8s" repeatCount="indefinite"/></rect>',
        f'<text x="57" y="552" fill="{t["muted"]}" font-family="monospace" font-size="10">PORTRAIT.DITHER = ACTIVE  ·  SIGNAL.LOCKED</text>',
        # right panel
        f'<rect x="475" y="89" width="669" height="468" rx="8" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<text x="493" y="115" fill="{t["chrome"]}" font-family="monospace" font-size="16" font-weight="700">SYSTEM.INFO</text>',
        f'<circle cx="1117" cy="109" r="5" fill="{t["accent"]}"><animate attributeName="opacity" values=".35;1;.35" dur="1.8s" repeatCount="indefinite"/></circle>',
        f'<text x="1046" y="114" fill="{t["accent"]}" font-family="monospace" font-size="11">ONLINE</text>',
    ]

    y = 151
    for label, value in ROWS:
        parts += [
            f'<text x="496" y="{y}" fill="{t["muted"]}" font-family="monospace" font-size="12">{esc(label)}</text>',
            f'<line x1="620" y1="{y-4}" x2="730" y2="{y-4}" stroke="{t["line"]}" stroke-dasharray="2 5"/>',
            f'<text x="748" y="{y}" fill="{t["text"]}" font-family="monospace" font-size="12" font-weight="600">{esc(value)}</text>',
        ]
        y += 29

    parts += [
        f'<text x="496" y="535" fill="{t["accent"]}" font-family="monospace" font-size="12">&gt; ready_for_opportunities.exe</text>',
        f'<rect x="724" y="524" width="7" height="13" fill="{t["accent"]}"><animate attributeName="opacity" values="1;1;0;0" dur="1s" repeatCount="indefinite"/></rect>',
        '</svg>'
    ]
    return "".join(parts)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        out = ASSETS / f"banner-{theme}.svg"
        out.write_text(render(theme), encoding="utf-8")
        print(f"generated {out}")


if __name__ == "__main__":
    main()
