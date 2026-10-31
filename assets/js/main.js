/* ==========================================================================
   MICROBIS — JS comun (navigație, lightbox galerie/video, formulare, reveal)
   Fișier vanilla JS, fără dependențe externe. Inclus pe toate paginile.
   ========================================================================== */
(function () {
  'use strict';

  /* -- limbă: paginile din /en/ au <html lang="en"> ------------------- */
  var EN = /^en/i.test(document.documentElement.lang || '');
  function T(ro, en) { return EN ? en : ro; }

  /* -- meniu mobil ---------------------------------------------------- */
  var toggle = document.querySelector('.nav__toggle');
  var links = document.querySelector('.nav__links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.documentElement.style.overflow = open ? 'hidden' : '';
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('open');
        document.documentElement.style.overflow = '';
      });
    });
  }

  /* -- an curent în footer --------------------------------------------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* -- înlocuire automată: placeholder foto → fotografie reală ---------
     Ca să puneți o fotografie reală într-o casetă .ph-photo, NU trebuie
     să ștergeți sau să înțelegeți markup-ul din interiorul ei (span-uri,
     etichete etc.) — adăugați doar atributul data-img pe div-ul cu clasa
     ph-photo, cu calea către fișier, și opțional data-img-alt cu o
     descriere scurtă. La încărcarea paginii, placeholder-ul e înlocuit
     automat cu fotografia, păstrând exact aceeași formă/proporție.

     Înainte:
       <div class="ph-photo" style="--ar:4/5" data-reveal>
         <div class="ph-photo__mark">...</div>
       </div>

     După (un singur atribut adăugat, nimic șters):
       <div class="ph-photo" style="--ar:4/5" data-reveal
            data-img="assets/img/trupa/echipa.jpg"
            data-img-alt="Trupa Microbis, fotografie de grup">
         <div class="ph-photo__mark">...</div>
       </div>

     Detaliu tehnic pentru README: vezi §2.2. */
  document.querySelectorAll('.ph-photo[data-img]').forEach(function (el) {
    var img = document.createElement('img');
    img.src = el.getAttribute('data-img');
    img.alt = el.getAttribute('data-img-alt') || '';
    img.loading = 'lazy';
    el.classList.add('ph-photo--filled');
    el.innerHTML = '';
    el.appendChild(img);
  });

  /* -- galerie foto spectacol: carusel infinit, centrat -----------------
     Markup așteptat pe pagina unui spectacol:
       <div class="prod-gallery-wrap" data-gallery
            data-gallery-folder="img/" data-gallery-files="">
         <button class="prod-gallery-arrow prev" aria-label="Anterior">‹</button>
         <div class="prod-gallery-track"></div>
         <button class="prod-gallery-arrow next" aria-label="Următor">›</button>
       </div>
     Ca să apară poze reale: puneți fișierele în folderul spectacolului
     (implicit subfolderul "img/" de lângă pagina .html) și listați
     numele lor, separate prin virgulă, în data-gallery-files — ex:
       data-gallery-files="01.jpg,02.jpg,03.jpg"
     Fără nicio listă, caseta arată automat câteva poziții placeholder,
     la fel ca restul site-ului (vezi data-gallery-placeholders, implicit
     6). Detaliu tehnic pentru README: vezi §2.3. */
  document.querySelectorAll('[data-gallery]').forEach(function (wrap) {
    var track = wrap.querySelector('.prod-gallery-track');
    if (!track) return;
    var folder = wrap.getAttribute('data-gallery-folder') || 'img/';
    var filesAttr = (wrap.getAttribute('data-gallery-files') || '').trim();
    var files = filesAttr
      ? filesAttr.split(',').map(function (s) { return s.trim(); }).filter(Boolean)
      : [];
    var placeholderCount = parseInt(wrap.getAttribute('data-gallery-placeholders') || '6', 10);
    var real = files.length > 0;
    var count = real ? files.length : placeholderCount;
    var baseCards = [];
    for (var i = 0; i < count; i++) {
      var card = document.createElement('div');
      card.className = 'prod-gallery-card';
      if (real) {
        var img = document.createElement('img');
        img.src = folder + files[i];
        img.alt = '';
        img.loading = 'lazy';
        card.appendChild(img);
      } else {
        card.innerHTML = '<div class="ph-photo__mark"><span class="ring-decor"></span>'
          + '<div class="ph-photo__label">' + T('Foto', 'Photo') + '</div><div class="ph-photo__sub">' + T('[ de completat ]', '[ to be added ]') + '</div></div>';
      }
      track.appendChild(card);
      baseCards.push(card);
    }
    var n = baseCards.length;
    if (n === 0) return;
    if (n < 2) { baseCards[0].classList.add('active'); return; }

    var clonesNeeded = Math.min(3, n);
    for (var c = 0; c < clonesNeeded; c++) {
      var after = baseCards[c % n].cloneNode(true);
      after.setAttribute('aria-hidden', 'true');
      track.appendChild(after);
    }
    for (var c2 = 0; c2 < clonesNeeded; c2++) {
      var before = baseCards[n - 1 - (c2 % n)].cloneNode(true);
      before.setAttribute('aria-hidden', 'true');
      track.insertBefore(before, track.firstChild);
    }

    var allCards = Array.from(track.querySelectorAll('.prod-gallery-card'));
    var idx = clonesNeeded;
    var isAnimating = false;
    var autoInterval = null;
    var pauseTimeout = null;

    function perView() {
      if (window.innerWidth <= 550) return 1;
      if (window.innerWidth <= 900) return 2;
      return 3;
    }
    function cardPercent() {
      var pv = perView();
      return pv === 1 ? 100 : pv === 2 ? 50 : 33.333;
    }
    function goTo(newIdx, animate) {
      idx = newIdx;
      var pv = perView();
      var center = (pv - 1) / 2;
      var val = -(idx - center) * cardPercent();
      track.style.transition = animate ? 'transform .6s cubic-bezier(.16,1,.3,1)' : 'none';
      track.style.transform = 'translateX(' + val + '%)';
      allCards.forEach(function (c) { c.classList.remove('active'); });
      if (allCards[idx]) allCards[idx].classList.add('active');
    }
    track.addEventListener('transitionend', function () {
      isAnimating = false;
      if (idx >= clonesNeeded + n) goTo(idx - n, false);
      else if (idx < clonesNeeded) goTo(idx + n, false);
    });
    function next(animate) { if (isAnimating) return; isAnimating = !!animate; goTo(idx + 1, animate); }
    function prev(animate) { if (isAnimating) return; isAnimating = !!animate; goTo(idx - 1, animate); }
    function startAuto() { stopAuto(); autoInterval = setInterval(function () { next(true); }, 4000); }
    function stopAuto() { if (autoInterval) { clearInterval(autoInterval); autoInterval = null; } }
    function pauseAutoTemporarily() {
      stopAuto();
      clearTimeout(pauseTimeout);
      pauseTimeout = setTimeout(function () { startAuto(); pauseTimeout = null; }, 6000);
    }
    var prevBtn = wrap.querySelector('.prod-gallery-arrow.prev');
    var nextBtn = wrap.querySelector('.prod-gallery-arrow.next');
    prevBtn && prevBtn.addEventListener('click', function () { prev(true); pauseAutoTemporarily(); });
    nextBtn && nextBtn.addEventListener('click', function () { next(true); pauseAutoTemporarily(); });
    wrap.addEventListener('mouseenter', stopAuto);
    wrap.addEventListener('mouseleave', function () { if (!pauseTimeout) startAuto(); });
    var startX = 0;
    track.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; stopAuto(); }, { passive: true });
    track.addEventListener('touchend', function (e) {
      var diff = e.changedTouches[0].clientX - startX;
      if (diff > 40) prev(true); else if (diff < -40) next(true);
      pauseAutoTemporarily();
    });
    window.addEventListener('resize', function () { goTo(idx, false); });
    goTo(idx, false);
    startAuto();
  });

  /* -- galerie tip ROLĂ DE FILM (folosită pentru „Margot” pe Acasă) -----
     Markup:
       <div class="film" data-film data-film-folder="spectacole/2026_margot/"
            data-film-files="2026_margot_01.jpg,2026_margot_02.jpg,..."></div>
     Scriptul construiește pelicula (perforații + cadre), cele două role
     care se rotesc și butonul Pauză/Pornește. Pelicula rulează continuu,
     se oprește la hover, iar click pe un cadru îl deschide mărit în
     lightbox. Cu „reducere animații” activată în sistem, nu rulează
     singură: se derulează manual, orizontal. */
  var REEL_SVG = '<svg viewBox="0 0 200 200" aria-hidden="true">'
    + '<circle cx="100" cy="100" r="96" class="reel__flange"/>'
    + '<circle cx="100" cy="100" r="62" class="reel__wound"/>'
    + '<circle cx="100" cy="100" r="50" class="reel__wound-line"/>'
    + '<circle cx="100" cy="100" r="38" class="reel__wound-line"/>'
    + [0, 72, 144, 216, 288].map(function (a) {
        return '<path class="reel__hole" transform="rotate(' + a + ' 100 100)" d="M100 22 a14 14 0 0 1 14 14 v14 a14 14 0 0 1 -28 0 v-14 a14 14 0 0 1 14 -14z"/>';
      }).join('')
    + '<circle cx="100" cy="100" r="20" class="reel__hub"/>'
    + '<circle cx="100" cy="100" r="7" class="reel__axle"/>'
    + '</svg>';
  document.querySelectorAll('[data-film]').forEach(function (wrap) {
    var folder = wrap.getAttribute('data-film-folder') || '';
    var files = (wrap.getAttribute('data-film-files') || '').split(',')
      .map(function (s) { return s.trim(); }).filter(Boolean);
    if (!files.length) return;
    var view = document.createElement('div');
    view.className = 'film__view';
    var track = document.createElement('div');
    track.className = 'film__track';
    for (var copy = 0; copy < 2; copy++) {
      files.forEach(function (f, i) {
        var a = document.createElement('a');
        a.className = 'film__frame';
        a.href = folder + f;
        if (copy) { a.setAttribute('aria-hidden', 'true'); a.tabIndex = -1; }
        else { a.setAttribute('aria-label', T('Mărește fotografia ', 'Enlarge photo ') + (i + 1)); }
        var img = document.createElement('img');
        img.src = folder + f;
        img.alt = '';
        img.loading = 'lazy';
        img.decoding = 'async';
        a.appendChild(img);
        a.addEventListener('click', function (e) {
          var lb = document.getElementById('lightbox');
          if (!lb) return;
          e.preventDefault();
          var inner = lb.querySelector('.lightbox__inner');
          inner.innerHTML = '';
          var big = document.createElement('img');
          big.className = 'lightbox__img';
          big.src = folder + f;
          big.alt = '';
          inner.appendChild(big);
          lb.classList.add('open');
          document.documentElement.style.overflow = 'hidden';
        });
        track.appendChild(a);
      });
    }
    track.style.setProperty('--film-dur', (files.length * 5) + 's');
    view.appendChild(track);
    wrap.appendChild(view);
    ['film__reel film__reel--left', 'film__reel film__reel--right'].forEach(function (cls) {
      var r = document.createElement('span');
      r.className = cls;
      r.innerHTML = REEL_SVG;
      wrap.appendChild(r);
    });
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'film__toggle';
    function label() {
      var paused = wrap.classList.contains('is-paused');
      btn.textContent = paused ? T('▶  Pornește pelicula', '▶  Play the reel') : T('❚❚  Oprește pelicula', '❚❚  Pause the reel');
      btn.setAttribute('aria-pressed', paused ? 'true' : 'false');
    }
    btn.addEventListener('click', function () { wrap.classList.toggle('is-paused'); label(); });
    label();
    wrap.appendChild(btn);
  });

  /* -- scroll reveal ----------------------------------------------------
     Conținutul e vizibil implicit din CSS (fără JS, se vede tot).
     Aici doar "înarmăm" cu .pre-reveal elementele aflate SUB prima
     fereastră vizibilă la încărcare — ca să nu existe niciun risc de
     bâlbâială vizuală pentru conținutul deja vizibil — apoi le animăm la
     scroll cu IntersectionObserver. Dacă IntersectionObserver lipsește,
     nu ascundem nimic: totul rămâne pur și simplu vizibil. */
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealEls.length) {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    var armed = [];
    revealEls.forEach(function (el, i) {
      var rect = el.getBoundingClientRect();
      var alreadyVisible = rect.top < vh && rect.bottom > 0;
      /* elementele foarte înalte (ex. lista de membri pe mobil) nu se
         ascund deloc: altfel pot rămâne invizibile pe ecrane mici */
      var tooTall = rect.height > vh * 0.8;
      if (!alreadyVisible && !tooTall) {
        el.classList.add('pre-reveal');
        el.style.transitionDelay = (i % 4) * 70 + 'ms';
        armed.push(el);
      }
    });
    if (armed.length) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0, rootMargin: '0px 0px -40px 0px' });
      armed.forEach(function (el) { io.observe(el); });
    }
  }

  /* -- lightbox foto / video ---------------------------------------------
     Orice element cu [data-lightbox] deschide un lightbox modal.
     - data-lightbox="video" + data-video-id="YOUTUBE_ID"  → embed YouTube
     - data-lightbox="photo"                                → mărește placeholder-ul
     ÎNLOCUIRE ULTERIOARĂ: când adăugați fotografii reale, puneți-le ca
     <img> în interiorul elementului .ph-photo (păstrați clasele pentru
     layout) — lightbox-ul va funcționa neschimbat. Pentru video, înlocuiți
     data-video-id="ID_DE_INLOCUIT" cu ID-ul real din URL-ul YouTube/Vimeo. */
  var lightbox = document.getElementById('lightbox');
  if (lightbox) {
    var inner = lightbox.querySelector('.lightbox__inner');
    var closeBtn = lightbox.querySelector('.lightbox__close');

    function openLightbox(trigger) {
      var type = trigger.getAttribute('data-lightbox');
      inner.innerHTML = '';
      if (type === 'video') {
        var vid = trigger.getAttribute('data-video-id') || 'ID_DE_INLOCUIT';
        /* cod provizoriu (YT_<folder-spectacol> sau ID_DE_INLOCUIT): clipul
           nu e încă pe YouTube → mesaj, nu un embed gol. Când clipul e
           urcat, înlocuiți codul din data-video-id cu ID-ul real (partea
           de după v= din adresa YouTube). */
        if (/^(YT_|ID_DE_INLOCUIT)/.test(vid)) {
          var soon = document.createElement('p');
          soon.className = 'lightbox__soon';
          soon.textContent = T('Video în curând.', 'Video coming soon.');
          inner.appendChild(soon);
          lightbox.classList.add('open');
          document.documentElement.style.overflow = 'hidden';
          return;
        }
        var iframe = document.createElement('iframe');
        iframe.src = 'https://www.youtube.com/embed/' + vid + '?autoplay=1&rel=0';
        iframe.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
        iframe.setAttribute('allowfullscreen', '');
        iframe.style.border = '0';
        inner.appendChild(iframe);
      } else {
        var clone = trigger.querySelector('.ph-photo').cloneNode(true);
        inner.appendChild(clone);
      }
      lightbox.classList.add('open');
      document.documentElement.style.overflow = 'hidden';
    }
    function closeLightbox() {
      lightbox.classList.remove('open');
      inner.innerHTML = '';
      document.documentElement.style.overflow = '';
    }
    document.querySelectorAll('[data-lightbox]').forEach(function (trigger) {
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        openLightbox(trigger);
      });
    });
    closeBtn && closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', function (e) { if (e.target === lightbox) closeLightbox(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeLightbox(); });
  }

  /* -- filtrare galerie pe producție -------------------------------------- */
  var filterBtns = document.querySelectorAll('.gallery-filters [data-filter]');
  var galleryItems = document.querySelectorAll('.gallery-grid [data-group]');
  if (filterBtns.length && galleryItems.length) {
    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var f = btn.getAttribute('data-filter');
        galleryItems.forEach(function (item) {
          var show = f === 'toate' || item.getAttribute('data-group') === f;
          item.style.display = show ? '' : 'none';
        });
      });
    });
  }

  /* -- formulare: validare simplă + stare trimitere ------------------------
     NOTĂ TEHNICĂ PENTRU BACKEND (vezi și README-tehnic-predare.md):
     Site-ul e static, deci formularele nu au, implicit, unde trimite datele.
     Mai jos, JS-ul face doar validare + simulează starea de succes local.
     Pentru funcționare reală, alegeți UNA din variante:
       1) Serviciu de formulare fără server (Formspree, Getform, Netlify
          Forms) — schimbați atributul `action` al <form> din HTML cu URL-ul
          primit de la serviciu și ștergeți preventDefault() de mai jos.
       2) Un mic backend propriu / integrare cu CMS-ul ales ulterior.
     Până atunci, fiecare formular are și un link "scrie-ne direct pe
     e-mail" ca variantă garantat funcțională. */
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var status = form.querySelector('.form-status');
      var required = form.querySelectorAll('[required]');
      var valid = true;
      required.forEach(function (field) {
        if (field.type === 'checkbox' ? !field.checked : !field.value.trim()) valid = false;
      });
      if (!valid) {
        e.preventDefault();
        if (status) {
          status.textContent = T('Te rugăm să completezi toate câmpurile obligatorii (*) și să confirmi acordul GDPR.', 'Please fill in all required fields (*) and confirm your GDPR consent.');
          status.className = 'form-status err';
        }
        return;
      }
      // Dacă action-ul e încă placeholder-ul din brief, interceptăm trimiterea
      // și arătăm un mesaj de succes simulat, ca să nu dea eroare de rețea.
      if (form.getAttribute('action') && form.getAttribute('action').indexOf('ID_DE_INLOCUIT') !== -1) {
        e.preventDefault();
        form.reset();
        if (status) {
          status.textContent = T('Formular OK din punct de vedere tehnic — dar nu e conectat încă la un serviciu real de trimitere. Vezi nota din README-tehnic-predare.md.', 'The form works technically, but it is not yet connected to a sending service.');
          status.className = 'form-status ok';
        }
      }
      // altfel, lăsăm submit-ul să meargă normal către action-ul configurat
    });
  });
})();
