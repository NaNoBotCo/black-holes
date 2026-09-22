/* waves.js — a chirp you can hear.
   Two masses spiral in: the frequency track from the leading-order formula, a cut near
   merger, and a ringdown at the final Kerr hole's fundamental tone. Played through Web
   Audio at its own frequencies, which for stellar masses sit inside human hearing. */
(function () {
  const root = document.getElementById('waves');
  if (!root) return;
  const cv = root.querySelector('canvas'), g = cv.getContext('2d');
  const M1 = root.querySelector('input[name=m1]'), M2 = root.querySelector('input[name=m2]');
  const read = root.querySelector('.read');
  const G = 6.6743e-11, c = 299792458, MSUN = 1.98892e30;
  let ac = null, model = null;
  function outs() { root.querySelector('output[for=m1]').textContent = M1.value + ' M☉'; root.querySelector('output[for=m2]').textContent = M2.value + ' M☉'; }
  function build() {
    const m1 = +M1.value, m2 = +M2.value, M = (m1 + m2) * MSUN, f0 = 20;
    const mc = Math.pow(m1 * m2, 0.6) / Math.pow(m1 + m2, 0.2) * MSUN;
    const k = (5 / 256) * Math.pow(c, 5) / Math.pow(G * mc, 5 / 3) * Math.pow(Math.PI, -8 / 3);
    const tc = k * Math.pow(f0, -8 / 3);
    const fcut = 2.2 * Math.pow(c, 3) / (Math.pow(6, 1.5) * Math.PI * G * M);
    const n = 8000, t = [], f = [], h = [];
    let ph = 0, dt = tc / n, cut = n;
    for (let i = 0; i < n; i++) {
      const tt = i * dt, ff = Math.min(Math.pow(k / (tc - tt), 3 / 8), fcut);
      if (ff >= fcut) { cut = i; break; }
      ph += 2 * Math.PI * ff * dt; t.push(tt); f.push(ff); h.push(Math.pow(ff / f0, 2 / 3) * Math.cos(ph));
    }
    const eta = m1 * m2 / ((m1 + m2) ** 2);
    const Mf = M * (1 - 0.057 * (eta / 0.25)), af = 0.69 * Math.sqrt(eta / 0.25);
    const fr = (1.5251 - 1.1568 * Math.pow(1 - af, 0.1292)) / (2 * Math.PI) * Math.pow(c, 3) / (G * Mf);
    const Q = 0.7 + 1.4187 * Math.pow(1 - af, -0.499), tau = Q / (Math.PI * fr);
    const A = h.length ? Math.abs(h[h.length - 1]) : 1, tEnd = t[t.length - 1];
    for (let i = 0; i < 600; i++) { const tr = i * tau * 6 / 600; t.push(tEnd + tr); f.push(fr); h.push(A * Math.exp(-tr / tau) * Math.cos(2 * Math.PI * fr * tr + ph)); }
    const erad = (M - Mf) / MSUN;
    model = { t, f, h, tc, fcut, fr, tau, mc: mc / MSUN, Mf: Mf / MSUN, af, erad, m1, m2 };
  }
  let W, H;
  function draw() {
    const w = Math.min(root.clientWidth, 960), dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = Math.round(w * dpr); H = Math.round(W * 0.42); cv.width = W; cv.height = H;
    const m = model; g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    const t0 = Math.max(0, m.t[m.t.length - 1] - Math.min(1.0, m.tc)), t1 = m.t[m.t.length - 1];
    const X = tt => 20 + (tt - t0) / (t1 - t0) * (W - 40);
    let hmax = 0; for (let i = 0; i < m.t.length; i++) if (m.t[i] >= t0) hmax = Math.max(hmax, Math.abs(m.h[i]));
    g.strokeStyle = '#ffb347'; g.lineWidth = 1.4; g.beginPath(); let first = true;
    for (let i = 0; i < m.t.length; i++) { if (m.t[i] < t0) continue; const x = X(m.t[i]), y = H * 0.42 - m.h[i] / hmax * H * 0.3; first ? g.moveTo(x, y) : g.lineTo(x, y); first = false; }
    g.stroke();
    g.strokeStyle = '#8fd0ff'; g.beginPath(); first = true;
    const fmax = Math.max(...m.f);
    for (let i = 0; i < m.t.length; i++) { if (m.t[i] < t0) continue; const x = X(m.t[i]), y = H * 0.97 - (m.f[i] / fmax) * H * 0.18; first ? g.moveTo(x, y) : g.lineTo(x, y); first = false; }
    g.stroke();
    g.fillStyle = '#b3ac9e'; g.font = `${11 * W / 960}px system-ui,sans-serif`;
    g.fillText(`strain, last ${(t1 - t0).toFixed(2)} s`, 20, 18);
    g.fillText(`frequency, 20 Hz → ${fmax.toFixed(0)} Hz`, 20, H * 0.97 - H * 0.2);
  }
  function play() {
    const m = model;
    if (!ac) ac = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ac.createOscillator(), gain = ac.createGain();
    osc.type = 'sine'; const now = ac.currentTime + 0.05;
    const span = Math.min(m.tc, 4.0), t0 = m.tc - span;
    // frequency and amplitude curves, sampled
    const N = 400, fs = [], gs = [];
    for (let i = 0; i <= N; i++) {
      const tt = t0 + span * i / N, ff = Math.min(Math.pow((5 / 256) * Math.pow(c, 5) / Math.pow(G * m.mc * MSUN, 5 / 3) * Math.pow(Math.PI, -8 / 3) / Math.max(m.tc - tt, 1e-4), 3 / 8), m.fcut);
      fs.push(ff); gs.push(0.08 * Math.pow(ff / 20, 2 / 3) / Math.pow(m.fcut / 20, 2 / 3) + 0.02);
    }
    osc.frequency.setValueCurveAtTime(new Float32Array(fs), now, span);
    gain.gain.setValueCurveAtTime(new Float32Array(gs), now, span);
    // ringdown
    osc.frequency.setValueAtTime(m.fr, now + span + 0.001);
    gain.gain.setValueAtTime(0.12, now + span + 0.001);
    gain.gain.exponentialRampToValueAtTime(0.0005, now + span + Math.max(6 * m.tau, 0.08));
    osc.connect(gain); gain.connect(ac.destination);
    osc.start(now); osc.stop(now + span + Math.max(6 * m.tau, 0.08) + 0.05);
  }
  function update() {
    outs(); build(); draw();
    const m = model;
    read.innerHTML = `<b>chirp mass ${m.mc.toFixed(1)} M☉</b> · ${(m.tc).toFixed(2)} s from 20 Hz to merger · merger near ${m.fcut.toFixed(0)} Hz · final hole ${m.Mf.toFixed(1)} M☉, spin ${m.af.toFixed(2)}, ringing at ${m.fr.toFixed(0)} Hz for ${(m.tau * 1000).toFixed(1)} ms\n`
      + `about ${m.erad.toFixed(1)} M☉ of mass left as waves — for a moment, brighter than every star in the visible universe put together`;
  }
  [M1, M2].forEach(el => el.addEventListener('input', update));
  root.querySelector('[data-play]').addEventListener('click', play);
  root.querySelectorAll('.presets button').forEach(b => b.addEventListener('click', () => { const p = JSON.parse(b.dataset.set); M1.value = p.m1; M2.value = p.m2; update(); }));
  update(); window.addEventListener('resize', draw);
})();
