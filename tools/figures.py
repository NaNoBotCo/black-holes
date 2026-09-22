#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figures.py — every diagram on the site, drawn from the equations as SVG.

Nothing here is traced from a picture: the rays are integrated, the shadows come from
Bardeen's formula, the embedding from Flamm's, the potentials from the metric. Units
G=c=M=1 unless a figure says otherwise.

    python3 tools/figures.py        # writes build/img/*.svg
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "img"

INK = "#f3efe6"
MUTE = "#b3ac9e"
LINE = "#2a2a38"
HOT = "#ffb347"
BLUE = "#8fd0ff"
RED = "#ff6a5e"
GOLD = "#ffd27a"
VIOLET = "#c8a6ff"
PANEL = "#12121b"
FONT = "'Avenir Next',Avenir,'Segoe UI',system-ui,sans-serif"
DISPLAY = "'Avenir Next Condensed','Arial Narrow Bold',Impact,system-ui,sans-serif"

G_SI = 6.67430e-11
C_SI = 299792458.0
HBAR = 1.054571817e-34
KB = 1.380649e-23
MSUN = 1.98892e30
AU = 1.495978707e11
YEAR = 3.15576e7
AGE = 13.787e9 * YEAR


def svg(w, h, body, title="", desc="", bg=PANEL):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'font-family="{FONT}" font-size="13" fill="{INK}">'
            f'<title>{title}</title><desc>{desc}</desc>'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


def xml(s: str) -> str:
    """Escape text for SVG, keeping the <tspan> markup a few labels carry."""
    import re
    s = re.sub(r"<tspan([^>]*)>", "\x01\\1\x03", s).replace("</tspan>", "\x02")
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace("\x01", "<tspan").replace("\x03", ">").replace("\x02", "</tspan>")


def txt(x, y, s, size=13, fill=INK, anchor="start", weight=400, family=FONT, extra=""):
    s = xml(s)
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{family}" {extra}>{s}</text>')


def path(pts, stroke=INK, width=1.5, dash="", fill="none", op=1.0, extra=""):
    if len(pts) < 2:
        return ""
    kept = [pts[0]]
    for x, y in pts[1:]:
        if abs(x - kept[-1][0]) + abs(y - kept[-1][1]) >= 0.6:
            kept.append((x, y))
    if kept[-1] != pts[-1]:
        kept.append(pts[-1])
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in kept)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{da} '
            f'opacity="{op}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def circle(cx, cy, r, fill="none", stroke=INK, width=1.5, dash="", op=1.0):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{da} opacity="{op}"/>'


def save(name, s):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(s, encoding="utf-8")
    print(f"  wrote build/img/{name}  {len(s) // 1024} KB")


# ---------------------------------------------------------------- physics helpers
def photon_path(b, gravity=True, r0=40.0, dphi=0.004, phi_max=4 * math.pi):
    """A light ray in the plane, by impact parameter b. Returns list of (x, y)."""
    u = 1.0 / r0
    # incoming from the +x side, moving in -x, offset b in y: at r0, sin(angle) = b/r0
    s = b / r0
    du = math.sqrt(max(1.0 / (b * b) - u * u, 0)) if b > 0 else 1e-9
    phi = math.asin(min(1.0, s))  # angle of the start point
    pts = []
    f = (lambda uu: 3 * uu * uu - uu) if gravity else (lambda uu: -uu)
    steps = int(phi_max / dphi)
    for _ in range(steps):
        r = 1.0 / u
        pts.append((r * math.cos(phi), r * math.sin(phi)))
        k1u, k1d = du, f(u)
        k2u, k2d = du + 0.5 * dphi * k1d, f(u + 0.5 * dphi * k1u)
        k3u, k3d = du + 0.5 * dphi * k2d, f(u + 0.5 * dphi * k2u)
        k4u, k4d = du + dphi * k3d, f(u + dphi * k3u)
        u += dphi / 6 * (k1u + 2 * k2u + 2 * k3u + k4u)
        du += dphi / 6 * (k1d + 2 * k2d + 2 * k3d + k4d)
        phi += dphi
        if u >= 0.5:
            pts.append((2 * math.cos(phi), 2 * math.sin(phi)))
            return pts, "in"
        if u <= 1.0 / (1.08 * r0):
            r = 1.0 / u
            pts.append((r * math.cos(phi), r * math.sin(phi)))
            return pts, "out"
    return pts, "stuck"


def photon_deflection(b, r0=400.0, dphi=0.002, phi_max=6 * math.pi):
    """The angle a ray with impact parameter b turns through, from its heading when it
    leaves: heading = φ + atan2(r, dr/dφ). Returns None if it falls in or circles."""
    u = 1.0 / r0
    du = math.sqrt(max(1.0 / (b * b) - u * u, 0))
    phi = math.asin(min(1.0, b / r0))
    f = lambda uu: 3 * uu * uu - uu  # noqa: E731
    for _ in range(int(phi_max / dphi)):
        k1u, k1d = du, f(u)
        k2u, k2d = du + 0.5 * dphi * k1d, f(u + 0.5 * dphi * k1u)
        k3u, k3d = du + 0.5 * dphi * k2d, f(u + 0.5 * dphi * k2u)
        k4u, k4d = du + dphi * k3d, f(u + dphi * k3u)
        u += dphi / 6 * (k1u + 2 * k2u + 2 * k3u + k4u)
        du += dphi / 6 * (k1d + 2 * k2d + 2 * k3d + k4d)
        phi += dphi
        if u >= 0.5:
            return None
        if u <= 1.0 / (1.05 * r0):
            r = 1.0 / u
            drdphi = -(r * r) * du
            heading = phi + math.atan2(r, drdphi)
            return (heading - math.pi) % (2 * math.pi)
    return None


def particle_path(L, E, r0, dphi=0.003, phi_max=14 * math.pi, outward=False):
    """A massive particle: d²u/dφ² + u = 1/L² + 3u², with u' from the energy equation."""
    u = 1.0 / r0
    v = (E * E - (1 - 2 * u) * (1 + L * L * u * u)) / (L * L)
    du = (1 if outward else -1) * math.sqrt(max(v, 0)) * (-1)
    phi = 0.0
    pts = []
    for _ in range(int(phi_max / dphi)):
        r = 1.0 / u
        pts.append((r * math.cos(phi), r * math.sin(phi)))
        f = lambda uu: 1.0 / (L * L) + 3 * uu * uu - uu  # noqa: E731
        k1u, k1d = du, f(u)
        k2u, k2d = du + 0.5 * dphi * k1d, f(u + 0.5 * dphi * k1u)
        k3u, k3d = du + 0.5 * dphi * k2d, f(u + 0.5 * dphi * k2u)
        k4u, k4d = du + dphi * k3d, f(u + dphi * k3u)
        u += dphi / 6 * (k1u + 2 * k2u + 2 * k3u + k4u)
        du += dphi / 6 * (k1d + 2 * k2d + 2 * k3d + k4d)
        phi += dphi
        if u >= 0.5 or u <= 0:
            break
    return pts


