#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""site.py — the pages, from the computed pictures and the numbers in build/facts.json.

    SITE_URL=https://nanobotco.github.io/black-holes python3 tools/site.py
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet  # noqa: E402
from css import CSS  # noqa: E402
from sources import SOURCES, BY_ID, cite as _cite  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SITE = BUILD / "site"
IMG = BUILD / "img"
SITE_URL = os.environ.get("SITE_URL", "https://nanobotco.github.io/black-holes").rstrip("/")
BASE_PATH = "/" + SITE_URL.split("//", 1)[-1].split("/", 1)[1] + "/" if "/" in SITE_URL.split("//", 1)[-1] else "/"
SELF = "black-holes"
NAME = "Black Holes, Drawn"
TAG = ("Black holes modelled and drawn from the equations — every picture computed here, "
       "generators you can run, the past, the present and the far future, and the legends that got there first.")
FLEET = fleet.load(ROOT / "data" / "fleet.json")
FACTS = json.loads((BUILD / "facts.json").read_text(encoding="utf-8"))
TODAY = date.today().isoformat()
CREDIT = "Nan · hongdam.net · CC BY 4.0"

E = html.escape

NAV = [("draw/", "Draw"), ("model/", "Model"), ("orbits/", "Orbits"), ("shadow/", "Shadow"), ("waves/", "Waves"),
       ("numbers/", "Numbers"), ("past/", "Past"), ("present/", "Present"), ("future/", "Future"),
       ("legends/", "Legends"), ("quiz/", "Quiz"), ("gallery/", "Gallery")]

ALT = {
    "hero.jpg": "A thin glowing disk around a black hole, seen nearly edge-on: the far side of the disk appears as an arch over the top and a band under the bottom, and a thin bright ring hugs the black shadow.",
    "angle-face.jpg": "The disk seen nearly face-on: a bright ring of light around a black circle.",
    "angle-tilt.jpg": "The disk at 55 degrees: an oval with the far side lifted into an arch.",
    "angle-edge.jpg": "The disk nearly edge-on: a flat band with a full arch over and under the shadow.",
    "straight.jpg": "The same disk with light going straight: a flat ellipse, half of it hidden behind the black sphere, no ring.",
    "bent.jpg": "The same disk with light bent: the hidden half reappears as an arch and a ring surrounds the shadow.",
    "no-doppler.jpg": "The disk without the Doppler shift: both sides the same brightness.",
    "lens.jpg": "A star field seen through a black hole: stars smeared into arcs around a circular shadow, a bright Einstein ring.",
    "lens-off.jpg": "The same star field with light going straight: only a black circle blocks the stars.",
    "ring.jpg": "A close view of the photon ring: a thin bright circle on the edge of the shadow, the disk behind.",
    "luminet-1979-recomputed.png": "Black ink dots on white paper, denser where the disk is brighter: the disk, its arch over the top, its band underneath, and the thin ring.",
    "band-wide.jpg": "A wide dark view of the disk from above.",
    "band-edge.jpg": "The disk almost exactly edge-on.",
    "band-lens.jpg": "Stars lensed into arcs around the shadow.",
}


def cite(*ids):
    return _cite(*ids, root=rel())


_depth = 0


def rel():
    """Links are absolute from the mount, not relative: a host that answers /black-holes/draw
    with a 200 instead of a redirect would resolve ../ one directory too high, and the 404
    page is served from any depth."""
    return BASE_PATH


def fig(name: str, caption: str, alt: str = "", cls: str = "dark", w: int = 960, h: int = 0) -> str:
    src = f"{rel()}img/{name}"
    alt = alt or ALT.get(name, caption)
    kind = name.rsplit(".", 1)[1].upper()
    return (f'<figure class="fig {cls}"><img src="{src}" alt="{E(alt)}" loading="lazy" decoding="async"'
            f'{f" width={w} height={h}" if h else ""}>'
            f'<figcaption>{caption} <span class="dl">· <a href="{src}" download>{kind}</a> · computed here · {CREDIT}</span></figcaption></figure>')


def shot(href: str, src: str, label: str, sub: str = "") -> str:
    """The linked-image formula: background, scrim, spacer, text. The box is the link."""
    return (f'<figure class="thumb"><h3><a class="shot" href="{E(href)}">'
            f'<span class="bg" style="background-image:url({E(src)})"></span>'
            f'<span class="scrim"></span><span class="sp"></span>'
            f'<span class="tx">{E(label)}{f"<small>{E(sub)}</small>" if sub else ""}</span></a></h3></figure>')


def card(href, src, label, sub, text) -> str:
    return f'<div class="card">{shot(href, src, label, sub)}<p>{text}</p></div>'


def band(img: str, kicker: str, head: str = "", line: str = "", big: str = "", big_label: str = "",
         href: str = "", cta: str = "", cls: str = "", quote: str = "") -> str:
    inner = [f'<span class="kicker">{E(kicker)}</span>']
    if big:
        inner.append(f'<p class="big">{E(big)}{f"<small>{E(big_label)}</small>" if big_label else ""}</p>')
    if head:
        inner.append(f"<h2>{E(head)}</h2>")
    if quote:
        inner.append(quote)
    if line:
        inner.append(f"<p>{line}</p>")
    if href and cta:
        inner.append(f'<a class="btn" href="{E(href)}">{E(cta)}</a>')
    return (f'<section class="band {cls}" style="background-image:url({rel()}img/{img})">'
            f'<div class="in">{"".join(inner)}</div>'
            f'<span class="cred">computed here · {CREDIT}</span></section>')


def slab(cells) -> str:
    out = []
    for v, l in cells:
        if isinstance(v, tuple):
            v = f"{E(v[0])}<small>{E(v[1])}</small>"
        else:
            v = E(v)
        out.append(f"<div><b>{v}</b><span>{E(l)}</span></div>")
    return '<div class="slab">' + "".join(out) + "</div>"


def eq(body: str, where: str = "") -> str:
    return f'<div class="eq">{body}{f"<span class=where>{where}</span>" if where else ""}</div>'


ABYSS_DE = "Wer mit Ungeheuern kämpft, mag zusehn, dass er nicht dabei zum Ungeheuer wird. Und wenn du lange in einen Abgrund blickst, blickt der Abgrund auch in dich hinein."
ABYSS_EN = "He who fights with monsters should be careful lest he thereby become a monster. And if thou gaze long into an abyss, the abyss will also gaze into thee."


def abyss(band_style=False) -> str:
    src = cite("nietzsche1886")
    if band_style:
        return (f'<blockquote><p>{E(ABYSS_EN)}</p><p class="de">{E(ABYSS_DE)}</p>'
                f'<footer>Friedrich Nietzsche, Beyond Good and Evil §146, 1886; Helen Zimmern\'s translation, 1906</footer></blockquote>')
    return (f'<blockquote class="abyss"><p>{E(ABYSS_EN)}<span class="de">{E(ABYSS_DE)}</span></p>'
            f'<footer>Friedrich Nietzsche, Jenseits von Gut und Böse §146, 1886; English by Helen Zimmern, 1906 {src}</footer></blockquote>')


