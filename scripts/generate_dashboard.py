from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
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

    border_alpha = 165 + int(55 * (0.5 + 0.5 * math.sin(t * math.tau)))
    d.rounded_rectangle((10, 10, W - 10, H - 10), radius=20, outline=(18, 189, 232, border_alpha), width=2)
    d.ellipse((29, 28, 41, 40), fill=(255, 95, 87, 255))
    d.ellipse((50, 28, 62, 40), fill=(254, 188, 46, 255))
    d.ellipse((71, 28, 83, 40), fill=(40, 200, 64, 255))
    d.text((105, 26), "jihad@dev:~/profile", font=font(15), fill=green)
    d.text((820, 27), "// BUILD SOMETHING USEFUL >_", font=font(12), fill=(90, 167, 255, 255))

    left_box = (28, 70, 505, 414)
    right_box = (525, 70, 1072, 414)
    panel_fill = (5, 19, 29, 248)
    d.rounded_rectangle(left_box, radius=16, fill=panel_fill, outline=(30, 151, 190, 255), width=2)
    d.rounded_rectangle(right_box, radius=16, fill=panel_fill, outline=(30, 151, 190, 255), width=2)
    d.text((51, 88), "● VISUAL_MAP", font=font(18, True), fill=cyan)
    d.text((389, 91), "SIGNAL_035%", font=font(10), fill=(178, 211, 224, 255))
    d.text((550, 88), "■ SYSTEM_INFO", font=font(18, True), fill=cyan)

    pulse = int(120 + 135 * (0.5 + 0.5 * math.sin(t * math.tau * 2)))
    d.text((955, 92), "ONLINE", font=font(11), fill=(53, 255, 158, pulse))
    r = 4 + int(2 * (0.5 + 0.5 * math.sin(t * math.tau * 2)))
    d.ellipse((1038-r, 96-r, 1038+r, 96+r), fill=(53, 255, 158, pulse))

    portrait_source = src.crop((25, 20, min(455, src.width), min(600, src.height))).convert("RGBA")
    portrait = fit_cover(portrait_source, (300, 270))
    portrait = ImageEnhance.Contrast(portrait.convert("RGB")).enhance(1.12).convert("RGBA")

    signal_w, signal_h = 410, 285
    signal = Image.new("RGBA", (signal_w, signal_h), (2, 15, 23, 255))
    sx = (signal_w - portrait.width) // 2
    sy = (signal_h - portrait.height) // 2

    # Raise portrait visibility while keeping the hacker/binary treatment dominant.
    p = portrait.copy()
    p.putalpha(165)
    signal.alpha_composite(p, (sx, sy))
    signal = Image.alpha_composite(signal, Image.new("RGBA", signal.size, (0, 24, 36, 68)))

    # Soft white hologram bloom over the face.
    bloom = Image.new("RGBA", signal.size, (0, 0, 0, 0))
    bl = ImageDraw.Draw(bloom)
    glow_alpha = 28 + int(14 * (0.5 + 0.5 * math.sin(t * math.tau * 1.4)))
    bl.ellipse((118, 36, 305, 250), fill=(235, 248, 255, glow_alpha))
    bloom = bloom.filter(ImageFilter.GaussianBlur(22))
    signal = Image.alpha_composite(signal, bloom)

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
    line_no = 0
    while y < signal_h - 4:
        if line_no % 3 == 1:
            fill = (225, 247, 255, 145)
        else:
            fill = (72, 234, 255, 120 + ((row_idx + idx) % 3) * 14)
        bd.text((10, y), rows[row_idx % len(rows)], font=bin_font, fill=fill)
        y += 17
        row_idx += 1
        line_no += 1

    # Thinner scanner: pale center with subtle cyan glow.
    scan_y = int(8 + (signal_h - 16) * ((idx % FRAMES) / (FRAMES - 1)))
    scan = Image.new("RGBA", signal.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    sd.rectangle((0, scan_y - 2, signal_w, scan_y + 3), fill=(35, 235, 255, 38))
    sd.rectangle((0, scan_y, signal_w, scan_y + 1), fill=(245, 252, 255, 180))
    scan = scan.filter(ImageFilter.GaussianBlur(0.8))
    signal = Image.alpha_composite(signal, scan)

    if idx in {5, 6, 15, 16, 25, 26}:
        gd = ImageDraw.Draw(signal)
        for gy, x1, x2 in ((66, 105, 315), (154, 75, 350), (223, 125, 300)):
            gd.rectangle((x1, gy, x2, gy + 1), fill=(242, 250, 255, 120))

    px, py = 48, 116
    canvas.alpha_composite(signal, (px, py))
    d.rounded_rectangle((px, py, px + signal_w, py + signal_h), radius=14, outline=cyan, width=2)
    d.text((52, 399), "> PORTRAIT.SIGNAL = 35%  •  WHITE_NOISE.LINKED", font=font(9), fill=(192, 215, 225, 255))

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

    status = "{>} READY_FOR_NEW_OPPORTUNITIES.exe"
    d.text((550, 387), status, font=font(11), fill=green)
    if (idx // 4) % 2 == 0:
        cursor_x = 550 + int(d.textlength(status, font=font(11))) + 5
        d.rectangle((cursor_x, 390, cursor_x + 6, 401), fill=green)

    # Footer identity: uppercase and comfortably separated.
    d.text((W // 2, 454), "JIHAD TIAZZITI", anchor="mm", font=font(24, True), fill=white)
    d.text((W // 2, 492), "MOBILE APPLICATION DEVELOPER", anchor="mm", font=font(10, True), fill=cyan)

    return canvas.convert("RGB")


def main():
    OUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGB")
    frames = [build_frame(src, i) for i in range(FRAMES)]
    frames[0].save(OUT_PNG, optimize=True)
    palette = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
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
