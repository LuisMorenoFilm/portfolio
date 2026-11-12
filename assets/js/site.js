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

  /* Hero: video de fondo solo en escritorio, sin reduccion de movimiento ni ahorrador de datos.
     Se inicia tras el evento load para no competir con la imagen LCP del poster */
  var heroV = document.getElementById('heroVideo');
  if (heroV) {
    var startHero = function () {
      var conn = navigator.connection || {};
      var allow = window.matchMedia('(min-width: 900px)').matches
        && !window.matchMedia('(prefers-reduced-motion: reduce)').matches
        && !conn.saveData;
      if (!allow) return;
      heroV.load();
      var p = heroV.play();
      if (p) p.then(function () { heroV.classList.add('is-on'); }).catch(function () {});
      else heroV.classList.add('is-on');
    };
    if (document.readyState === 'complete') startHero();
    else window.addEventListener('load', startHero, { once: true });
  }

  /* Formulario de contacto: envio real via Web3Forms; sin clave, fallback mailto */
  var form = document.getElementById('mailtoForm');
  if (form) {
    var status = form.querySelector('.form-status');
    function mailtoFallback() {
      var get = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
      var nombre = get('f-name'), email = get('f-email'), tel = get('f-phone'), tipo = get('f-type'), msg = get('f-msg');
      var subject = 'Consulta web: ' + (tipo || 'Proyecto') + (nombre ? ' — ' + nombre : '');
      var body = (msg || '') + '\n\n—\n' + nombre + (email ? ' · ' + email : '') + (tel ? '\nTeléfono: ' + tel : '') + '\n' + (tipo ? 'Tipo: ' + tipo : '');
      window.location.href = 'mailto:' + (form.getAttribute('data-to') || '') +
        '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var key = (form.getAttribute('data-key') || '').trim();
      var btn = form.querySelector('button[type=submit]');
      var nombre = form.elements['name'].value.trim();
      var email = form.elements['email'].value.trim();
      var tipo = form.elements['type'].value;
      var msg = form.elements['message'].value.trim();
      if (!key) { mailtoFallback(); return; }
      status.className = 'form-status';
      status.textContent = status.dataset.lang === 'es' ? 'Enviando…' : 'Sending…';
      btn.disabled = true;
      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          access_key: key,
          subject: 'Web — ' + (tipo || 'Project') + (nombre ? ' — ' + nombre : ''),
          from_name: 'Web Luis Moreno Film',
          replyto: email,
          name: nombre, email: email, phone: form.elements['phone'].value.trim(), type: tipo, message: msg, botcheck: ''
        })
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && res.j.success) {
            status.textContent = status.dataset.ok;
            status.className = 'form-status is-ok';
            form.reset();
          } else {
            status.textContent = status.dataset.err;
            status.className = 'form-status is-err';
            btn.disabled = false;
          }
        }).catch(function () {
          status.textContent = status.dataset.err;
          status.className = 'form-status is-err';
          btn.disabled = false;
        });
    });
  }

  /* Año en footer */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* Slider (Sobre mí): autoplay discreto, pausa al pasar/focar, respeta reduced-motion */
  document.querySelectorAll('.slider').forEach(function (root) {
    var slides = root.querySelectorAll('.slide');
    var dots = root.querySelectorAll('.dot');
    if (slides.length < 2) return;
    var i = 0, timer = null;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function show(n) {
      slides[i].classList.remove('is-on');
      if (dots[i]) dots[i].classList.remove('is-on');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('is-on');
      if (dots[i]) dots[i].classList.add('is-on');
    }
    function play() { if (!timer && !reduce) timer = setInterval(function () { show(i + 1); }, +root.dataset.interval || 5000); }
    function stop() { clearInterval(timer); timer = null; }
    dots.forEach(function (d) {
      d.addEventListener('click', function () { stop(); show(+d.dataset.slide); play(); });
    });
    root.addEventListener('mouseenter', stop);
    root.addEventListener('mouseleave', play);
    root.addEventListener('focusin', stop);
    root.addEventListener('focusout', play);
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : play(); });
    play();
  });
})();
