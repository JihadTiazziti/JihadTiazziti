from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

SOURCE = Path("github_profile_card_jihad (1).png")
OUTPUT = Path("assets/profile-animation.gif")

WIDTH = 1100
FRAME_COUNT = 36
DURATION_MS = 95


def load_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def glow_line(size, y, opacity):
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for offset, alpha in [(0, opacity), (2, opacity // 2), (5, opacity // 4)]:
        draw.line((0, y + offset, w, y + offset), fill=(0, 238, 255, alpha), width=2)
    return layer.filter(ImageFilter.GaussianBlur(radius=2.0))


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source image: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    base = Image.open(SOURCE).convert("RGBA")
    height = round(base.height * WIDTH / base.width)
    base = base.resize((WIDTH, height), Image.Resampling.LANCZOS)

    mono = load_font(max(14, round(WIDTH * 0.014)))
    small = load_font(max(12, round(WIDTH * 0.0115)))

    frames = []
    message = "> SYSTEM ONLINE  •  KOTLIN  •  ANDROID  •  FLUTTER"

    for i in range(FRAME_COUNT):
        t = i / FRAME_COUNT
        frame = base.copy()
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Subtle animated cyan border pulse.
        pulse = int(75 + 70 * (0.5 + 0.5 * math.sin(t * math.tau)))
        inset = 3
        draw.rounded_rectangle(
            (inset, inset, frame.width - inset - 1, frame.height - inset - 1),
            radius=14,
            outline=(0, 230, 255, pulse),
            width=2,
        )

        # Terminal scan line crossing the whole card.
        scan_y = int((frame.height + 30) * t) - 15
        overlay = Image.alpha_composite(overlay, glow_line(frame.size, scan_y, 115))
        draw = ImageDraw.Draw(overlay)

        # Soft moving highlight on the right panel.
        highlight_x = int(frame.width * (0.48 + 0.46 * t))
        draw.rectangle(
            (highlight_x - 26, 0, highlight_x + 26, frame.height),
            fill=(0, 255, 210, 12),
        )

        # Typewriter status near the bottom of the card.
        visible = min(len(message), max(1, int((i / (FRAME_COUNT - 1)) * (len(message) + 8))))
        typed = message[:visible]
        tx = int(frame.width * 0.37)
        ty = int(frame.height * 0.885)
        draw.rounded_rectangle(
            (tx - 10, ty - 7, frame.width - 24, ty + 29),
            radius=8,
            fill=(3, 12, 18, 165),
        )
        draw.text((tx, ty), typed, font=small, fill=(70, 255, 176, 235))

        # Blinking cursor.
        if (i // 4) % 2 == 0:
            cursor_x = tx + int(draw.textlength(typed, font=small)) + 5
            draw.rectangle((cursor_x, ty + 3, cursor_x + 8, ty + 20), fill=(0, 255, 170, 235))

        # Small live indicator in the top-right corner.
        r = 5 + int(2 * (0.5 + 0.5 * math.sin(t * math.tau * 2)))
        cx, cy = frame.width - 35, 25
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(40, 255, 160, 235))
        draw.text((cx - 98, cy - 9), "LIVE", font=mono, fill=(80, 255, 185, 220))

        frame = Image.alpha_composite(frame, overlay).convert("RGB")
        frames.append(frame)

    # Use one shared palette to reduce file size and color flicker.
    palette = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    gif_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]

    gif_frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=gif_frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Generated {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    main()
