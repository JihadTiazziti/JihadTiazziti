from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = Path("github_profile_card_jihad (1).png")
OUT = Path("assets/profile-dashboard.png")
W, H = 1200, 540


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


def fit_crop(im, size):
    tw, th = size
    ratio = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * ratio), round(im.height * ratio)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return im.crop((left, top, left + tw, top + th))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGB")

    # The original portrait is preserved in the left side of the existing card.
    # Crop only that portrait region, then apply the cyber signal treatment.
    portrait = src.crop((0, 0, min(500, src.width), src.height))
    portrait = fit_crop(portrait, (490, 330)).convert("RGBA")

    canvas = Image.new("RGBA", (W, H), (3, 10, 16, 255))
    d = ImageDraw.Draw(canvas)

    cyan = (38, 222, 255, 255)
    green = (53, 255, 158, 255)
    white = (237, 246, 255, 255)
    muted = (112, 155, 200, 255)
    line = (18, 61, 80, 255)

    # Background and frame
    d.rounded_rectangle((12, 12, W - 12, H - 12), radius=22, outline=(18, 189, 232, 255), width=2)
    d.ellipse((32, 31, 44, 43), fill=(255, 95, 87, 255))
    d.ellipse((54, 31, 66, 43), fill=(254, 188, 46, 255))
    d.ellipse((76, 31, 88, 43), fill=(40, 200, 64, 255))
    d.text((112, 29), "jihad@dev:~/profile", font=font(17), fill=green)
    d.text((900, 30), "// BUILD SOMETHING USEFUL >_", font=font(14), fill=(90, 167, 255, 255))

    # Panels
    left_box = (32, 76, 552, 448)
    right_box = (572, 76, 1168, 448)
    d.rounded_rectangle(left_box, radius=18, fill=(5, 19, 29, 248), outline=(30, 151, 190, 255), width=2)
    d.rounded_rectangle(right_box, radius=18, fill=(5, 19, 29, 248), outline=(30, 151, 190, 255), width=2)
    d.text((58, 95), "● VISUAL_MAP", font=font(20, True), fill=cyan)
    d.text((432, 98), "SIGNAL_020%", font=font(12), fill=(120, 165, 196, 255))
    d.text((600, 95), "■ SYSTEM_INFO", font=font(20, True), fill=cyan)
    d.text((1045, 99), "ONLINE", font=font(13), fill=green)
    d.ellipse((1130, 99, 1142, 111), fill=green)

    # Portrait area - keep face recognizable but signal-dominant.
    px, py = 42, 118
    signal = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
    signal.alpha_composite(portrait)

    # dark cyan wash makes the portrait about 20-30% visually dominant
    wash = Image.new("RGBA", portrait.size, (0, 23, 34, 128))
    signal = Image.alpha_composite(signal, wash)

    # mild cyan monochrome veil, preserving facial structure
    veil = Image.new("RGBA", portrait.size, (0, 185, 220, 35))
    signal = Image.alpha_composite(signal, veil)

    # Binary stream overlay
    bd = ImageDraw.Draw(signal)
    bin_font = font(10)
    rows = [
        "01001101 11001010 00101100 10110101 01100110",
        "10100110 00110101 11001001 01010110 10010101",
        "00110110 11100101 01001011 10101001 00110110",
        "11001010 01010101 10110010 00101101 11100010",
    ]
    y = 14
    r = 0
    while y < portrait.height - 8:
        bd.text((14, y), rows[r % len(rows)], font=bin_font, fill=(50, 232, 255, 150))
        y += 19
        r += 1

    # horizontal scan signal
    scan = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    sy = 168
    sd.rectangle((0, sy - 2, portrait.width, sy + 2), fill=(50, 238, 255, 185))
    scan = scan.filter(ImageFilter.GaussianBlur(1.2))
    signal = Image.alpha_composite(signal, scan)

    canvas.alpha_composite(signal, (px, py))
    d.rounded_rectangle((px, py, px + portrait.width, py + portrait.height), radius=16, outline=cyan, width=2)
    d.text((58, 428), "> PORTRAIT.SIGNAL = 20%   •   BINARY_STREAM.ACTIVE", font=font(11), fill=(140, 166, 187, 255))

    # Right panel info
    rows_info = [
        ("Name", "Jihad Tiazziti", white),
        ("Role", "Mobile Application Developer", white),
        ("Stack", "Kotlin / Android / Flutter / Firebase", white),
        ("Status", "● Open to opportunities", green),
        ("Focus", "Android & Mobile Apps", white),
        ("Current", "J-Shop", white),
    ]
    y = 150
    for label, value, value_color in rows_info:
        d.text((610, y), label, font=font(16), fill=muted)
        d.text((790, y), value, font=font(16, label == "Name"), fill=value_color)
        d.line((610, y + 28, 1134, y + 28), fill=line, width=1)
        y += 47

    d.text((600, 423), "{>} READY_FOR_NEW_OPPORTUNITIES.exe", font=font(13), fill=green)

    # Footer identity
    d.text((600, 474), "Jihad Tiazziti", anchor="ma", font=font(34, True), fill=white)
    d.text((600, 510), "MOBILE APPLICATION DEVELOPER", anchor="ma", font=font(14), fill=cyan)

    canvas.convert("RGB").save(OUT, quality=94, optimize=True)
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