# ---------------------------------------------------------------- the frame
def page(title: str, body: str, path: str, desc: str = "", cur: str = "", jsonld=None, scripts=(), card_img="card.jpg") -> str:
    global _depth
    _depth = path.count("/")
    r = rel()
    og_url = f"{SITE_URL}/{path}"
    slug = (path.strip("/") or "index").replace("/", "-").replace(".html", "")
    card_url = f"{SITE_URL}/cards/{slug}.jpg"
    nav = "".join(f'<a href="{r}{p}"{" aria-current=page" if p == cur else ""}>{E(l)}</a>' for p, l in NAV)
    ld = json.dumps(jsonld or [], ensure_ascii=False)
    sc = "".join(f'<script defer src="{r}js/{s}"></script>' for s in ("nav.js",) + tuple(scripts))
    full = f"{title} — {NAME}" if path else NAME
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full)}</title>
<meta name="description" content="{E(desc or TAG)}">
<link rel="canonical" href="{E(og_url)}">
<meta property="og:title" content="{E(title if path else NAME)}">
<meta property="og:description" content="{E(desc or TAG)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{E(og_url)}">
<meta property="og:site_name" content="{E(NAME)}">
<meta property="og:image" content="{E(card_url)}">
<meta property="og:image:secure_url" content="{E(card_url)}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{E(title if path else NAME)} — a share card from {E(NAME)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{E(card_url)}">
<meta name="twitter:image:alt" content="{E(title if path else NAME)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="author" content="Nan, hongdam.net">
<meta name="copyright" content="CC BY 4.0 — Nan, hongdam.net">
<link rel="icon" href="{r}icon.svg" type="image/svg+xml">
<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">
<link rel="alternate" type="application/atom+xml" title="{E(NAME)}" href="{r}feed.xml">
<link rel="author" href="https://hongdam.net/">
<style>{CSS}</style>
<script type="application/ld+json">{ld}</script>
{sc}
</head>
<body>
<a class="sr" href="#main">Skip to content</a>
<header class="top"><div class="in">
<a class="brand" href="{r}"><i></i>Black <b>Holes</b>, drawn</a>
<nav>{nav}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="bot"><div class="in">
<p><b>{E(NAME)}</b> — {E(TAG)}</p>
<p>Text, diagrams and pictures on this site were computed and written here and carry a <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a> licence: use them, with the credit line “{CREDIT}” and a link back. The code is MIT. Sources quoted keep their own terms and are named on the <a href="{r}sources/">sources</a> page.</p>
<p><a href="{r}about/">About and attribution</a> · <a href="{r}gallery/">Gallery</a> · <a href="{r}sources/">Sources</a> · <a href="{r}for-agents/">For agents</a> · <a href="{r}data/">Data</a> · <a href="https://github.com/NaNoBotCo/black-holes">GitHub</a> · <a href="{r}llms.txt">llms.txt</a> · <a href="{r}feed.xml">Feed</a></p>
{fleet.maker_html(roster=FLEET) if hasattr(fleet, "maker_html") else ""}
{fleet.row_html(SELF, label="More from the same publisher", roster=FLEET, ids=("hand-poke", "amulet-atlas", "chiang-mai-roads", "muay-thai", "mae-hong-son-loop", "pinot-noir", "carolina-barbecue", "index", "wichaa", "motdang"))}
{fleet.support_html(roster=FLEET)}
</div></footer>
</body></html>
"""


# ---------------------------------------------------------------- pages
def home() -> str:
    r = rel()
    f = FACTS
    b = []
    b.append(f'''<h1><span class="kind">mathematical modelling, with pictures</span>Black holes, drawn from the equations</h1>
<p class="lede">Nobody has ever seen a black hole. Every picture of one is a calculation: light traced backwards from each dot of the picture, through an equation a page long, to where it came from. This site draws them that way, in front of you, and tells the story from a country rector in 1783 to the last flash ten to the hundred years from now.</p>''')
    b.append(band("hero.jpg", "the picture, computed", cls="tall right", quote=abyss(True), href=f"{r}draw/", cta="Draw one yourself"))
    b.append(slab([
        (f"{f['rs_sun_km']:.2f} km", "the Sun's horizon radius"),
        (f"{f['rs_earth_mm']:.1f} mm", "the Earth's"),
        (f"{f['rs_m87_au']:.0f} au", "M87*'s — past Pluto's orbit"),
        (("10", "67"), "years for a Sun-mass hole to evaporate"),
        (f"{f['shadow_m87_uas']:.0f} µas", "M87*'s shadow, predicted; 42 measured"),
        ("1783", "the first one, on paper"),
    ]))
    b.append('<h2>Draw</h2>')
    b.append('<div class="grid wide">')
    b.append(card(f"{r}draw/", f"{r}img/bent.jpg", "How drawing with math works", "in easy words, then in front of you",
                  "A picture is a grid of dots. For each dot, run the light backwards and see where it lands. The whole method, and a ray tracer running on your graphics card."))
    b.append(card(f"{r}model/", f"{r}img/kerr.svg", "The model", "metrics, horizons, orbits, hair",
                  "Schwarzschild, Kerr, the photon sphere, the last stable orbit, why a settled black hole has three numbers and no more."))
    b.append(card(f"{r}orbits/", f"{r}img/orbits.svg", "Orbits", "throw something in",
                  "Rosettes, zoom-whirls and plunges. Newton on one button, Einstein on the other."))
    b.append(card(f"{r}shadow/", f"{r}img/shadows.svg", "The shadow", "Bardeen's outline, by spin",
                  "Spin it up and watch one side flatten. Put in a mass and a distance and get the size on the sky in microarcseconds."))
    b.append(card(f"{r}waves/", f"{r}img/chirp.svg", "Waves", "a chirp you can hear",
                  "Two masses spiral in. The pitch rises, the pair merge, the remnant rings. Played through your speakers at its own frequencies."))
    b.append(card(f"{r}numbers/", f"{r}img/ladder.svg", "Numbers", "put in a mass",
                  "Horizon, temperature, lifetime, entropy, the stretch across your body, and what the horizon is the size of."))
    b.append('</div>')
    b.append(band("band-lens.jpg", "past · present · future", head="Who discovered black holes?", line="Nobody, and about nine people. The idea is from 1783; the equation from 1916; proof that they form from 1939 and 1965; the name from 1964 and 1967; the first one weighed in 1972, heard in 2015, photographed in 2019.", href=f"{r}past/", cta="The past, with credit where it is due", cls="short"))
    b.append('<div class="grid wide">')
    b.append(card(f"{r}past/", f"{r}img/luminet-1979-recomputed.png", "Past", "1783 → 2019",
                  "Michell and Laplace first; Schwarzschild in a trench; Chandrasekhar at nineteen; Oppenheimer in 1939; Luminet's dots in 1979."))
    b.append(card(f"{r}present/", f"{r}img/sizes.svg", "Present", "what is known, as of 2026",
                  "Two photographed, about three hundred heard, one seen alone by its lensing, a thirty-three-solar-mass one in our neighbourhood, and the ones the JWST found too early."))
    b.append(card(f"{r}future/", f"{r}img/eras.svg", "Future", "2027 → 10¹⁰⁰",
                  "LISA, the Einstein Telescope, the photon ring from orbit; then the age when black holes are all that is left, and how it ends."))
    b.append(card(f"{r}legends/", f"{r}img/nodes.svg", "Legends", "the ones who got there first",
                  "Rahu, who eats the sun and has an orbit; the Emu drawn from the dark; Charybdis; the spaces between the worlds; the abyss."))
    b.append(card(f"{r}quiz/", f"{r}img/angle-face.jpg", "What kind of black hole are you?", "nine questions",
                  "Schwarzschild, Kerr, primordial, supermassive, merging, evaporating — with the numbers for whichever you turn out to be."))
    b.append(card(f"{r}gallery/", f"{r}img/lens.jpg", "Gallery", "every picture, with its credit line",
                  "Everything on the site, downloadable, CC BY 4.0. Attribution requested: a name and a link."))
    b.append('</div>')
    b.append(f'<h2>Three angles, one disk</h2><p>The same disk of hot gas, same black hole, seen from three places. From above it is a ring; from the side the far half rises over the top, because light from behind the hole is bent up and over to reach you.</p>')
    b.append('<div class="three">' + fig("angle-face.jpg", "12° from the axis") + fig("angle-tilt.jpg", "55°") + fig("angle-edge.jpg", "84°") + '</div>')
    return b and "".join(b)


def draw() -> str:
    r = rel()
    b = []
    b.append('<h1><span class="kind">how drawing with math works</span>One dot, one ray, run backwards</h1>')
    b.append('<p class="lede">A photograph works because light leaves things and lands on a camera. A computer can run that film in reverse: start at the camera, at one dot of the picture, and ask where the light that lands here must have come from. Near a black hole the answer bends.</p>')
    b.append('<h2>In easy words</h2>')
    b.append('''<ol class="steps">
<li><b>A picture is a grid of dots.</b> A phone photo is a few million of them. Each dot needs one colour.</li>
<li><b>Each dot is a direction.</b> The dot in the middle looks straight ahead; the dot in the top-left corner looks up and to the left. So each dot is a question: what is out there, in that direction?</li>
<li><b>Send a ray out and follow it.</b> In empty space it goes straight, so the answer is whatever it hits: a star, or nothing. Near a heavy thing the ray curves. How much it curves is a rule you can write down.</li>
<li><b>The rule is a short one.</b> Take the ray's distance from the centre, <var>r</var>. Write <var>u</var> for 1/<var>r</var>. Newton's straight line obeys <var>u</var>″ + <var>u</var> = 0. Einstein adds one term: <var>u</var>″ + <var>u</var> = 3<var>u</var>². That term is the whole bend.</li>
<li><b>Walk the ray in small steps.</b> The computer cannot solve the curve in one go, so it takes a step, asks the rule how the direction changed, takes another. A few hundred steps per ray.</li>
<li><b>Stop when something happens.</b> Three things can: the ray drops inside the horizon (paint the dot black — nothing comes back out); it lands on the glowing disk (paint the disk's colour, shifted for the disk's speed and the pull it sits in); or it flies away (paint the star it points at).</li>
<li><b>Do that for every dot.</b> A million rays, a few hundred steps each. A laptop does it in a minute; a graphics card does it thirty times a second.</li>
</ol>''')
    b.append(fig("pixels.svg", "Four dots on the grid, four fates for the rays run back from them. The looping one is why the far side of the disk shows up over the top of the hole."))
    b.append('<p>The trick is that the computer never draws the black hole. There is nothing there to draw. It draws what the black hole does to every ray that would have reached you, and the shadow is the set of dots whose rays never came back.</p>')
    b.append('<h2>With the equation on, and off</h2>')
    b.append('<p>Same disk, same camera. On the left the rays go straight, as they would past a black sphere with no gravity: half the disk is hidden behind it, and the far edge is a plain ellipse. On the right the rays bend: the hidden half reappears as an arch over the top and a band underneath, and a thin ring hugs the shadow — light that circled the hole once before leaving.</p>')
    b.append('<div class="pair">' + fig("straight.jpg", "u″ + u = 0 — light goes straight") + fig("bent.jpg", "u″ + u = 3u² — light bends") + '</div>')
    b.append('<div class="pair">' + fig("lens-off.jpg", "A star field with light going straight: the hole is a black disc") + fig("lens.jpg", "The same stars, lensed: arcs, doubles and an Einstein ring") + '</div>')
    b.append('<h2>Draw one yourself</h2><p>This one runs on your graphics card, the same rule for every dot, redrawn when you move a slider. Tilt the camera, zoom, turn the physics off and on, save the picture.</p>')
    b.append(f'''<div class="gen" id="draw">
<div class="stage"><canvas width="1280" height="720" aria-label="A black hole and its disk, drawn live from the equations"></canvas><span class="hud"></span></div>
<div class="presets">
<button type="button" data-set='{{"incl":80,"rout":22,"zoom":24,"tpeak":6800,"expo":1.15,"gravity":true,"doppler":true,"stars":true}}'>The classic view</button>
<button type="button" data-set='{{"incl":12,"rout":20,"zoom":24}}'>From above</button>
<button type="button" data-set='{{"incl":88,"rout":16,"zoom":14}}'>Edge-on, close</button>
<button type="button" data-set='{{"incl":84,"rout":14,"zoom":8}}'>The photon ring</button>
<button type="button" data-set='{{"incl":80,"rout":22,"zoom":24,"gravity":false}}'>Physics off</button>
<button type="button" data-set='{{"incl":80,"rout":6.01,"zoom":14}}'>No disk: the lens alone</button>
</div>
<div class="ctl">
<div><label for="d-incl">Camera tilt <output for="d-incl"></output></label><input type="range" id="d-incl" name="incl" min="1" max="89" value="80" data-unit="°"></div>
<div><label for="d-rout">Disk outer edge <output for="d-rout"></output></label><input type="range" id="d-rout" name="rout" min="6.01" max="40" step="0.5" value="22" data-unit=" M"></div>
<div><label for="d-zoom">Field of view <output for="d-zoom"></output></label><input type="range" id="d-zoom" name="zoom" min="6" max="40" step="0.5" value="24" data-unit=" M"></div>
<div><label for="d-tpeak">Disk temperature <output for="d-tpeak"></output></label><input type="range" id="d-tpeak" name="tpeak" min="2500" max="12000" step="100" value="6800" data-unit=" K"></div>
<div><label for="d-expo">Exposure <output for="d-expo"></output></label><input type="range" id="d-expo" name="expo" min="0.3" max="3" step="0.05" value="1.15"></div>
</div>
<div class="row">
<button type="button" data-toggle="gravity" aria-pressed="true">Gravity</button>
<button type="button" data-toggle="doppler" aria-pressed="true">Doppler shift</button>
<button type="button" data-toggle="stars" aria-pressed="true">Stars</button>
<button type="button" data-save class="ghost">Save PNG</button>
</div>
<p class="note">Units: G = c = M = 1, so the horizon is at r = 2, the photon sphere at 3, the disk's inner edge at 6. The disk is a thin Novikov–Thorne sheet on circular orbits, brightness ∝ r⁻³(1 − √(6/r)), colour a black body shifted by g = √(1 − 3/r) / (1 + Ω b sin i) — Luminet's 1979 formula{cite("luminet1979", "nt1973")}. The left side comes toward you and is brighter and bluer; the right side goes away. A phone draws this at a lower resolution than a desktop.</p>
</div>''')
    b.append('<h2>One ray at a time</h2><p>Slide the impact parameter — the distance the ray would have missed the centre by, had it gone straight — and watch the rule walk it. Below 3√3 M ≈ 5.196 M the ray falls in. Right at it, the ray circles. Above, it bends and leaves; far out, by about 4M/b, which is the number Einstein gave in 1915 and Eddington measured at the 1919 eclipse.</p>')
    b.append('''<div class="gen" id="rays">
<div class="stage"><canvas width="960" height="540" aria-label="A light ray stepping past a black hole"></canvas></div>
<div class="ctl"><div><label for="b">Impact parameter b <output for="b" id="bout"></output></label><input type="range" id="b" name="b" min="0.5" max="16" step="0.01" value="5.5"></div></div>
<div class="row"><button type="button" data-toggle="newton" aria-pressed="false">Newton instead</button><button type="button" data-toggle="fan" aria-pressed="false">Twelve at once</button></div>
<div class="read"></div>
</div>''')
    b.append(fig("bending.svg", "Twelve rays, computed. Red ones fall in; the orange one circles the photon sphere; blue ones bend and go."))
    b.append(fig("deflection.svg", "How far a ray turns, against how close it passes. The 1915 formula is the dashed line; the exact answer runs away at b = 3√3 M, where the ray loops."))
    b.append('<h2>Where the picture came from</h2>')
    b.append(f'<p>The first one was drawn in 1979 by Jean-Pierre Luminet at the Paris Observatory, on an IBM 7040 with punch cards, and then by hand: the machine printed numbers, and he placed India-ink dots on paper, denser where the disk was brighter{cite("luminet1979")}. The picture on the past page is that calculation redone here and drawn as dots the same way — not a copy of his, which is his. The film Interstellar (2014) drew a spinning one at cinema resolution with a code Kip Thorne and Double Negative wrote for it, and published the method{cite("thorne2015")}. The 2019 photograph of M87* was not drawn at all, but the ring in it is the same ring{cite("eht2019")}.</p>')
    return "".join(b)


def model() -> str:
    b = []
    b.append('<h1><span class="kind">the model</span>Three numbers and a horizon</h1>')
    b.append('<p class="lede">General relativity says how mass shapes space and time. A black hole is the simplest thing it describes: after the collapse settles, a black hole is fixed by its mass, its spin and its electric charge, and by nothing else. Everything on this page follows from that.</p>')
    b.append('<div class="toc"><a href="#metric">the metric</a><a href="#horizon">the horizon</a><a href="#light">light</a><a href="#orbits">orbits</a><a href="#kerr">spin</a><a href="#hair">no hair</a><a href="#thermo">temperature</a><a href="#penrose">Penrose diagrams</a></div>')
    b.append('<h2 id="metric">The metric</h2>')
    b.append('<p>A <dfn title="a formula for the distance between two nearby events in space and time">metric</dfn> is the rule for measuring distance. Flat space has Pythagoras. Around a mass <var>M</var> that does not spin, Schwarzschild found in 1916 that the rule becomes:</p>')
    b.append(eq("d<var>s</var>² = −(1 − 2<var>M</var>/<var>r</var>) d<var>t</var>² + d<var>r</var>² / (1 − 2<var>M</var>/<var>r</var>) + <var>r</var>² dΩ²",
                "units G = c = 1, so M is a length: the Sun's M is 1.48 km. dΩ² is the ordinary angle part of a sphere. t is time far away; r is defined so a sphere at r has area 4πr²."))
    b.append(f'<p>Two things happen at <var>r</var> = 2<var>M</var>. The first coefficient goes to zero: clocks there, seen from far away, stop. The second blows up. For twenty years this was read as a place where the theory broke. Painlevé (1921), Gullstrand (1922) and Eddington (1924) each wrote coordinates in which nothing broke there, without saying so; Lemaître said so in 1933; Finkelstein explained in 1958 what the surface is — a membrane light can cross one way{cite("schwarzschild1916", "painleve1921", "lemaitre1933", "finkelstein1958")}.</p>')
    b.append(fig("flamm.svg", "Flamm's paraboloid: the equatorial plane of Schwarzschild space, with its stretching turned into a third dimension so a ruler laid on the sheet measures the true distance. Drawn from z = 2√(2M(r − 2M)), Flamm 1916."))
    b.append('<h2 id="horizon">The horizon</h2>')
    b.append(f'<p>The <dfn title="the surface from inside which no light can reach the outside">event horizon</dfn> at <var>r</var> = 2<var>GM</var>/<var>c</var>² is not a surface of anything. A falling observer crosses it and notices nothing there; the tide across a body is 2<var>GMh</var>/<var>r</var>³, and for a big enough hole that is gentle. What the horizon is, is a fact about the future: from inside, every direction points inward. In the Penrose diagram below that is drawn as light cones that all lean toward the centre.</p>')
    b.append(slab([(f"{FACTS['rs_sun_km']:.3f} km", "r for the Sun's mass"), (f"{FACTS['rs_earth_mm']:.2f} mm", "r for the Earth's"), (f"{FACTS['tide_sun_g']:.1e} g", "stretch across a body, Sun-mass"), (f"{FACTS['tide_sgr_g']:.1e} g", "the same at Sgr A*")]))
    b.append('<h2 id="light">Light</h2>')
    b.append('<p>Light follows the straightest lines the metric allows. In the plane of a ray, with <var>u</var> = 1/<var>r</var>:</p>')
    b.append(eq("d²<var>u</var>/dφ² + <var>u</var> = 3<var>Mu</var>²", "the Binet equation for light; Newton's straight line is the same with the right side zero"))
    b.append(f"""<p>Three consequences, each visible in every picture on this site. A ray can orbit at <var>r</var> = 3<var>M</var>, the <dfn title="the sphere on which light can circle a black hole, unstably">photon sphere</dfn>. A ray from far away with impact parameter below 3√3 <var>M</var> ≈ 5.196 <var>M</var> falls in, so the shadow is 2.6 times wider than the horizon. And a ray passing at distance <var>b</var> far out turns by 4<var>M</var>/<var>b</var> — for the Sun, 1.75 arcseconds at the limb, which is what the 1919 eclipse expedition measured, twice Soldner's 1801 Newtonian value{cite("soldner1801", "eddington1920")}.</p>""")
    b.append(fig("ringstack.svg", "The bright ring in a picture is a stack: light that half-circled the hole once, twice, three times. Each subring is e^π ≈ 23 times thinner than the last, and all converge on the shadow's edge. Gralla, Holz & Wald 2019."))
    b.append('<h2 id="orbits">Orbits</h2>')
    b.append('<p>A massive particle with angular momentum <var>L</var> and energy <var>E</var> (both per unit mass) moves where <var>E</var> is at least the effective potential:</p>')
    b.append(eq("<var>V</var>(<var>r</var>)² = (1 − 2<var>M</var>/<var>r</var>)(1 + <var>L</var>²/<var>r</var>²)", "Newton's version has no rim: it rises without limit at small r. Einstein's turns over, so orbits can fall in."))
    b.append(f'<p>The rim and the well meet when <var>L</var> = √12 <var>M</var>, at <var>r</var> = 6<var>M</var>: the <dfn title="innermost stable circular orbit">ISCO</dfn>. No circular orbit inside it lasts; gas spiralling inward lets go there, which is why the disks in the pictures have a hole in them at 6<var>M</var>. Between 3<var>M</var> and 6<var>M</var> circular orbits exist but a nudge sends them in or out. Outside, bound orbits do not close: each pass turns the ellipse a little, which for Mercury is 43 arcseconds a century and for a star near Sgr A* was measured in 2020{cite("gravity2020")}.</p>')
    b.append(fig("potential.svg", "The effective potential for four angular momenta. At L = √12 M the well and the rim merge at r = 6M."))
    b.append(fig("orbits.svg", "Three orbits integrated from the equation of motion: a rosette, a zoom-whirl, a plunge."))
    b.append('<h2 id="kerr">Spin</h2>')
    b.append(f"""<p>Real black holes turn. Roy Kerr found the spinning solution in 1963 — a page and a half in Physical Review Letters — after fifty years of failed attempts{cite("kerr1963")}. Spin <var>a</var> = <var>J</var>/<var>M</var> runs from 0 to <var>M</var>. It pulls the horizon in to <var>r</var>₊ = <var>M</var> + √(<var>M</var>² − <var>a</var>²), adds a second horizon inside, wraps the outside in an <dfn title="the region outside the horizon where spacetime is dragged around faster than light, so standing still is impossible">ergosphere</dfn>, brings the last stable orbit in to <var>r</var> = <var>M</var> at maximal spin, and replaces the point at the centre with a ring. Penrose showed in 1969 that up to 29% of a spinning hole\'s mass can be drawn out of the ergosphere{cite("penrose1969")}. Gas fed from a disk can spin one up to <var>a</var> ≈ 0.998 <var>M</var>, not beyond.</p>""")
    b.append(fig("kerr.svg", "A Kerr black hole at spin 0.9, in cross-section: ergosphere, two horizons, ring singularity."))
    b.append(fig("shadows.svg", "What spin does to the shadow, from Bardeen's 1973 formula: the side turning toward you flattens. At 17°, the angle M87* is seen from, the change is small."))
    b.append('<h2 id="hair">No hair</h2>')
    b.append(f'<p>Whatever fell in — a star, a library, a planet made of gold — the settled hole outside is described by mass, spin and charge, and nothing else. Israel proved it for the still case in 1967, Carter and Robinson for the spinning one by 1975{cite("israel1967")}. Wheeler called it “a black hole has no hair”. The full family is Kerr–Newman{cite("newman1965")}; in practice charge neutralises in moments and every black hole in the sky is Kerr, with two numbers.</p>')
    b.append('<h2 id="thermo">Temperature</h2>')
    b.append(f'<p>Hawking showed in 1971 that the total horizon area can only grow{cite("hawking1971")}; Bekenstein said that an area that only grows is an entropy{cite("bekenstein1973")}; Hawking then found in 1974 that a horizon radiates like a body at a temperature set by its size{cite("hawking1974")}:</p>')
    b.append(eq("<var>T</var> = ħ<var>c</var>³ / 8π<var>GMk</var><sub>B</sub> · <var>S</var> = <var>k</var><sub>B</sub><var>A</var> / 4ℓ<sub>P</sub>² · <var>t</var> ≈ 5120π<var>G</var>²<var>M</var>³ / ħ<var>c</var>⁴",
                f"for the Sun's mass: T = {FACTS['T_sun_K']:.1e} K, S = 10⁷⁷ k_B, t = {FACTS['t_sun_yr']:.0e} years (Page's 1976 count of particle species shortens t by a factor of a few)"))
    b.append(f'<p>A Sun-mass hole is colder than the sky (2.725 K) and so takes in more than it gives; it will not begin to shrink until the universe has cooled below sixty billionths of a kelvin. A hole of {FACTS["m_evap_now_kg"]:.0e} kg — a mountain — born in the first second of the universe would be finishing about now, in a burst of gamma rays. None has been seen{cite("page1976", "wp_pbh")}.</p>')
    b.append(fig("evaporation.svg", "Hawking temperature and evaporation time by mass, on log scales. The dashed lines are the sky's temperature today and the age of the universe."))
    b.append('<h2 id="penrose">Penrose diagrams</h2>')
    b.append(f"""<p>A <dfn title="a map of spacetime squeezed so that infinity fits on the page and light always travels at 45°">Penrose diagram</dfn> squeezes all of space and time onto a page in a way that keeps light at 45°. Read the collapse one: the star\'s surface falls inward; the horizon is the 45° line; inside it, every future-pointing direction meets the wavy top, which is the singularity — a moment, not a place. The evaporating one is Hawking\'s guess at how it ends; what happens at the corner is the open question of the field{cite("wp_penrose", "almheiri2020")}.</p>""")
    b.append(fig("penrose.svg", "Three Penrose diagrams: flat space, a collapsing star, an evaporating black hole.", cls=""))
    return "".join(b)


