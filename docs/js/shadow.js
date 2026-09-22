/* shadow.js — the outline of a spinning black hole's shadow, from Bardeen's 1973 formula,
   and how big it looks from Earth for a given mass and distance. */
(function () {
  const root = document.getElementById('shadow');
  if (!root) return;
  const cv = root.querySelector('canvas'), g = cv.getContext('2d');
  const A = root.querySelector('input[name=a]'), TH = root.querySelector('input[name=th]');
  const M = root.querySelector('input[name=mass]'), D = root.querySelector('input[name=dist]');
  const read = root.querySelector('.read');
  const G = 6.6743e-11, c = 299792458, MSUN = 1.98892e30, PC = 3.0857e16;
  function outs() {
    root.querySelector('output[for=a]').textContent = (+A.value).toFixed(3);
    root.querySelector('output[for=th]').textContent = TH.value + '°';
    root.querySelector('output[for=mass]').textContent = fmtM(Math.pow(10, +M.value));
    root.querySelector('output[for=dist]').textContent = fmtD(Math.pow(10, +D.value));
  }
  function fmtM(m) { return m >= 1e9 ? (m / 1e9).toFixed(1) + ' billion M☉' : m >= 1e6 ? (m / 1e6).toFixed(1) + ' million M☉' : m >= 1e3 ? (m / 1e3).toFixed(1) + ' thousand M☉' : m.toFixed(0) + ' M☉'; }
  function fmtD(d) { return d >= 1e6 ? (d / 1e6).toFixed(1) + ' Mpc' : d >= 1e3 ? (d / 1e3).toFixed(1) + ' kpc' : d.toFixed(0) + ' pc'; }
  function curve(a, thdeg) {
    const th = thdeg * Math.PI / 180, out = [];
    if (a < 1e-4) { for (let t = 0; t <= 6.2832; t += .02) out.push([Math.sqrt(27) * Math.cos(t), Math.sqrt(27) * Math.sin(t)]); return out; }
    const top = [];
    for (let r = 1.0001; r <= 4; r += .0015) {
      const Dl = r * r - 2 * r + a * a;
      const xi = ((r * r - a * a) - r * Dl) / (a * (r - 1));
      const eta = r * r * r * (4 * Dl - r * (r - 1) * (r - 1)) / (a * a * (r - 1) * (r - 1));
      const b2 = eta + a * a * Math.cos(th) ** 2 - xi * xi / Math.tan(th) ** 2;
      if (b2 < 0) continue;
      top.push([-xi / Math.sin(th), Math.sqrt(b2)]);
    }
    return top.concat(top.slice().reverse().map(p => [p[0], -p[1]]));
  }
  let W, H;
  function draw() {
    const w = Math.min(root.clientWidth, 960), dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = Math.round(w * dpr); H = Math.round(W * 0.56); cv.width = W; cv.height = H;
    const a = +A.value, th = Math.max(0.5, +TH.value);
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    const cx = W * 0.5, cy = H * 0.5, k = H * 0.075;
    // a glow ring, for the eye: the direct emission near the photon orbit
    const pts = curve(a, th);
    for (let i = 4; i >= 1; i--) {
      g.strokeStyle = `rgba(255,179,71,${0.06 * i})`; g.lineWidth = k * (0.5 - 0.08 * i) * 2.2;
      g.beginPath(); pts.forEach((p, j) => { const x = cx + p[0] * k, y = cy - p[1] * k; j ? g.lineTo(x, y) : g.moveTo(x, y); }); g.closePath(); g.stroke();
    }
    g.strokeStyle = '#2a2a38'; g.lineWidth = 1; g.beginPath(); g.moveTo(cx - 8 * k, cy); g.lineTo(cx + 8 * k, cy); g.moveTo(cx, cy - 5 * k); g.lineTo(cx, cy + 5 * k); g.stroke();
    g.setLineDash([3, 4]); g.strokeStyle = '#b3ac9e'; g.beginPath(); g.arc(cx, cy, Math.sqrt(27) * k, 0, 6.29); g.stroke(); g.setLineDash([]);
    g.fillStyle = '#000'; g.strokeStyle = '#ffb347'; g.lineWidth = 3; g.beginPath();
    pts.forEach((p, j) => { const x = cx + p[0] * k, y = cy - p[1] * k; j ? g.lineTo(x, y) : g.moveTo(x, y); }); g.closePath(); g.fill(); g.stroke();
    g.fillStyle = '#b3ac9e'; g.font = `${11 * W / 960}px system-ui,sans-serif`; g.textAlign = 'left';
    g.fillText('dotted: the a = 0 shadow, radius 3√3 M', 12, H - 12);
    g.fillText('← spin', cx + 5.5 * k, cy - 6);
    // widths
    let xmin = 1e9, xmax = -1e9, ymax = 0; for (const p of pts) { xmin = Math.min(xmin, p[0]); xmax = Math.max(xmax, p[0]); ymax = Math.max(ymax, Math.abs(p[1])); }
    const m = Math.pow(10, +M.value) * MSUN, d = Math.pow(10, +D.value) * PC;
    const rg = G * m / (c * c);
    const uas = x => (x * rg / d) * 206264.806 * 1e6;
    read.innerHTML = `<b>a = ${a.toFixed(3)}</b> seen from ${th.toFixed(0)}° off the spin axis · width ${(xmax - xmin).toFixed(2)} M · height ${(2 * ymax).toFixed(2)} M · shift ${((xmax + xmin) / 2).toFixed(2)} M\n`
      + `${fmtM(m / MSUN)} at ${fmtD(d / PC)}: <b>${uas(xmax - xmin).toFixed(1)} µas</b> across (M87*'s ring measured 42 ± 3; Sgr A*'s 51.8 ± 2.3) · GM/c² = ${(rg / 1e3).toExponential(2)} km`;
  }
  [A, TH, M, D].forEach(el => el.addEventListener('input', () => { outs(); draw(); }));
  root.querySelectorAll('.presets button').forEach(b => b.addEventListener('click', () => { const p = JSON.parse(b.dataset.set); for (const kk in p) root.querySelector(`input[name=${kk}]`).value = p[kk]; outs(); draw(); }));
  outs(); draw(); window.addEventListener('resize', draw);
})();
