/* nav.js — the bar gets out of the way on a phone: scroll down and it slides away,
   scroll up any amount and it comes back. */
(function () {
  let last = window.scrollY, ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      if (y > last + 6 && y > 80) document.body.classList.add('nav-away');
      else if (y < last - 2) document.body.classList.remove('nav-away');
      last = y; ticking = false;
    });
  }, { passive: true });
})();
