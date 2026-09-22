#!/usr/bin/env python3
"""The numbers the site prints, checked against the ones in the literature."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import figures as F  # noqa: E402

fails = []


def check(name, got, want, tol):
    ok = abs(got - want) <= tol * abs(want)
    print(f"  {'ok ' if ok else 'BAD'} {name}: {got:.4g} (want {want:.4g})")
    if not ok:
        fails.append(name)


# horizon radii
check("Sun r_s km", F.r_s(F.MSUN) / 1e3, 2.953, 0.002)
check("Earth r_s mm", F.r_s(5.972e24) * 1e3, 8.87, 0.01)
# Hawking temperature of the Sun: 6.17e-8 K
check("T_H Sun", F.hawking_T(F.MSUN), 6.17e-8, 0.01)
# evaporation time of the Sun, Hawking's leading form: ~2.1e67 yr
check("t_evap Sun yr", F.t_evap(F.MSUN) / F.YEAR, 2.1e67, 0.05)
# Bardeen: a=0 shadow radius 3√3
pts = F.kerr_shadow(0.0, 90)
check("shadow a=0 radius", float(abs(pts[:, 0]).max()), math.sqrt(27), 0.001)
# a=0.998 at 90°: the height stays near 2·3√3 at every spin; only the width changes
pts = F.kerr_shadow(0.998, 90)
check("shadow a=0.998 height", float(pts[:, 1].max() - pts[:, 1].min()), 10.39, 0.03)
# light deflection far out: 4/b
# exact to second order: 4/b + 15π/4 /b² = 0.1333 + 0.0131
check("deflection b=30", F.photon_deflection(30.0, r0=2000), 4 / 30 + 15 * math.pi / 4 / 900, 0.02)
check("deflection b=100", F.photon_deflection(100.0, r0=5000), 0.04 + 15 * math.pi / 4 / 1e4, 0.02)
# chirp: 36+29 from 20 Hz, GW150914 lasted ~0.2 s from 35 Hz → ~0.9 s from 20 Hz
t, h, f, tr, hr, fr, fisco, mc = F.chirp()
check("chirp mass", mc, 28.1, 0.02)
check("ringdown Hz", fr, 250, 0.15)
# the facts file the site reads
facts = json.loads((ROOT / "build" / "facts.json").read_text())
check("M87* shadow µas", facts["shadow_m87_uas"], 39.7, 0.03)
check("Sgr A* shadow µas", facts["shadow_sgr_uas"], 53.3, 0.03)

site = ROOT / "build" / "site"
for p in ("index.html", "draw/index.html", "quiz/index.html", "past/index.html", "legends/index.html"):
    if not (site / p).exists():
        fails.append(p)
        print(f"  BAD missing {p}")
html = (site / "index.html").read_text()
for must in ("abyss", "CC BY 4.0", "hongdam", "Michell"):
    if must.lower() not in html.lower():
        fails.append(must); print(f"  BAD front page lacks {must}")
if fails:
    print(f"FAILED: {fails}"); sys.exit(1)
print("tests pass")