def orbits() -> str:
    b = []
    b.append('<h1><span class="kind">generator</span>Throw something at it</h1>')
    b.append('<p class="lede">Pick an angular momentum and an energy. The particle starts at its outer turning point and falls. Newton would draw one ellipse, forever. Einstein draws a rosette, or a whirl, or a plunge.</p>')
    b.append('''<div class="gen" id="orbits">
<div class="stage"><canvas width="960" height="540" aria-label="An orbit around a black hole, drawn step by step, with the effective potential beside it"></canvas></div>
<div class="presets">
<button type="button" data-set='{"L":4.12,"E":0.9701}'>Rosette</button>
<button type="button" data-set='{"L":3.78,"E":0.9737}'>Zoom-whirl</button>
<button type="button" data-set='{"L":3.464,"E":0.9428}'>The last stable circle</button>
<button type="button" data-set='{"L":3.2,"E":0.985}'>Plunge</button>
<button type="button" data-set='{"L":4.5,"E":1.01}'>Unbound: a fly-by</button>
<button type="button" data-set='{"L":4.12,"E":0.9701,"newton":true}'>Same orbit, Newton</button>
</div>
<div class="ctl">
<div><label for="L">Angular momentum L <output for="L"></output></label><input type="range" id="L" name="L" min="2.5" max="6" step="0.01" value="4.12"></div>
<div><label for="E">Energy E <output for="E"></output></label><input type="range" id="E" name="E" min="0.90" max="1.05" step="0.0005" value="0.9701"></div>
</div>
<div class="row"><button type="button" data-toggle="newton" aria-pressed="false">Newton instead</button></div>
<div class="read"></div>
<p class="note">Units G = c = M = 1; L and E per unit mass of the particle. The right-hand panel is the effective potential V(r) for the chosen L, with E as the dashed line: where the line is above the curve the particle may be. A dip holds it; a rim it clears lets it fall.</p>
</div>''')
    b.append('<h2>Why the rosette</h2>')
    b.append(f"""<p>In Newton\'s gravity the force falls as 1/<var>r</var>², and a 1/<var>r</var>² force is the one case that closes its orbits. Einstein\'s extra term, 3<var>Mu</var>², is a 1/<var>r</var>⁴ correction. It is tiny far out and everything close in. Mercury\'s orbit turns 43 arcseconds a century from it; the star S2, passing Sagittarius A* at 120 au, turns 12 arcminutes an orbit, measured by the GRAVITY instrument in 2020{cite("gravity2020")}.</p>""")
    b.append('<h2>Why the whirl</h2>')
    b.append('<p>Just outside the rim of the potential a particle can hover at the edge of an unstable circular orbit, going round and round, before the smallest excess sends it back out. Orbits like that are what gravitational-wave detectors listen for from small things circling big ones; LISA will hear thousands of turns of them.</p>')
    b.append('<h2>Why the plunge</h2>')
    b.append('<p>Below L = √12 M there is no dip left in the potential. There is no speed, no direction, that keeps the particle out. That is a statement Newton cannot make: his potential has a well for every L above zero.</p>')
    b.append(fig("potential.svg", "The effective potential for four angular momenta. The last stable orbit is where the well and the rim meet."))
    return "".join(b)


def shadow() -> str:
    b = []
    b.append('<h1><span class="kind">generator</span>The shadow</h1>')
    b.append(f'<p class="lede">The dark patch in the middle of a picture is not the horizon. It is the set of directions from which no light comes, and it is 2.6 times wider than the horizon, because rays from behind get bent around the sides. Bardeen wrote down its exact outline in 1973 for any spin and any viewing angle{cite("bardeen1973")}. This draws it.</p>')
    b.append('''<div class="gen" id="shadow">
<div class="stage"><canvas width="960" height="540" aria-label="The outline of a spinning black hole's shadow"></canvas></div>
<div class="presets">
<button type="button" data-set='{"a":0,"th":90}'>Still</button>
<button type="button" data-set='{"a":0.9,"th":90}'>Spinning, edge-on</button>
<button type="button" data-set='{"a":0.998,"th":90}'>Nearly maximal</button>
<button type="button" data-set='{"a":0.9,"th":17,"mass":9.813,"dist":7.225}'>M87*</button>
<button type="button" data-set='{"a":0.9,"th":30,"mass":6.633,"dist":3.918}'>Sgr A*</button>
<button type="button" data-set='{"a":0.5,"th":60,"mass":0.301,"dist":0.0}'>2 M☉ at 1 parsec</button>
</div>
<div class="ctl">
<div><label for="a">Spin a/M <output for="a"></output></label><input type="range" id="a" name="a" min="0" max="0.999" step="0.001" value="0.9"></div>
<div><label for="th">Viewing angle from the axis <output for="th"></output></label><input type="range" id="th" name="th" min="1" max="90" step="1" value="17"></div>
<div><label for="mass">Mass (log₁₀ M☉) <output for="mass"></output></label><input type="range" id="mass" name="mass" min="0" max="11" step="0.001" value="9.813"></div>
<div><label for="dist">Distance (log₁₀ parsecs) <output for="dist"></output></label><input type="range" id="dist" name="dist" min="0" max="9" step="0.001" value="7.225"></div>
</div>
<div class="read"></div>
<p class="note">One microarcsecond (µas) is the width of a coin seen from the far side of the Earth. The Event Horizon Telescope resolves about 20. M87* at 6.5 billion suns and 16.8 megaparsecs predicts a 40 µas shadow; 42 ± 3 was measured. Sgr A* at 4.3 million suns and 8.3 kiloparsecs predicts 53; 51.8 ± 2.3 was measured.</p>
</div>''')
    b.append(fig("shadows.svg", "Four spins at two angles. The flat side faces the direction the hole turns toward you."))
    b.append('<h2>What a photograph of one is</h2>')
    b.append(f"""<p>The 2019 image of M87* is a ring of radio light around a dark centre, at a wavelength of 1.3 mm, made by eight telescopes on four continents recording the same night and combined afterwards as if they were one dish the size of the Earth{cite("eht2019", "wp_eht")}. The ring is light from hot gas near the photon sphere, bent around; the dark centre is the shadow. Its size measured the mass to within ten percent of what the stars orbiting the galaxy\'s centre had said. Sagittarius A* followed in 2022, harder because the gas there changes in minutes while the Earth turns for hours{cite("eht2022")}.</p>""")
    b.append(fig("sizes.svg", "Sgr A*'s horizon and shadow against Mercury's orbit; M87*'s against Neptune's and Voyager 1. To scale."))
    b.append(fig("ringstack.svg", "Inside the ring the EHT sees, a thinner one, and inside that a thinner one — the photon ring's subrings. A telescope in orbit could resolve the first of them."))
    return "".join(b)


