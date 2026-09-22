# Black Holes, Drawn

Black holes modelled and drawn from the equations. Every picture on the site was
computed here; every diagram was drawn from the formula it shows; the generators run
the same equations in your browser.

**Live:** https://nanobotco.github.io/black-holes/

## What is on it

- **Draw** — how a computer draws a black hole, in easy words: a picture is a grid of
  dots, each dot a ray run backwards through `u″ + u = 3u²`. Then a ray tracer on your
  graphics card, and a one-ray-at-a-time stepper.
- **Model** — Schwarzschild, Kerr, the horizon, the photon sphere, the last stable
  orbit, no hair, Hawking temperature, Penrose diagrams.
- **Orbits · Shadow · Waves · Numbers** — four generators: a geodesic playground,
  Bardeen's shadow outline with the size on the sky, a chirp with sound, a calculator.
- **Past** — who discovered black holes, with credit to the ones before the
  "discoverer": Michell 1783, Laplace, Soldner, Droste, Stoner and Anderson, Lemaître.
- **Present** — as of 2026: two photographed, about three hundred heard, Gaia BH3, the
  JWST's early ones, the open questions.
- **Future** — Roman, the Einstein Telescope, Cosmic Explorer, BHEX, LISA; then the
  black hole era to 10¹⁰⁰ years.
- **Legends** — Rahu, the Emu in the Sky, Charybdis, the spaces between the worlds,
  Ginnungagap, Apep, Dante's centre, Nietzsche's abyss — each beside the physics it
  rhymes with, and where the rhyme breaks.
- **Quiz** — what kind of black hole are you. Nine kinds, with their numbers.
- **Gallery** — every picture and diagram, downloadable.

## Build

```
python3 tools/render.py     # the ray-traced pictures (numpy, PIL), ~4 minutes
python3 tools/figures.py    # the diagrams (SVG) and build/facts.json
python3 tools/site.py       # the pages, into build/site/
./publish.sh                # all of it, checked, into docs/
python3 tools/serve.py 8823 # a local preview, mounted at /black-holes/
```

Python 3.9+, numpy, Pillow. The pages are static HTML with inline CSS and the scripts in `js/`.

## For machines

Everything here is meant to be taken. The terms in prose: [for-agents](https://nanobotco.github.io/black-holes/for-agents/).
The shapes that save a crawl: `llms.txt`, `llms-full.txt` (every page as one text file),
`corpus.jsonl` (one object per section with its citations), `data/*.json` (the numbers,
the figures, the sources, the pages, a schema.org Dataset), `feed.xml`, and a 1200×630
share card per page in `cards/`. The credit sits inside each picture file as well (EXIF
on the JPEGs, text chunks on the PNG, `cc:license` metadata in the SVGs).

Attribution string: **Nan, Black Holes, Drawn (2026), https://nanobotco.github.io/black-holes/, CC BY 4.0**

## Licence and attribution

Text, diagrams and pictures: [CC BY 4.0](LICENSE). Credit line:
**"Nan · hongdam.net · CC BY 4.0"** with a link to the site. Code: [MIT](LICENSE-CODE).
Sources keep their own terms; see `NOTICE.txt` and the site's sources page.

SPDX: `CC-BY-4.0` (content) · `MIT` (code).

Built at [Hongdam](https://hongdam.net/), Chiang Rai.
Contact: Nan · nan@motdang.net · Sponsor: [Ko-fi](https://ko-fi.com/defiantchiangmai) · [Patreon](https://www.patreon.com/nanobotco)

<!-- fleet-roster -->

## Elsewhere from the same publisher

- [Mot Dang](https://motdang.net/) — city directory for Chiang Mai and Chiang Rai
- [The Mae Hong Son Loop](https://nanobotco.github.io/mae-hong-son-loop/) — motorcycling the 600 km loop out of Chiang Mai — curves counted, air measured
- [Muay Thai](https://motdang.net/muay-thai/) — the eight limbs, the thirty named techniques, the ceremony, and every gym on the map
- [Roads of Chiang Mai](https://motdang.net/roads/) — the square of 1296, four rings, and what each one did to the city — counted from the map
- [wichaa](https://wichaa.net/) — Lanna manuscripts, the amulet market, and the traditions around them
- [Hand Poke](https://nanobotco.github.io/hand-poke/) — 28 traditions of marking skin by hand — the leg-tattoo zone of Burma, the Shan States and Lanna, counted
- [Quantum Computing, plainly](https://nanobotco.github.io/quantum-computing/) — the history and theory of quantum computing in plain words, with demos; refreshed weekly
- [Goin' Fast](https://nanobotco.github.io/goin-fast/) — a dirt-simple explainer about speed — twenty measured speeds from the ground under the house to light, and what each one costs
- [The Three-Body Problem](https://nanobotco.github.io/three-body/) — the mathematics of the three-body problem in plain words, with the orbits found rather than copied
- [Amulet Atlas](https://nanobotco.github.io/amulet-atlas/) — amulets, charms and talismans worldwide
- [Carolina Barbecue](https://nanobotco.github.io/carolina-barbecue/) — barbecue in North and South Carolina
- [Wing Country](https://nanobotco.github.io/buffalo-wings/) — the American chicken wing
- [Pink Box](https://nanobotco.github.io/pink-box/) — the American mom-and-pop donut shop
- [Basque Tables](https://nanobotco.github.io/basque-tables/) — Basque dining rooms of California, Nevada and Idaho
- [Pinot Country](https://nanobotco.github.io/pinot-noir/) — pinot noir: the vine, the regions, the cellars
- [Care Abroad](https://nanobotco.github.io/care-abroad/) — treatment across borders, with published prices and their dates
- [Thai Roots](https://nanobotco.github.io/thairoots/) — a root dictionary of Thai, with a word decomposer
- [The index](https://nanobotco.github.io/index/) — every corpus, site and repository, counted
- [Uptake](https://nanobotco.github.io/uptake/) — a field manual on publishing for machines that copy
- [NaNoBotCo](https://nanobotco.github.io/) — the portal
- [ฮักฝรั่ง](https://hakfarang.net/) — เรื่องเงิน วีซ่า และชีวิตกับแฟนฝรั่ง
- [Offrampt](https://offrampt.net/) — turning crypto into spendable local money, Thailand first

All of it, counted: https://nanobotco.github.io/index/ · roster as JSON: https://nanobotco.github.io/index/fleet.json
