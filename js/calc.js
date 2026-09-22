/* calc.js — put in a mass, get the black hole. Every line is one formula, printed. */
(function () {
  const root = document.getElementById('calc');
  if (!root) return;
  const G = 6.6743e-11, c = 299792458, hbar = 1.054571817e-34, kB = 1.380649e-23, MSUN = 1.98892e30, MEARTH = 5.972e24, AU = 1.495978707e11, YR = 3.15576e7, LY = 9.4607e15, PC = 3.0857e16;
  const sl = root.querySelector('input[name=logm]'), num = root.querySelector('input[name=m]'), unit = root.querySelector('select[name=unit]');
  const table = root.querySelector('tbody'), bar = root.querySelector('.scale'), say = root.querySelector('.say');
  const UNITS = { kg: 1, earth: MEARTH, sun: MSUN };
  const SIZES = [
    [1.6e-35, 'the Planck length'], [1e-15, 'a proton'], [1e-10, 'an atom'], [1e-6, 'a bacterium'], [1e-4, 'a grain of sand'], [1e-2, 'a marble'], [0.1, 'a fist'],
    [1.7, 'a person'], [10, 'a house'], [100, 'a football pitch'], [1e3, 'a village'], [1e4, 'a city'], [1e5, 'a mountain range'], [6.4e6, 'the Earth (radius)'],
    [7e7, 'Jupiter (radius)'], [7e8, 'the Sun (radius)'], [5.8e10, "Mercury's orbit"], [1.5e11, "the Earth's orbit"], [7.8e11, "Jupiter's orbit"], [4.5e12, "Neptune's orbit"],
    [2.5e13, 'Voyager 1'], [LY, 'a light-year'], [4.2 * LY, 'the way to the nearest star'],
  ];
  const fmt = (x, d = 3) => { if (!isFinite(x)) return '∞'; const a = Math.abs(x); if (a >= 1e5 || a < 1e-3) { const e = Math.floor(Math.log10(a)); return `${(x / 10 ** e).toFixed(2)} × 10<sup>${e}</sup>`; } return x.toPrecision(d).replace(/\.?0+$/, ''); };
  function len(m) { if (m < 1e-9) return `${fmt(m)} m`; if (m < 1e-3) return `${fmt(m * 1e6)} µm`; if (m < 1) return `${fmt(m * 100)} cm`; if (m < 1e3) return `${fmt(m)} m`; if (m < 0.05 * AU) return `${fmt(m / 1e3)} km`; if (m < 0.05 * LY) return `${fmt(m / AU)} au`; return `${fmt(m / LY)} light-years`; }
  function time(s) { if (s < 1e-9) return `${fmt(s)} s`; if (s < 60) return `${fmt(s)} s`; if (s < YR) return `${fmt(s / 86400)} days`; return `${fmt(s / YR)} years`; }
  function nearest(r) { let best = SIZES[0]; for (const s of SIZES) if (Math.abs(Math.log10(s[0] / r)) < Math.abs(Math.log10(best[0] / r))) best = s; const ratio = r / best[0]; return ratio > 3 ? `${fmt(ratio, 2)} times ${best[1]}` : ratio < 1 / 3 ? `a ${fmt(1 / ratio, 2)}th of ${best[1]}` : `about ${best[1]}`; }
  function calc(M) {
    const rs = 2 * G * M / (c * c), rph = 1.5 * rs, risco = 3 * rs;
    const T = hbar * c ** 3 / (8 * Math.PI * G * M * kB);
    const tev = 5120 * Math.PI * G ** 2 * M ** 3 / (hbar * c ** 4);
    const A = 4 * Math.PI * rs * rs, lp2 = hbar * G / c ** 3, S = kB * A / (4 * lp2);
    const rho = M / (4 / 3 * Math.PI * rs ** 3);
    const kappa = c ** 4 / (4 * G * M);
    const tide = 2 * G * M * 1.8 / rs ** 3;
    const Tisco = 2 * Math.PI * Math.sqrt(risco ** 3 / (G * M));
    const rtide10g = Math.cbrt(2 * G * M * 1.8 / 98.1);
    const rows = [
      ['Horizon radius', `r<sub>s</sub> = 2GM/c²`, len(rs) + ` — <span class="mute">${nearest(rs)}</span>`],
      ['Shadow diameter', `2·3√3·GM/c² ≈ 2.6 r<sub>s</sub>`, len(2 * Math.sqrt(27) * G * M / c ** 2)],
      ['Photon sphere', `1.5 r<sub>s</sub>`, len(rph)],
      ['Last stable orbit', `3 r<sub>s</sub>`, len(risco) + ` — one lap takes ${time(Tisco)}`],
      ['Hawking temperature', `ħc³ / 8πGMk<sub>B</sub>`, `${fmt(T)} K` + (T > 2.725 ? ' — hotter than the sky, so it shrinks' : ' — colder than the sky, so it grows')],
      ['Time to evaporate', `5120πG²M³ / ħc⁴`, time(tev) + (tev > 4.35e17 ? ` — ${fmt(tev / 4.35e17, 2)} times the age of the universe` : '')],
      ['Entropy', `k<sub>B</sub> A / 4ℓ<sub>P</sub>²`, `${fmt(S / kB)} k<sub>B</sub> — ${fmt(S / kB / Math.log(2))} bits`],
      ['Mean density inside r<sub>s</sub>', `M / (4/3 π r<sub>s</sub>³)`, `${fmt(rho)} kg/m³` + (rho < 1000 ? ' — less than water' : rho < 2e17 ? '' : ' — denser than a nucleus')],
      ['Surface gravity', `c⁴ / 4GM`, `${fmt(kappa)} m/s²`],
      ['Stretch across a body at the horizon', `2GMh/r<sub>s</sub>³, h = 1.8 m`, `${fmt(tide)} m/s² = ${fmt(tide / 9.81)} g`],
      ['Where the stretch reaches 10 g', `(2GMh / 98 m/s²)<sup>1/3</sup>`, rtide10g > rs ? `${len(rtide10g)} out — ${fmt(rtide10g / rs, 2)} horizon radii` : `inside the horizon — the crossing is gentle`],
    ];
    table.innerHTML = rows.map(r => `<tr><td>${r[0]}</td><td class="mute">${r[1]}</td><td>${r[2]}</td></tr>`).join('');
    // the bar: log scale of sizes with the horizon marked
    const lo = -35, hi = 17, pct = x => (Math.log10(x) - lo) / (hi - lo) * 100;
    bar.innerHTML = SIZES.filter((s, i) => i % 2 === 0).map(s => `<i style="left:${pct(s[0])}%"><span>${s[1]}</span></i>`).join('') + `<b style="left:${pct(rs)}%"><span>horizon</span></b>`;
    say.innerHTML = `A black hole of ${fmt(M)} kg (${fmt(M / MSUN, 2)} M☉) has a horizon ${len(2 * rs)} across.`;
  }
  function fromSlider() { const M = 10 ** +sl.value; num.value = (M / UNITS[unit.value]).toPrecision(3); calc(M); }
  function fromNum() { const M = +num.value * UNITS[unit.value]; if (M > 0) { sl.value = Math.log10(M); calc(M); } }
  sl.addEventListener('input', fromSlider); num.addEventListener('input', fromNum); unit.addEventListener('change', fromNum);
  root.querySelectorAll('.presets button').forEach(b => b.addEventListener('click', () => { sl.value = Math.log10(+b.dataset.kg); fromSlider(); }));
  fromSlider();
})();