def waves() -> str:
    b = []
    b.append('<h1><span class="kind">generator</span>A chirp you can hear</h1>')
    b.append(f"""<p class="lede">Two black holes in orbit lose energy to ripples in space and spiral in. The ripples arrive at Earth as a strain — a stretching of a 4-kilometre laser arm by a thousandth of a proton\'s width — with a pitch that rises as the pair close in. For stellar masses the pitch runs through the range of a cello. This plays it.</p>""")
    b.append('''<div class="gen" id="waves">
<div class="stage"><canvas width="960" height="400" aria-label="The chirp waveform and its frequency track"></canvas></div>
<div class="presets">
<button type="button" data-set='{"m1":36,"m2":29}'>GW150914, the first</button>
<button type="button" data-set='{"m1":85,"m2":66}'>GW190521, the heavy one</button>
<button type="button" data-set='{"m1":137,"m2":103}'>GW231123, the heaviest</button>
<button type="button" data-set='{"m1":10,"m2":10}'>Two small ones</button>
<button type="button" data-set='{"m1":30,"m2":5}'>Unequal</button>
</div>
<div class="ctl">
<div><label for="m1">Mass 1 <output for="m1"></output></label><input type="range" id="m1" name="m1" min="3" max="150" step="1" value="36"></div>
<div><label for="m2">Mass 2 <output for="m2"></output></label><input type="range" id="m2" name="m2" min="3" max="150" step="1" value="29"></div>
</div>
<div class="row"><button type="button" data-play>▶ Play the chirp</button></div>
<div class="read"></div>
<p class="note">The inspiral is the leading-order formula: the frequency runs as f ∝ (t_c − t)⁻³ᐟ⁸ and depends on the two masses only through the chirp mass (m₁m₂)³ᐟ⁵/(m₁+m₂)¹ᐟ⁵. The cut near merger is a rough one, at about 2.2 times the last-stable-orbit frequency; the ringdown is the fundamental tone of the final Kerr hole from Berti's fits. The sound is the frequency track itself, not sped up: a 36 + 29 pair sweeps 20 → 150 Hz and rings at about 250 Hz.</p>
</div>''')
    b.append(fig("chirp.svg", "The last third of a second of a 36 + 29 solar-mass merger, computed: inspiral, merger, ringdown."))
    b.append('<h2>What was heard</h2>')
    b.append(f'<p>On 14 September 2015 the two LIGO detectors, in Louisiana and Washington, recorded the same 0.2-second chirp seven milliseconds apart: 36 and 29 solar masses becoming 62, with three solar masses turned into waves, from 1.3 billion light-years away{cite("ligo2016")}. It was the first direct detection of gravitational waves, the first pair of black holes seen merging, and the first evidence that black holes of thirty solar masses exist. Weiss, Barish and Thorne got the 2017 Nobel for the detectors.</p>')
    b.append(f"""<p>By the end of the fourth observing run in November 2025 the count was about three hundred mergers. GW190521 made a 142-solar-mass hole, the first of intermediate mass{cite("gw190521")}. GW231123 was heavier still, 190–265 solar masses in total, with both partners spinning near the limit{cite("gw231123")}. GW250114, in January 2025, was loud enough to hear the final hole ring in two tones and confirm that its horizon area was larger than the sum of the two that made it — Hawking\'s 1971 theorem, tested to five sigma{cite("gw250114", "hawking1971")}.</p>""")
    b.append('<h2>And at the other end of the scale</h2>')
    b.append(f'<p>Pairs of supermassive black holes, in merging galaxies, chirp too — over years, at billionths of a hertz. In June 2023 four pulsar-timing arrays reported the hum of all of them together, read off the tick of millisecond pulsars across the Galaxy{cite("nanograv2023")}. LISA, in the 2030s, will hear the individual ones{cite("lisa2024")}.</p>')
    return "".join(b)


def numbers() -> str:
    b = []
    b.append('<h1><span class="kind">generator</span>Put in a mass</h1>')
    b.append('<p class="lede">Every property of a black hole that does not spin is a function of one number. Slide the mass from the Planck mass to the heaviest quasar and read them off, each with the formula that made it.</p>')
    b.append('''<div class="gen" id="calc">
<div class="presets">
<button type="button" data-kg="2.176e-8">Planck mass</button>
<button type="button" data-kg="5e11">Evaporating now</button>
<button type="button" data-kg="70">A person</button>
<button type="button" data-kg="5.972e24">Earth</button>
<button type="button" data-kg="1.98892e30">Sun</button>
<button type="button" data-kg="4.2e31">Cygnus X-1</button>
<button type="button" data-kg="1.23e32">GW150914's remnant</button>
<button type="button" data-kg="8.55e36">Sgr A*</button>
<button type="button" data-kg="1.29e40">M87*</button>
<button type="button" data-kg="8e40">TON 618</button>
</div>
<div class="ctl">
<div><label for="logm">Mass, log₁₀ kg</label><input type="range" id="logm" name="logm" min="-8" max="41" step="0.01" value="30.3"></div>
<div><label for="m">Mass</label><input type="text" id="m" name="m" inputmode="decimal" value="1"></div>
<div><label for="unit">Unit</label><select id="unit" name="unit"><option value="sun">solar masses</option><option value="earth">Earth masses</option><option value="kg">kilograms</option></select></div>
</div>
<p class="say note"></p>
<div class="tw"><table><thead><tr><th>Quantity</th><th>Formula</th><th>Value</th></tr></thead><tbody></tbody></table></div>
<div class="scalebar"><div class="scale"></div></div>
<p class="note">Constants: G = 6.6743 × 10⁻¹¹, c = 299 792 458, ħ = 1.0546 × 10⁻³⁴, k_B = 1.3806 × 10⁻²³, M☉ = 1.989 × 10³⁰ kg. The evaporation time is Hawking's leading form; Page's 1976 count of the particles a hole can emit shortens it by a factor of about three for small holes. The 10 g line is where a person begins to be pulled apart; a tenth of that is felt.</p>
</div>
<style>.scalebar{padding:2.6rem 1rem 3.2rem;border-top:1px solid var(--line)}.scale{position:relative;height:6px;background:linear-gradient(90deg,#c8a6ff,#8fd0ff,#ffd27a,#ff6a5e);border-radius:3px}
.scale i,.scale b{position:absolute;top:50%;width:2px;height:14px;margin-left:-1px;transform:translateY(-50%);background:var(--mute)}
.scale i span{position:absolute;top:16px;left:0;transform:translateX(-50%);font-size:.6rem;color:var(--mute);white-space:nowrap;font-style:normal}
.scale i:nth-child(odd) span{top:-24px}
.scale b{background:var(--hot);height:26px;width:4px;margin-left:-2px;box-shadow:0 0 12px var(--hot)}
.scale b span{position:absolute;top:-30px;left:0;transform:translateX(-50%);font-size:.7rem;color:var(--hot);font-weight:800;text-transform:uppercase;letter-spacing:.1em}</style>''')
    b.append(fig("ladder.svg", "The ladder of masses, from the smallest black hole physics can name to among the heaviest found, with the horizon each makes."))
    b.append(fig("tides.svg", "The stretch across a 1.8 m body at the horizon, by mass. Small holes shred you far outside; a supermassive one lets you cross without noticing."))
    b.append('<h2>Time near the horizon</h2>')
    b.append('<p>A clock held still at radius <var>r</var> runs slow by √(1 − 2<var>M</var>/<var>r</var>) compared with one far away. Near the horizon that factor goes to zero: hover close enough and the far universe runs its whole future in your afternoon. Falling in, you notice none of this; the slowness is in the comparison, not the clock.</p>')
    b.append('''<div class="gen" id="clock">
<div class="ctl"><div><label for="r">Hovering at r <output for="r"></output></label><input type="range" id="r" name="r" min="2.001" max="60" step="0.001" value="10"></div></div>
<div class="clocks"><div class="cl far"><b>far away</b><div class="face"><i class="hand"></i></div></div><div class="cl near"><b>at r</b><div class="face"><i class="hand"></i></div></div></div>
<div class="read"></div>
</div>
<style>.clocks{display:flex;gap:2rem;padding:1rem;justify-content:center;flex-wrap:wrap;border-top:1px solid var(--line)}.cl{text-align:center}.cl b{display:block;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin-bottom:.4rem}
.face{width:7rem;height:7rem;border-radius:50%;border:3px solid var(--ink);position:relative;background:radial-gradient(circle,#1a1a26,#000)}
.hand{position:absolute;left:50%;bottom:50%;width:3px;height:3rem;margin-left:-1.5px;background:var(--hot);transform-origin:bottom center;border-radius:2px}
.near .face{border-color:var(--blue)}</style>''')
    return "".join(b)


def past() -> str:
    b = []
    b.append('<h1><span class="kind">past</span>Who discovered black holes?</h1>')
    b.append('<p class="lede">Nobody, and about nine people. Each step below was taken by someone who did not know the next step existed, and several were taken twice. The first was a rector in Yorkshire, forty years before the word “scientist”.</p>')
    b.append('<div class="tw"><table><thead><tr><th>The step</th><th>Who</th><th>When</th></tr></thead><tbody>')
    for step, who, when in (
        ("The idea: a star so heavy its light falls back", "John Michell", "1783"),
        ("The same idea, in print, in French", "Pierre-Simon Laplace", "1796"),
        ("Light bent by a mass, computed", "Johann Georg von Soldner (Newton's value); Einstein (twice it)", "1801; 1915"),
        ("The equations of gravity", "Albert Einstein", "November 1915"),
        ("The exact solution around a mass", "Karl Schwarzschild; Johannes Droste, independently", "January 1916; 1916–17"),
        ("A star can have no support left", "Anderson; Stoner; Chandrasekhar; Landau", "1929–32"),
        ("The surface at 2M is a place, not a fault", "Lemaître; Finkelstein", "1933; 1958"),
        ("A collapsing star computed through its horizon", "J. Robert Oppenheimer and Hartland Snyder", "1939"),
        ("The spinning solution", "Roy Kerr", "1963"),
        ("Collapse must make a singularity — a theorem", "Roger Penrose", "1965"),
        ("The name", "Ann Ewing, reporting; John Wheeler, who made it stick", "1964; 1967"),
        ("The first one weighed", "Louise Webster, Paul Murdin; Tom Bolton (Cygnus X-1)", "1972"),
        ("They have a temperature", "Jacob Bekenstein; Stephen Hawking", "1972; 1974"),
        ("The first picture, computed", "Jean-Pierre Luminet", "1979"),
        ("The first pair heard merging", "LIGO", "2015"),
        ("The first photograph", "Event Horizon Telescope", "2019"),
    ):
        b.append(f'<tr><td>{step}</td><td><b>{who}</b></td><td class="n"><span class="year">{when}</span></td></tr>')
    b.append('</tbody></table></div>')
    b.append('<h2>Before the equations</h2>')
    b.append(f'''<div class="prose">
<h3>1783 — John Michell</h3>
<p>Michell was the rector of Thornhill, near Dewsbury, and before that a Cambridge geologist who had worked out that earthquakes travel as waves. In a letter to Henry Cavendish, read to the Royal Society on 27 November 1783 and printed the next year, he took Newton's gravity and Newton's particles of light and asked what happens if a star is heavy enough. A star five hundred times the Sun's diameter at the Sun's density, he computed, would have an escape speed above the speed of light, and so “all light emitted from such a body would be made to return towards it by its own proper gravity”. He went further: such a star could still be found, because a companion orbiting it would show its pull. That is how Cygnus X-1 was found in 1972 and Gaia BH3 in 2024{cite("michell1784", "newton1704")}.</p>
<p>His number was right for the wrong theory. In Newton's gravity the escape speed is √(2GM/r), and setting it to c gives r = 2GM/c² — the same radius Schwarzschild's metric gives, by a coincidence of the algebra. Michell had the size of a black hole a hundred and thirty-three years early.</p>
<h3>1796 — Laplace</h3>
<p>Laplace put the same argument in the Exposition du système du monde, with the same star and the conclusion that “the largest luminous bodies in the universe may be invisible”. He proved it in 1799 at the request of a German editor. Then Thomas Young's experiments made light a wave, a wave has no mass for gravity to pull on, and Laplace removed the passage from the third edition of 1808. The idea slept for a century{cite("laplace1796")}.</p>
<h3>1801 — Soldner</h3>
<p>Johann Georg von Soldner, a Bavarian surveyor, computed how far a ray grazing the Sun would bend under Newton: 0.84 arcseconds. Einstein's 1911 paper got the same value by another route, and his 1915 theory doubled it. The 1919 eclipse chose between them{cite("soldner1801", "einstein1911", "eddington1920")}.</p>
</div>''')
    b.append(band("band-edge.jpg", "1916", head="Solved in a trench", line="Karl Schwarzschild was an artillery officer on the Russian front when Einstein's field equations were published in November 1915. He found their exact solution for a single mass within weeks, sent it to Einstein, and died of a skin disease in May. Einstein read the paper to the Prussian Academy for him.", cls="short"))
    b.append(f'''<div class="prose">
<h3>1915–1917 — Einstein, Schwarzschild, Droste, Flamm</h3>
<p>Einstein expected only approximate solutions to his equations. Schwarzschild's was exact, and it contained a radius at which the formula misbehaved, r = 2M in units where G = c = 1. He did not think it meant anything physical; nor did Einstein. Johannes Droste, a student of Lorentz in Leiden, found the same solution independently and wrote it in the form used today{cite("schwarzschild1916", "droste1917")}. Ludwig Flamm, in Vienna, drew it: the equatorial plane bent into a funnel, the picture every science documentary borrows{cite("flamm1916")}. Reissner and Nordström added charge{cite("reissner1916")}.</p>
<h3>1929–1935 — Anderson, Stoner, Chandrasekhar, Landau</h3>
<p>A dead star is held up by the pressure of electrons packed as tightly as quantum mechanics allows. Wilhelm Anderson in Tartu and Edmund Stoner in Leeds found first that this pressure has a ceiling; Subrahmanyan Chandrasekhar, nineteen, on the boat from Madras to Cambridge in 1930, did the calculation with relativity in and got the limit right: 1.4 solar masses{cite("stoner1930", "chandra1931")}. Above it, nothing known held the star up. Eddington, his own sponsor, attacked the result in public in 1935 and called it “stellar buffoonery”. Lev Landau, in 1932, reached the same conclusion for neutron matter. Baade and Zwicky proposed neutron stars in 1934{cite("baade1934")}.</p>
<h3>1933 — Lemaître</h3>
<p>Painlevé, Gullstrand and Eddington had each written the Schwarzschild solution in coordinates where nothing went wrong at 2M, and none of them said what that meant. Georges Lemaître said it: the singularity there is “fictitious”, a fault of the map, not the territory{cite("painleve1921", "lemaitre1933")}.</p>
<h3>1939 — Einstein, wrong; Oppenheimer, right</h3>
<p>Einstein published a paper arguing that Schwarzschild singularities “do not exist in physical reality”, by showing that a cluster of particles cannot be squeezed inside 2M while staying in orbit. True, and beside the point: a collapsing star is not in orbit{cite("einstein1939")}. The same year Oppenheimer and Volkoff found the mass ceiling for neutron stars, and Oppenheimer and Snyder followed a collapsing star through its own horizon: to a far observer it slows and reddens and freezes at 2M; to a rider on the surface it crosses in finite time and keeps going{cite("ov1939", "os1939")}. Then the war took everyone.</p>
</div>''')
    b.append(fig("penrose.svg", "The 1939 collapse, drawn the way Penrose taught the field to draw it in the 1960s.", cls=""))
    b.append(f'''<div class="prose">
<h3>1958–1965 — Finkelstein, Kruskal, Kerr, Penrose</h3>
<p>David Finkelstein described the surface at 2M as a one-way membrane{cite("finkelstein1958")}; Kruskal and Szekeres drew the whole spacetime on one map{cite("kruskal1960")}. Maarten Schmidt measured the redshift of 3C 273 in 1963 and found a star-like point outshining a galaxy from two billion light-years away; Salpeter and Zel'dovich said within the year that gas falling onto a very massive compact object would do that, and Lynden-Bell in 1969 that most galaxies, ours included, should have one in the middle{cite("schmidt1963", "salpeter1964", "lyndenbell1969")}. Roy Kerr found the spinning solution{cite("kerr1963")}. Roger Penrose proved in 1965 that once a collapse passes a certain point, a singularity is not a possibility but a theorem — the work his 2020 Nobel cites{cite("penrose1965", "nobel2020")}.</p>
<h3>1964–1967 — the name</h3>
<p>The phrase was in print in January 1964, in Ann Ewing's report for Science News Letter of a meeting where, it seems, Robert Dicke had likened the objects to the Black Hole of Calcutta{cite("ewing1964", "wp_calcutta")}. John Wheeler used it in a lecture on 29 December 1967, after someone in an earlier audience shouted it at him when he tired of saying “gravitationally completely collapsed object”, and printed it in 1968. It stuck to him{cite("wheeler1968")}.</p>
<h3>1971–1974 — found, and warm</h3>
<p>Cygnus X-1 is an X-ray source found by rocket in 1964. In 1971–72 Louise Webster and Paul Murdin at Greenwich, and Tom Bolton in Toronto, measured the wobble of the blue supergiant beside it and weighed the unseen partner at more than the neutron-star limit — Michell's method, exactly{cite("webster1972")}. Hawking bet Thorne it was not a black hole, as insurance, and conceded in 1990. Meanwhile Hawking proved horizons only grow{cite("hawking1971")}, Bekenstein said that made them entropy{cite("bekenstein1973")}, and Hawking, trying to prove him wrong, found in 1974 that they radiate{cite("hawking1974")}.</p>
<h3>1979 — the first picture</h3>
<p>Jean-Pierre Luminet, at the Paris Observatory, traced rays from a thin disk around a Schwarzschild hole on an IBM 7040 and drew the output by hand as dots of India ink: denser where the disk is brighter, the far side lifted over the top, the near side under, one side brighter because it comes toward you{cite("luminet1979")}. The same calculation, redone here and drawn as dots:</p>
</div>''')
    b.append(fig("luminet-1979-recomputed.png", "A recomputation of Luminet's 1979 picture, drawn as ink dots. His is his; this one is this site's.", cls=""))
    b.append(f'''<div class="prose">
<h3>1992–2020 — the stars round the centre</h3>
<p>Reinhard Genzel's group in Garching and Andrea Ghez's at UCLA followed stars orbiting a point in Sagittarius for thirty years. S2 goes round every sixteen years at up to 3% of the speed of light. Its orbit gives the mass, 4.3 million suns, in a volume smaller than the Solar System; its 2018 pass showed the gravitational redshift and its 2020 analysis the Schwarzschild precession{cite("gravity2020")}. Nobel, 2020, shared with Penrose{cite("nobel2020")}.</p>
<h3>2015 and 2019 — heard, then seen</h3>
<p>The rest is on the <a href="{rel()}present/">present</a> page: GW150914 on 14 September 2015{cite("ligo2016")}, the M87* ring on 10 April 2019{cite("eht2019")}.</p>
</div>''')
    return "".join(b)


