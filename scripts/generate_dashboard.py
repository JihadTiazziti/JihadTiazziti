from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math

SRC = Path("github_profile_card_jihad (1).png")
OUT = Path("assets/profile-dashboard.gif")

W, H = 1200, 560
FRAME_COUNT = 42
DURATION = 95


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit_cover(im, size):
    tw, th = size
    ratio = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * ratio), round(im.height * ratio)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return im.crop((left, top, left + tw, top + th))


def pulse(t, speed=1.0):
    return 0.5 + 0.5 * math.sin(t * math.tau * speed)


def build_frame(base_source, idx):
    t = idx / FRAME_COUNT

    canvas = Image.new("RGBA", (W, H), (3, 10, 16, 255))
    d = ImageDraw.Draw(canvas)

    cyan = (38, 222, 255, 255)
    cyan2 = (72, 234, 255, 255)
    green = (53, 255, 158, 255)
    white = (237, 246, 255, 255)
    muted = (112, 155, 200, 255)
    line = (18, 61, 80, 255)

    # outer frame
    d.rounded_rectangle((12, 12, W - 12, H - 12), radius=22, outline=(18, 189, 232, 255), width=2)

    # top bar
    d.ellipse((32, 31, 44, 43), fill=(255, 95, 87, 255))
    d.ellipse((54, 31, 66, 43), fill=(254, 188, 46, 255))
    d.ellipse((76, 31, 88, 43), fill=(40, 200, 64, 255))
    d.text((112, 29), "jihad@dev:~/profile", font=font(17), fill=green)
    d.text((905, 30), "// BUILD SOMETHING USEFUL >", font=font(14), fill=(90, 167, 255, 255))

    # panels
    left_box = (32, 76, 552, 455)
    right_box = (572, 76, 1168, 455)

    d.rounded_rectangle(left_box, radius=18, fill=(5, 19, 29, 248), outline=(30, 151, 190, 255), width=2)
    d.rounded_rectangle(right_box, radius=18, fill=(5, 19, 29, 248), outline=(30, 151, 190, 255), width=2)

    d.text((58, 95), "● VISUAL_MAP", font=font(20, True), fill=cyan)
    d.text((435, 98), "SIGNAL_020%", font=font(12), fill=(120, 165, 196, 255))

    d.text((600, 95), "■ SYSTEM_INFO", font=font(20, True), fill=cyan)

    online_alpha = 180 + int(75 * pulse(t, 1.8))
    d.text((1045, 99), "ONLINE", font=font(13), fill=(53, 255, 158, online_alpha))
    d.ellipse((1130, 99, 1142, 111), fill=(53, 255, 158, online_alpha))

    # extract portrait source from the left side of the uploaded card
    portrait_source = base_source.crop((0, 0, min(500, base_source.width), base_source.height))

    # more visible face
    portrait = fit_cover(portrait_source, (300, 270))
    portrait = ImageEnhance.Contrast(portrait.convert("RGB")).enhance(1.18).convert("RGBA")
    portrait = ImageEnhance.Brightness(portrait).enhance(1.05).convert("RGBA")

    signal_w, signal_h = 410, 285
    signal = Image.new("RGBA", (signal_w, signal_h), (2, 15, 23, 255))
    sx = (signal_w - portrait.width) // 2
    sy = (signal_h - portrait.height) // 2

    p = portrait.copy()
    p.putalpha(160)
    signal.alpha_composite(p, (sx, sy))

    signal = Image.alpha_composite(signal, Image.new("RGBA", signal.size, (0, 24, 36, 62)))

    # stronger white hologram bloom
    bloom = Image.new("RGBA", signal.size, (0, 0, 0, 0))
    bl = ImageDraw.Draw(bloom)
    glow_alpha = 52 + int(24 * pulse(t, 1.4))
    bl.ellipse((110, 30, 312, 255), fill=(245, 250, 255, glow_alpha))
    bl.ellipse((145, 70, 280, 220), fill=(255, 255, 255, 24))
    bloom = bloom.filter(ImageFilter.GaussianBlur(24))
    signal = Image.alpha_composite(signal, bloom)

    # binary overlay with more white signal
    bd = ImageDraw.Draw(signal)
    bin_font = font(10)
    rows = [
        "0101010 1010101 0101011 0011010 1110010",
        "1010011 0011011 1100101 0101010 1001010",
        "0011011 1110010 0100101 1010100 0011011",
        "1100101 0101010 1011001 0010110 1110001",
    ]

    y = 14
    row_idx = 0
    line_no = 0
    while y < signal_h - 4:
        if line_no % 2 == 0:
            fill = (238, 248, 255, 178)
        else:
            fill = (88, 236, 255, 150 + ((row_idx + idx) % 3) * 14)
        bd.text((10, y), rows[row_idx % len(rows)], font=bin_font, fill=fill)
        y += 17
        row_idx += 1
        line_no += 1

    # animated scan line
    scan = Image.new("RGBA", signal.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    scan_y = 35 + int((signal_h - 70) * ((idx % FRAME_COUNT) / (FRAME_COUNT - 1)))
    sd.rectangle((0, scan_y - 5, signal_w, scan_y + 6), fill=(35, 235, 255, 72))
    sd.rectangle((0, scan_y - 1, signal_w, scan_y + 2), fill=(255, 255, 255, 248))
    scan = scan.filter(ImageFilter.GaussianBlur(1.2))
    signal = Image.alpha_composite(signal, scan)

    # slight glitch / flash
    if idx in {8, 21, 34}:
        flash = Image.new("RGBA", signal.size, (255, 255, 255, 22))
        signal = Image.alpha_composite(signal, flash)

    # signal placement
    px, py = 50, 120
    canvas.alpha_composite(signal, (px, py))

    # signal border
    d.rounded_rectangle((px, py, px + signal_w, py + signal_h), radius=14, outline=cyan, width=2)

    # inner scanner frame
    inner_x1 = px + 26
    inner_y1 = py + 18
    inner_x2 = inner_x1 + 230
    inner_y2 = inner_y1 + 210
    d.rounded_rectangle((inner_x1, inner_y1, inner_x2, inner_y2), radius=10, outline=(58, 220, 255, 190), width=1)

    d.text((58, 435), "> PORTRAIT.SIGNAL = 20%   •   WHITE_NOISE.LINKED", font=font(11), fill=(140, 166, 187, 255))

    # right info
    rows_info = [
        ("Name", "Jihad Tiazziti", white),
        ("Role", "Mobile Application Developer", white),
        ("Stack", "Kotlin / Android / Flutter / Firebase", white),
        ("Status", "● Open to opportunities", green),
        ("Focus", "Android & Mobile Apps", white),
        ("Current", "J-Shop", white),
    ]

    y_info = 150
    for label, value, value_color in rows_info:
        d.text((610, y_info), label, font=font(16), fill=muted)
        d.text((790, y_info), value, font=font(16, label == "Name"), fill=value_color)
        d.line((610, y_info + 28, 1134, y_info + 28), fill=line, width=1)
        y_info += 47

    # blinking cursor
    cursor_on = (idx // 3) % 2 == 0
    ready_text = "{>} READY_FOR_NEW_OPPORTUNITIES.exe"
    d.text((600, 425), ready_text, font=font(13), fill=green)
    if cursor_on:
        cursor_x = 600 + int(ImageDraw.Draw(Image.new("RGB", (10, 10))).textlength(ready_text, font=font(13)))
        d.rectangle((cursor_x + 4, 428, cursor_x + 10, 438), fill=green)

    # footer identity fixed
    d.text((W // 2, 500), "JIHAD TIAZZITI", anchor="ma", font=font(28, True), fill=white)
    d.text((W // 2, 526), "MOBILE APPLICATION DEVELOPER", anchor="ma", font=font(12), fill=cyan)

    return canvas.convert("RGB")


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    source = Image.open(SRC).convert("RGB")

    frames = [build_frame(source, i) for i in range(FRAME_COUNT)]

    palette = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    out_frames = [f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]

    out_frames[0].save(
        OUT,
        save_all=True,
        append_images=out_frames[1:],
        duration=DURATION,
        loop=0,
        optimize=True,
        disposal=2,
    )

    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
