from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

SOURCE = Path("github_profile_card_jihad (1).png")
OUTPUT = Path("assets/profile-animation.gif")
WIDTH = 1100
FRAME_COUNT = 60
DURATION_MS = 85


def load_font(size: int, mono: bool = True):
    candidates = []
    if mono:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ]
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def make_glow_line(size, y, opacity, color=(0, 245, 255)):
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for off, alpha, width in [(0, opacity, 2), (2, opacity // 2, 4), (6, opacity // 4, 8)]:
        draw.line((0, y + off, w, y + off), fill=(*color, alpha), width=width)
    return layer.filter(ImageFilter.GaussianBlur(radius=2.2))


def rounded_panel(size, box, fill, outline=None, radius=12, width=2):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    return layer


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source image: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    base = Image.open(SOURCE).convert("RGBA")
    height = round(base.height * WIDTH / base.width)
    base = base.resize((WIDTH, height), Image.Resampling.LANCZOS)
    W, H = base.size

    mono_small = load_font(max(13, round(W * 0.012)))
    mono_mid = load_font(max(16, round(W * 0.0145)))
    mono_big = load_font(max(22, round(W * 0.02)))

    rx1, ry1, rx2, ry2 = int(W * 0.49), int(H * 0.06), int(W * 0.965), int(H * 0.92)

    boot_lines = [
        "BOOTING JIHAD_OS v2.0",
        "LOADING  KOTLIN MODULES ........ OK",
        "SYNCING  ANDROID SDK ............ OK",
        "CHECKING FLUTTER ENV ............ OK",
        "VERIFYING FIREBASE ACCESS ....... OK",
        "ATTACHING GITHUB PROFILE ........ OK",
        "SYSTEM READY",
    ]

    particles = [
        (int(W * 0.53) + (i * 73) % int(W * 0.38), int(H * 0.12) + (i * 41) % int(H * 0.68), 1 + (i % 3))
        for i in range(18)
    ]

    frames = []
    for i in range(FRAME_COUNT):
        t = i / (FRAME_COUNT - 1)
        frame = Image.new("RGBA", (W, H), (4, 10, 16, 255))

        reveal = ease_out_cubic(min(1.0, t / 0.22))
        slide_y = int(24 * (1 - reveal))
        base_alpha = int(255 * reveal)
        base_layer = base.copy()
        base_layer.putalpha(base_alpha)
        frame.alpha_composite(base_layer, (0, slide_y))

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        vign = int(110 * (1 - reveal))
        if vign > 0:
            d.rectangle((0, 0, W, H), fill=(0, 0, 0, vign))

        pulse = int(70 + 80 * (0.5 + 0.5 * math.sin(t * math.tau * 1.15)))
        d.rounded_rectangle((3, 3, W - 4, H - 4), radius=14, outline=(0, 240, 255, pulse), width=2)

        boot_progress = ease_out_cubic((t - 0.06) / 0.26)
        if boot_progress > 0:
            bx1, by1 = rx1 + 24, ry1 + 24
            bx2, by2 = rx2 - 22, ry1 + 168
            panel = rounded_panel(
                (W, H),
                (bx1, by1, bx2, by2),
                fill=(2, 11, 18, int(170 * boot_progress)),
                outline=(0, 210, 230, int(150 * boot_progress)),
                radius=12,
                width=2,
            )
            overlay.alpha_composite(panel)
            boot_draw = ImageDraw.Draw(overlay)
            boot_draw.text((bx1 + 18, by1 + 12), "> boot.log", font=mono_mid, fill=(50, 255, 170, int(220 * boot_progress)))

            sequence = max(0.0, min(1.0, (t - 0.10) / 0.35)) * len(boot_lines)
            lines_to_show = min(len(boot_lines), max(1, int(sequence) + 1))
            ly = by1 + 42
            for idx, line in enumerate(boot_lines[:lines_to_show]):
                if idx == lines_to_show - 1 and lines_to_show < len(boot_lines):
                    local_progress = max(0.0, min(1.0, sequence - idx))
                    line = line[: max(1, int(len(line) * local_progress))]
                boot_draw.text((bx1 + 20, ly), line, font=mono_small, fill=(210, 245, 250, int(220 * boot_progress)))
                ly += 18

        scan_y = int((H + 40) * t) - 20
        overlay = Image.alpha_composite(overlay, make_glow_line((W, H), scan_y, 90, color=(0, 238, 255)))
        d = ImageDraw.Draw(overlay)

        scan2_t = (t * 1.6) % 1.0
        scan2_x = int(lerp(rx1, rx2, scan2_t))
        d.rectangle((scan2_x - 16, ry1, scan2_x + 16, ry2), fill=(40, 255, 210, 10))

        badge_p = 0.5 + 0.5 * math.sin(t * math.tau * 2.2)
        br = 5 + int(2 * badge_p)
        cx, cy = W - 34, 26
        d.ellipse((cx - br, cy - br, cx + br, cy + br), fill=(50, 255, 150, 230))
        d.text((cx - 112, cy - 9), "LIVE PROFILE", font=mono_small, fill=(80, 255, 185, 220))

        tag_progress = ease_out_cubic((t - 0.28) / 0.22)
        if tag_progress > 0:
            tags = [
                ("STATUS", "OPEN TO WORK"),
                ("FOCUS", "ANDROID / FLUTTER"),
                ("MODE", "BUILD • LEARN • IMPROVE"),
            ]
            ty = int(H * 0.74)
            tx = int(W * 0.53)
            for idx, (a, b) in enumerate(tags):
                local = ease_out_cubic((t - (0.28 + idx * 0.05)) / 0.18)
                if local <= 0:
                    continue
                y = ty + idx * 36
                d.rounded_rectangle((tx, y, tx + 340, y + 28), radius=8, fill=(3, 12, 18, int(120 * local)), outline=(0, 170, 200, int(100 * local)), width=1)
                d.text((tx + 10, y + 6), f"{a}:", font=mono_small, fill=(65, 255, 165, int(220 * local)))
                d.text((tx + 82, y + 6), b, font=mono_small, fill=(230, 245, 250, int(220 * local)))

        msg = "> profile.ready  •  kotlin  •  android  •  flutter  •  github  •  portfolio"
        typed_p = ease_out_cubic((t - 0.34) / 0.34)
        if typed_p > 0:
            char_count = max(1, int(len(msg) * min(1.0, typed_p)))
            typed = msg[:char_count]
            tx = int(W * 0.37)
            ty = int(H * 0.89)
            d.rounded_rectangle((tx - 12, ty - 8, W - 22, ty + 30), radius=9, fill=(2, 10, 15, 175), outline=(0, 140, 170, 120), width=1)
            d.text((tx, ty), typed, font=mono_small, fill=(80, 255, 175, 235))
            if (i // 4) % 2 == 0:
                cursor_x = tx + int(d.textlength(typed, font=mono_small)) + 4
                d.rectangle((cursor_x, ty + 3, cursor_x + 8, ty + 20), fill=(0, 255, 170, 235))

        if i in {17, 18, 36, 37, 49}:
            for gy in [int(H * 0.2), int(H * 0.51), int(H * 0.77)]:
                h = 5
                crop = frame.crop((0, gy, W, gy + h))
                shifted = Image.new("RGBA", (W, h), (0, 0, 0, 0))
                shift = 8 if i % 2 == 0 else -8
                shifted.paste(crop, (shift, 0))
                frame.alpha_composite(shifted, (0, gy))
                d.rectangle((0, gy, W, gy + h), outline=(0, 255, 255, 40), width=1)

        for idx, (px, py, size) in enumerate(particles):
            offset_y = int(4 * math.sin(t * math.tau * (1.0 + idx * 0.07) + idx))
            opacity = 55 + int(35 * (0.5 + 0.5 * math.sin(t * math.tau * 1.7 + idx)))
            d.ellipse((px, py + offset_y, px + size * 2, py + offset_y + size * 2), fill=(0, 235, 255, opacity))

        if 0.18 < t < 0.28:
            a = int(170 * (1 - abs(t - 0.23) / 0.05))
            d.text((int(W * 0.515), int(H * 0.17)), "PROFILE INITIALIZED", font=mono_big, fill=(200, 255, 255, a))

        frame = Image.alpha_composite(frame, overlay).convert("RGB")
        frames.append(frame)

    palette = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    out_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    out_frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=out_frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Generated {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    main()