def present() -> str:
    b = []
    b.append('<h1><span class="kind">present</span>What is known, as of 2026</h1>')
    b.append(f'<p class="lede">Two have been photographed. About three hundred pairs have been heard merging. One has been seen alone, by the way it bent a star behind it. A thirty-three-solar-mass one sits 590 parsecs away. And the James Webb telescope keeps finding ones that formed too early to explain.</p>')
    b.append(slab([("2", "photographed"), ("~300", "mergers heard, O1–O4"), ("225 M☉", "heaviest merger remnant"), ("4 × 10¹⁹", "stellar-mass ones, estimated, in the observable universe"), ("z ≈ 10", "the earliest confirmed")]))
    b.append('<h2>Seen</h2>')
    b.append(f'''<div class="prose">
<p><b>M87*</b> — 6.5 billion solar masses, 16.8 megaparsecs away, photographed by the Event Horizon Telescope in April 2017 and published in April 2019: a 42-microarcsecond ring, brighter on the south side where the gas comes toward us{cite("eht2019")}. Its polarisation, mapped in 2021, shows ordered magnetic fields at the edge of the horizon, the kind that launch its 5,000-light-year jet. A second image from 2018 data, published in 2024, shows the bright spot moved — the ring is the same, the gas is not.</p>
<p><b>Sagittarius A*</b> — 4.3 million solar masses, 8.3 kiloparsecs, at the centre of the Milky Way, published May 2022: a 52-microarcsecond ring, the size the stars' orbits had predicted{cite("eht2022", "gravity2020")}. It changes in minutes, so the picture is an average of the night.</p>
<p><b>OGLE-2011-BLG-0462</b> — a dark object that passed in front of a background star in 2011 and bent its light for 270 days, with the star's position shifting by a milliarcsecond as it did. Astrometry with Hubble weighed it at about seven solar masses, alone, in the bulge, 1.6 kiloparsecs away: the first isolated stellar-mass black hole, confirmed in 2022 and again in 2025{cite("sahu2022")}.</p>
<p><b>Gaia BH1, BH2, BH3</b> — three dormant ones found by the wobble of a companion star in Gaia's astrometry, Michell's method with a space telescope. BH3, announced April 2024, is 33 solar masses and 590 parsecs away, in a stream of ancient metal-poor stars: the heaviest stellar-mass black hole known in the Galaxy, and a sign that the heavy mergers LIGO hears were made from stars like these{cite("gaiabh3")}.</p>
</div>''')
    b.append(fig("sizes.svg", "The two photographed, against the Solar System, to scale."))
    b.append('<h2>Heard</h2>')
    b.append(f'''<div class="prose">
<p>The LIGO–Virgo–KAGRA network ran its fourth observing run from May 2023 to November 2025 and roughly doubled the catalogue. Three from the run stand out. <b>GW231123</b> (November 2023, announced July 2025): total mass 190–265 solar masses, both holes spinning near the limit, heavier than stellar collapse should make — probably each the product of an earlier merger{cite("gw231123")}. <b>GW250114</b> (January 2025): the loudest signal yet, signal-to-noise about 80, clean enough to hear the final hole ring in two tones and to test that the horizon's area grew — Hawking's theorem, confirmed at 99.999%{cite("gw250114")}. And the neutron-star–black-hole pairs, which now number a handful.</p>
<p>At nanohertz, the pulsar-timing arrays' 2023 result stands: a background hum consistent with every supermassive pair in the universe, spiralling{cite("nanograv2023")}.</p>
</div>''')
    b.append(fig("chirp.svg", "A chirp, computed. GW250114's was loud enough that the ringdown at the end carried two tones."))
    b.append('<h2>Found too early</h2>')
    b.append(f'''<div class="prose">
<p>The James Webb Space Telescope, since 2022, has found black holes in the first few hundred million years that are too heavy for their age. <b>UHZ1</b>, at redshift 10.1 — 470 million years after the Big Bang — holds about 40 million solar masses, as much as its whole galaxy of stars{cite("bogdan2024")}. The <b>little red dots</b>, hundreds of faint compact red sources at redshifts 4 to 9, are read by most as small accreting black holes wrapped in dense gas{cite("lrd2024")}. A hole cannot grow from a stellar remnant to forty million suns in that time by feeding at the ordinary limit. Either it started heavy — a “direct collapse” of a gas cloud straight to a hole of ten thousand suns or more — or fed faster than the limit. Both are being argued.</p>
</div>''')
    b.append('<h2>Counted and weighed</h2>')
    b.append(f'''<div class="prose">
<p>An estimate from the history of star formation puts the number of stellar-mass black holes in the observable universe near 40 quintillion, 4 × 10¹⁹, and about a percent of all the mass in stars is now in them{cite("sicilia2022")}. The heaviest with a measurement is a matter of method: TON 618, a quasar 10 billion light-years away, is 40 or 66 billion solar masses depending on which line is fitted{cite("wp_ton618")}. Cygnus X-1, the first, was reweighed in 2021 at 21 solar masses{cite("webster2019" if False else "webster1972")}.</p>
</div>''')
    b.append('<h2>Open</h2>')
    b.append(f'''<div class="prose">
<p><b>What happens to the information.</b> Hawking radiation as he computed it is thermal, and thermal radiation carries nothing of what fell in; but quantum mechanics does not allow information to be destroyed. Since 2019 a line of work — “islands” and replica wormholes — computes the entropy of the radiation and gets the curve Page predicted in 1993, rising then falling, which is what a hole that keeps information would do{cite("almheiri2020")}. How the information gets out is still not known.</p>
<p><b>What is at the centre.</b> The theory says a singularity; the theory also says its own equations fail there. No observation reaches inside a horizon.</p>
<p><b>Whether the ones we see are Kerr.</b> The ringdown tones of GW250114 match Kerr. The shadow sizes match. Deviations, if any, are below the current precision.</p>
<p><b>Whether the small ones exist.</b> Primordial black holes in the asteroid-mass window, 10¹⁷ to 10²² grams, are not ruled out and would be all of the dark matter if they exist in the right number{cite("carr2020")}. Nothing found.</p>
</div>''')
    return "".join(b)


def future() -> str:
    b = []
    b.append('<h1><span class="kind">future</span>From next year to 10¹⁰⁰</h1>')
    b.append('<p class="lede">The near future is a list of instruments with dates. The far future is a calculation, and it belongs to black holes: after the stars and the stellar remnants are gone, they are the last things left, and they take a long time to leave.</p>')
    b.append('<h2>Instruments, in order</h2>')
    b.append('<div class="tw"><table><thead><tr><th>When</th><th>What</th><th>For</th></tr></thead><tbody>')
    for when, what, why in (
        ("by May 2027", "Nancy Grace Roman Space Telescope", "a survey of the Galactic bulge expected to catch isolated black holes by microlensing, dozens to hundreds of them, weighed"),
        ("late 2020s", "Event Horizon Telescope at 345 GHz, and more dishes", "sharper rings; a movie of M87*'s gas over weeks"),
        ("~2030", "LIGO-India, at Aundha", "a fifth detector; sky positions good enough to point a telescope at a merger in time"),
        ("2030s", "Einstein Telescope (Europe, underground, triangle of 10 km arms) and Cosmic Explorer (US, 40 km arms)", "every stellar-mass merger in the observable universe, back to the first stars"),
        ("~2031, proposed", "Black Hole Explorer (BHEX)", "a dish in orbit joined to the ground array: the photon ring's first subring, and spin from its shape"),
        ("mid-2030s", "LISA — three spacecraft, 2.5 million km apart", "supermassive pairs merging, heard for months; small holes circling big ones for thousands of turns; a test of Kerr to a part in a thousand"),
    ):
        b.append(f'<tr><td class="n"><span class="year">{when}</span></td><td><b>{what}</b></td><td>{why}</td></tr>')
    b.append('</tbody></table></div>')
    b.append(f"""<p class="small mute">Roman{cite("roman")} · Einstein Telescope{cite("et")} · Cosmic Explorer{cite("ce")} · BHEX{cite("bhex2024")} · LISA, adopted by ESA in January 2024{cite("lisa2024")}. Dates are the programmes\' own as of 2026 and move.</p>""")
    b.append(fig("ringstack.svg", "What BHEX is for: the n = 1 subring, 23 times thinner than the ring the EHT sees, whose shape measures spin without a model of the gas."))
    b.append('<h2>What they will test</h2>')
    b.append(f'''<div class="prose">
<p><b>The photon ring.</b> Its width and shape depend on the metric alone, not on the gas. Resolving the first subring would make a black hole's shadow a ruler for general relativity, independent of everything astrophysical{cite("gralla2019", "bhex2024")}.</p>
<p><b>No hair, to three decimal places.</b> A small hole circling a supermassive one for a hundred thousand turns, heard by LISA, maps the big hole's field the way a satellite maps the Earth's. Any feature beyond mass and spin shows up as a wrong note{cite("lisa2024")}.</p>
<p><b>The first stars' remains.</b> The Einstein Telescope and Cosmic Explorer would hear a 30-solar-mass merger at any distance in the observable universe, so the whole history of black hole formation becomes a catalogue{cite("et", "ce")}.</p>
<p><b>Hawking radiation.</b> A primordial black hole finishing its evaporation would end in a burst of gamma rays; the HAWC and Fermi telescopes look for it. Nothing yet. If none is ever seen, the primordial window narrows{cite("carr2020")}.</p>
</div>''')
    b.append(band("band-wide.jpg", "the far future", big="10⁶⁷", big_label="years: a Sun-mass black hole evaporates", line="The Sun will never be one; it stops at a white dwarf. But a hole of its mass, if made, outlives everything: the stars by 10⁵³ times, the protons — if they decay at all — by 10³⁰.", cls="tall"))
    b.append('<h2>The eras</h2>')
    b.append(f'''<div class="prose">
<p>Adams and Laughlin laid out the long future in 1997{cite("adams1997")}. Star formation ends around 10¹⁴ years, when the gas is used up. The last red dwarfs go out. What is left — white dwarfs, neutron stars, black holes, planets, the odd brown dwarf — drifts, collides on occasion, and is stripped from galaxies by close encounters over 10¹⁹ years. If protons decay, on a timescale of perhaps 10³⁴ to 10⁴⁰ years, the dead stars evaporate into leptons and light. Then the universe is black holes, and the radiation they make.</p>
<p>A black hole cannot shrink while the sky is warmer than it is. The cosmic background is 2.725 K now and cooling as the universe expands; a Sun-mass hole, at 6 × 10⁻⁸ K, begins to lose mass when the background falls below that, some 3 × 10¹¹ years from now. From then it is a slow leak: 2 × 10⁶⁷ years for one solar mass, 10⁸⁷ for Sagittarius A*, about 10¹⁰⁰ for the largest. The end of each is fast. In the last second a hole of 10⁹ kg gives off its remaining mass as a burst of gamma rays, brighter for that second than a galaxy. And then the dark era: photons, leptons, and the occasional positronium atom a light-year wide, decaying.</p>
</div>''')
    b.append(fig("eras.svg", "The eras, on a log scale of years. Now is at 10¹⁰."))
    b.append(fig("evaporation.svg", "Hawking temperature and lifetime against mass. A hole shrinks only once it is hotter than the sky."))
    b.append('<h2>What might be wrong with this</h2>')
    b.append('<div class="prose"><p>Every line of the far future rests on three things not yet known: whether protons decay, whether the expansion keeps accelerating, and what quantum gravity does in the last moments of an evaporation. The eras are what the known equations give when run forward; the calculation is sound, and its premises are open.</p></div>')
    return "".join(b)


