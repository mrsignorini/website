/* ============================================================
   signorini.cloud — interactions
   ============================================================ */
(function () {
  'use strict';

  /* ---------- Theme ---------- */
  var root = document.documentElement;
  var STORE_THEME = 'sig-theme';
  var STORE_ACCENT = 'sig-accent';
  var STORE_FONT = 'sig-font';

  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    try { localStorage.setItem(STORE_THEME, t); } catch (e) {}
    syncSeg('themeSeg', 'data-theme-val', t);
  }
  var savedTheme = null;
  try { savedTheme = localStorage.getItem(STORE_THEME); } catch (e) {}
  if (savedTheme) applyTheme(savedTheme);

  var toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      applyTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });
  }

  /* ---------- Accent ---------- */
  var ACCENTS = [
    { name: 'Electric blue', hex: '#5c80ff', rgb: '92, 128, 255' },
    { name: 'Amber', hex: '#f5a623', rgb: '245, 166, 35' },
    { name: 'Teal', hex: '#2dd4bf', rgb: '45, 212, 191' },
    { name: 'Violet', hex: '#a78bfa', rgb: '167, 139, 250' }
  ];
  function applyAccent(a) {
    root.style.setProperty('--accent', a.hex);
    root.style.setProperty('--accent-rgb', a.rgb);
    try { localStorage.setItem(STORE_ACCENT, a.hex); } catch (e) {}
    var sw = document.querySelectorAll('#swatches .swatch');
    sw.forEach(function (el) { el.classList.toggle('sel', el.dataset.hex === a.hex); });
  }
  var savedAccent = null;
  try { savedAccent = localStorage.getItem(STORE_ACCENT); } catch (e) {}

  /* ---------- Font ---------- */
  function applyFont(f) {
    root.style.setProperty('--font-display', f);
    try { localStorage.setItem(STORE_FONT, f); } catch (e) {}
    syncSeg('fontSeg', 'data-font', f);
  }
  var savedFont = null;
  try { savedFont = localStorage.getItem(STORE_FONT); } catch (e) {}
  if (savedFont) applyFont(savedFont);

  function syncSeg(id, attr, val) {
    var seg = document.getElementById(id);
    if (!seg) return;
    seg.querySelectorAll('button').forEach(function (b) {
      b.classList.toggle('sel', b.getAttribute(attr) === val);
    });
  }

  /* ---------- Build tweaks UI ---------- */
  var swWrap = document.getElementById('swatches');
  if (swWrap) {
    ACCENTS.forEach(function (a) {
      var b = document.createElement('button');
      b.className = 'swatch';
      b.style.background = a.hex;
      b.dataset.hex = a.hex;
      b.title = a.name;
      b.setAttribute('aria-label', a.name);
      b.addEventListener('click', function () { applyAccent(a); });
      swWrap.appendChild(b);
    });
  }
  applyAccent(ACCENTS.filter(function (a) { return a.hex === savedAccent; })[0] || ACCENTS[0]);

  var themeSeg = document.getElementById('themeSeg');
  if (themeSeg) themeSeg.querySelectorAll('button').forEach(function (b) {
    b.addEventListener('click', function () { applyTheme(b.getAttribute('data-theme-val')); });
  });
  syncSeg('themeSeg', 'data-theme-val', root.getAttribute('data-theme'));

  var fontSeg = document.getElementById('fontSeg');
  if (fontSeg) fontSeg.querySelectorAll('button').forEach(function (b) {
    b.addEventListener('click', function () { applyFont(b.getAttribute('data-font')); });
  });
  syncSeg('fontSeg', 'data-font', getComputedStyle(root).getPropertyValue('--font-display').trim());

  /* ---------- Nav scrolled state ---------- */
  var nav = document.getElementById('nav');
  function onScroll() {
    if (nav) {
      if (window.scrollY > 24) nav.classList.add('scrolled');
      else nav.classList.remove('scrolled');
    }
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Scroll reveal ---------- */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Active nav link ---------- */
  var sections = ['about', 'stack', 'experience', 'project', 'contact'];
  var linkMap = {};
  document.querySelectorAll('#navLinks a').forEach(function (a) {
    var href = a.getAttribute('href');
    var id = href.includes('#') ? href.split('#')[1] : '';
    if (id) linkMap[id] = a;
  });
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          var id = e.target.id;
          Object.keys(linkMap).forEach(function (k) { linkMap[k].classList.remove('active'); });
          if (linkMap[id]) linkMap[id].classList.add('active');
        }
      });
    }, { threshold: 0.5, rootMargin: '-30% 0px -50% 0px' });
    sections.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) spy.observe(el);
    });
  }

  /* ---------- Mobile nav ---------- */
  var burger = document.getElementById('navBurger');
  var mobileNav = document.getElementById('navLinks');
  function closeMobileNav() {
    if (!mobileNav || !burger) return;
    mobileNav.classList.remove('open');
    burger.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
  }
  if (burger && mobileNav) {
    burger.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('open');
      burger.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
    });
    mobileNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMobileNav);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMobileNav();
    });
  }

  /* ---------- Tweaks host protocol ---------- */
  var panel = document.getElementById('tweaks');
  function setTweaks(on) { if (panel) panel.classList.toggle('on', !!on); }
  window.addEventListener('message', function (ev) {
    var d = ev.data || {};
    if (d.type === 'tweaks:show' || d.type === 'tweaks-show') setTweaks(true);
    else if (d.type === 'tweaks:hide' || d.type === 'tweaks-hide') setTweaks(false);
    else if (d.type === 'tweaks:toggle') setTweaks(!panel.classList.contains('on'));
    else if (typeof d.tweaksEnabled === 'boolean') setTweaks(d.tweaksEnabled);
  });
})();
