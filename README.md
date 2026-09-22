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

## Licence and attribution

Text, diagrams and pictures: [CC BY 4.0](LICENSE). Credit line:
**"Nan · hongdam.net · CC BY 4.0"** with a link to the site. Code: [MIT](LICENSE-CODE).
Sources keep their own terms; see `NOTICE.txt` and the site's sources page.

Built at [Hongdam](https://hongdam.net/), Chiang Rai.
