#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render.py — the pictures, computed.

A Schwarzschild black hole with a thin disk, traced ray by ray in numpy. Units G=c=M=1,
so the horizon sits at r=2, the photon sphere at r=3, the innermost stable orbit at r=6.

For each pixel a light ray is followed backwards from the camera. In the plane that the
ray and the centre share, its path obeys

    d²u/dφ² + u = 3u²        (u = 1/r)

which is Newton's straight line (u'' + u = 0) plus one term. That term is all the bending.
The ray ends in one of three ways: below r=2 (paint it black), on the disk (paint the
disk's colour, shifted by the disk's motion and the well it sits in), or off to the sky
(paint the star it points at).

    python3 tools/render.py             # every picture, into build/img/
    python3 tools/render.py hero        # one
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "img"


# ---------------------------------------------------------------- the sky
def star_sky(w=4096, h=2048, n=26000, seed=7):
    """An equirectangular star map: a few thousand points with a power-law spread of
    brightness, a faint band for the galaxy, softened so a magnified patch still reads
    as stars rather than as a grid."""
    rng = np.random.default_rng(seed)
    sky = np.zeros((h, w, 3), np.float32)
    # a galactic band, tilted
    yy, xx = np.mgrid[0:h, 0:w]
    lon = (xx / w) * 2 * np.pi
    lat = (yy / h - 0.5) * np.pi
    band = np.exp(-((lat - 0.35 * np.sin(lon + 1.1)) / 0.13) ** 2)
    sky += (band[..., None] * np.array([0.020, 0.024, 0.040], np.float32))
    # stars
    x = rng.integers(0, w, n)
    y = (np.arcsin(rng.uniform(-1, 1, n)) / np.pi + 0.5) * h
    y = np.clip(y.astype(int), 0, h - 1)
    mag = rng.pareto(2.2, n) * 0.06 + 0.02
    mag = np.clip(mag, 0, 2.5)
    tint = rng.uniform(0, 1, n)
    col = np.where(tint[:, None] < 0.3, [1.0, 0.86, 0.72],
                   np.where(tint[:, None] < 0.75, [0.95, 0.96, 1.0], [0.72, 0.82, 1.0])).astype(np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            wgt = 1.0 if (dx == 0 and dy == 0) else (0.30 if dx * dy == 0 else 0.10)
            sky[np.clip(y + dy, 0, h - 1), (x + dx) % w] += (mag * wgt)[:, None] * col
    return sky


_SKY = None


def sky():
    global _SKY
    if _SKY is None:
        _SKY = star_sky()
    return _SKY


def sample_sky(v):
    """v: (N,3) unit vectors → (N,3) colours."""
    s = sky()
    h, w = s.shape[:2]
    lon = np.arctan2(v[:, 1], v[:, 0])
    lat = np.arcsin(np.clip(v[:, 2], -1, 1))
    x = ((lon / (2 * np.pi)) % 1.0) * w
    y = (lat / np.pi + 0.5) * h
    xi = np.clip(x.astype(int), 0, w - 1)
    yi = np.clip(y.astype(int), 0, h - 1)
    return s[yi, xi]


# ---------------------------------------------------------------- colour
def blackbody_rgb(T):
    """Temperature in kelvin → linear RGB, roughly along the Planckian locus. Good enough
    for a picture; not a colorimetric calculation."""
    T = np.clip(T, 1000.0, 40000.0) / 100.0
    r = np.where(T <= 66, 255.0, 329.698727446 * np.power(np.maximum(T - 60, 1e-6), -0.1332047592))
    g = np.where(T <= 66, 99.4708025861 * np.log(np.maximum(T, 1e-6)) - 161.1195681661,
                 288.1221695283 * np.power(np.maximum(T - 60, 1e-6), -0.0755148492))
    b = np.where(T >= 66, 255.0, np.where(T <= 19, 0.0, 138.5177312231 * np.log(np.maximum(T - 10, 1e-6)) - 305.0447927307))
    rgb = np.stack([r, g, b], -1) / 255.0
    rgb = np.clip(rgb, 0, 1) ** 2.2  # to linear
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    return rgb / np.maximum(lum[..., None], 1e-6)


# ---------------------------------------------------------------- the trace
def trace(W, H, incl_deg=80.0, r_cam=60.0, half_width=24.0, r_in=6.0, r_out=22.0,
          gravity=True, disk=True, dphi=0.012, phi_max=3.2 * np.pi, t_peak=6500.0,
          doppler=True, verbose=True):
    """Returns (rgb linear (H,W,3), kind (H,W) 0=hole 1=disk 2=sky, r_hit (H,W), g (H,W))."""
    i = np.radians(incl_deg)
    n = np.array([np.sin(i), 0.0, np.cos(i)])           # camera direction from the centre
    f = -n                                                # looking at the centre
    right = np.array([0.0, 1.0, 0.0])
    up = np.cross(right, f)
    up /= np.linalg.norm(up)

    ys, xs = np.mgrid[0:H, 0:W]
    px = (xs + 0.5) / W * 2 - 1
    py = 1 - (ys + 0.5) / H * 2
    aspect = H / W
    sx = px * half_width / r_cam
    sy = py * half_width * aspect / r_cam
    d = f[None, None, :] + sx[..., None] * right + sy[..., None] * up
    d = d.reshape(-1, 3)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    N = d.shape[0]

    # the plane of each ray: e1 toward the camera, e2 the sideways part of the direction
    e1 = np.tile(n, (N, 1))
    dn = d @ n
    e2 = d - dn[:, None] * e1
    e2n = np.linalg.norm(e2, axis=1)
    e2n = np.maximum(e2n, 1e-9)
    e2 /= e2n[:, None]

    # signed impact parameters in the image plane (units of M)
    bx = r_cam * (d @ right)
    by = r_cam * (d @ up)

    u = np.full(N, 1.0 / r_cam)
    du = -dn / (r_cam * e2n)        # inward, so positive
    phi = np.zeros(N)
    z_prev = (1.0 / u) * (np.cos(phi) * e1[:, 2] + np.sin(phi) * e2[:, 2])

    kind = np.full(N, -1, np.int8)
    r_hit = np.zeros(N)
    esc_dir = np.zeros((N, 3))
    active = np.arange(N)

    def acc(uu):
        return (3.0 * uu * uu - uu) if gravity else (-uu)

    step = 0
    t0 = time.time()
    while active.size:
        a = active
        ua, dua = u[a], du[a]
        # RK4 on (u, u')
        k1u, k1d = dua, acc(ua)
        k2u, k2d = dua + 0.5 * dphi * k1d, acc(ua + 0.5 * dphi * k1u)
        k3u, k3d = dua + 0.5 * dphi * k2d, acc(ua + 0.5 * dphi * k2u)
        k4u, k4d = dua + dphi * k3d, acc(ua + dphi * k3u)
        un = ua + dphi / 6 * (k1u + 2 * k2u + 2 * k3u + k4u)
        dun = dua + dphi / 6 * (k1d + 2 * k2d + 2 * k3d + k4d)
        pn = phi[a] + dphi
        u[a], du[a], phi[a] = un, dun, pn

        done = np.zeros(a.size, bool)

        # fell in
        fell = un >= 0.5
        kind[a[fell]] = 0
        done |= fell

        # the disk: sign change of z between steps, at a radius on the disk
        if disk:
            zn = (1.0 / np.maximum(un, 1e-9)) * (np.cos(pn) * e1[a, 2] + np.sin(pn) * e2[a, 2])
            zp = z_prev[a]
            cross = (zp * zn < 0) & (un > 0) & ~done
            if cross.any():
                t = zp[cross] / (zp[cross] - zn[cross])
                u_c = (1 - t) * (un[cross] - dphi * dun[cross]) + t * un[cross]
                rc = 1.0 / np.maximum(u_c, 1e-9)
                hit = (rc >= r_in) & (rc <= r_out)
                idx = a[cross][hit]
                kind[idx] = 1
                r_hit[idx] = rc[hit]
                dm = np.zeros(a.size, bool)
                dm[np.flatnonzero(cross)[hit]] = True
                done |= dm
            z_prev[a] = zn

        # escaped
        esc = (un <= 0) & ~done
        if esc.any():
            idx = a[esc]
            kind[idx] = 2
            # the angle where u reaches zero, between the two steps — taking the step's
            # own angle quantises every star into a radial streak dphi long
            up_ = un[esc] - dphi * dun[esc]
            t = up_ / np.maximum(up_ - un[esc], 1e-12)
            pe = pn[esc] - dphi + t * dphi
            esc_dir[idx] = np.cos(pe)[:, None] * e1[idx] + np.sin(pe)[:, None] * e2[idx]
            done |= esc

        # ran out of turns: these are the rays circling the photon sphere
        stuck = (pn > phi_max) & ~done
        kind[a[stuck]] = 0
        done |= stuck

        active = a[~done]
        step += 1
        if verbose and step % 100 == 0:
            print(f"    step {step:4d}  active {active.size:8d}  {time.time() - t0:5.1f}s", flush=True)

    kind[kind < 0] = 0

    # ------------------------------------------------ shade
    rgb = np.zeros((N, 3), np.float32)
    m = kind == 2
    if m.any():
        v = esc_dir[m]
        v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
        rgb[m] = sample_sky(v)

    g = np.ones(N)
    m = kind == 1
    if m.any():
        r = r_hit[m]
        # the disk's own temperature: a thin disk with zero torque at its inner edge
        t_prof = (r ** -3 * (1 - np.sqrt(r_in / r)))
        t_prof = np.clip(t_prof, 0, None) ** 0.25
        # Kepler's law here is Ω = r^-3/2; the shift is Luminet 1979 eq. for a thin disk
        omega = r ** -1.5
        if doppler:
            gg = np.sqrt(np.clip(1 - 3.0 / r, 0, None)) / (1 + omega * bx[m] * np.sin(i))
        else:
            gg = np.sqrt(np.clip(1 - 3.0 / r, 0, None))
        g[m] = gg
        t_em = t_peak * t_prof / t_prof.max()
        t_obs = gg * t_em
        bright = (gg ** 4) * (t_em / t_peak) ** 4
        rgb[m] = blackbody_rgb(t_obs) * bright[:, None] * 1.6

    return (rgb.reshape(H, W, 3), kind.reshape(H, W), r_hit.reshape(H, W), g.reshape(H, W))


def tonemap(rgb, exposure=1.0, gamma=2.2):
    x = 1 - np.exp(-rgb * exposure)
    return np.clip(x, 0, 1) ** (1 / gamma)


def save(rgb, path: Path, exposure=1.0, quality=88):
    path.parent.mkdir(parents=True, exist_ok=True)
    im = (tonemap(rgb, exposure) * 255).astype(np.uint8)
    Image.fromarray(im).save(path, quality=quality, optimize=True, progressive=True)
    print(f"  wrote {path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")


def halftone(lum, cell=4, dot_max=None, invert=False):
    """Luminet's 1979 picture was an IBM 7040's numbers drawn by hand as dots of India ink,
    denser where the disk is brighter. This does the same with a grid of dots."""
    H, W = lum.shape
    dot_max = dot_max or cell * 0.62
    Hc, Wc = H // cell, W // cell
    L = lum[:Hc * cell, :Wc * cell].reshape(Hc, cell, Wc, cell).mean(axis=(1, 3))
    L = np.clip(L, 0, 1)
    scale = 4
    paper = np.full((Hc * cell * scale, Wc * cell * scale), 255, np.uint8)
    yy, xx = np.mgrid[0:cell * scale, 0:cell * scale]
    cx = cy = (cell * scale - 1) / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    for j in range(Hc):
        for i in range(Wc):
            v = L[j, i]
            if v <= 0.02:
                continue
            rad = np.sqrt(v) * dot_max * scale
            blk = dist <= rad
            ys, xs = j * cell * scale, i * cell * scale
            tile = paper[ys:ys + cell * scale, xs:xs + cell * scale]
            tile[blk] = 0
    im = Image.fromarray(paper).resize((Wc * cell, Hc * cell), Image.LANCZOS)
    return im


# ---------------------------------------------------------------- the pictures
def do_hero():
    rgb, kind, r, g = trace(1600, 900, incl_deg=80, r_out=22, t_peak=6800)
    save(rgb, OUT / "hero.jpg", exposure=1.15)
    # the same, larger disk, for the share card
    save(rgb, OUT / "card.jpg", exposure=1.15, quality=82)


def do_angles():
    for name, inc in (("face", 12), ("tilt", 55), ("edge", 84)):
        rgb, *_ = trace(1200, 675, incl_deg=inc, r_out=20, t_peak=6800)
        save(rgb, OUT / f"angle-{name}.jpg", exposure=1.15)


def do_flat():
    """What the same disk looks like when light goes straight: no lensing, no ring."""
    rgb, *_ = trace(1200, 675, incl_deg=80, r_out=22, gravity=False, t_peak=6800)
    save(rgb, OUT / "straight.jpg", exposure=1.15)
    rgb, *_ = trace(1200, 675, incl_deg=80, r_out=22, gravity=True, t_peak=6800)
    save(rgb, OUT / "bent.jpg", exposure=1.15)


def do_nodoppler():
    rgb, *_ = trace(1200, 675, incl_deg=80, r_out=22, doppler=False, t_peak=6800)
    save(rgb, OUT / "no-doppler.jpg", exposure=1.15)


def do_lens():
    """No disk. Only the sky, bent: the Einstein ring of the whole background."""
    rgb, *_ = trace(1200, 675, incl_deg=80, disk=False, half_width=14)
    save(rgb, OUT / "lens.jpg", exposure=2.2)
    rgb, *_ = trace(1200, 675, incl_deg=80, disk=False, half_width=14, gravity=False)
    save(rgb, OUT / "lens-off.jpg", exposure=2.2)


def do_luminet():
    """A recomputation in the spirit of Luminet (1979): bolometric, one colour, dots."""
    rgb, kind, r, g = trace(1000, 640, incl_deg=80, r_out=16, half_width=18, t_peak=6800)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    lum = np.where(kind == 1, lum, 0)      # the disk only: he drew no stars
    lum = tonemap(lum[..., None], exposure=1.8)[..., 0]
    im = halftone(lum, cell=4)
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / "luminet-1979-recomputed.png", optimize=True)
    print("  wrote build/img/luminet-1979-recomputed.png")