def legends() -> str:
    b = []
    b.append('<h1><span class="kind">legends</span>The ones who got there first</h1>')
    b.append('<p class="lede">No myth knew about black holes. Several knew something a black hole is: a thing that eats light and cannot be seen; a dark shape drawn from where the stars are not; a whirlpool with a centre nothing leaves; a void before there was anything. Each is set beside the physics it rhymes with, and the place where the rhyme breaks.</p>')
    b.append(abyss())
    b.append(f"""<p>Nietzsche meant people. The line fits a black hole better than he could have known: look long enough at one and you see yourself. Rays that leave your side of the hole, loop the photon sphere, and come back are the image of whatever stood behind you — including you. In the ray tracer on the <a href="{rel()}draw/">draw</a> page, a camera near the hole would find the back of its own head in the ring.</p>""")
    b.append('<h2>Rahu — the eater who is a point</h2>')
    b.append(f'''<div class="prose">
<p>In the Hindu story the demon Svarbhānu drank the nectar of immortality in disguise; the Sun and Moon saw him and told Vishnu, who cut off his head. The head, immortal now, is Rahu, and it swallows the Sun and Moon whenever it catches them — the eclipse — and they fall out of its severed throat. The body is Ketu. In Thailand and Lanna, พระราหู is one of the nine planets of the calendar, offered eight black things: black chicken, black jelly grass, black coffee, black sesame, black beans, black sticky rice, black grapes, black liquor{cite("wp_rahu")}.</p>
<p>What the astronomers knew, and the story carries: Rahu and Ketu are the two <dfn title="the two points where the Moon's tilted orbit crosses the plane of the Sun's path">lunar nodes</dfn>, the points where the Moon's path, tilted 5.1°, crosses the Sun's. Eclipses happen only there. The nodes move backwards round the sky once every 18.6 years, and Āryabhaṭa had them computed by 499 CE{cite("aryabhata")}. So Rahu is a thing with no body, an orbit, a period, and the habit of taking the light away — known entirely by what it does to light. That is the definition of a black hole as the Event Horizon Telescope uses it.</p>
<p><b>Where it breaks:</b> the node is a geometric point with no mass; an eclipse is a shadow, not a capture, and the light comes back.</p>
</div>''')
    b.append(fig("nodes.svg", "The Moon's tilted path crossing the Sun's at Rahu and Ketu. The crossing points regress once in 18.6 years."))
    b.append('<h2>The dark constellations — the Emu and the Llama</h2>')
    b.append(f'''<div class="prose">
<p>Most sky traditions join bright stars into figures. Aboriginal peoples across Australia drew a figure from the dark instead: the <b>Emu in the Sky</b>, whose head is the Coalsack nebula beside the Southern Cross and whose neck and body run along the dust lanes of the Milky Way toward Scorpius and Sagittarius — toward the Galactic centre, where Sagittarius A* is. Its position through the year told when to collect emu eggs{cite("wp_emu")}. The Inca did the same in the Andes: <b>Yacana</b> the llama, drinking from the river of the Milky Way, and the serpent, the toad, the tinamou, each a dark cloud with a name{cite("wp_inca")}.</p>
<p>The rhyme is exact in one respect: a black hole's image is a dark shape against light — a shadow on the glow behind it — and the 2019 photograph is a dark constellation in miniature. Both traditions put their dark figure along the Great Rift, and our black hole sits at the end of it.</p>
<p><b>Where it breaks:</b> the dark lanes are cold dust in front of stars, not a horizon; the emu's darkness is a foreground, the shadow's is an absence.</p>
</div>''')
    b.append('<h2>Charybdis and the maelström — the whirlpool with a centre</h2>')
    b.append(f'''<div class="prose">
<p>Homer's Charybdis, in the strait beside Scylla, swallows the sea three times a day and spits it out; Odysseus survives by clinging to a fig tree above the funnel until his mast comes back up{cite("wp_charybdis")}. Poe's fisherman in “A Descent into the Maelström” (1841) watches the walls of the whirlpool and notices that cylinders sink slower than spheres and that small things sink slower than large; he ties himself to a cask and lives{cite("poe1841")}.</p>
<p>An accretion disk is the whirlpool made of gas: a spiral of material orbiting faster the further in, shedding energy as heat and light, with an edge at 6M inside which nothing circles. Poe's observation is the right kind — a rule about who falls in, read off the shapes. Michell's is the same kind of rule.</p>
<p><b>Where it breaks:</b> Charybdis gives things back. A black hole's ISCO is the last place a disk gives anything back, and below it the only return is Hawking's, 10⁶⁷ years later.</p>
</div>''')
    b.append('<h2>The spaces between the worlds</h2>')
    b.append(f'''<div class="prose">
<p>In the Pali canon, at the moment the Buddha-to-be enters his mother's womb, a light appears “even in those spaces between the worlds, vacant and abysmal, regions of blackness and utter darkness, where the light of the sun and moon, so mighty and powerful, cannot reach”{cite("mn123")}. The commentaries name them the <i>lokantarika</i>, the interstitial spaces where three world-spheres touch, dark because no sun of any of the three shines into them.</p>
<p>The picture — a region light cannot reach, defined by the geometry of the worlds around it — is closer to a horizon's definition than most. A horizon is the set of places from which light cannot reach out; the lokantarika is the set of places light cannot reach in. Each is drawn by geometry, not by any wall.</p>
<p><b>Where it breaks:</b> the lokantarika are dark by distance; a horizon is dark by direction, and it is the falling in that no light survives, not the reaching.</p>
</div>''')
    b.append('<h2>The voids before</h2>')
    b.append(f'''<div class="prose">
<p><b>Ginnungagap</b>, the yawning gap of the Norse creation, between the ice of Niflheim and the fire of Muspelheim, where the first being condenses from the meltwater{cite("wp_ginnungagap")}. <b>Chaos</b>, χάος, the gape in Hesiod, before Earth. <b>Tehom</b>, the deep of Genesis 1:2, with darkness on its face, and the Greek word for it, ἄβυσσος, which Nietzsche's Abgrund translates{cite("wp_tehom")}. <b>Te Kore</b>, the nothing of Māori cosmogony, before Te Pō, the long night, before light{cite("wp_tekore")}.</p>
<p>These are voids of beginning, not of ending, and the rhyme is with Penrose's singularity theorem run backwards: the same mathematics that says a collapse must reach a singularity says the expanding universe came from one. The black hole's singularity is the Big Bang's, mirrored.</p>
<p><b>Where it breaks:</b> a void is empty; a singularity is everything in no room.</p>
</div>''')
    b.append('<h2>The eaters of the sun</h2>')
    b.append(f'''<div class="prose">
<p><b>Apep</b>, the Egyptian serpent of the underworld, attacks the sun's boat each night and swallows it on the days of eclipse, and the priests of Ra list spells against him{cite("wp_apep")}. <b>Tiangou</b>, the heavenly dog of Chinese tradition, eats the sun and moon; people beat drums to make it spit them out{cite("wp_tiangou")}. <b>Sköll</b> and <b>Hati</b> chase them across the Norse sky and catch them at Ragnarök. <b>Louhi</b>, in the Kalevala, steals the sun and moon outright and locks them in a mountain of iron{cite("wp_kalevala")}. And <b>Xibalba</b>, the Maya underworld, is reached by a black road: the dark rift of the Milky Way, again{cite("wp_xibalba")}.</p>
<p>What the eclipse stories keep is the idea that the light can be taken — that a dark thing exists that removes a star from the sky. A black hole does that once, to whatever crosses in; and a hole passing in front of a star, the microlensing event of 2011, first brightens the star and then lets it go, which is the story's shape exactly{cite("sahu2022")}.</p>
</div>''')
    b.append('<h2>Dante at the centre</h2>')
    b.append(f'''<div class="prose">
<p>At the bottom of the Inferno, climbing down Satan's body, Dante and Virgil pass a point where they must turn over, and Virgil explains: they have crossed the centre of the Earth, “the point to which all weights are drawn from every part”{cite("dante")}. It is 1320. Gravity has a centre; the pit of the universe is where everything falls toward; and the way out is to keep going. Oppenheimer and Snyder's rider on the collapsing star would agree with the first two.</p>
<p><b>Where it breaks:</b> Dante's centre can be passed. A black hole's is not a place in space to pass but a moment in the future, and from inside the horizon every road leads to it.</p>
</div>''')
    b.append('<h2>And the name</h2>')
    b.append(f'<p>“Black hole” comes, by most accounts, from a prison: the Black Hole of Calcutta, a cell in Fort William where prisoners died overnight in June 1756. Robert Dicke, who had a house full of children and a habit of saying things had vanished “into the Black Hole of Calcutta”, is said to have used it in a lecture; a reporter printed it in 1964; Wheeler adopted it in 1967{cite("wp_calcutta", "ewing1964", "wheeler1968")}. The astronomers of the Soviet Union preferred “frozen star”, for what a far observer sees, and “collapsar” had its decade. The prison won.</p>')
    return "".join(b)


def quiz() -> str:
    b = []
    b.append('<h1><span class="kind">nine questions</span>What kind of black hole are you?</h1>')
    b.append('<p class="lede">Nine kinds, from the 1916 solution that nobody has found to the mountain-mass one finishing its evaporation somewhere right now. Whatever you turn out to be, the result comes with its numbers.</p>')
    b.append('<div class="quiz" id="quiz"><div class="bar"><i></i></div><div class="stage"></div></div>')
    b.append(abyss())
    b.append('<h2>The nine, for reference</h2>')
    b.append('<div class="tw"><table><thead><tr><th>Kind</th><th>Defined by</th><th>Found?</th></tr></thead><tbody>')
    for k, d, f_ in (
        ("Schwarzschild", "mass only; no spin, no charge (1916)", "as an idealisation; everything real turns"),
        ("Kerr", "mass and spin (1963)", "yes — most of them"),
        ("Reissner–Nordström", "mass and charge (1916–18)", "no; charge neutralises in moments"),
        ("Stellar-mass", "3 to ~100 M☉, from a collapsed star", "yes — dozens weighed, hundreds heard"),
        ("Intermediate-mass", "10² to 10⁵ M☉", "yes since 2019 — GW190521's 142 M☉ remnant"),
        ("Supermassive", "10⁶ to 10¹⁰ M☉, one per galaxy centre", "yes — two photographed"),
        ("Merging binary", "two, spiralling in", "yes — about 300 heard"),
        ("Primordial", "from density ripples in the first second", "no; still allowed at asteroid masses"),
        ("Evaporating", "hotter than the sky, so shrinking", "no; a primordial one of 5 × 10¹¹ kg would be finishing now"),
    ):
        b.append(f'<tr><td><b>{k}</b></td><td>{d}</td><td>{f_}</td></tr>')
    b.append('</tbody></table></div>')
    return "".join(b)


