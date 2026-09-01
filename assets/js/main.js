/* ==========================================================================
   MICROBIS — JS comun (navigație, lightbox galerie/video, formulare, reveal)
   Fișier vanilla JS, fără dependențe externe. Inclus pe toate paginile.
   ========================================================================== */
(function () {
  'use strict';

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
      if (!alreadyVisible) {
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
      }, { threshold: .15, rootMargin: '0px 0px -40px 0px' });
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
          status.textContent = 'Te rugăm să completezi toate câmpurile obligatorii (*) și să confirmi acordul GDPR.';
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
          status.textContent = 'Formular OK din punct de vedere tehnic — dar nu e conectat încă la un serviciu real de trimitere. Vezi nota din README-tehnic-predare.md.';
          status.className = 'form-status ok';
        }
      }
      // altfel, lăsăm submit-ul să meargă normal către action-ul configurat
    });
  });
})();