def kerr_shadow(a, theta_deg, n=600):
    """Bardeen (1973): the shadow's edge as (alpha, beta) in units of M for spin a and
    an observer at inclination theta from the spin axis."""
    th = math.radians(theta_deg)
    if a < 1e-4:
        t = np.linspace(0, 2 * np.pi, n)
        R = math.sqrt(27)
        return np.c_[R * np.cos(t), R * np.sin(t)]
    rs = np.linspace(1.0001, 4.0, 4000)
    D = rs * rs - 2 * rs + a * a
    xi = ((rs * rs - a * a) * 1 - rs * D) / (a * (rs - 1))
    eta = rs ** 3 * (4 * D - rs * (rs - 1) ** 2) / (a * a * (rs - 1) ** 2)
    alpha = -xi / math.sin(th)
    b2 = eta + a * a * math.cos(th) ** 2 - xi * xi / math.tan(th) ** 2
    ok = b2 >= 0
    alpha, beta = alpha[ok], np.sqrt(b2[ok])
    top = np.c_[alpha, beta]
    bot = np.c_[alpha[::-1], -beta[::-1]]
    return np.vstack([top, bot])


def hawking_T(M_kg):
    return HBAR * C_SI ** 3 / (8 * math.pi * G_SI * M_kg * KB)


def t_evap(M_kg):
    return 5120 * math.pi * G_SI ** 2 * M_kg ** 3 / (HBAR * C_SI ** 4)


def r_s(M_kg):
    return 2 * G_SI * M_kg / C_SI ** 2


# ---------------------------------------------------------------- 1. light bending
def fig_bending():
    W, H = 960, 560
    cx, cy, S = 400, 330, 15.5   # px per M
    body = []
    body.append(f'<rect width="{W}" height="{H}" fill="#000"/>')
    # rays
    bs = [2.0, 3.5, 4.6, 5.0, 5.19, 5.21, 5.5, 6.5, 8.0, 10.0, 13.0, 17.0]
    for b in bs:
        pts, end = photon_path(b, r0=34)
        if end == "stuck":
            pts = pts[:2400]
        col = RED if end == "in" else (GOLD if b < 5.6 else BLUE)
        if abs(b - 5.19) < 0.02 or abs(b - 5.21) < 0.02:
            col = HOT
        body.append(path([(cx + x * S, cy - y * S) for x, y in pts], stroke=col, width=1.6, op=0.95))
    body.append(circle(cx, cy, 3 * S, stroke=MUTE, dash="4 4", width=1))
    body.append(circle(cx, cy, 2 * S, fill="#000", stroke=INK, width=2))
    body.append(circle(cx, cy, 2 * S, fill="none", stroke=HOT, width=1, op=.5))
    body.append(txt(cx, cy + 5, "r = 2M", 12, MUTE, "middle"))
    body.append(txt(cx + 3 * S + 4, cy - 3 * S + 4, "photon sphere r = 3M", 12, MUTE))
    body.append(txt(W - 24, 34, "Light past a black hole, by impact parameter b", 20, INK, "end", weight=800, family=DISPLAY))
    body.append(txt(W - 24, 56, "b is the distance a ray would have missed the centre by, had it gone straight; rays arrive from the right", 12, MUTE, "end"))
    for y, c, s in ((H - 62, RED, "b < 3√3 M ≈ 5.196 M: falls in"),
                    (H - 44, HOT, "b ≈ 5.196 M: circles the photon sphere — the ring in every picture"),
                    (H - 26, BLUE, "b > 5.196 M: bent by roughly 4M/b and gone")):
        body.append(f'<rect x="24" y="{y - 10}" width="14" height="4" fill="{c}"/>')
        body.append(txt(46, y - 5, s, 12, INK))
    body.append(txt(W - 24, H - 26, "d²u/dφ² + u = 3Mu²", 15, GOLD, "end", family="serif"))
    return svg(W, H, "".join(body), "Light rays bent by a black hole, by impact parameter",
               "Rays with small impact parameter fall in; one circles the photon sphere; the rest deflect.", bg="#000")


