from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

SRC = Path("github_profile_card_jihad (1).png")
OUT_GIF = Path("assets/profile-dashboard.gif")
OUT_PNG = Path("assets/profile-dashboard.png")
W, H = 1100, 525
FRAMES = 32
DURATION = 105


def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit_cover(im, size):
    tw, th = size
    ratio = max(tw / im.width, th / im.height)
    nw, nh = max(1, round(im.width * ratio)), max(1, round(im.height * ratio))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return im.crop((left, top, left + tw, top + th))


def build_frame(src, idx):
    t = idx / FRAMES
    canvas = Image.new("RGBA", (W, H), (3, 10, 16, 255))
    d = ImageDraw.Draw(canvas)

    cyan = (38, 222, 255, 255)
    green = (53, 255, 158, 255)
    white = (237, 246, 255, 255)
    muted = (112, 155, 200, 255)
    line = (18, 61, 80, 255)

    # Outer terminal frame
    border_alpha = 165 + int(55 * (0.5 + 0.5 * math.sin(t * math.tau)))
    d.rounded_rectangle((10, 10, W - 10, H - 10), radius=20, outline=(18, 189, 232, border_alpha), width=2)
    d.ellipse((29, 28, 41, 40), fill=(255, 95, 87, 255))
    d.ellipse((50, 28, 62, 40), fill=(254, 188, 46, 255))
    d.ellipse((71, 28, 83, 40), fill=(40, 200, 64, 255))
    d.text((105, 26), "jihad@dev:~/profile", font=font(15), fill=green)
    d.text((820, 27), "// BUILD SOMETHING USEFUL >_", font=font(12), fill=(90, 167, 255, 255))

    # Main panels
    left_box = (28, 70, 505, 414)
    right_box = (525, 70, 1072, 414)
    panel_fill = (5, 19, 29, 248)
    d.rounded_rectangle(left_box, radius=16, fill=panel_fill, outline=(30, 151, 190, 255), width=2)
    d.rounded_rectangle(right_box, radius=16, fill=panel_fill, outline=(30, 151, 190, 255), width=2)
    d.text((51, 88), "● VISUAL_MAP", font=font(18, True), fill=cyan)
    d.text((389, 91), "SIGNAL_020%", font=font(10), fill=(120, 165, 196, 255))
    d.text((550, 88), "■ SYSTEM_INFO", font=font(18, True), fill=cyan)

    # ONLINE indicator pulse
    pulse = int(120 + 135 * (0.5 + 0.5 * math.sin(t * math.tau * 2)))
    d.text((955, 92), "ONLINE", font=font(11), fill=(53, 255, 158, pulse))
    r = 4 + int(2 * (0.5 + 0.5 * math.sin(t * math.tau * 2)))
    d.ellipse((1038-r, 96-r, 1038+r, 96+r), fill=(53, 255, 158, pulse))

    # Extract the portrait from the left side of the original card.
    # Tight crop + controlled cover prevents both giant-face zoom and tiny portrait syndrome.
    portrait_source = src.crop((25, 20, min(455, src.width), min(600, src.height))).convert("RGBA")
    portrait = fit_cover(portrait_source, (300, 270))

    signal_w, signal_h = 410, 285
    signal = Image.new("RGBA", (signal_w, signal_h), (2, 15, 23, 255))
    sx = (signal_w - portrait.width) // 2
    sy = (signal_h - portrait.height) // 2

    # Portrait remains recognizable but the cyber layer is still dominant.
    p = portrait.copy()
    p.putalpha(122)
    signal.alpha_composite(p, (sx, sy))
    signal = Image.alpha_composite(signal, Image.new("RGBA", signal.size, (0, 24, 36, 92)))

    # Moving binary stream.
    bd = ImageDraw.Draw(signal)
    bin_font = font(9)
    rows = [
        "01001101 11001010 00101100 10110101 01100110",
        "10100110 00110101 11001001 01010110 10010101",
        "00110110 11100101 01001011 10101001 00110110",
        "11001010 01010101 10110010 00101101 11100010",
    ]
    phase = idx % len(rows)
    y = 10 - (idx % 5)
    row_idx = phase
    while y < signal_h - 4:
        alpha = 118 + ((row_idx + idx) % 3) * 18
        bd.text((10, y), rows[row_idx % len(rows)], font=bin_font, fill=(50, 232, 255, alpha))
        y += 17
        row_idx += 1

    # Animated horizontal scanner.
    scan_y = int(8 + (signal_h - 16) * ((idx % FRAMES) / (FRAMES - 1)))
    scan = Image.new("RGBA", signal.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    sd.rectangle((0, scan_y - 1, signal_w, scan_y + 2), fill=(45, 240, 255, 210))
    scan = scan.filter(ImageFilter.GaussianBlur(1.0))
    signal = Image.alpha_composite(signal, scan)

    # Occasional tiny glitch bars.
    if idx in {7, 8, 19, 20, 29}:
        gd = ImageDraw.Draw(signal)
        for gy in (72, 164, 228):
            gd.rectangle((0, gy, signal_w, gy + 2), fill=(70, 255, 230, 95))

    px, py = 48, 116
    canvas.alpha_composite(signal, (px, py))
    d.rounded_rectangle((px, py, px + signal_w, py + signal_h), radius=14, outline=cyan, width=2)
    d.text((52, 399), "> PORTRAIT.SIGNAL = 20%  •  BINARY_STREAM.ACTIVE", font=font(9), fill=(140, 166, 187, 255))

    # Right-side information
    rows_info = [
        ("Name", "Jihad Tiazziti", white),
        ("Role", "Mobile Application Developer", white),
        ("Stack", "Kotlin / Android / Flutter / Firebase", white),
        ("Status", "● Open to opportunities", green),
        ("Focus", "Android & Mobile Apps", white),
        ("Current", "J-Shop", white),
    ]
    y = 137
    for label, value, value_color in rows_info:
        d.text((550, y), label, font=font(14), fill=muted)
        d.text((712, y), value, font=font(14, label == "Name"), fill=value_color)
        d.line((550, y + 25, 1045, y + 25), fill=line, width=1)
        y += 43

    # Animated terminal status cursor.
    status = "{>} READY_FOR_NEW_OPPORTUNITIES.exe"
    d.text((550, 387), status, font=font(11), fill=green)
    if (idx // 4) % 2 == 0:
        cursor_x = 550 + int(d.textlength(status, font=font(11))) + 5
        d.rectangle((cursor_x, 390, cursor_x + 6, 401), fill=green)

    # Cleaner footer identity: smaller and safely inside the card.
    d.text((W // 2, 462), "Jihad Tiazziti", anchor="ma", font=font(25, True), fill=white)
    d.text((W // 2, 491), "MOBILE APPLICATION DEVELOPER", anchor="ma", font=font(11), fill=cyan)

    return canvas.convert("RGB")


def main():
    OUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGB")

    frames = [build_frame(src, i) for i in range(FRAMES)]
    frames[0].save(OUT_PNG, optimize=True)

    palette = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=112)
    gif_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    gif_frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=gif_frames[1:],
        duration=DURATION,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Generated {OUT_GIF} and {OUT_PNG}")


if __name__ == "__main__":
    main()
