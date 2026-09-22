/* quiz.js — what kind of black hole are you.
   Nine questions. Each answer gives points to a few of nine kinds. Highest wins; the
   result is the physics of that kind, with its numbers. */
(function () {
  const root = document.getElementById('quiz');
  if (!root) return;
  const KINDS = {
    schw: { name: 'Schwarzschild', kick: 'still, uncharged, exact', blurb: 'The 1916 solution: mass and nothing else. No spin, no charge, one number. You are the reference everything else is measured against, and the one nobody has found in the wild — everything real turns at least a little.',
      facts: [['1', 'parameter: M'], ['3M', 'photon sphere'], ['6M', 'last stable orbit'], ['0', 'spin']], draw: 'still' },
    kerr: { name: 'Kerr', kick: 'spinning, dragging, fast', blurb: 'The 1963 solution. You turn, and you turn everything near you: inside your ergosphere standing still is not an option. Your horizon is smaller than a still hole of the same mass, your last stable orbit sits closer, and your shadow has a flat side. Most real black holes are you.',
      facts: [['2', 'parameters: M, a'], ['0.998', 'the spin ceiling for a disk-fed hole'], ['1.24M', 'ISCO at maximal spin'], ['29%', 'of your mass is extractable (Penrose)']], draw: 'spin' },
    rn: { name: 'Reissner–Nordström', kick: 'charged, theoretical, unlikely', blurb: 'Mass and electric charge, 1916–18. You are allowed by the equations and found nowhere: a charged hole pulls opposite charge from the gas around it and neutralises in moments. Two horizons, a repulsive core, and a place in every textbook.',
      facts: [['2', 'parameters: M, Q'], ['2', 'horizons'], ['≈0', 'found in nature'], ['1916', 'Reissner; Nordström 1918']], draw: 'charge' },
    stellar: { name: 'Stellar-mass', kick: 'born in a supernova, three to a hundred suns', blurb: 'A star ran out of fuel and its core fell through itself. You are the common kind: the Galaxy holds something like a hundred million of you, most alone and dark. The ones we know feed from a companion, or were heard merging.',
      facts: [['~10⁸', 'in the Milky Way, estimated'], ['21', 'M☉: Cygnus X-1, the first found'], ['33', 'M☉: Gaia BH3'], ['10⁹', 'g of stretch at your horizon']], draw: 'star' },
    imbh: { name: 'Intermediate-mass', kick: 'the missing middle', blurb: 'Between a hundred and a hundred thousand suns: too heavy to come from one star, too light to sit in a galactic centre. For decades the catalogue had none. GW190521 made a 142-solar-mass one in 2019, and the middle is now a place rather than a gap.',
      facts: [['142', 'M☉: GW190521, the first'], ['10²–10⁵', 'M☉: the range'], ['~14,000', 'M☉: the mass where crossing the horizon is a 10 g stretch'], ['?', 'how you form']], draw: 'mid' },
    smbh: { name: 'Supermassive', kick: 'the centre of everything, patient', blurb: 'Millions to billions of suns, one per galaxy, sitting in the middle. Your horizon is the size of a planetary system and gentle to cross. You were photographed first. When you feed you outshine your galaxy, and your jets reach for a million light-years.',
      facts: [['4.3 × 10⁶', 'M☉: Sagittarius A*'], ['6.5 × 10⁹', 'M☉: M87*'], ['0.085', 'au: Sgr A*\'s horizon'], ['10⁸⁷', 'years: Sgr A*\'s lifetime']], draw: 'giant' },
    binary: { name: 'Merging binary', kick: 'two, becoming one, loudly', blurb: 'You had a partner and you are spiralling in. The last seconds are the loudest event in the universe: a few solar masses turned into ripples in space, heard on Earth as a rising chirp. What is left is one hole, kicked, ringing like a bell, then quiet.',
      facts: [['3', 'M☉ radiated by GW150914'], ['~300', 'mergers heard by end of O4'], ['225', 'M☉: GW231123\'s remnant'], ['250', 'Hz: the final ring']], draw: 'pair' },
    pbh: { name: 'Primordial', kick: 'from the first second, and maybe dark matter', blurb: 'You did not come from a star; you came from a dense patch of the newborn universe. You might be the mass of an asteroid with a horizon the width of a proton. Nobody has found one of you. If you exist in the right mass window, you might be what dark matter is.',
      facts: [['10⁻²³', 's: when you formed, roughly'], ['10¹⁷–10²²', 'g: the open dark-matter window'], ['5 × 10¹¹', 'kg: the mass finishing now'], ['0', 'confirmed']], draw: 'tiny' },
    evap: { name: 'Evaporating', kick: 'small, hot, ending', blurb: 'Hawking radiation runs the other way for you: you are hotter than the sky, so you lose mass, so you get hotter. The last seconds are a flash of gamma rays brighter than a galaxy. Somewhere in the universe, if primordial holes exist, this is happening now.',
      facts: [['10¹²', 'K at 10¹¹ kg'], ['10³⁰', 'J: the final burst, roughly'], ['1974', 'Hawking'], ['↑', 'temperature as mass ↓']], draw: 'flash' },
  };
  const Q = [
    ['When do you get things done?', [['Steadily, the same way, forever.', { schw: 3, smbh: 1 }], ['In a spin. Fast, and I take people with me.', { kerr: 3, binary: 1 }], ['I sit in the middle and let things come to me.', { smbh: 3 }], ['In one burst, and then it is over.', { evap: 3, binary: 1 }]]],
    ['Your ideal size?', [['Bigger than a planetary system.', { smbh: 3 }], ['A city, give or take.', { stellar: 3, binary: 1 }], ['Somewhere in between; nobody has a name for it.', { imbh: 3 }], ['Smaller than an atom.', { pbh: 3, evap: 2 }]]],
    ['How did you come to be?', [['Something big fell apart and I was what remained.', { stellar: 3, binary: 1 }], ['I was here before almost everything.', { pbh: 3 }], ['Two of us became one.', { binary: 3, imbh: 1 }], ['I grew, slowly, eating whatever came near.', { smbh: 3, kerr: 1 }]]],
    ['Your relationship status?', [['In a very intense long-distance thing, getting closer.', { binary: 3 }], ['Single. Everything else is just passing through.', { schw: 2, stellar: 1 }], ['I have a whole galaxy orbiting me.', { smbh: 3 }], ['Complicated: I attract the opposite of whatever I am.', { rn: 3 }]]],
    ['Pick a temperature.', [['Colder than empty space.', { smbh: 2, stellar: 1, kerr: 1 }], ['Warmer than the sky, and warming.', { evap: 3, pbh: 1 }], ['I do not have one. I am an idealisation.', { schw: 2, rn: 2 }], ['Hot enough to outshine a galaxy, briefly.', { evap: 2, binary: 1 }]]],
    ['What can be known about you from outside?', [['Exactly one thing: how heavy I am.', { schw: 3 }], ['Two things: how heavy, how fast I turn.', { kerr: 3 }], ['Three, if you count the charge nobody believes in.', { rn: 3 }], ['You will hear me before you see me.', { binary: 3 }]]],
    ['Your shadow?', [['A perfect circle.', { schw: 3 }], ['A circle with one flat side.', { kerr: 3 }], ['Fifty microarcseconds and famous.', { smbh: 3 }], ['Too small for any telescope there will ever be.', { pbh: 2, evap: 2 }]]],
    ['Someone falls in. You…', [['…let them cross without noticing. It is a big horizon.', { smbh: 3 }], ['…stretch them into a string a long way out.', { stellar: 3, imbh: 1 }], ['…spin them around a few thousand times first.', { kerr: 3 }], ['…are too small for anyone to fall into.', { pbh: 2, evap: 1 }]]],
    ['Your ending?', [['I do not end. Not in any time worth counting.', { smbh: 3, schw: 1 }], ['A flash, then nothing.', { evap: 3 }], ['A merger, a ring, and then I am something else.', { binary: 3 }], ['Nobody has proved I began.', { pbh: 3, rn: 1 }]]],
  ];
  const stage = root.querySelector('.stage'), bar = root.querySelector('.bar i');
  let i = 0, score = {};
  for (const k in KINDS) score[k] = 0;
  function ask() {
    bar.style.width = (i / Q.length * 100) + '%';
    if (i >= Q.length) return result();
    const [q, opts] = Q[i];
    stage.innerHTML = `<p class="q"><small>${i + 1} of ${Q.length}</small>${q}</p><div class="opts">${opts.map((o, j) => `<button type="button" data-j="${j}">${o[0]}</button>`).join('')}</div>`;
    stage.querySelectorAll('button').forEach(b => b.addEventListener('click', () => { const pts = opts[+b.dataset.j][1]; for (const k in pts) score[k] += pts[k]; i++; ask(); }));
  }
  function result() {
    bar.style.width = '100%';
    const order = Object.keys(KINDS).sort((a, b) => score[b] - score[a]);
    const k = order[0], K = KINDS[k], runner = KINDS[order[1]];
    stage.innerHTML = `<div class="res"><span class="kick">you are</span><h3>${K.name}</h3><canvas width="520" height="300" aria-hidden="true"></canvas><p class="kick">${K.kick}</p><p>${K.blurb}</p>
      <div class="facts">${K.facts.map(f => `<div><b>${f[0]}</b>${f[1]}</div>`).join('')}</div>
      <p class="also">Runner-up: ${runner.name} — ${runner.kick}.</p>
      <div class="row"><button type="button" data-again>Again</button><button type="button" data-copy>Copy the result</button></div></div>`;
    stage.querySelector('[data-again]').addEventListener('click', () => { i = 0; for (const kk in score) score[kk] = 0; ask(); });
    stage.querySelector('[data-copy]').addEventListener('click', e => {
      const text = `What kind of black hole are you? I am ${K.name} — ${K.kick}. ${location.href}`;
      if (navigator.share) navigator.share({ text }).catch(() => { });
      else if (navigator.clipboard) navigator.clipboard.writeText(text).then(() => { e.currentTarget.textContent = 'Copied'; });
    });
    draw(stage.querySelector('canvas'), K.draw);
  }
  function draw(cv, kind) {
    const g = cv.getContext('2d'), W = cv.width, H = cv.height, cx = W / 2, cy = H / 2;
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    // stars
    let s = 7; const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
    for (let n = 0; n < 160; n++) { g.fillStyle = `rgba(255,255,255,${0.2 + rnd() * 0.8})`; g.fillRect(rnd() * W, rnd() * H, 1.2, 1.2); }
    const glow = (r, col) => { const gr = g.createRadialGradient(cx, cy, r * 0.9, cx, cy, r * 1.9); gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, H); };
    const hole = (x, y, r) => { g.fillStyle = '#000'; g.beginPath(); g.arc(x, y, r, 0, 6.29); g.fill(); g.strokeStyle = '#ffb347'; g.lineWidth = 2; g.stroke(); };
    if (kind === 'still') { glow(60, 'rgba(255,179,71,.35)'); hole(cx, cy, 60); }
    if (kind === 'spin') { glow(56, 'rgba(255,179,71,.35)'); g.strokeStyle = 'rgba(143,208,255,.8)'; g.lineWidth = 2; g.beginPath(); g.ellipse(cx, cy, 120, 40, 0, 0, 6.29); g.stroke(); g.fillStyle = '#000'; g.beginPath(); g.ellipse(cx, cy, 62, 56, 0, 0, 6.29); g.fill(); g.strokeStyle = '#ffb347'; g.beginPath(); g.moveTo(cx - 62, cy); g.bezierCurveTo(cx - 62, cy - 75, cx + 45, cy - 75, cx + 45, cy); g.bezierCurveTo(cx + 45, cy + 75, cx - 62, cy + 75, cx - 62, cy); g.stroke(); }
    if (kind === 'charge') { glow(50, 'rgba(200,166,255,.35)'); hole(cx, cy, 50); g.strokeStyle = '#c8a6ff'; g.setLineDash([4, 4]); g.beginPath(); g.arc(cx, cy, 30, 0, 6.29); g.stroke(); g.setLineDash([]); g.fillStyle = '#c8a6ff'; g.font = 'bold 28px system-ui'; g.textAlign = 'center'; g.fillText('+', cx, cy + 10); }
    if (kind === 'star') { glow(30, 'rgba(255,179,71,.4)'); g.strokeStyle = '#ffb347'; g.lineWidth = 3; g.beginPath(); g.ellipse(cx, cy, 110, 22, -0.2, 0, 6.29); g.stroke(); hole(cx, cy, 30); }
    if (kind === 'mid') { glow(44, 'rgba(255,210,122,.3)'); hole(cx, cy, 44); g.fillStyle = '#b3ac9e'; g.font = '13px system-ui'; g.textAlign = 'center'; g.fillText('?', cx, cy + 5); }
    if (kind === 'giant') { glow(95, 'rgba(255,179,71,.3)'); hole(cx, cy, 95); g.strokeStyle = 'rgba(143,208,255,.7)'; g.lineWidth = 1; for (let r = 110; r < 160; r += 12) { g.beginPath(); g.ellipse(cx, cy, r, r * 0.3, 0.3, 0, 6.29); g.stroke(); } }
    if (kind === 'pair') { glow(30, 'rgba(255,179,71,.3)'); hole(cx - 45, cy, 28); hole(cx + 45, cy, 22); g.strokeStyle = 'rgba(143,208,255,.6)'; g.lineWidth = 1.2; for (let r = 90; r < 250; r += 18) { g.beginPath(); g.arc(cx, cy, r, 0, 6.29); g.stroke(); } }
    if (kind === 'tiny') { g.fillStyle = '#f3efe6'; g.beginPath(); g.arc(cx, cy, 2, 0, 6.29); g.fill(); g.strokeStyle = '#b3ac9e'; g.lineWidth = 1; g.beginPath(); g.arc(cx, cy, 40, 0, 6.29); g.stroke(); g.fillStyle = '#b3ac9e'; g.font = '12px system-ui'; g.textAlign = 'center'; g.fillText('(to scale: you are the dot)', cx, cy + 62); }
    if (kind === 'flash') { const gr = g.createRadialGradient(cx, cy, 0, cx, cy, 130); gr.addColorStop(0, '#fff'); gr.addColorStop(0.15, '#ffd27a'); gr.addColorStop(0.5, 'rgba(255,106,94,.4)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, H); }
  }
  ask();
})();