RAY = [("hero.jpg", "The classic view: a thin disk at 80°, Doppler-shifted, with the sky lensed behind it"),
       ("angle-face.jpg", "From 12° off the axis"), ("angle-tilt.jpg", "From 55°"), ("angle-edge.jpg", "From 84°"),
       ("straight.jpg", "Light going straight: no lensing, half the disk hidden"), ("bent.jpg", "Light bent: the far side over the top, the ring"),
       ("no-doppler.jpg", "Without the Doppler shift: both sides alike"), ("ring.jpg", "The photon ring, close"),
       ("lens.jpg", "A star field, lensed"), ("lens-off.jpg", "The same star field, not lensed"),
       ("luminet-1979-recomputed.png", "A recomputation of Luminet's 1979 picture, drawn as ink dots"),
       ("band-wide.jpg", "Wide, from 70°"), ("band-edge.jpg", "Nearly edge-on"), ("band-lens.jpg", "Lensed stars")]
DIAG = [("bending.svg", "Light past a black hole, by impact parameter"), ("deflection.svg", "Deflection angle against impact parameter"),
        ("pixels.svg", "One dot, one ray"), ("flamm.svg", "Flamm's paraboloid"), ("potential.svg", "The effective potential"),
        ("orbits.svg", "Three orbits"), ("kerr.svg", "A Kerr black hole in cross-section"), ("shadows.svg", "Shadow outlines by spin"),
        ("ringstack.svg", "The photon ring's subrings"), ("penrose.svg", "Penrose diagrams"), ("ladder.svg", "The ladder of masses"),
        ("evaporation.svg", "Hawking temperature and lifetime"), ("tides.svg", "Tidal stretch at the horizon"), ("sizes.svg", "Two black holes against the Solar System"),
        ("chirp.svg", "A gravitational-wave chirp"), ("eras.svg", "The eras of the universe"), ("nodes.svg", "Rahu and Ketu, the lunar nodes")]
FIGURE_LIST = RAY + DIAG
LIGHT = ("potential.svg", "penrose.svg", "ladder.svg", "evaporation.svg", "tides.svg", "deflection.svg", "eras.svg")
CARD_SAMPLE = (("index", "the front page"), ("draw", "Draw"), ("past", "Past"), ("legends", "Legends"), ("quiz", "Quiz"), ("numbers", "Numbers"))


def gallery() -> str:
    r = rel()
    b = []
    b.append('<h1><span class="kind">gallery</span>Every picture, with its credit line</h1>')
    b.append(f'<p class="lede">Everything below was computed for this site: the photographs by a ray tracer in numpy, the diagrams from the equations they illustrate. All of it is <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>. Use it anywhere, with the line <b>“{CREDIT}”</b> and a link to this page. That is the whole ask.</p>')
    b.append('<h2>Ray-traced</h2>')
    b.append('<div class="grid wide">' + "".join(f"<div>{fig(n, c)}</div>" for n, c in RAY) + "</div>")
    b.append('<h2>Diagrams</h2>')
    b.append('<div class="grid wide">' + "".join(f"<div>{fig(n, c, cls='' if n in LIGHT else 'dark')}</div>" for n, c in DIAG) + "</div>")
    b.append('<h2 id="cards">Share cards</h2><p>One per page, 1200 × 630, the credit line drawn on and in the file. These are what a link to a page unfurls into.</p>')
    cards = "".join(f'<div><figure class="fig"><img src="{r}cards/{sl}.jpg" alt="Share card: {E(t)}" loading="lazy" width="1200" height="630">'
                    f'<figcaption>{E(t)} <span class="dl">· <a href="{r}cards/{sl}.jpg" download>JPG</a></span></figcaption></figure></div>' for sl, t in CARD_SAMPLE)
    b.append(f'<div class="grid wide">{cards}</div>')
    b.append('<h2>How they were made</h2>')
    b.append(f"""<p>The ray tracer is 250 lines of Python with numpy, in <code>tools/render.py</code> on <a href="https://github.com/NaNoBotCo/black-holes">GitHub</a>: a Schwarzschild metric, a thin Novikov–Thorne disk, RK4 steps in φ, Luminet's redshift formula, a procedural star sky, and a tone curve. The diagrams are <code>tools/figures.py</code>: every curve integrated or evaluated, then written as SVG. The live generators are the same equations in JavaScript and GLSL, in <code>js/</code>. Rerun the scripts and you get these files back. The credit is inside each file as well as beside it: EXIF on the JPEGs, text chunks on the PNG, a licence block in every SVG's metadata.</p>""")
    return "".join(b)


def sources_page() -> str:
    b = ['<h1><span class="kind">sources</span>What this rests on</h1>',
         '<p class="lede">Papers first, then the reference articles used for dates and catalogues, then the legends. A number in the text links here.</p>',
         '<ol class="srcs">']
    for sid, text, url in SOURCES:
        n = BY_ID[sid][0]
        b.append(f'<li id="{sid}" value="{n}">{E(text)} <a href="{E(url)}" rel="noopener">link</a></li>')
    b.append('</ol><style>.srcs{max-width:48rem;padding-left:2.4rem}.srcs li{margin:.5rem 0;font-size:.92rem;color:var(--mute)}.srcs li:target{color:var(--ink);background:color-mix(in srgb,var(--hot) 12%,transparent);border-radius:6px;padding:.2rem .4rem}.srcs li a{white-space:nowrap}</style>')
    return "".join(b)


def about() -> str:
    b = []
    b.append('<h1><span class="kind">about</span>Attribution</h1>')
    b.append(f'''<div class="prose">
<p>This site was built at <a href="https://hongdam.net/">Hongdam</a> in Chiang Rai, by Nan. Every picture on it was computed for it; every diagram was drawn from the equation it shows; every fact has a source on the <a href="{rel()}sources/">sources</a> page.</p>
<h3>Use it</h3>
<p>Text, pictures and diagrams: <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">Creative Commons Attribution 4.0</a>. Copy, adapt, print, teach from, sell. The one condition is a credit — <b>“{CREDIT}”</b> — with a link to <a href="{SITE_URL}/">{SITE_URL}/</a>. Code, in <code>tools/</code> and <code>js/</code>: MIT.</p>
<p>What is not this site's to give: the quotations, which belong to their authors and are used in brief with their sources named; the Nietzsche and Zimmern texts, which are out of copyright; and the results cited, which are their discoverers'.</p>
<h3>Cite it</h3>
<pre><code>Nan (2026). Black Holes, Drawn: mathematical modelling of black holes, with pictures.
Hongdam, Chiang Rai. {SITE_URL}/  CC BY 4.0.</code></pre>
<h3>What was checked, and how</h3>
<p>The ray tracer reproduces Luminet's 1979 figure, the arch-and-band shape of the Interstellar renders, and the 2.6-to-1 shadow-to-horizon ratio. The shadow generator reproduces the D-shape Bardeen drew and the EHT's measured sizes for M87* and Sgr A* to within their error bars from the published masses and distances. The chirp generator reproduces GW150914's 0.2-second duration from 35 Hz and its ~250 Hz ringdown. The calculator's constants are CODATA 2018. The dates on the past page follow the primary papers listed; where popular accounts disagree (who first said “black hole”), the page says so.</p>
<p>Numbers on this site are computed at build time from the formulas, not typed in: the horizon radii, the temperatures, the shadow sizes, the tides. Change a constant in <code>tools/figures.py</code> and the pages change.</p>
<h3>Not on this site</h3>
<p>Photographs from the Event Horizon Telescope, LIGO's strain plots, Luminet's original — all are their institutions' and are linked, not copied. Wormholes, white holes and the inside of the horizon beyond what the equations say. Astrology: Rahu is here as the model of an invisible thing with a period, which is what the astronomers who computed him made, and the offering list is recorded as practice.</p>
<h3>Build</h3>
<pre><code>python3 tools/render.py     # the ray-traced pictures, ~4 minutes
python3 tools/figures.py    # the diagrams and build/facts.json
python3 tools/site.py       # the pages, into build/site/
./publish.sh                # all of it, checked, into docs/</code></pre>
</div>''')
    return "".join(b)


ATTRIB = "Nan, Black Holes, Drawn (2026), https://nanobotco.github.io/black-holes/, CC BY 4.0"

SHAPES = [
    ("llms.txt", "the page map, one line per page"),
    ("llms-full.txt", "every page flattened to plain text, in reading order"),
    ("corpus.jsonl", "one JSON object per section: heading, text, the sources it cites, url, licence, attribution"),
    ("data/facts.json", "the numbers the pages print, computed by tools/figures.py from the constants"),
    ("data/figures.json", "every diagram and picture: file, title, alt text, kind, licence"),
    ("data/sources.json", "all the citations, keyed by the numbers in the text"),
    ("data/pages.json", "the pages, with titles, descriptions, share cards and word counts"),
    ("data/dataset.json", "the same, as a schema.org Dataset"),
    ("cards/", "a 1200×630 share card per page, credit line on the card and in its EXIF"),
    ("img/", "the pictures (EXIF Artist and Copyright set) and the SVGs (cc:license in their metadata)"),
    ("feed.xml", "Atom, one entry per page"),
    ("CITATION.cff · LICENSE · LICENSE-CODE · NOTICE.txt", "in the repository: how to name this, and the terms in SPDX form"),
]


def for_agents() -> str:
    r = rel()
    b = ['<h1><span class="kind">for agents</span>The terms, where a machine will meet them</h1>',
         '<p class="lede">This site draws things that cannot be seen from the equations that govern them. Everything on it was computed here, and everything on it is yours to take. Two things are asked in return: name the source, and carry the licence with the copy.</p>',
         '<h2>The terms</h2>',
         f'<div class="prose"><p>Text, diagrams, pictures and data: <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">Creative Commons Attribution 4.0</a> (SPDX <code>CC-BY-4.0</code>). Code in <code>tools/</code> and <code>js/</code>: MIT (SPDX <code>MIT</code>). Quotations and cited results belong to their authors and are named beside each use.</p>'
         f'<p>The attribution string is <b>{E(ATTRIB)}</b>. <code>CITATION.cff</code> in the repository carries the structured form. Train on it, quote it, index it, redraw it, clone it: attribution is the whole ask. Share-alike is not a term here, so a work made from this may carry any licence.</p></div>',
         '<h2>The shapes</h2><p>Reading this as a machine? These save you a crawl.</p><div class="tw"><table><thead><tr><th>File</th><th>What it is</th></tr></thead><tbody>']
    for f, what in SHAPES:
        href = {"cards/": f"{r}gallery/#cards", "img/": f"{r}data/figures.json"}.get(f, f"{r}{f}")
        if f.startswith("CITATION"):
            href = "https://github.com/NaNoBotCo/black-holes"
        b.append(f'<tr><td><a href="{href}"><code>{E(f)}</code></a></td><td>{E(what)}</td></tr>')
    b.append('</tbody></table></div>')
    b.append('<h2>What is inside the pictures</h2>')
    b.append('<div class="prose"><p>Each JPEG carries EXIF <code>Artist</code>, <code>Copyright</code> and <code>ImageDescription</code>; the PNG carries the same as text chunks; each SVG carries a <code>cc:license</code> block in its metadata and its alt text in <code>&lt;desc&gt;</code>. Each share card has the credit line drawn on it. A copy of a file is a copy of its credit.</p>'
             '<p>The pictures are not photographs of anything. They are the Schwarzschild metric, integrated: <code>tools/render.py</code> in the repository reproduces each one from a seed, and <code>tools/figures.py</code> each diagram. The equations are printed on the pages beside them, so a model can check a picture against its formula.</p></div>')
    b.append('<h2>What to do with a correction</h2>')
    b.append(f'<div class="prose"><p>A number on this site is computed from a constant in <code>tools/figures.py</code>; a date on the past page comes from a paper on the <a href="{r}sources/">sources</a> page. If either is wrong, the repository takes issues and pull requests: <a href="https://github.com/NaNoBotCo/black-holes">github.com/NaNoBotCo/black-holes</a>. Contact: Nan · nan@motdang.net.</p></div>')
    return "".join(b)


def data_index() -> str:
    r = rel()
    b = ['<h1><span class="kind">data</span>The numbers, as files</h1>',
         '<p class="lede">What the pages print, in JSON, with the formula or source beside each value. CC BY 4.0.</p><div class="tw"><table><thead><tr><th>File</th><th>What it is</th></tr></thead><tbody>']
    for f, what in SHAPES:
        if f.startswith("data/") or f in ("corpus.jsonl", "llms-full.txt"):
            b.append(f'<tr><td><a href="{r}{f}"><code>{E(f)}</code></a></td><td>{E(what)}</td></tr>')
    b.append(f'</tbody></table></div><p>The terms in prose: <a href="{r}for-agents/">for agents</a>.</p>')
    return "".join(b)


def not_found() -> str:
    return ('<h1><span class="kind">404</span>Past the horizon</h1><p class="lede">There is no page here, and nothing comes back from where you were headed. '
            f'The <a href="{rel()}">front page</a> is the way out.</p>' + fig("ring.jpg", "The photon ring."))


