"""Génère le fond d'écran quotidien (style pluie d'hiver) pour iPhone 14 Pro.

Usage : python3 generate.py items.json fond.png
items.json : {"entete": "JEUDI 12 NOVEMBRE",
              "items": [{"cat": "HISTOIRE", "date": "12 nov. 1990", "texte": "..."},
                        {"cat": "ÉCONOMIE", ...}, {"cat": "ACTUALITÉ", ...}]}
"""
import json, random, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1179, 2556
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def f(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    random.seed(data.get("entete", ""))  # décor différent chaque jour

    # Fond : ville floue derrière une vitre
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(18 + 20 * t), int(26 + 22 * t), int(40 + 18 * t)))
    bg = bg.convert("RGBA")
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bok)
    cols = [(255, 190, 110), (255, 150, 80), (140, 180, 255), (200, 220, 255), (255, 220, 160)]
    for _ in range(70):
        x = random.randint(-50, W + 50); y = random.randint(int(H * .35), H + 50); r = random.randint(25, 110)
        bd.ellipse([x - r, y - r, x + r, y + r], fill=random.choice(cols) + (random.randint(40, 110),))
    bg = Image.alpha_composite(bg, bok.filter(ImageFilter.GaussianBlur(28)))

    # Traînées de pluie
    rain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain)
    for _ in range(260):
        x = random.randint(0, W); y = random.randint(0, H); l = random.randint(40, 160)
        rd.line([(x, y), (x - l * 0.12, y + l)], fill=(200, 215, 235, random.randint(25, 70)), width=2)
    bg = Image.alpha_composite(bg, rain.filter(ImageFilter.GaussianBlur(1)))

    # Gouttes sur la vitre
    dr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dr)
    for _ in range(180):
        x = random.randint(0, W); y = random.randint(0, H); r = random.randint(3, 13)
        dd.ellipse([x - r, y - r * 1.2, x + r, y + r * 1.2], fill=(210, 225, 245, 55))
        dd.ellipse([x - r * .4, y - r * .8, x, y - r * .3], fill=(255, 255, 255, 120))
    bg = Image.alpha_composite(bg, dr)

    # Mise en page du texte (calcul de la hauteur du panneau)
    items = data["items"]
    wrapped = [textwrap.wrap(i["texte"], 36) for i in items]
    px0, py0, px1 = 70, 1000, W - 70
    content_h = 55 + 80 + sum(58 + 58 * len(w) + 48 for w in wrapped) + 10
    py1 = min(py0 + content_h, H - 120)

    crop = bg.crop((px0, py0, px1, py1)).filter(ImageFilter.GaussianBlur(30))
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, *crop.size], radius=50, fill=255)
    bg.paste(crop, (px0, py0), mask)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([px0, py0, px1, py1], radius=50, fill=(15, 22, 35, 120),
                                         outline=(255, 255, 255, 50), width=2)
    bg = Image.alpha_composite(bg, ov)
    d = ImageDraw.Draw(bg)

    acc = [(240, 195, 120), (130, 210, 170), (140, 185, 255)]
    x = px0 + 60; y = py0 + 55
    d.text((x, y), data["entete"], font=f("DejaVuSans-Bold.ttf", 34), fill=(220, 228, 240)); y += 80
    cat_font = f("DejaVuSans-Bold.ttf", 32)
    for i, (it, lines) in enumerate(zip(items, wrapped)):
        d.text((x, y), it["cat"], font=cat_font, fill=acc[i % 3])
        w = d.textlength(it["cat"], font=cat_font)
        d.text((x + w + 20, y + 2), "· " + it["date"], font=f("DejaVuSans.ttf", 30), fill=(170, 180, 200)); y += 58
        for l in lines:
            d.text((x, y), l, font=f("DejaVuSerif.ttf", 42), fill=(245, 245, 250)); y += 58
        y += 48
        if i < len(items) - 1:
            d.line([(x, y - 24), (px1 - 60, y - 24)], fill=(255, 255, 255, 40), width=1)
    bg.convert("RGB").save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