# ---------------------------------------------------------------- 2. Flamm's paraboloid
def fig_flamm():
    W, H = 960, 560
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    # z = 2 sqrt(2 (r-2)) with M=1, drawn with a simple oblique projection
    def proj(x, y, z):
        ang = math.radians(28)
        X = 480 + (x - y) * math.cos(ang) * 17
        Y = 250 + (x + y) * math.sin(ang) * 17 - z * 13
        return X, Y
    rs_ = [2, 2.2, 2.6, 3.2, 4, 5, 6, 7.5, 9, 11, 13.5]
    for r in rs_:
        z = 2 * math.sqrt(2 * (r - 2))
        pts = [proj(r * math.cos(t), r * math.sin(t), z) for t in np.linspace(0, 2 * np.pi, 120)]
        col = HOT if r == 6 else (INK if r == 2 else MUTE)
        body.append(path(pts, stroke=col, width=1.6 if r in (2, 6) else 1, op=0.9))
    for t in np.linspace(0, 2 * np.pi, 24, endpoint=False):
        pts = [proj(r * math.cos(t), r * math.sin(t), 2 * math.sqrt(2 * (r - 2))) for r in np.linspace(2, 13.5, 60)]
        body.append(path(pts, stroke=MUTE, width=.7, op=0.6))
    body.append(txt(24, 34, "Flamm's paraboloid, 1916", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(24, 56, "the equatorial slice of Schwarzschild space, bent into a third dimension so its stretching shows", 12, MUTE))
    x, y = proj(6, 0, 2 * math.sqrt(8))
    body.append(txt(x + 8, y + 4, "r = 6M, last stable orbit", 12, HOT))
    x, y = proj(2, 0, 0)
    body.append(txt(x + 10, y + 16, "r = 2M, the throat", 12, INK))
    body.append(txt(W - 24, H - 26, "z(r) = 2√(2M (r − 2M))", 15, GOLD, "end", family="serif"))
    body.append(txt(W - 24, H - 46, "distance along the sheet is the distance a ruler measures; the funnel is not a picture of falling", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "Flamm's paraboloid", "The curved equatorial slice of Schwarzschild spacetime.", bg="#000")


# ---------------------------------------------------------------- 3. effective potential
def fig_potential():
    W, H = 960, 520
    x0, x1, y0, y1 = 70, 930, 470, 50
    rmin, rmax, vmin, vmax = 2.0, 30.0, 0.86, 1.06
    def X(r): return x0 + (r - rmin) / (rmax - rmin) * (x1 - x0)
    def Y(v): return y0 - (v - vmin) / (vmax - vmin) * (y0 - y1)
    body = []
    for v in np.arange(0.86, 1.061, 0.02):
        body.append(path([(x0, Y(v)), (x1, Y(v))], stroke=LINE, width=1))
        body.append(txt(x0 - 8, Y(v) + 4, f"{v:.2f}", 11, MUTE, "end"))
    for r in (2, 3, 6, 10, 15, 20, 25, 30):
        body.append(path([(X(r), y0), (X(r), y0 + 5)], stroke=MUTE, width=1))
        body.append(txt(X(r), y0 + 18, f"{r}M", 11, MUTE, "middle"))
    body.append(path([(X(6), y0), (X(6), y1)], stroke=HOT, width=1, dash="3 4", op=.7))
    body.append(txt(X(6) + 5, y1 + 14, "ISCO r = 6M", 12, HOT))
    for L, col, lab in ((3.0, MUTE, "L = 3.0M  (no circular orbit at all: plunge)"),
                        (math.sqrt(12), HOT, "L = √12 M ≈ 3.46M  (the last stable circle, at r = 6M)"),
                        (4.0, BLUE, "L = 4.0M  (a stable well and an unstable rim)"),
                        (4.6, VIOLET, "L = 4.6M")):
        rs_ = np.linspace(rmin, rmax, 600)
        V = np.sqrt((1 - 2 / rs_) * (1 + L * L / rs_ ** 2))
        pts = [(X(r), Y(v)) for r, v in zip(rs_, V) if vmin <= v <= vmax]
        body.append(path(pts, stroke=col, width=2))
    body.append(txt(x0, 34, "Effective potential for a massive particle around a Schwarzschild black hole", 18, INK, weight=800, family=DISPLAY))
    body.append(txt(x0, H - 8, "V(r) = √((1 − 2M/r)(1 + L²/r²)) — a particle with energy E moves where E ≥ V; a dip holds an orbit, a rim lets it fall over", 12, MUTE))
    yy = 70
    for col, lab in ((MUTE, "L = 3.0M: no well, everything plunges"), (HOT, "L = √12 M: the well and the rim meet — r = 6M"),
                     (BLUE, "L = 4.0M: a well at r ≈ 12M, a rim at r ≈ 4M"), (VIOLET, "L = 4.6M: deeper well, higher rim")):
        body.append(f'<rect x="{x1 - 330}" y="{yy - 9}" width="14" height="4" fill="{col}"/>')
        body.append(txt(x1 - 310, yy - 4, lab, 12, INK))
        yy += 20
    return svg(W, H, "".join(body), "Effective potential", "Curves of the effective potential for four angular momenta.")


# ---------------------------------------------------------------- 4. Penrose diagrams
def fig_penrose():
    W, H = 960, 400
    body = []
    def diamond(ox, label):
        s = 130
        pts = [(ox, 200 - s), (ox + s, 200), (ox, 200 + s), (ox - s, 200), (ox, 200 - s)]
        body.append(path(pts, stroke=INK, width=1.8))
        body.append(txt(ox, 200 - s - 10, "i⁺", 12, MUTE, "middle"))
        body.append(txt(ox, 200 + s + 16, "i⁻", 12, MUTE, "middle"))
        body.append(txt(ox + s + 8, 204, "i⁰", 12, MUTE))
        body.append(txt(ox + s / 2 + 12, 200 - s / 2 - 4, "𝓘⁺", 12, MUTE))
        body.append(txt(ox + s / 2 + 12, 200 + s / 2 + 12, "𝓘⁻", 12, MUTE))
        for k in (-0.6, -0.3, 0, 0.3, 0.6):
            # lines of constant t and r, mapped
            t = np.linspace(-6, 6, 200)
            r = np.full_like(t, abs(k) * 6)
            u, v = np.arctan(t - r), np.arctan(t + r)
            X = ox + (v - u) / math.pi * s
            Y = 200 - (u + v) / math.pi * s
            body.append(path(list(zip(X, Y)), stroke=LINE, width=1))
        body.append(txt(ox, 200 + s + 40, label, 13, INK, "middle", weight=700))

    diamond(160, "Flat space (Minkowski)")

    # collapse
    ox, s = 480, 130
    top = 200 - s
    # right half diamond with a horizon line and a wavy singularity on top
    body.append(path([(ox - 60, top), (ox + s * 0.0 + 70, top)], stroke=RED, width=2.5, dash="6 4"))
    body.append(txt(ox + 5, top - 10, "singularity r = 0", 12, RED, "middle"))
    body.append(path([(ox + 70, top), (ox + s + 70 - 130 + 130, 200), (ox + 70, 200 + s)], stroke=INK, width=1.8))
    body.append(path([(ox - 60, top), (ox + 70, 200 - 0)], stroke=HOT, width=2))
    body.append(txt(ox + 20, 200 - 40, "horizon", 12, HOT))
    # the star's surface: a timelike curve from i- into the singularity
    tt = np.linspace(0, 1, 80)
    Xs = ox - 60 + 8 * np.sin(tt * 3)
    Ys = 200 + s - tt * (2 * s)
    body.append(path(list(zip(Xs, Ys)), stroke=BLUE, width=2.2))
    body.append(f'<path d="M{ox - 60},{200 + s} L{ox - 60},{top} L{ox + 70},{top} L{ox + 70},{200 + s} Z" fill="{BLUE}" opacity=".07"/>')
    body.append(txt(ox - 66, 200 + 60, "star's surface", 12, BLUE, "end"))
    body.append(txt(ox - 66, 200 + 76, "(Oppenheimer–Snyder 1939)", 10, MUTE, "end"))
    body.append(txt(ox + 130 + 8, 204, "i⁰", 12, MUTE))
    body.append(txt(ox + 110, 200 - 70, "𝓘⁺", 12, MUTE))
    body.append(txt(ox + 40, 200 + s + 40, "A star collapses", 13, INK, "middle", weight=700))

    # evaporation
    ox = 790
    body.append(path([(ox - 60, top + 40), (ox + 30, top + 40)], stroke=RED, width=2.5, dash="6 4"))
    body.append(path([(ox - 60, top + 40), (ox + 30, top - 50)], stroke=HOT, width=2))
    body.append(path([(ox + 30, top - 50), (ox + 30 + 0, top - 50)], stroke=HOT, width=2))
    body.append(path([(ox + 30, top - 50), (ox + 30 + 100, top + 50), (ox + 30, 200 + s)], stroke=INK, width=1.8))
    body.append(path([(ox + 30, top - 50), (ox - 60, top - 50 + 90)], stroke=INK, width=1.8, dash="2 3", op=.5))
    tt = np.linspace(0, 1, 80)
    Xs = ox - 60 + 8 * np.sin(tt * 3)
    Ys = 200 + s - tt * (s + 90)
    body.append(path(list(zip(Xs, Ys)), stroke=BLUE, width=2.2))
    body.append(txt(ox + 36, top - 54, "the last flash", 12, GOLD))
    body.append(txt(ox - 66, top + 44, "r = 0", 12, RED, "end"))
    body.append(txt(ox + 10, 200 + s + 40, "…and evaporates (Hawking)", 13, INK, "middle", weight=700))
    body.append(txt(ox + 90, 200 - 10, "𝓘⁺", 12, MUTE))
    body.append(txt(W - 12, 20, "Penrose diagrams: light always travels at 45°; infinity is pulled in to the edges", 12, MUTE, "end"))
    return svg(W, H, "".join(body), "Penrose diagrams", "Flat space, a collapsing star, an evaporating black hole.")


# ---------------------------------------------------------------- 5. Kerr shadows
def fig_shadows():
    W, H = 960, 480
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    for k, (theta, ox, lab) in enumerate(((90, 250, "seen edge-on (θ = 90°)"), (17, 710, "seen like M87* (θ = 17°)"))):
        cy, S = 250, 24
        body.append(path([(ox - 7 * S, cy), (ox + 7 * S, cy)], stroke=LINE, width=1))
        body.append(path([(ox, cy - 7 * S), (ox, cy + 7 * S)], stroke=LINE, width=1))
        for a, col in ((0.0, MUTE), (0.5, BLUE), (0.9, HOT), (0.998, RED)):
            pts = kerr_shadow(a, theta)
            body.append(path([(ox + x * S, cy - y * S) for x, y in pts], stroke=col, width=2))
        body.append(txt(ox, cy + 7 * S + 30, lab, 13, INK, "middle", weight=700))
        body.append(txt(ox + 5.3 * S, cy - 5.3 * S, "5M", 11, MUTE))
    yy = 40
    body.append(txt(24, yy, "The shadow's outline, by spin", 20, INK, weight=800, family=DISPLAY))
    for a, col, s in ((0.0, MUTE, "a = 0: a circle of radius 3√3 M"), (0.5, BLUE, "a = 0.5"), (0.9, HOT, "a = 0.9: the near side flattens"), (0.998, RED, "a = 0.998: the D")):
        yy += 20
        body.append(f'<rect x="24" y="{yy - 9}" width="14" height="4" fill="{col}"/>')
        body.append(txt(46, yy - 4, s, 12, INK))
    body.append(txt(W - 24, H - 20, "Bardeen 1973; the flat side faces the direction of spin", 12, MUTE, "end"))
    return svg(W, H, "".join(body), "Kerr black hole shadows", "Shadow outlines for spins 0, 0.5, 0.9 and 0.998 at two inclinations.", bg="#000")


# ---------------------------------------------------------------- 6. the mass ladder
LADDER = [
    (2.176e-8, "Planck mass — the smallest black hole physics can name", HOT),
    (5.0e11, "one that finishes evaporating about now (born in the first second)", RED),
    (5.97e24, "Earth (its horizon: a marble, 18 mm across)", BLUE),
    (1.989e30, "the Sun (a town, 5.9 km across)", GOLD),
    (2.8 * 1.989e30, "smallest black hole a star can leave (Tolman–Oppenheimer–Volkoff, roughly)", MUTE),
    (7.0 * 1.989e30, "the one seen alone, by microlensing (2022)", INK),
    (21.2 * 1.989e30, "Cygnus X-1 — the first found", INK),
    (33 * 1.989e30, "Gaia BH3 — the heaviest stellar one in the Galaxy", INK),
    (62 * 1.989e30, "GW150914's remnant — the first heard", INK),
    (142 * 1.989e30, "GW190521's remnant — the first intermediate-mass", INK),
    (225 * 1.989e30, "GW231123's remnant — the heaviest merger heard so far", INK),
    (4.3e6 * 1.989e30, "Sagittarius A* — ours (horizon: 0.085 au)", HOT),
    (6.5e9 * 1.989e30, "M87* — the first photographed (horizon: 128 au)", HOT),
    (4.0e10 * 1.989e30, "TON 618 — among the heaviest known", VIOLET),
]


def fig_ladder():
    W, H = 960, 720
    body = []
    x0, x1 = 60, 900
    lo, hi = -9, 42
    def X(m): return x0 + (math.log10(m) - lo) / (hi - lo) * (x1 - x0)
    y_axis = 120
    body.append(path([(x0, y_axis), (x1, y_axis)], stroke=INK, width=2))
    for e in range(lo, hi + 1, 3):
        x = X(10 ** e)
        body.append(path([(x, y_axis - 6), (x, y_axis + 6)], stroke=INK, width=1))
        body.append(txt(x, y_axis - 12, f"10<tspan font-size='9' dy='-6'>{e}</tspan>", 10, MUTE, "middle"))
    body.append(txt(x0, 40, "The ladder of masses, and the horizon each makes", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(x0, 62, "kilograms, one tick per thousandfold; r = 2GM/c², so the horizon grows in step with the mass", 12, MUTE))
    y = 160
    for m, lab, col in LADDER:
        x = X(m)
        body.append(path([(x, y_axis + 8), (x, y - 12)], stroke=col, width=1, op=.5))
        body.append(circle(x, y, 5, fill=col, stroke="none"))
        r = r_s(m)
        if r < 1e-3:
            rs_ = f"{r * 1e6:.3g} µm" if r >= 1e-9 else f"{r:.2g} m"
        elif r < 1:
            rs_ = f"{r * 100:.3g} cm"
        elif r < 1e3:
            rs_ = f"{r:.3g} m"
        elif r < AU / 10:
            rs_ = f"{r / 1e3:.3g} km"
        else:
            rs_ = f"{r / AU:.3g} au"
        anchor = "start" if x < 620 else "end"
        dx = 12 if anchor == "start" else -12
        body.append(txt(x + dx, y + 4, f"{lab}", 12, INK, anchor))
        body.append(txt(x + dx, y + 18, f"horizon diameter {rs_}", 10.5, col, anchor))
        y += 40
    return svg(W, H, "".join(body), "The ladder of black hole masses", "Log scale of masses from the Planck mass to TON 618, with horizon sizes.")


# ---------------------------------------------------------------- 7. evaporation and temperature
def fig_evaporation():
    W, H = 960, 480
    body = []
    # left: temperature; right: lifetime
    def panel(ox, title, yfun, ylab, ylo, yhi, hline, hlab, xlo=-9, xhi=42):
        x0, x1, y0, y1 = ox, ox + 400, 400, 80
        def X(e): return x0 + (e - xlo) / (xhi - xlo) * (x1 - x0)
        def Y(e): return y0 - (e - ylo) / (yhi - ylo) * (y0 - y1)
        for e in range(xlo, xhi + 1, 6):
            body.append(path([(X(e), y0), (X(e), y0 + 5)], stroke=MUTE, width=1))
            body.append(txt(X(e), y0 + 18, f"10<tspan font-size='8' dy='-5'>{e}</tspan>", 10, MUTE, "middle"))
        for e in range(int(ylo), int(yhi) + 1, 20):
            body.append(path([(x0, Y(e)), (x1, Y(e))], stroke=LINE, width=1))
            body.append(txt(x0 - 6, Y(e) + 4, f"10<tspan font-size='8' dy='-5'>{e}</tspan>", 10, MUTE, "end"))
        es = np.linspace(xlo, xhi, 200)
        pts = [(X(e), Y(math.log10(yfun(10 ** e)))) for e in es if ylo <= math.log10(yfun(10 ** e)) <= yhi]
        body.append(path(pts, stroke=HOT, width=2.2))
        body.append(path([(x0, Y(hline)), (x1, Y(hline))], stroke=BLUE, width=1.5, dash="5 4"))
        body.append(txt(x1, Y(hline) - 6, hlab, 11, BLUE, "end"))
        body.append(txt(x0, 50, title, 16, INK, weight=800, family=DISPLAY))
        body.append(txt(x0, y0 + 40, "mass, kg", 11, MUTE))
        body.append(txt(x0 - 6, y1 - 14, ylab, 11, MUTE, "end"))
        for m, lab in ((MSUN, "Sun"), (5.97e24, "Earth"), (5e11, "PBH"), (4.3e6 * MSUN, "Sgr A*")):
            e = math.log10(m)
            v = math.log10(yfun(m))
            if ylo <= v <= yhi:
                body.append(circle(X(e), Y(v), 4, fill=GOLD, stroke="none"))
                body.append(txt(X(e) + 7, Y(v) - 6, lab, 10.5, GOLD))
    panel(70, "Hawking temperature", hawking_T, "kelvin", -20, 40, math.log10(2.725), "the sky today, 2.725 K")
    panel(540, "Time to evaporate", lambda m: t_evap(m) / YEAR, "years", -60, 110, math.log10(13.787e9), "the age of the universe")
    body.append(txt(W - 20, H - 10, "T = ħc³ / 8πGMk · t = 5120πG²M³ / ħc⁴  (Hawking 1974; Page 1976 shortens t by a factor of a few)", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "Hawking temperature and evaporation time by mass", "Two log-log charts.")


# ---------------------------------------------------------------- 8. the chirp
def chirp(m1=36.0, m2=29.0, f0=20.0, n=6000):
    """Newtonian inspiral phase to a cut at the ISCO frequency, then a damped ringdown at
    the fundamental Kerr mode. Enough to draw; not a template."""
    M = (m1 + m2) * MSUN
    mc = ((m1 * m2) ** 0.6 / (m1 + m2) ** 0.2) * MSUN
    k = (5 / 256) * (C_SI ** 5 / (G_SI * mc) ** (5 / 3)) * math.pi ** (-8 / 3)
    tc = k * f0 ** (-8 / 3)
    f_isco = C_SI ** 3 / (6 ** 1.5 * math.pi * G_SI * M)
    f_isco *= 2.2   # the plunge past the last stable orbit, roughly: to merger
    t = np.linspace(0, tc * 0.9999, n)
    f = (k / (tc - t)) ** (3 / 8) * 1.0
    # k f^-8/3 = tc - t → f = (k/(tc-t))^(3/8)
    f = np.clip(f, f0, f_isco)
    ph = 2 * np.pi * np.cumsum(f) * (t[1] - t[0])
    h = (f / f0) ** (2 / 3) * np.cos(ph)
    cut = np.argmax(f >= f_isco * 0.999) if (f >= f_isco * 0.999).any() else n - 1
    t, h, f = t[:cut], h[:cut], f[:cut]
    # ringdown: final mass ~0.95 M, spin 0.69
    Mf, a = 0.95 * M, 0.69
    fr = (1.5251 - 1.1568 * (1 - a) ** 0.1292) / (2 * math.pi) * C_SI ** 3 / (G_SI * Mf)
    Q = 0.7 + 1.4187 * (1 - a) ** -0.499
    tau = Q / (math.pi * fr)
    tr = np.linspace(0, 6 * tau, 400)
    hr = h[-1] * np.exp(-tr / tau) * np.cos(2 * np.pi * fr * tr + ph[cut - 1] % (2 * np.pi))
    return t, h, f, tr + t[-1], hr, fr, f_isco, mc / MSUN


def fig_chirp():
    W, H = 960, 420
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    t, h, f, tr, hr, fr, fisco, mc = chirp()
    T = np.concatenate([t, tr]); Hh = np.concatenate([h, hr])
    t0 = T[-1] - 0.32
    m = T >= t0
    T, Hh = T[m], Hh[m]
    x0, x1, y0 = 40, 920, 200
    X = x0 + (T - T[0]) / (T[-1] - T[0]) * (x1 - x0)
    Y = y0 - Hh / abs(Hh).max() * 120
    body.append(path(list(zip(X, Y)), stroke=HOT, width=1.4))
    body.append(txt(x0, 40, "A chirp: 36 + 29 solar masses, the last third of a second", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(x0, 62, f"chirp mass {mc:.1f} M☉ — the one number the shape of the chirp gives away; the pitch rises as the pair spiral in, then rings down at {fr:.0f} Hz", 12, MUTE))
    body.append(txt(x1, y0 + 150, "time →", 12, MUTE, "end"))
    body.append(txt(x0, y0 + 150, "strain h(t), in units of its peak; inspiral by formula to about merger, then a damped ring at the final hole's tone", 11, MUTE))
    # frequency track
    xs = x0 + (t - T[0]) / (T[-1] - T[0]) * (x1 - x0)
    mm = t >= t0
    fy = y0 + 190 - (f[mm] - 20) / (fisco - 20) * 60
    body.append(path(list(zip(xs[mm], fy)), stroke=BLUE, width=1.5))
    body.append(txt(x0, y0 + 205, f"frequency, 20 Hz → {fisco:.0f} Hz at merger, roughly", 11, BLUE))
    return svg(W, H, "".join(body), "A gravitational-wave chirp", "Newtonian inspiral and Kerr ringdown for a 36+29 solar mass pair.", bg="#000")


# ---------------------------------------------------------------- 9. Kerr cross-section
def fig_kerr():
    W, H = 960, 520
    a = 0.9
    cx, cy, S = 480, 270, 95
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    rp = 1 + math.sqrt(1 - a * a)
    rm = 1 - math.sqrt(1 - a * a)
    th = np.linspace(0, 2 * np.pi, 400)
    # Boyer-Lindquist r,θ to flat-ish x,z for drawing: x = sqrt(r²+a²) sinθ, z = r cosθ
    def xz(r, t):
        return cx + math.sqrt(r * r + a * a) * math.sin(t) * S, cy - r * math.cos(t) * S
    re = 1 + np.sqrt(1 - a * a * np.cos(th) ** 2)
    body.append(path([xz(r, t) for r, t in zip(re, th)], stroke=BLUE, width=2, fill=BLUE, op=.9, extra='fill-opacity=".10"'))
    body.append(path([xz(rp, t) for t in th], stroke=HOT, width=2.4, fill="#000", extra='fill-opacity="1"'))
    body.append(path([xz(rm, t) for t in th], stroke=RED, width=1.6, dash="4 3"))
    # ring singularity: r=0, θ=π/2 → x = ±a
    body.append(circle(cx - a * S, cy, 3, fill=GOLD, stroke="none"))
    body.append(circle(cx + a * S, cy, 3, fill=GOLD, stroke="none"))
    body.append(path([(cx - a * S, cy), (cx + a * S, cy)], stroke=GOLD, width=1, dash="2 3"))
    body.append(path([(cx, cy - 2.6 * S), (cx, cy + 2.6 * S)], stroke=MUTE, width=1, dash="6 5", op=.6))
    body.append(txt(cx + 6, cy - 2.5 * S, "spin axis", 11, MUTE))
    body.append(txt(24, 34, f"A spinning black hole in cross-section, a = {a}", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(24, 56, "Kerr 1963 — the parts of it, in Boyer–Lindquist coordinates", 12, MUTE))
    yy = 90
    for col, s in ((BLUE, "ergosphere: inside it, standing still is impossible; everything is dragged around"),
                   (HOT, f"outer horizon r₊ = M + √(M² − a²) = {rp:.2f}M"),
                   (RED, f"inner horizon r₋ = M − √(M² − a²) = {rm:.2f}M"),
                   (GOLD, "ring singularity at r = 0, θ = 90°, radius a")):
        body.append(f'<rect x="24" y="{yy - 9}" width="14" height="4" fill="{col}"/>')
        body.append(txt(46, yy - 4, s, 12, INK))
        yy += 20
    body.append(txt(W - 24, H - 20, "the ergosphere touches the horizon at the poles and bulges at the equator: r_E = M + √(M² − a²cos²θ)", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "Kerr black hole cross-section", "Ergosphere, two horizons and the ring singularity for spin 0.9.", bg="#000")


# ---------------------------------------------------------------- 10. a pixel is a ray
def fig_pixels():
    W, H = 960, 520
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    # camera on the left: a grid
    gx, gy, cell = 60, 150, 22
    for i in range(10):
        for j in range(10):
            body.append(f'<rect x="{gx + i * cell}" y="{gy + j * cell}" width="{cell - 2}" height="{cell - 2}" fill="{PANEL}" stroke="{LINE}"/>')
    body.append(txt(gx, gy - 14, "the picture: a grid of dots", 12, MUTE))
    # black hole on the right
    cx, cy, S = 700, 260, 26
    # disk seen edge-on-ish: an ellipse
    body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{9 * S}" ry="{1.2 * S}" fill="none" stroke="{HOT}" stroke-width="2" opacity=".8"/>')
    body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{3.2 * S}" ry="{.45 * S}" fill="#000" stroke="{HOT}" stroke-width="1" opacity=".8"/>')
    body.append(circle(cx, cy, 2 * S, fill="#000", stroke=INK, width=2))
    body.append(circle(cx, cy, 3 * S, stroke=MUTE, width=1, dash="3 4"))
    # a star
    body.append(circle(905, 70, 4, fill=BLUE, stroke="none"))
    body.append(txt(905, 56, "a star", 11, BLUE, "middle"))
    # four rays from four pixels
    def ray(px, py, kind, col, label, lx, ly):
        x0, y0 = gx + px * cell + cell / 2, gy + py * cell + cell / 2
        body.append(f'<rect x="{gx + px * cell}" y="{gy + py * cell}" width="{cell - 2}" height="{cell - 2}" fill="{col}"/>')
        if kind == "in":
            pts = [(x0, y0), (cx - 6 * S, cy - 0.4 * S), (cx - 2.4 * S, cy - 0.9 * S), (cx - 1.6 * S, cy - 1.1 * S)]
        elif kind == "disk":
            pts = [(x0, y0), (cx - 7 * S, cy - 1.4 * S), (cx - 4.5 * S, cy - 0.8 * S), (cx - 4.2 * S, cy + 0.02 * S)]
        elif kind == "star":
            pts = [(x0, y0), (cx - 6 * S, cy - 3.4 * S), (cx - 2.5 * S, cy - 3.6 * S), (cx + 2 * S, cy - 4.4 * S), (905, 70)]
        else:
            pts = [(x0, y0), (cx - 6 * S, cy + 3.2 * S), (cx - 3 * S, cy + 3.0 * S), (cx - 1 * S, cy + 3.2 * S), (cx + 2 * S, cy + 2.4 * S), (cx + 3.2 * S, cy + 0.6 * S), (cx + 2.8 * S, cy - 1.6 * S), (cx + 0.5 * S, cy - 3.2 * S), (cx - 3 * S, cy - 3.2 * S), (cx - 4.6 * S, cy - 2.3 * S)]
        d = "M" + " ".join((f"{x:.1f},{y:.1f}" if i == 0 else f"L{x:.1f},{y:.1f}") for i, (x, y) in enumerate(pts))
        body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        body.append(txt(lx, ly, label, 12, col))
    ray(9, 4, "in", RED, "this dot's ray falls in → paint it black", 60, 430)
    ray(9, 6, "disk", HOT, "this one lands on the disk → paint the disk's colour, shifted", 60, 452)
    ray(9, 1, "star", BLUE, "this one bends and leaves → paint the star it ends up pointing at", 60, 474)
    ray(9, 8, "loop", GOLD, "this one loops once before it lands: the disk's far side, seen over the top", 60, 496)
    body.append(txt(24, 34, "One dot, one ray, run backwards", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(24, 56, "the computer never draws the black hole; it draws what the black hole does to light that would have reached each dot", 12, MUTE))
    return svg(W, H, "".join(body), "A pixel is a ray", "Four pixels and the four fates of the rays traced back from them.", bg="#000")


# ---------------------------------------------------------------- 11. tides
def fig_tides():
    W, H = 960, 480
    body = []
    x0, x1, y0, y1 = 80, 920, 400, 70
    xlo, xhi, ylo, yhi = 0, 11, -6, 12   # log10 M/Msun, log10 (m/s²)
    def X(e): return x0 + (e - xlo) / (xhi - xlo) * (x1 - x0)
    def Y(e): return y0 - (e - ylo) / (yhi - ylo) * (y0 - y1)
    for e in range(xlo, xhi + 1):
        body.append(path([(X(e), y0), (X(e), y0 + 5)], stroke=MUTE, width=1))
        body.append(txt(X(e), y0 + 18, f"10<tspan font-size='8' dy='-5'>{e}</tspan>", 10, MUTE, "middle"))
    for e in range(ylo, yhi + 1, 3):
        body.append(path([(x0, Y(e)), (x1, Y(e))], stroke=LINE, width=1))
        body.append(txt(x0 - 6, Y(e) + 4, f"10<tspan font-size='8' dy='-5'>{e}</tspan>", 10, MUTE, "end"))
    h = 1.8
    es = np.linspace(xlo, xhi, 200)
    def tide(Msun):
        M = Msun * MSUN
        r = r_s(M)
        return 2 * G_SI * M * h / r ** 3
    pts = [(X(e), Y(math.log10(tide(10 ** e)))) for e in es]
    body.append(path(pts, stroke=HOT, width=2.2))
    for g_, lab in ((9.81, "1 g: a gentle pull"), (98.1, "10 g: fighter-pilot territory"), (9810, "1000 g: no body survives this")):
        body.append(path([(x0, Y(math.log10(g_))), (x1, Y(math.log10(g_)))], stroke=BLUE, width=1.2, dash="5 4"))
        body.append(txt(x1, Y(math.log10(g_)) - 5, lab, 11, BLUE, "end"))
    for m, lab in ((1, "Sun-mass"), (21, "Cyg X-1"), (1.4e4, "~14,000 M☉: 10 g"), (4.3e6, "Sgr A*"), (6.5e9, "M87*")):
        e = math.log10(m)
        body.append(circle(X(e), Y(math.log10(tide(m))), 4.5, fill=GOLD, stroke="none"))
        body.append(txt(X(e) + 8, Y(math.log10(tide(m))) - 8, lab, 11, GOLD))
    body.append(txt(x0, 36, "The stretch across a 1.8 m body at the horizon, by the hole's mass", 18, INK, weight=800, family=DISPLAY))
    body.append(txt(x0, 56, "Δa = 2GMh/r³ with r the horizon: the bigger the hole, the gentler the crossing — a small one shreds you far outside", 12, MUTE))
    body.append(txt(x0, y0 + 42, "mass, solar masses", 11, MUTE))
    body.append(txt(x0 - 6, y1 - 14, "m/s² head-to-foot", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "Tidal stretch at the horizon versus mass", "Log-log chart.")


# ---------------------------------------------------------------- 12. sizes to scale
def fig_sizes():
    W, H = 960, 520
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    # left: Sgr A* vs Mercury's orbit; right: M87* vs the outer solar system
    def orbits(ox, oy, S, items, hole_r, hole_lab, title, sub):
        for r_au, lab, col in items:
            body.append(circle(ox, oy, r_au * S, stroke=col, width=1.2, dash="3 3", op=.9))
            body.append(txt(ox + r_au * S * 0.707 + 4, oy - r_au * S * 0.707 - 4, lab, 11, col))
        body.append(circle(ox, oy, hole_r * S, fill="#000", stroke=HOT, width=2))
        body.append(circle(ox, oy, hole_r * S * 2.6, fill="none", stroke=HOT, width=1, dash="2 3", op=.8))
        body.append(txt(ox, oy + hole_r * S * 2.6 + 14, hole_lab, 11, HOT, "middle"))
        body.append(txt(ox - 200, 40, title, 18, INK, weight=800, family=DISPLAY))
        body.append(txt(ox - 200, 60, sub, 11.5, MUTE))
    rs_sgr = r_s(4.3e6 * MSUN) / AU
    orbits(250, 300, 420, [(0.387, "Mercury", BLUE), (0.723, "Venus", BLUE), (0.0466, "Sun's radius", GOLD)], rs_sgr / 2,
           "Sgr A*: horizon 0.085 au; shadow 2.6× that", "Sagittarius A*, 4.3 million suns", "against the inner solar system, to scale")
    rs_m87 = r_s(6.5e9 * MSUN) / AU
    orbits(720, 300, 1.05, [(30.1, "Neptune", BLUE), (39.5, "Pluto", BLUE), (167, "Voyager 1, 2025", VIOLET)], rs_m87 / 2,
           "M87*: horizon 128 au across; shadow ~330 au", "M87*, 6.5 billion suns", "against the outer solar system, to scale")
    body.append(txt(W - 20, H - 14, "the shadow is 3√3/2 ≈ 2.6 times the horizon: light from behind is bent around the sides", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "Two black holes against the solar system", "Sgr A* against Mercury's orbit; M87* against Neptune's.", bg="#000")


# ---------------------------------------------------------------- 13. orbit types
def orbit_from_turns(r1, r2):
    """E and L for a bound Schwarzschild orbit between periapsis r1 and apoapsis r2."""
    a1, a2 = 1 - 2 / r1, 1 - 2 / r2
    L2 = (a2 - a1) / (a1 / r1 ** 2 - a2 / r2 ** 2)
    L = math.sqrt(L2)
    E = math.sqrt(a2 * (1 + L2 / r2 ** 2))
    return E, L


def fig_orbits():
    W, H = 960, 470
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    cases = []
    E, L = orbit_from_turns(9.0, 22.0)
    cases.append(("precession", L, E, 22.0, f"L = {L:.2f}M, E = {E:.4f}: between r = 9M and 22M — a rosette, Mercury's precession made enormous", 5.6, 10 * math.pi))
    E, L = orbit_from_turns(4.05, 30.0)
    cases.append(("zoom-whirl", L, E, 30.0, f"L = {L:.2f}M, E = {E:.4f}: out to 30M, then whirls near r ≈ 4M before zooming out again", 4.1, 12 * math.pi))
    cases.append(("plunge", 3.2, 0.985, 16.0, "L = 3.2M: below L = √12 M the potential has no well; it spirals in and crosses r = 2M", 7.6, 8 * math.pi))
    for k, (name, L, E, r0, lab, S, pm) in enumerate(cases):
        ox, oy = 165 + k * 315, 215
        pts = particle_path(L, E, r0, phi_max=pm)
        body.append(circle(ox, oy, 6 * S, stroke=LINE, width=1, dash="3 3"))
        body.append(path([(ox + x * S, oy - y * S) for x, y in pts], stroke=(BLUE, HOT, RED)[k], width=1.3, op=.95))
        body.append(circle(ox, oy, 2 * S, fill="#000", stroke=INK, width=2))
        body.append(txt(ox, 372, name, 15, INK, "middle", weight=800, family=DISPLAY))
        for i, line in enumerate(_wrap(lab, 46)):
            body.append(txt(ox, 390 + i * 15, line, 11, MUTE, "middle"))
    body.append(txt(24, 34, "Three orbits Newton's gravity cannot draw", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(24, 56, "integrated from d²u/dφ² + u = M/L² + 3Mu²; the dotted circle is r = 6M", 12, MUTE))
    return svg(W, H, "".join(body), "Three orbits", "Precessing, zoom-whirl and plunging orbits around a Schwarzschild black hole.", bg="#000")


def _wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- 14. deflection angle
def fig_deflection():
    W, H = 960, 440
    body = []
    x0, x1, y0, y1 = 80, 920, 370, 60
    blo, bhi = 5.0, 30.0
    dlo, dhi = 0.0, 2.2   # radians
    def X(b): return x0 + (b - blo) / (bhi - blo) * (x1 - x0)
    def Y(d): return y0 - (d - dlo) / (dhi - dlo) * (y0 - y1)
    for b in range(5, 31, 5):
        body.append(path([(X(b), y0), (X(b), y0 + 5)], stroke=MUTE, width=1))
        body.append(txt(X(b), y0 + 18, f"{b}M", 10.5, MUTE, "middle"))
    for d in (0, 0.5, 1.0, 1.5, 2.0):
        body.append(path([(x0, Y(d)), (x1, Y(d))], stroke=LINE, width=1))
        body.append(txt(x0 - 6, Y(d) + 4, f"{d:.1f} rad", 10.5, MUTE, "end"))
    # weak-field line 4/b
    bs = np.linspace(5.3, 30, 200)
    body.append(path([(X(b), Y(4 / b)) for b in bs], stroke=BLUE, width=1.6, dash="5 4"))
    # exact: integrate
    exact = []
    for b in np.linspace(5.22, 30, 120):
        d = photon_deflection(b)
        if d is not None:
            exact.append((b, d))
    body.append(path([(X(b), Y(d)) for b, d in exact if 0 <= d <= dhi and b >= 5.3], stroke=HOT, width=2.2))
    body.append(txt(x0, 36, "How far a ray turns, by how close it passes", 18, INK, weight=800, family=DISPLAY))
    body.append(txt(x0, 56, "Einstein's 4GM/c²b (dashed) is right far out; near b = 3√3 M the exact answer runs away — the ray loops", 12, MUTE))
    body.append(f'<rect x="{x1 - 300}" y="82" width="14" height="4" fill="{HOT}"/>' + txt(x1 - 280, 87, "exact (integrated)", 12, INK))
    body.append(f'<rect x="{x1 - 300}" y="102" width="14" height="4" fill="{BLUE}"/>' + txt(x1 - 280, 107, "4M/b, the 1915 formula", 12, INK))
    body.append(txt(x0, y0 + 40, "impact parameter b", 11, MUTE))
    return svg(W, H, "".join(body), "Deflection angle versus impact parameter", "Exact versus weak-field.")


# ---------------------------------------------------------------- 15. Rahu: the invisible point
def fig_nodes():
    W, H = 960, 440
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    cx, cy = 480, 230
    body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="330" ry="90" fill="none" stroke="{GOLD}" stroke-width="1.4" stroke-dasharray="4 4"/>')
    body.append(txt(cx + 340, cy + 4, "the Sun's path", 11, GOLD))
    # the Moon's orbit tilted 5.1° — drawn as a second ellipse rotated a little
    body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="330" ry="90" fill="none" stroke="{BLUE}" stroke-width="1.6" transform="rotate(-9 {cx} {cx and cy})"/>')
    body.append(txt(cx - 340, cy - 66, "the Moon's path, tilted 5.1°", 11, BLUE, "end"))
    # nodes: intersections
    for sgn, lab in ((1, "Rahu ☊ — the ascending node"), (-1, "Ketu ☋ — the descending node")):
        x = cx + sgn * 300
        y = cy - sgn * 38 * 0 + (-1 if sgn > 0 else 1) * 40
        body.append(circle(x, y, 7, fill="#000", stroke=RED, width=2.5))
        body.append(txt(x, y + (24 if sgn > 0 else -14), lab, 12, RED, "middle"))
    body.append(circle(cx, cy, 18, fill=GOLD, stroke="none"))
    body.append(txt(cx, cy + 5, "☉", 18, "#000", "middle"))
    body.append(txt(24, 34, "Rahu is a point, not a body — and it has an orbit", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(24, 56, "eclipses happen only where the Moon's tilted path crosses the Sun's; the crossing points drift backwards once every 18.6 years", 12, MUTE))
    body.append(txt(W - 24, H - 40, "Indian astronomers computed the nodes by the 5th century (Āryabhaṭa, 499); the Thai and Lanna calendar carries them as พระราหู", 11, MUTE, "end"))
    body.append(txt(W - 24, H - 22, "an invisible thing, known by its period and by the light it takes away: the oldest model of a light-eater", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "The lunar nodes: Rahu and Ketu", "The Moon's tilted orbit crosses the ecliptic at two points that regress every 18.6 years.", bg="#000")


# ---------------------------------------------------------------- 16. photon ring stack
def fig_ringstack():
    """The photon ring: each extra half-orbit adds a thinner ring, e^-π narrower."""
    W, H = 960, 440
    body = [f'<rect width="{W}" height="{H}" fill="#000"/>']
    cx, cy, S = 300, 230, 34
    b_c = math.sqrt(27)
    # the direct image edge (schematic) and subrings converging on b_c
    body.append(circle(cx, cy, b_c * S * 1.24, stroke=HOT, width=26, op=.35))
    for n in range(0, 4):
        r = b_c * S * (1 + 0.24 * math.exp(-math.pi * n))
        w = max(1.2, 9 * math.exp(-math.pi * n * .6))
        body.append(circle(cx, cy, r, stroke=GOLD if n else HOT, width=w))
    body.append(circle(cx, cy, b_c * S, stroke=INK, width=1, dash="3 3"))
    body.append(txt(cx, cy + 5, "shadow", 13, MUTE, "middle"))
    body.append(txt(24, 34, "The photon ring is a stack", 20, INK, weight=800, family=DISPLAY))
    body.append(txt(24, 56, "light that half-circles the hole once, twice, three times before leaving; each subring is e^π ≈ 23 times thinner", 12, MUTE))
    x = 620
    rows = [("n = 0", "the direct image of the disk", HOT), ("n = 1", "one half-turn: the far side of the disk, over the top", GOLD),
            ("n = 2", "one full turn: a ring 23× thinner, on the edge of the shadow", GOLD), ("n = 3…", "thinner again; the sum converges on b = 3√3 M", GOLD)]
    for i, (a, b, c) in enumerate(rows):
        yy = 150 + i * 46
        body.append(txt(x, yy, a, 16, c, weight=800, family=DISPLAY))
        for j, line in enumerate(_wrap(b, 40)):
            body.append(txt(x + 60, yy + j * 15, line, 12, INK))
    body.append(txt(W - 24, H - 20, "Gralla, Holz & Wald 2019; Johnson et al. 2020 — a space telescope could resolve n = 1", 11, MUTE, "end"))
    return svg(W, H, "".join(body), "The photon ring subrings", "Schematic of the direct image and the n=1,2,3 subrings.", bg="#000")


# ---------------------------------------------------------------- 17. black hole eras
def fig_eras():
    W, H = 960, 300
    body = []
    x0, x1, y = 60, 900, 150
    lo, hi = 0, 100
    def X(e): return x0 + (e - lo) / (hi - lo) * (x1 - x0)
    eras = [(0, 6, "primordial", VIOLET), (6, 14, "stars burn", GOLD), (14, 40, "degenerate remnants", BLUE), (40, 100, "black holes only", HOT)]
    for a, b, lab, col in eras:
        body.append(f'<rect x="{X(a)}" y="{y - 30}" width="{X(b) - X(a)}" height="60" fill="{col}" opacity=".22"/>')
        body.append(path([(X(a), y - 30), (X(a), y + 30)], stroke=col, width=1.5))
        body.append(txt((X(a) + X(b)) / 2, y + 5 if b - a > 7 else y - 40, lab, 13, INK, "middle", weight=700))
    for e in range(0, 101, 10):
        body.append(txt(X(e), y + 52, f"10<tspan font-size='8' dy='-5'>{e}</tspan>", 10.5, MUTE, "middle"))
    body.append(txt(x0, y + 70, "years after the Big Bang, log scale — Adams & Laughlin 1997", 11, MUTE))
    body.append(txt(x0, 36, "The eras of the universe, and who is left at the end", 18, INK, weight=800, family=DISPLAY))
    body.append(txt(x0, 56, "now ≈ 10¹⁰ years; a Sun-mass hole lasts 10⁶⁷; the largest last to 10¹⁰⁰, then the dark era", 12, MUTE))
    body.append(circle(X(10.14), y - 30, 5, fill=INK, stroke="none"))
    body.append(txt(X(10.14), y - 40, "now", 11, INK, "middle"))
    for e, lab in ((67, "1 M☉ gone"), (87, "Sgr A* gone"), (100, "TON 618 gone")):
        body.append(circle(X(e), y + 30, 4, fill=HOT, stroke="none"))
        body.append(txt(X(e), y + 42 - 60 - 8, lab, 10.5, HOT, "middle"))
    return svg(W, H, "".join(body), "Eras of the universe", "Timeline to 10^100 years.")


FIGS = {
    "bending.svg": fig_bending, "flamm.svg": fig_flamm, "potential.svg": fig_potential,
    "penrose.svg": fig_penrose, "shadows.svg": fig_shadows, "ladder.svg": fig_ladder,
    "evaporation.svg": fig_evaporation, "chirp.svg": fig_chirp, "kerr.svg": fig_kerr,
    "pixels.svg": fig_pixels, "tides.svg": fig_tides, "sizes.svg": fig_sizes,
    "orbits.svg": fig_orbits, "deflection.svg": fig_deflection, "nodes.svg": fig_nodes,
    "ringstack.svg": fig_ringstack, "eras.svg": fig_eras,
}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        save(name, fn())
    # the numbers the site prints, computed here rather than typed there
    facts = {
        "rs_sun_km": r_s(MSUN) / 1e3, "rs_earth_mm": r_s(5.972e24) * 1e3,
        "rs_sgr_au": r_s(4.3e6 * MSUN) / AU, "rs_m87_au": r_s(6.5e9 * MSUN) / AU,
        "T_sun_K": hawking_T(MSUN), "t_sun_yr": t_evap(MSUN) / YEAR,
        "m_evap_now_kg": (AGE * HBAR * C_SI ** 4 / (5120 * math.pi * G_SI ** 2)) ** (1 / 3),
        "shadow_m87_uas": 2 * math.sqrt(27) * G_SI * 6.5e9 * MSUN / C_SI ** 2 / (16.8e6 * 3.0857e16) * 206264.806 * 1e6,
        "shadow_sgr_uas": 2 * math.sqrt(27) * G_SI * 4.297e6 * MSUN / C_SI ** 2 / (8277 * 3.0857e16) * 206264.806 * 1e6,
        "tide_sun_g": 2 * G_SI * MSUN * 1.8 / r_s(MSUN) ** 3 / 9.81,
        "tide_sgr_g": 2 * G_SI * 4.3e6 * MSUN * 1.8 / r_s(4.3e6 * MSUN) ** 3 / 9.81,
    }
    (ROOT / "build" / "facts.json").write_text(json.dumps(facts, indent=1), encoding="utf-8")
    print("  wrote build/facts.json")