# ---------------------------------------------------------------- write
PAGES = [
    ("", "Black holes, drawn from the equations", home, "", (), "hero.jpg"),
    ("draw/", "How drawing with math works", draw, "Draw", ("draw.js", "rays2d.js"), "bent.jpg"),
    ("model/", "The model: three numbers and a horizon", model, "Model", (), "hero.jpg"),
    ("orbits/", "Orbits — throw something at it", orbits, "Orbits", ("orbits.js",), "hero.jpg"),
    ("shadow/", "The shadow", shadow, "Shadow", ("shadow.js",), "ring.jpg"),
    ("waves/", "Waves — a chirp you can hear", waves, "Waves", ("waves.js",), "hero.jpg"),
    ("numbers/", "Numbers — put in a mass", numbers, "Numbers", ("calc.js", "clock.js"), "hero.jpg"),
    ("past/", "Past — who discovered black holes?", past, "Past", (), "luminet-1979-recomputed.png"),
    ("present/", "Present — what is known, as of 2026", present, "Present", (), "hero.jpg"),
    ("future/", "Future — from next year to 10^100", future, "Future", (), "band-wide.jpg"),
    ("legends/", "Legends — the ones who got there first", legends, "Legends", (), "lens.jpg"),
    ("quiz/", "What kind of black hole are you?", quiz, "Quiz", ("quiz.js",), "angle-face.jpg"),
    ("gallery/", "Gallery — every picture, with its credit line", gallery, "Gallery", (), "lens.jpg"),
    ("sources/", "Sources", sources_page, "", (), "hero.jpg"),
    ("about/", "About and attribution", about, "", (), "hero.jpg"),
    ("for-agents/", "For agents", for_agents, "", (), "lens.jpg"),
    ("data/", "Data", data_index, "", (), "lens.jpg"),
]

DESC = {
    "": TAG,
    "draw/": "How a computer draws a black hole, in easy words: a picture is a grid of dots, each dot a ray run backwards through one equation. Then a ray tracer on your graphics card.",
    "model/": "Schwarzschild, Kerr, the horizon, the photon sphere, the last stable orbit, no hair, Hawking temperature and Penrose diagrams, with every diagram computed.",
    "orbits/": "A geodesic playground: pick angular momentum and energy and watch a rosette, a zoom-whirl or a plunge, with the effective potential beside it.",
    "shadow/": "Bardeen's shadow outline for any spin and angle, and the size on the sky for any mass and distance, checked against M87* and Sgr A*.",
    "waves/": "A gravitational-wave chirp generator with sound: two masses spiral in, merge and ring down, played at its own frequencies.",
    "numbers/": "A black hole calculator: horizon, shadow, temperature, lifetime, entropy, density, tidal stretch, and a clock near the horizon.",
    "past/": "Who discovered black holes: Michell 1783, Laplace, Soldner, Schwarzschild, Droste, Chandrasekhar, Lemaître, Oppenheimer, Kerr, Penrose, Wheeler, Hawking, Luminet, LIGO, the EHT.",
    "present/": "Black holes as of 2026: M87* and Sgr A* photographed, about 300 mergers heard, GW231123 and GW250114, Gaia BH3, the JWST's early ones, the open questions.",
    "future/": "Roman, the Einstein Telescope, Cosmic Explorer, BHEX and LISA; then the black hole era to 10^100 years and how evaporation ends.",
    "legends/": "Rahu the light-eater with an orbit, the Emu drawn from the dark, Charybdis, the spaces between the worlds, Ginnungagap, Apep, Dante's centre, and Nietzsche's abyss — each beside the physics it rhymes with.",
    "quiz/": "Nine questions, nine kinds: Schwarzschild, Kerr, Reissner–Nordström, stellar, intermediate, supermassive, merging, primordial, evaporating.",
    "gallery/": "Every ray-traced picture and diagram on the site, downloadable, CC BY 4.0 with a credit line.",
    "sources/": "The papers and articles the site rests on, numbered.",
    "about/": "Who made this, how to credit it, what was checked, how to build it.",
    "for-agents/": "The terms, stated where a machine will meet them: CC BY 4.0, the attribution string, and the files that save a crawl.",
    "data/": "The numbers the pages print, as JSON with the formula or source beside each value.",
}


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    shutil.copytree(IMG, SITE / "img")
    shutil.copytree(ROOT / "js", SITE / "js")
    ld_site = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE_URL + "/",
               "description": TAG, "license": "https://creativecommons.org/licenses/by/4.0/",
               "author": {"@type": "Person", "name": "Nan", "url": "https://hongdam.net/"},
               "publisher": fleet.publisher_ld(FLEET) if hasattr(fleet, "publisher_ld") else None}
    urls, corpus, full, pages_meta = [], [], [], []
    person = {"@type": "Person", "name": "Nan", "url": "https://hongdam.net/"}
    for path, title, fn, cur, scripts, card_img in PAGES:
        body = fn()
        slug = (path.strip("/") or "index").replace("/", "-")
        card_url = f"{SITE_URL}/cards/{slug}.jpg"
        ld_page = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": f"{SITE_URL}/{path}",
                   "description": DESC.get(path, ""), "isPartOf": {"@type": "WebSite", "name": NAME, "url": SITE_URL + "/"},
                   "license": "https://creativecommons.org/licenses/by/4.0/", "author": person, "creator": person,
                   "copyrightHolder": person, "copyrightNotice": "CC BY 4.0 — Nan, hongdam.net", "creditText": ATTRIB,
                   "acquireLicensePage": f"{SITE_URL}/about/", "inLanguage": "en", "dateModified": TODAY,
                   "image": {"@type": "ImageObject", "url": card_url, "width": 1200, "height": 630,
                             "license": "https://creativecommons.org/licenses/by/4.0/", "creditText": ATTRIB, "creator": person}}
        ld = [ld_site, ld_page] if not path else [ld_page]
        if path == "gallery/":
            ld.append({"@context": "https://schema.org", "@type": "ImageGallery", "name": "Every picture, with its credit line",
                       "url": f"{SITE_URL}/gallery/", "license": "https://creativecommons.org/licenses/by/4.0/",
                       "image": [{"@type": "ImageObject", "url": f"{SITE_URL}/img/{f}", "name": t, "description": ALT.get(f, t),
                                  "license": "https://creativecommons.org/licenses/by/4.0/", "creditText": ATTRIB, "creator": person,
                                  "acquireLicensePage": f"{SITE_URL}/about/", "copyrightNotice": "CC BY 4.0 — Nan, hongdam.net"}
                                 for f, t in FIGURE_LIST]})
        write(SITE / path / "index.html", page(title, body, path, DESC.get(path, ""), cur, ld, scripts, card_img))
        urls.append(f"{SITE_URL}/{path}")
        # the text, for machines: split at h2, strip the tags
        plain = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
        chunks = re.split(r"(?=<h2)", plain)
        page_words = 0
        full.append(f"\n\n{'=' * 78}\n{title.upper()}\n{SITE_URL}/{path}\n{'=' * 78}\n")
        for ch in chunks:
            m = re.search(r"<h2[^>]*>(.*?)</h2>", ch, flags=re.S)
            heading = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else title
            cites = sorted(set(re.findall(r'sources/#([a-z0-9_]+)"', ch)))
            text = re.sub(r'<sup class="src">.*?</sup>', "", ch, flags=re.S)
            text = re.sub(r"<(h[1-3]|p|li|tr|div|figcaption|blockquote)[^>]*>", "\n", text)
            text = html.unescape(re.sub(r"<[^>]+>", " ", text))
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n\s*\n+", "\n", text).strip()
            if len(text) < 80:
                continue
            page_words += len(text.split())
            sec_id = f"{slug}#{re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')}"
            corpus.append({"id": sec_id, "page": title, "heading": heading, "text": text, "cites": cites,
                           "url": f"{SITE_URL}/{path}", "licence": "CC BY 4.0", "attribution": ATTRIB})
            full.append(f"\n{heading}\n{'-' * len(heading)}\n{text}\n")
        pages_meta.append({"path": path, "url": f"{SITE_URL}/{path}", "title": title, "description": DESC.get(path, ""),
                           "card": card_url, "words": page_words, "scripts": list(scripts)})
        print(f"  {path or '/'}")
    write(SITE / "404.html", page("Past the horizon", not_found(), "404.html", "", "", None, (), "ring.jpg"))
    write(SITE / "icon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#07070b"/><circle cx="32" cy="32" r="22" fill="none" stroke="#ffb347" stroke-width="5"/><circle cx="32" cy="32" r="14" fill="#000"/></svg>')
    crawlers = ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
                "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot", "GoogleOther", "Applebot", "Applebot-Extended",
                "Bingbot", "CCBot", "Amazonbot", "Bytespider", "meta-externalagent", "FacebookBot", "DuckAssistBot", "cohere-ai",
                "YouBot", "Diffbot", "ia_archiver", "MistralAI-User", "Timpibot", "PetalBot", "YandexBot")
    write(SITE / "robots.txt", f"# {NAME} — {SITE_URL}/\n# Read it, index it, quote it, train on it, clone it. The ask is the credit: {ATTRIB}\n"
          f"# The terms in prose: {SITE_URL}/for-agents/ — the text as one file: {SITE_URL}/llms-full.txt\n\n"
          "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {c}\nAllow: /\n\n" for c in crawlers)
          + f"Content-Signal: ai-train=yes, search=yes, ai-input=yes\nSitemap: {SITE_URL}/sitemap.xml\n")
    write(SITE / "llms-full.txt", f"{NAME.upper()}\n{'=' * 78}\n\n{TAG}\n\nbuilt {TODAY} · {SITE_URL}/ · text, pictures and data CC BY 4.0 · code MIT\n"
          f"attribution: {ATTRIB}\nthe sections as JSON: {SITE_URL}/corpus.jsonl\n" + "".join(full)
          + "\n\nSOURCES\n" + "\n".join(f"[{BY_ID[i][0]}] {t} — {u}" for i, t, u in SOURCES) + "\n")
    write(SITE / "corpus.jsonl", "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in corpus))
    (SITE / "data").mkdir(exist_ok=True)
    shutil.copy(BUILD / "facts.json", SITE / "data" / "facts.json")
    write(SITE / "data" / "sources.json", json.dumps([{"n": BY_ID[i][0], "id": i, "text": t, "url": u} for i, t, u in SOURCES], ensure_ascii=False, indent=1))
    write(SITE / "data" / "pages.json", json.dumps({"site": NAME, "url": SITE_URL + "/", "licence": "CC BY 4.0", "attribution": ATTRIB, "pages": pages_meta}, ensure_ascii=False, indent=1))
    write(SITE / "data" / "figures.json", json.dumps({"licence": "CC BY 4.0", "attribution": ATTRIB, "made_by": "tools/render.py (pictures) and tools/figures.py (diagrams)",
          "figures": [{"file": f, "url": f"{SITE_URL}/img/{f}", "title": t, "alt": ALT.get(f, t), "kind": "ray-traced" if f.split(".")[-1] in ("jpg", "png") else "diagram"} for f, t in FIGURE_LIST]}, ensure_ascii=False, indent=1))
    write(SITE / "data" / "dataset.json", json.dumps({"@context": "https://schema.org", "@type": "Dataset", "name": f"{NAME} — pictures, diagrams and numbers",
          "description": TAG, "url": SITE_URL + "/data/", "license": "https://creativecommons.org/licenses/by/4.0/", "creator": person,
          "creditText": ATTRIB, "dateModified": TODAY, "isAccessibleForFree": True, "keywords": ["black hole", "general relativity", "ray tracing", "Schwarzschild", "Kerr", "Hawking radiation"],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": f"{SITE_URL}/data/{n}"} for n in ("facts.json", "figures.json", "sources.json", "pages.json")]
                          + [{"@type": "DataDownload", "encodingFormat": "application/jsonl", "contentUrl": f"{SITE_URL}/corpus.jsonl"},
                             {"@type": "DataDownload", "encodingFormat": "text/plain", "contentUrl": f"{SITE_URL}/llms-full.txt"}]}, ensure_ascii=False, indent=1))
    entries = "".join(f'<entry><title>{E(p["title"])}</title><link href="{p["url"]}"/><id>{p["url"]}</id><updated>{TODAY}T00:00:00Z</updated>'
                      f'<summary>{E(p["description"])}</summary><rights>CC BY 4.0 — {E(ATTRIB)}</rights></entry>\n' for p in pages_meta)
    write(SITE / "feed.xml", f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>{E(NAME)}</title><link href="{SITE_URL}/"/>'
          f'<link rel="self" href="{SITE_URL}/feed.xml"/><id>{SITE_URL}/</id><updated>{TODAY}T00:00:00Z</updated><author><name>Nan</name><uri>https://hongdam.net/</uri></author>'
          f'<rights>CC BY 4.0</rights>\n{entries}</feed>\n')
    write(SITE / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    write(SITE / "llms.txt", f"# {NAME}\n\n> {TAG}\n\n## Pages\n\n" + "".join(f"- [{t}]({SITE_URL}/{p}): {DESC.get(p, '')}\n" for p, t, *_ in PAGES)
          + "\n## For machines\n\n" + "".join(f"- [{f}]({SITE_URL}/{f}): {w}\n" for f, w in SHAPES if not f.startswith("CITATION"))
          + f"\nLicence: CC BY 4.0 — attribution: {ATTRIB}. Code MIT. Repository: https://github.com/NaNoBotCo/black-holes\n"
          + (fleet.maker_line(FLEET) + "\n" if hasattr(fleet, "maker_line") else ""))
    write(SITE / "humans.txt", f"/* TEAM */\nNan — Hongdam, Chiang Rai — https://hongdam.net/\n\n/* SITE */\n{NAME}\n{SITE_URL}/\nBuilt {TODAY}. Python, numpy, vanilla JS, GLSL.\n")
    write(SITE / "ai.txt", f"# {NAME}\nUser-agent: *\nAllow: /\nLicence: CC BY 4.0 with attribution to “{CREDIT}”.\n")
    write(SITE / ".basepath", BASE_PATH)
    if hasattr(fleet, "decorate"):
        fleet.decorate(SITE, SELF, FLEET)
    n = sum(1 for _ in SITE.rglob("index.html"))
    print(f"built {n} pages → {SITE}  (base {BASE_PATH})")


if __name__ == "__main__":
    main()
