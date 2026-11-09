/* LUIS MORENO FILM — sitio estático (sin dependencias) */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Header con fondo al hacer scroll */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 24);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* Menú móvil */
  var menuBtn = document.querySelector('.menu-btn');
  var menu = document.getElementById('mobileMenu');
  if (menuBtn && menu) {
    var setOpen = function (open) {
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menu.classList.toggle('is-open', open);
      document.body.classList.toggle('menu-locked', open);
      if (open) {
        var first = menu.querySelector('a');
        if (first) first.focus();
      } else {
        menuBtn.focus();
      }
    };
    menuBtn.addEventListener('click', function () {
      setOpen(menuBtn.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) setOpen(false);
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        menu.classList.remove('is-open');
        document.body.classList.remove('menu-locked');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* Reveal on scroll */
  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length) {
    if (reduced || !('IntersectionObserver' in window)) {
      revealEls.forEach(function (el) { el.classList.add('in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      revealEls.forEach(function (el) { io.observe(el); });
    }
  }

  /* Filtros de proyectos (?f=slug) */
  var filters = document.querySelector('.filters');
  if (filters) {
    var cards = document.querySelectorAll('[data-cat]');
    var emptyMsg = document.querySelector('[data-empty]');
    var apply = function (cat) {
      var visible = 0;
      cards.forEach(function (c) {
        var show = cat === 'all' || c.getAttribute('data-cat') === cat;
        c.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      filters.querySelectorAll('.chip').forEach(function (ch) {
        ch.classList.toggle('is-active', ch.getAttribute('data-filter') === cat);
      });
      if (emptyMsg) emptyMsg.style.display = visible ? 'none' : 'block';
    };
    filters.addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (chip) apply(chip.getAttribute('data-filter'));
    });
    var f = new URLSearchParams(window.location.search).get('f');
    if (f) apply(f);
  }

  /* Facade de vídeo: carga el iframe solo al pulsar */
  document.querySelectorAll('[data-video-src]').forEach(function (wrap) {
    var btn = wrap.querySelector('button.launch');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var src = wrap.getAttribute('data-video-src');
      if (!src) return;
      var iframe = document.createElement('iframe');
      iframe.src = src;
      iframe.allow = 'autoplay; fullscreen; picture-in-picture; web-share';
      iframe.allowFullscreen = true;
      iframe.setAttribute('title', wrap.getAttribute('data-video-title') || 'Video');
      var old = wrap.querySelector('img');
      if (old) old.remove();
      btn.remove();
      wrap.appendChild(iframe);
    });
  });

  /* Formulario mailto (sitio estático: abre el cliente de correo) */
  var form = document.getElementById('mailtoForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var get = function (id) {
        var el = document.getElementById(id);
        return el ? el.value.trim() : '';
      };
      var nombre = get('f-name'), email = get('f-email'), tipo = get('f-type'), msg = get('f-msg');
      var subject = 'Consulta web: ' + (tipo || 'Proyecto') + (nombre ? ' — ' + nombre : '');
      var body = (msg || '') + '\n\n—\n' + nombre + (email ? ' · ' + email : '') + '\n' + (tipo ? 'Tipo: ' + tipo : '');
      var to = form.getAttribute('data-to') || '';
      window.location.href = 'mailto:' + to +
        '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(body);
    });
  }

  /* Año en footer */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
