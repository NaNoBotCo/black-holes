/* clock.js — two clocks, one of them near a black hole.
   For someone hovering at radius r, dτ/dt = √(1 − 2M/r). The far clock keeps coordinate
   time. Inside r = 3M the hovering takes more than a rocket can give; at 2M, infinity. */
(function () {
  const root = document.getElementById('clock');
  if (!root) return;
  const R = root.querySelector('input[name=r]'), out = root.querySelector('output[for=r]');
  const hands = { far: root.querySelector('.far .hand'), near: root.querySelector('.near .hand') };
  const read = root.querySelector('.read');
  let t0 = performance.now(), farT = 0, nearT = 0, last = t0;
  function factor() { const r = +R.value; return Math.sqrt(Math.max(1 - 2 / r, 0)); }
  function show() { const r = +R.value; out.textContent = r.toFixed(2) + ' M'; }
  R.addEventListener('input', show); show();
  function tick(now) {
    const dt = (now - last) / 1000; last = now;
    const f = factor(); farT += dt; nearT += dt * f;
    hands.far.style.transform = `rotate(${(farT * 6) % 360}deg)`;
    hands.near.style.transform = `rotate(${(nearT * 6) % 360}deg)`;
    const r = +R.value;
    const g = 1 / f;
    read.innerHTML = `r = ${r.toFixed(2)} M · dτ/dt = √(1 − 2M/r) = <b>${f.toFixed(4)}</b>\n`
      + `far clock ${farT.toFixed(1)} s · near clock ${nearT.toFixed(1)} s · one year hovering here is ${isFinite(g) ? (g).toFixed(3) : '∞'} years outside`
      + (r < 3 ? ' · <b>below 3M</b>: hovering needs more than light-speed sideways motion to help; nothing hovers here for long' : '')
      + (r > 2 && r < 2.02 ? ' · a hair above the horizon: the far universe runs its whole future while your second hand moves' : '')
      + `\nsurface gravity felt while hovering: ${r > 2 ? (1 / (r * r * f)).toFixed(3) : '∞'} in units of c⁴/GM — it diverges at the horizon, which is why nothing hovers there`;
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
