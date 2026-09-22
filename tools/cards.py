#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cards.py — a share card per page, 1200×630, drawn from the page's own picture.

A link with no picture shares as a grey box; a link with the wrong-shaped picture shares
as a crop of it. Each card here is the page's picture under a scrim, a kicker, the
headline, and one number where there is a number worth leading with. The credit line
is on the card itself, so a screenshot of the card still carries it.

    python3 tools/cards.py            # into build/site/cards/
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "build" / "img"
OUT = ROOT / "build" / "site" / "cards"
W, H = 1200, 630
FONTS = Path("/System/Library/Fonts/Supplemental")
DISPLAY = FONTS / "Arial Black.ttf"
BODY = FONTS / "Arial Bold.ttf"
HOT = (255, 179, 71)
CREAM = (243, 239, 230)
MUTE = (190, 182, 168)


def font(path: Path, size: int):
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:  # noqa: BLE001
        return ImageFont.load_default()


def picture(name: str) -> Image.Image | None:
    p = IMG / name
    if not p.exists():
        return None
    if p.suffix == ".svg":
        png = ROOT / "build" / "preview" / (p.stem + ".card.png")
        png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["rsvg-convert", "-w", "1400", str(p), "-o", str(png)], check=True)
        return Image.open(png).convert("RGB")
    return Image.open(p).convert("RGB")


def fit(d, text, path, size, max_w, max_lines):
    while size > 28:
        f = font(path, size)
        avg = max(1, d.textlength("MMMMMMMMMM", font=f) / 10)
        lines = textwrap.wrap(text, max(8, int(max_w / avg))) or [text]
        if len(lines) <= max_lines and all(d.textlength(x, font=f) <= max_w for x in lines):
            return f, lines
        size -= 4
    return font(path, size), textwrap.wrap(text, 26)[:max_lines]


