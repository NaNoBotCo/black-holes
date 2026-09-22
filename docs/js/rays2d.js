/* rays2d.js — one ray at a time, stepped in front of you.
   The plane through the centre and the ray. Slide b, watch the equation walk. */
(function () {
  const root = document.getElementById('rays');
  if (!root) return;
  const cv = root.querySelector('canvas');
  const cx2 = cv.getContext('2d');
  const bEl = root.querySelector('input[name=b]');
  const bOut = root.querySelector('output[for=b]');
  const read = root.querySelector('.read');
  let newton = false, fan = false;
  root.querySelector('[data-toggle=newton]').addEventListener('click', e => { newton = !newton; e.currentTarget.setAttribute('aria-pressed', newton); restart(); });
  root.querySelector('[data-toggle=fan]').addEventListener('click', e => { fan = !fan; e.currentTarget.setAttribute('aria-pressed', fan); restart(); });
  bEl.addEventListener('input', () => { bOut.textContent = (+bEl.value).toFixed(2) + ' M'; restart(); });
  bOut.textContent = (+bEl.value).toFixed(2) + ' M';

  const R0 = 30, S = 12;   // start radius, px per M
  let W, H, cx, cy, rays = [], raf = 0, step = 0;
  function size() {
    const w = Math.min(root.clientWidth, 960);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = Math.round(w * dpr); H = Math.round(W * 0.56);
    cv.width = W; cv.height = H; cx = W * 0.55; cy = H * 0.5;
  }
  function mk(b) {
    const u = 1 / R0, du = Math.sqrt(Math.max(1 / (b * b) - u * u, 0)), phi = Math.asin(Math.min(1, b / R0));
    return { b, u, du, phi, pts: [], end: '' };
  }
  function acc(u) { return newton ? -u : 3 * u * u - u; }
  function stepRay(r, dphi) {
    if (r.end) return;
    const { u, du } = r;
    const k1u = du, k1d = acc(u);
    const k2u = du + .5 * dphi * k1d, k2d = acc(u + .5 * dphi * k1u);
    const k3u = du + .5 * dphi * k2d, k3d = acc(u + .5 * dphi * k2u);
    const k4u = du + dphi * k3d, k4d = acc(u + dphi * k3u);
    r.u += dphi / 6 * (k1u + 2 * k2u + 2 * k3u + k4u);
    r.du += dphi / 6 * (k1d + 2 * k2d + 2 * k3d + k4d);
    r.phi += dphi;
    const rr = 1 / r.u;
    if (r.u >= .5) { r.end = 'in'; r.pts.push([2 * Math.cos(r.phi), 2 * Math.sin(r.phi)]); return; }
    if (r.u <= 1 / (1.6 * R0)) {
      r.end = 'out'; r.pts.push([rr * Math.cos(r.phi), rr * Math.sin(r.phi)]);
      // the turn, from the heading on the way out: φ + atan2(r, dr/dφ), less the straight-through π
      r.defl = ((r.phi + Math.atan2(rr, -rr * rr * r.du)) - Math.PI + 4 * Math.PI) % (2 * Math.PI);
      return;
    }
    if (r.phi > 6 * Math.PI) { r.end = 'stuck'; return; }
    r.pts.push([rr * Math.cos(r.phi), rr * Math.sin(r.phi)]);
  }
  function restart() {
    cancelAnimationFrame(raf); size(); step = 0;
    const b = +bEl.value;
    rays = fan ? [2, 3, 4, 4.8, 5.1, 5.196, 5.3, 5.8, 7, 9, 12, 16].map(mk) : [mk(b)];
    for (const r of rays) r.pts.push([R0 * Math.cos(r.phi), R0 * Math.sin(r.phi)]);
    raf = requestAnimationFrame(tick);
  }
  function col(r) { return r.end === 'in' ? '#ff6a5e' : (Math.abs(r.b - 5.196) < .02 ? '#ffb347' : (r.b < 5.196 ? '#ff6a5e' : '#8fd0ff')); }
  function draw() {
    const g = cx2; g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    g.strokeStyle = '#2a2a38'; g.lineWidth = 1;
    for (let r = 5; r <= 30; r += 5) { g.beginPath(); g.arc(cx, cy, r * S * W / 960, 0, 6.29); g.stroke(); }
    g.setLineDash([4, 4]); g.strokeStyle = '#b3ac9e'; g.beginPath(); g.arc(cx, cy, 3 * S * W / 960, 0, 6.29); g.stroke(); g.setLineDash([]);
    g.fillStyle = '#000'; g.strokeStyle = '#f3efe6'; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, 2 * S * W / 960, 0, 6.29); g.fill(); g.stroke();
    g.fillStyle = '#b3ac9e'; g.font = `${12 * W / 960}px system-ui,sans-serif`; g.textAlign = 'center';
    g.fillText('r = 2M', cx, cy + 4 * W / 960);
    g.fillText('r = 3M', cx, cy - 3.6 * S * W / 960);
    const k = S * W / 960;
    for (const r of rays) {
      g.strokeStyle = col(r); g.lineWidth = fan ? 1.4 : 2.2; g.beginPath();
      r.pts.forEach((p, i) => { const x = cx + p[0] * k, y = cy - p[1] * k; i ? g.lineTo(x, y) : g.moveTo(x, y); });
      g.stroke();
      const p = r.pts[r.pts.length - 1];
      if (!r.end) { g.fillStyle = col(r); g.beginPath(); g.arc(cx + p[0] * k, cy - p[1] * k, 3.5, 0, 6.29); g.fill(); }
    }
  }
  function tick() {
    const dphi = 0.01;
    for (let i = 0; i < 6; i++) for (const r of rays) stepRay(r, dphi);
    step += 6; draw();
    const r = rays[0];
    if (!fan) {
      const rr = 1 / r.u;
      const eq = newton ? "u'' + u = 0" : "u'' + u = 3u²";
      read.innerHTML = `<b>${eq}</b>   b = ${r.b.toFixed(3)} M   φ = ${r.phi.toFixed(2)} rad   r = ${rr.toFixed(2)} M   u = 1/r = ${r.u.toFixed(4)}   du/dφ = ${r.du.toFixed(4)}   step ${step}\n`
        + (r.end === 'in' ? '<b>fell in</b> — crossed r = 2M; nothing comes back from there'
          : r.end === 'out' ? `<b>left</b> — turned by ${(r.defl * 180 / Math.PI).toFixed(1)}°; the 1915 formula 4M/b says ${(4 / r.b * 180 / Math.PI).toFixed(1)}°`
            : r.end === 'stuck' ? '<b>circling</b> — this is the photon sphere; a hair either way and it falls or leaves' : 'stepping…');
    } else {
      read.innerHTML = `<b>twelve rays</b>, b from 2 M to 16 M · red fall in · orange circles at b = 3√3 M ≈ 5.196 M · blue are bent and gone`;
    }
    if (rays.some(x => !x.end)) raf = requestAnimationFrame(tick);
  }
  restart();
  window.addEventListener('resize', restart);
})();
