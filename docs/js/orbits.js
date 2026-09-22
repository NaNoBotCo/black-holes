/* orbits.js — throw something at a black hole.
   A massive particle in Schwarzschild: d²u/dφ² + u = M/L² + 3Mu², with the energy
   equation fixing the start. Newton's version drops the last term. */
(function () {
  const root = document.getElementById('orbits');
  if (!root) return;
  const cv = root.querySelector('canvas'), g = cv.getContext('2d');
  const L = root.querySelector('input[name=L]'), E = root.querySelector('input[name=E]');
  const read = root.querySelector('.read');
  let newton = false, raf = 0, st = null, W, H;
  function outs() { root.querySelector('output[for=L]').textContent = (+L.value).toFixed(2) + ' M'; root.querySelector('output[for=E]').textContent = (+E.value).toFixed(4); }
  [L, E].forEach(el => el.addEventListener('input', () => { outs(); restart(); }));
  root.querySelector('[data-toggle=newton]').addEventListener('click', e => { newton = !newton; e.currentTarget.setAttribute('aria-pressed', newton); restart(); });
  root.querySelectorAll('.presets button').forEach(b => b.addEventListener('click', () => {
    const p = JSON.parse(b.dataset.set); L.value = p.L; E.value = p.E;
    if ('newton' in p) { newton = p.newton; root.querySelector('[data-toggle=newton]').setAttribute('aria-pressed', newton); }
    outs(); restart();
  }));
  function V(r, l) { return newton ? Math.sqrt(Math.max(1 - 2 / r + l * l / (r * r), 0)) : Math.sqrt(Math.max((1 - 2 / r) * (1 + l * l / (r * r)), 0)); }
  function size() {
    const w = Math.min(root.clientWidth, 960), dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = Math.round(w * dpr); H = Math.round(W * 0.56); cv.width = W; cv.height = H;
  }
  function restart() {
    cancelAnimationFrame(raf); size();
    const l = +L.value, e = +E.value;
    // start at the outer turning point if there is one, else far out and falling
    // V(r) → 1 far out, so a bound orbit's outer turning point is the largest r with V ≤ E
    let r0 = 40;
    for (let r = 60; r > 2.05; r -= 0.02) { if (V(r, l) <= e) { r0 = r - 0.01; break; } }
    const u = 1 / r0;
    const v = newton ? (e * e - (1 - 2 * u + l * l * u * u)) / (l * l) : (e * e - (1 - 2 * u) * (1 + l * l * u * u)) / (l * l);
    st = { l, e, u, du: -Math.sqrt(Math.max(v, 0)), phi: 0, pts: [[r0, 0]], end: '', turns: 0, rmin: r0, rmax: r0, steps: 0 };
    raf = requestAnimationFrame(tick);
  }
  function acc(u, l) { return 1 / (l * l) + (newton ? 0 : 3 * u * u) - u; }
  function tick() {
    const s = st, d = 0.004;
    for (let i = 0; i < 40 && !s.end; i++) {
      const k1u = s.du, k1d = acc(s.u, s.l);
      const k2u = s.du + .5 * d * k1d, k2d = acc(s.u + .5 * d * k1u, s.l);
      const k3u = s.du + .5 * d * k2d, k3d = acc(s.u + .5 * d * k2u, s.l);
      const k4u = s.du + d * k3d, k4d = acc(s.u + d * k3u, s.l);
      s.u += d / 6 * (k1u + 2 * k2u + 2 * k3u + k4u); s.du += d / 6 * (k1d + 2 * k2d + 2 * k3d + k4d); s.phi += d; s.steps++;
      const r = 1 / s.u;
      if (s.u >= .5) { s.end = 'in'; s.pts.push([2, s.phi]); break; }
      if (s.u <= 1 / 200) { s.end = 'out'; break; }
      s.rmin = Math.min(s.rmin, r); s.rmax = Math.max(s.rmax, r);
      if (s.steps % 3 === 0) s.pts.push([r, s.phi]);
      if (s.phi > 60 * Math.PI) { s.end = 'long'; break; }
    }
    draw();
    const per = (s.phi / (2 * Math.PI)).toFixed(2);
    read.innerHTML = `<b>${newton ? "u'' + u = M/L²" : "u'' + u = M/L² + 3Mu²"}</b>   L = ${s.l.toFixed(2)} M   E = ${s.e.toFixed(4)}   r = ${(1 / s.u).toFixed(2)} M   turns ${per}   closest ${s.rmin.toFixed(2)} M   farthest ${s.rmax.toFixed(1)} M\n`
      + (s.end === 'in' ? '<b>fell in.</b> ' + (s.l < Math.sqrt(12) && !newton ? 'With L below √12 M ≈ 3.46 M there is no stable circle at any radius.' : 'The energy carried it over the rim of the potential.')
        : s.end === 'out' ? '<b>escaped.</b> E above 1 is an unbound orbit: it came, it bent, it left.'
          : s.end === 'long' ? '<b>still going</b> after thirty turns — a bound orbit. Newton would close it into one ellipse; Einstein turns it into a rosette.' : 'stepping…');
    if (!s.end) raf = requestAnimationFrame(tick);
  }
  function draw() {
    const s = st; g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    const cx = W * 0.36, cy = H * 0.5, k = Math.min(W * 0.34, H * 0.47) / Math.max(s.rmax, 12);
    g.strokeStyle = '#2a2a38'; g.lineWidth = 1;
    for (let r = 6; r <= s.rmax + 6; r += 6) { g.beginPath(); g.arc(cx, cy, r * k, 0, 6.29); g.stroke(); }
    g.setLineDash([3, 4]); g.strokeStyle = '#ffb347'; g.beginPath(); g.arc(cx, cy, 6 * k, 0, 6.29); g.stroke(); g.setLineDash([]);
    g.strokeStyle = s.end === 'in' ? '#ff6a5e' : '#8fd0ff'; g.lineWidth = 1.6; g.beginPath();
    s.pts.forEach((p, i) => { const x = cx + p[0] * Math.cos(p[1]) * k, y = cy - p[0] * Math.sin(p[1]) * k; i ? g.lineTo(x, y) : g.moveTo(x, y); });
    g.stroke();
    g.fillStyle = '#000'; g.strokeStyle = '#f3efe6'; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, Math.max(2 * k, 3), 0, 6.29); g.fill(); g.stroke();
    if (!s.end) { const p = s.pts[s.pts.length - 1]; g.fillStyle = '#ffd27a'; g.beginPath(); g.arc(cx + p[0] * Math.cos(p[1]) * k, cy - p[0] * Math.sin(p[1]) * k, 4, 0, 6.29); g.fill(); }
    g.fillStyle = '#b3ac9e'; g.font = `${11 * W / 960}px system-ui,sans-serif`; g.textAlign = 'left';
    g.fillText('dotted: r = 6M, the last stable circle', 12, H - 12);
    // the potential, at right
    const x0 = W * 0.70, x1 = W * 0.97, y0 = H * 0.86, y1 = H * 0.14;
    const rmin = 2, rmax = 40, vlo = 0.85, vhi = 1.12;
    const X = r => x0 + (Math.log(r / rmin) / Math.log(rmax / rmin)) * (x1 - x0), Y = v => y0 - (v - vlo) / (vhi - vlo) * (y0 - y1);
    g.strokeStyle = '#2a2a38'; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y0); g.moveTo(x0, y0); g.lineTo(x0, y1); g.stroke();
    g.strokeStyle = '#c8a6ff'; g.lineWidth = 2; g.beginPath(); let first = true;
    for (let r = rmin + .02; r <= rmax; r *= 1.01) { const v = V(r, s.l); if (v < vlo || v > vhi) { first = true; continue; } first ? g.moveTo(X(r), Y(v)) : g.lineTo(X(r), Y(v)); first = false; }
    g.stroke();
    g.strokeStyle = '#ffd27a'; g.lineWidth = 1.2; g.setLineDash([4, 3]); g.beginPath(); g.moveTo(x0, Y(s.e)); g.lineTo(x1, Y(s.e)); g.stroke(); g.setLineDash([]);
    const r = 1 / s.u; if (r >= rmin && r <= rmax) { g.fillStyle = '#ffd27a'; g.beginPath(); g.arc(X(r), Y(s.e), 4, 0, 6.29); g.fill(); }
    g.fillStyle = '#b3ac9e'; g.fillText('effective potential V(r), and E as the dashed line', x0, y1 - 8);
    g.fillText('r = 2M', x0, y0 + 14); g.textAlign = 'right'; g.fillText('40M (log)', x1, y0 + 14);
  }
  outs(); restart();
  window.addEventListener('resize', restart);
})();