def do_ring():
    """Close in on the photon ring: the disk seen from 84°, tight crop."""
    rgb, *_ = trace(1200, 675, incl_deg=84, r_out=14, half_width=9, t_peak=6800)
    save(rgb, OUT / "ring.jpg", exposure=1.0)


def do_bands():
    """Wide, dark, quiet frames for the parallax bands."""
    rgb, *_ = trace(1600, 700, incl_deg=70, r_out=26, half_width=34, t_peak=6000)
    save(rgb, OUT / "band-wide.jpg", exposure=0.9, quality=80)
    rgb, *_ = trace(1600, 700, incl_deg=88, r_out=18, half_width=16, t_peak=7500)
    save(rgb, OUT / "band-edge.jpg", exposure=1.0, quality=80)
    rgb, *_ = trace(1600, 700, incl_deg=80, disk=False, half_width=12)
    save(rgb, OUT / "band-lens.jpg", exposure=2.4, quality=80)


JOBS = {"hero": do_hero, "angles": do_angles, "flat": do_flat, "lens": do_lens,
        "luminet": do_luminet, "ring": do_ring, "bands": do_bands, "nodoppler": do_nodoppler}

if __name__ == "__main__":
    want = sys.argv[1:] or list(JOBS)
    for w in want:
        print(f"[{w}]", flush=True)
        JOBS[w]()