def card(out: Path, headline: str, kicker: str, big: str = "", big_label: str = "",
         pic: str = "", focus: float = 0.5):
    base = Image.new("RGB", (W, H), (7, 7, 11))
    im = picture(pic) if pic else None
    if im is not None:
        r = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        # crop toward the focus (0 = left, 1 = right) so the interesting part shows
        x = int((im.width - W) * focus)
        base.paste(im, (-x, (H - im.height) // 2))
    # scrim: heavy at the left and the bottom, where the type goes
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        sd.line([(x, 0), (x, H)], fill=int(235 - 130 * min(1.0, x / (W * 0.85))))
    bottom = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(bottom)
    for y in range(H):
        bd.line([(0, y), (W, y)], fill=int(40 + 200 * max(0.0, (y - H * 0.3) / (H * 0.7))))
    scrim = Image.blend(scrim, bottom, 0.5).filter(ImageFilter.GaussianBlur(2))
    base = Image.composite(Image.new("RGB", (W, H), (7, 7, 11)), base, scrim)

    d = ImageDraw.Draw(base)
    pad = 64
    y = pad
    kf = font(BODY, 24)
    d.text((pad, y), kicker.upper(), font=kf, fill=HOT, spacing=4)
    y += 46
    if big:
        bf = font(DISPLAY, 132)
        SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        base_part = big.rstrip(SUP)
        sup = "".join(str(SUP.index(c)) for c in big[len(base_part):])
        bbox = d.textbbox((pad, y), base_part, font=bf)
        d.text((pad, y), base_part, font=bf, fill=(255, 255, 255))
        if sup:
            sf = font(DISPLAY, 66)
            d.text((bbox[2] + 6, y + 4), sup, font=sf, fill=(255, 255, 255))
        y = bbox[3] + 8
        if big_label:
            d.text((pad, y), big_label, font=font(BODY, 26), fill=HOT)
            y += 44
    y += 10
    hf, lines = fit(d, headline, DISPLAY, 70 if not big else 48, W - pad * 2, 3 if not big else 2)
    for line in lines:
        d.text((pad, y), line, font=hf, fill=(255, 255, 255))
        y += int(hf.size * 1.14)
    # the mark: a ring, then the name
    mf = font(DISPLAY, 26)
    cy = H - pad - 14
    d.ellipse([pad, cy - 14, pad + 28, cy + 14], outline=HOT, width=4, fill=(0, 0, 0))
    d.text((pad + 40, cy - 17), "BLACK ", font=mf, fill=CREAM)
    x2 = pad + 40 + d.textlength("BLACK ", font=mf)
    d.text((x2, cy - 17), "HOLES", font=mf, fill=HOT)
    x3 = x2 + d.textlength("HOLES", font=mf)
    d.text((x3, cy - 17), ", DRAWN", font=mf, fill=CREAM)
    cf = font(BODY, 18)
    credit = "computed here · Nan · hongdam.net · CC BY 4.0"
    d.text((W - pad - d.textlength(credit, font=cf), cy - 10), credit, font=cf, fill=MUTE)
    d.rectangle([0, 0, W - 1, H - 1], outline=HOT, width=5)
    out.parent.mkdir(parents=True, exist_ok=True)
    exif = Image.Exif()
    exif[0x013B] = "Nan, hongdam.net"                       # Artist
    exif[0x8298] = "CC BY 4.0 — https://nanobotco.github.io/black-holes/"   # Copyright
    exif[0x010E] = headline                                 # ImageDescription
    base.save(out, "JPEG", quality=84, optimize=True, progressive=True, exif=exif.tobytes())


CARDS = [
    # slug, headline, kicker, big, big_label, picture, focus
    ("index", "Black holes, drawn from the equations", "mathematical modelling, with pictures", "", "", "hero.jpg", 0.5),
    ("draw", "One dot, one ray, run backwards", "how drawing with math works", "3u²", "the whole bend, in one term", "bent.jpg", 0.55),
    ("model", "Three numbers and a horizon", "the model", "2M", "the horizon, in units where G = c = 1", "band-edge.jpg", 0.5),
    ("orbits", "Throw something at it", "generator", "6M", "the last stable circle", "angle-face.jpg", 0.5),
    ("shadow", "The shadow, by spin", "generator", "2.6×", "wider than the horizon", "ring.jpg", 0.5),
    ("waves", "A chirp you can hear", "generator", "3", "solar masses turned into waves by GW150914", "band-wide.jpg", 0.5),
    ("numbers", "Put in a mass", "generator", "10⁶⁷", "years for a Sun-mass hole to evaporate", "ring.jpg", 0.5),
    ("past", "Who discovered black holes?", "past", "1783", "John Michell, rector of Thornhill", "luminet-1979-recomputed.png", 0.5),
    ("present", "What is known, as of 2026", "present", "2", "photographed; about 300 heard", "angle-tilt.jpg", 0.5),
    ("future", "From next year to 10¹⁰⁰", "future", "2035", "LISA, three spacecraft, 2.5 million km apart", "band-wide.jpg", 0.5),
    ("legends", "The ones who got there first", "legends", "18.6", "years: Rahu's orbit, computed by 499 CE", "band-lens.jpg", 0.5),
    ("quiz", "What kind of black hole are you?", "nine questions", "9", "kinds, each with its numbers", "angle-face.jpg", 0.5),
    ("gallery", "Every picture, with its credit line", "gallery", "31", "pictures and diagrams, CC BY 4.0", "lens.jpg", 0.5),
    ("sources", "What this rests on", "sources", "88", "papers and articles, numbered", "lens-off.jpg", 0.5),
    ("about", "Attribution", "about", "CC BY", "use it, credit it, link back", "hero.jpg", 0.5),
    ("for-agents", "For agents", "the terms, where a machine will meet them", "", "", "lens.jpg", 0.5),
]

if __name__ == "__main__":
    for slug, head, kick, big, label, pic, focus in CARDS:
        card(OUT / f"{slug}.jpg", head, kick, big, label, pic, focus)
        print(f"  cards/{slug}.jpg")
