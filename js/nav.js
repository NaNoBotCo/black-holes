/* nav.js — the top bar folds to the brand past the fold, leaves on scroll-down and
   returns on 90 px of deliberate scroll-up (motdang's rule, 2026-09-28). Up and down
   accumulate separately. The fold keeps the page's height: the rows it drops become
   margin under the bar, so nothing below moves. Scroll anchoring is off for the
   instant of the fold: the height is read between the two steps, and Chrome anchored
   on that half-folded layout and threw the page back to the top. */
(function () {
  const h = document.querySelector("header.top");
  if (!h) return;
  const b = document.body;
  let y = window.pageYOffset, up = 0, dn = 0, ticking = false;
  function tight(on) {
    if (on === b.classList.contains("nav-tight")) return;
    const r = document.documentElement.style;
    r.overflowAnchor = "none";
    h.style.marginBottom = "";
    const a = h.offsetHeight;
    b.classList.toggle("nav-tight", on);
    if (on) h.style.marginBottom = Math.max(0, a - h.offsetHeight) + "px";
    void h.offsetHeight;
    r.overflowAnchor = "";
  }
  function frame() {
    ticking = false;
    const n = window.pageYOffset, d = n - y;
    y = n;
    if (n < 60) { up = dn = 0; b.classList.remove("nav-away"); tight(false); return; }
    tight(true);
    if (d > 0) { dn += d; up = 0; if (dn > 14) b.classList.add("nav-away"); }
    else if (d < 0) { up -= d; dn = 0; if (up > 90) b.classList.remove("nav-away"); }
  }
  addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
  addEventListener("resize", () => {
    if (b.classList.contains("nav-tight")) { b.classList.remove("nav-tight"); tight(true); }
  }, { passive: true });
  addEventListener("focusin", (e) => {
    if (h.contains(e.target)) { b.classList.remove("nav-away"); tight(false); }
  });
  frame();
})();
