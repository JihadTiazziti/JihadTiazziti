from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = "JihadTiazziti"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#101720",
        "text": "#f0f6fc",
        "muted": "#8b949e",
        "grid": "#30363d",
        "accent": "#22d3ee",
        "accent2": "#00ff9c",
        "bar": "#58a6ff",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "text": "#1f2328",
        "muted": "#57606a",
        "grid": "#d0d7de",
        "accent": "#0969da",
        "accent2": "#1a7f37",
        "bar": "#8250df",
    },
}


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"generated {path.relative_to(ROOT)}")


def api_get(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-assets",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def load_live_data():
    fallback = {
        "public_repos": 2,
        "followers": 2,
        "stars": 0,
        "forks": 0,
        "languages": {"Kotlin": 1},
    }
    try:
        user = api_get(f"https://api.github.com/users/{USERNAME}")
        repos = api_get(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner"
        )
        repos = [r for r in repos if not r.get("fork")]
        stars = sum(int(r.get("stargazers_count", 0)) for r in repos)
        forks = sum(int(r.get("forks_count", 0)) for r in repos)
        languages: dict[str, int] = {}
        for repo in repos[:30]:
            url = repo.get("languages_url")
            if not url:
                continue
            try:
                lang_data = api_get(url)
            except Exception:
                continue
            for name, value in lang_data.items():
                languages[name] = languages.get(name, 0) + int(value)
        if not languages:
            languages = fallback["languages"]
        return {
            "public_repos": int(user.get("public_repos", len(repos))),
            "followers": int(user.get("followers", 0)),
            "stars": stars,
            "forks": forks,
            "languages": languages,
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        print(f"GitHub API unavailable, using fallback values: {exc}")
        return fallback


def card_shell(width: int, height: int, theme: dict[str, str], body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <rect width="{width}" height="{height}" rx="16" fill="{theme['bg']}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="15" fill="none" stroke="{theme['grid']}"/>
  {body}
</svg>'''


def radar_points(items, cx, cy, radius, scale=10.0):
    n = len(items)
    points = []
    for i, item in enumerate(items):
        angle = -math.pi / 2 + (2 * math.pi * i / n)
        r = radius * float(item["value"]) / scale
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    return points


def polygon(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def radar_svg(config: dict, theme: dict[str, str]) -> str:
    width, height = 430, 330
    cx, cy, radius = 215, 170, 105
    items = config["items"]
    n = len(items)
    body = [
        f'<text x="24" y="34" fill="{theme["text"]}" font-size="18" font-weight="700" font-family="monospace">{escape(config["title"])}</text>',
        f'<text x="24" y="54" fill="{theme["muted"]}" font-size="11" font-family="monospace">self-rated development focus</text>',
    ]

    for level in (0.25, 0.5, 0.75, 1.0):
        ring = []
        for i in range(n):
            angle = -math.pi / 2 + (2 * math.pi * i / n)
            ring.append((cx + math.cos(angle) * radius * level, cy + math.sin(angle) * radius * level))
        body.append(
            f'<polygon points="{polygon(ring)}" fill="none" stroke="{theme["grid"]}" stroke-width="1"/>'
        )

    for i, item in enumerate(items):
        angle = -math.pi / 2 + (2 * math.pi * i / n)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        body.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{theme["grid"]}" stroke-width="1"/>'
        )
        lx = cx + math.cos(angle) * (radius + 32)
        ly = cy + math.sin(angle) * (radius + 26)
        anchor = "middle"
        if math.cos(angle) > 0.35:
            anchor = "start"
        elif math.cos(angle) < -0.35:
            anchor = "end"
        body.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="{theme["text"]}" font-size="11" font-family="monospace">{escape(str(item["label"]))}</text>'
        )

    data_points = radar_points(items, cx, cy, radius)
    body.append(
        f'<polygon points="{polygon(data_points)}" fill="{theme["accent"]}" fill-opacity="0.20" stroke="{theme["accent"]}" stroke-width="2.5"/>'
    )
    for x, y in data_points:
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{theme["accent2"]}"/>')

    return card_shell(width, height, theme, "\n  ".join(body))


def stats_svg(data: dict, theme: dict[str, str]) -> str:
    width, height = 500, 205
    metrics = [
        ("Public repos", data["public_repos"]),
        ("Followers", data["followers"]),
        ("Stars earned", data["stars"]),
        ("Forks", data["forks"]),
    ]
    body = [
        f'<text x="26" y="36" fill="{theme["text"]}" font-size="19" font-weight="700" font-family="monospace">GitHub system stats</text>',
        f'<text x="26" y="57" fill="{theme["muted"]}" font-size="11" font-family="monospace">generated inside this repository</text>',
    ]
    positions = [(28, 84), (258, 84), (28, 143), (258, 143)]
    for (label, value), (x, y) in zip(metrics, positions):
        body.append(f'<rect x="{x}" y="{y}" width="210" height="46" rx="10" fill="{theme["panel"]}"/>')
        body.append(f'<text x="{x + 14}" y="{y + 19}" fill="{theme["muted"]}" font-size="11" font-family="monospace">{escape(label)}</text>')
        body.append(f'<text x="{x + 14}" y="{y + 39}" fill="{theme["accent"]}" font-size="19" font-weight="700" font-family="monospace">{value}</text>')
    return card_shell(width, height, theme, "\n  ".join(body))


def languages_svg(data: dict, theme: dict[str, str]) -> str:
    width, height = 500, 205
    languages = sorted(data["languages"].items(), key=lambda kv: kv[1], reverse=True)[:5]
    total = sum(v for _, v in languages) or 1
    body = [
        f'<text x="26" y="36" fill="{theme["text"]}" font-size="19" font-weight="700" font-family="monospace">Repository language mix</text>',
        f'<text x="26" y="57" fill="{theme["muted"]}" font-size="11" font-family="monospace">aggregated from public repositories</text>',
    ]
    y = 82
    max_bar = 300
    for idx, (name, value) in enumerate(languages):
        pct = value / total
        bar_w = max(3, int(max_bar * pct))
        body.append(f'<text x="26" y="{y + 12}" fill="{theme["text"]}" font-size="11" font-family="monospace">{escape(name)}</text>')
        body.append(f'<rect x="150" y="{y}" width="300" height="13" rx="6" fill="{theme["panel"]}"/>')
        color = theme["accent"] if idx % 2 == 0 else theme["accent2"]
        body.append(f'<rect x="150" y="{y}" width="{bar_w}" height="13" rx="6" fill="{color}"/>')
        body.append(f'<text x="462" y="{y + 11}" text-anchor="end" fill="{theme["muted"]}" font-size="10" font-family="monospace">{pct * 100:.0f}%</text>')
        y += 24
    return card_shell(width, height, theme, "\n  ".join(body))


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    skills = json.loads((ASSETS / "skills.json").read_text(encoding="utf-8"))
    toolmix = json.loads((ASSETS / "toolmix.json").read_text(encoding="utf-8"))
    live = load_live_data()

    for theme_name, theme in THEMES.items():
        write(ASSETS / f"radar-skills-{theme_name}.svg", radar_svg(skills, theme))
        write(ASSETS / f"radar-tools-{theme_name}.svg", radar_svg(toolmix, theme))
        write(ASSETS / f"card-stats-{theme_name}.svg", stats_svg(live, theme))
        write(ASSETS / f"card-languages-{theme_name}.svg", languages_svg(live, theme))


if __name__ == "__main__":
    main()
