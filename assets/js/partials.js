/* ============================================================
   Microbis — header, utility-bar și footer, generate dintr-un
   singur loc.

   De ce există acest fișier: înainte, header-ul și footer-ul erau
   copiate manual în toate cele 14 pagini HTML — orice schimbare
   (logo, meniu, date de contact) însemna 14 editări identice, ușor
   de dezsincronizat. Acum există o singură sursă, aici, iar fiecare
   pagină doar o invocă printr-un rând de cod.

   CE MODIFICAȚI AICI ca să schimbați ceva pe TOT site-ul:
   - logo-ul: variabila LOGO_SRC de mai jos + fișierul assets/img/logo.png
   - dimensiunea logo-ului: clasa .logo__mark din assets/css/style.css
   - linkurile din meniu: array-ul NAV_ITEMS
   - datele de contact / rețele sociale din footer: funcția
     microbisFooter()

   NU trebuie să atingeți nicio pagină individuală pentru asta.
   ============================================================ */

(function () {

  /* Limba paginii: paginile din /en/ au <html lang="en">. Toate textele
     din meniu și footer există în ambele limbi (TXT.ro / TXT.en). */
  var LANG = /^en/i.test(document.documentElement.lang || '') ? 'en' : 'ro';

  var TXT = {
    ro: {
      nav: { acasa: 'Acasă', despre: 'Povestea', spectacole: 'Spectacole', membri: 'Membri', calendar: 'Calendar', presa: 'Presă', contact: 'Contact' },
      cta: 'Audiții', menu: 'Deschide meniul',
      aegis: 'Sub egida Casei de Cultură a Studenților Sibiu ↗',
      logoSub: 'Teatru-dans · CCS Sibiu',
      about: 'Compania de Teatru-Dans a Casei de Cultură a Studenților Sibiu. Din 1993, corpul ca limbaj.',
      ccs: 'Casa de Cultură a Studenților Sibiu ↗',
      colSite: 'Site', colInv: 'Implică-te', colContact: 'Contact',
      calendar: 'Calendar spectacole', auditii: 'Audiții', presa: 'Presă &amp; critică', contact: 'Contact',
      address: 'Calea Dumbrăvii nr. 34, Sibiu',
      copy: 'Microbis — Casa de Cultură a Studenților Sibiu',
      credit: 'Site realizat de dr. ing. Radu Pascu — Asociația AVANS PROIECT, 2026',
      privacy: 'Confidențialitate &amp; GDPR',
      switchLabel: 'EN', switchTitle: 'English version', switchLang: 'en'
    },
    en: {
      nav: { acasa: 'Home', despre: 'Our story', spectacole: 'Performances', membri: 'Members', calendar: 'Calendar', presa: 'Press', contact: 'Contact' },
      cta: 'Auditions', menu: 'Open menu',
      aegis: 'Under the aegis of the University Cultural Center of Sibiu ↗',
      logoSub: 'Theatre dance · Sibiu',
      about: 'The theatre dance company of the University Cultural Center of Sibiu. Since 1993, the body as language.',
      ccs: 'University Cultural Center of Sibiu ↗',
      colSite: 'Site', colInv: 'Get involved', colContact: 'Contact',
      calendar: 'Performance calendar', auditii: 'Auditions', presa: 'Press &amp; reviews', contact: 'Contact',
      address: '34 Calea Dumbrăvii, Sibiu, Romania',
      copy: 'Microbis — University Cultural Center of Sibiu',
      credit: 'Website by Dr. Eng. Radu Pascu — AVANS PROIECT Association, 2026',
      privacy: 'Privacy &amp; GDPR',
      switchLabel: 'RO', switchTitle: 'Versiunea în limba română', switchLang: 'ro'
    }
  };
  var t = TXT[LANG];

  var NAV_ITEMS = [
    { key: 'acasa',      href: 'index.html' },
    { key: 'despre',     href: 'index.html#despre' },
    { key: 'spectacole', href: 'spectacole/index.html' },
    { key: 'membri',     href: 'membri.html' },
    // Calendar ascuns temporar (pagina rămâne în site, dar fără link). Pentru reactivare, scoateți // de pe rândul de mai jos.
    // { key: 'calendar',   href: 'calendar.html' },
    { key: 'presa',      href: 'presa.html' },
    { key: 'contact',    href: 'contact.html' }
  ];

  // link către o pagină din aceeași limbă (root = pagina e în rădăcina
  // limbii, nu în /spectacole/)
  function pathFromRoot(root, href) {
    if (href === 'spectacole/index.html') return root ? href : 'index.html';
    return root ? href : '../' + href;
  }
  // cale către fișiere comune (assets/, imagini) — care există o singură
  // dată, în rădăcina site-ului, pentru ambele limbi
  function assetPath(root, href) {
    return (LANG === 'en' ? '../' : '') + (root ? '' : '../') + href;
  }
  // aceeași pagină în cealaltă limbă
  function otherLangHref(root) {
    var file = (location.pathname.split('/').pop() || 'index.html');
    if (LANG === 'ro') return (root ? 'en/' : '../en/spectacole/') + file;
    return (root ? '../' : '../../spectacole/') + file;
  }

  function esc(s) { return s; }

  /**
   * Generează utility-bar + header.
   * @param {string} active - cheia din NAV_ITEMS activă pe pagina curentă,
   *                           sau 'auditii' (butonul CTA), sau null.
   * @param {boolean} root - true dacă pagina e în rădăcina limbii,
   *                          false dacă e în /spectacole/.
   */
  window.microbisHeader = function (active, root) {
    var logoSrc = assetPath(root, 'assets/img/logo.png');
    var homeHref = pathFromRoot(root, 'index.html');
    var auditiiHref = pathFromRoot(root, 'auditii.html');

    var linksHtml = NAV_ITEMS.map(function (item) {
      var current = item.key === active ? ' aria-current="page"' : '';
      return '<li><a href="' + pathFromRoot(root, item.href) + '"' + current + '>' + esc(t.nav[item.key]) + '</a></li>';
    }).join('');

    var auditiiCurrent = active === 'auditii' ? ' aria-current="page"' : '';
    var sw = '<a href="' + otherLangHref(root) + '" class="lang-switch" hreflang="' + t.switchLang + '" lang="' + t.switchLang + '" title="' + t.switchTitle + '">' + t.switchLabel + '</a>';

    return (
      '<div class="utility-bar"><div class="container">' +
        '<a href="https://casastudentilorsibiu.ro/" target="_blank" rel="noopener">' + t.aegis + '</a>' +
        '<div class="utility-bar__social">' +
          '<a href="https://www.instagram.com/microbisdancecompany/" target="_blank" rel="noopener">Instagram</a>' +
          '<a href="https://www.facebook.com/MicrobisDanceCompany/" target="_blank" rel="noopener">Facebook</a>' +
        '</div>' +
      '</div></div>' +
      '<header class="site-header"><div class="container">' +
        '<a href="' + homeHref + '" class="logo">' +
          '<img src="' + logoSrc + '" alt="Microbis" class="logo__mark">' +
          '<span><span class="logo__sub">' + t.logoSub + '</span></span>' +
        '</a>' +
        '<nav class="nav">' +
          '<ul class="nav__links">' + linksHtml + '</ul>' +
          sw +
          '<a href="' + auditiiHref + '" class="btn btn-primary nav__cta"' + auditiiCurrent + '>' + t.cta + '</a>' +
          '<button class="nav__toggle" aria-label="' + t.menu + '" aria-expanded="false"><span></span><span></span><span></span></button>' +
        '</nav>' +
      '</div></header>'
    );
  };

  /**
   * Generează footer-ul.
   * @param {boolean} root - true în rădăcina limbii, false în /spectacole/.
   */
  window.microbisFooter = function (root) {
    var pfx = root ? '' : '../';
    var logoSrc = assetPath(root, 'assets/img/logo.png');
    var spectacoleHref = root ? 'spectacole/index.html' : 'index.html';

    return (
      '<footer class="site-footer"><div class="container">' +
        '<div class="footer-grid">' +
          '<div class="footer-col">' +
            '<a href="' + pfx + 'index.html" class="logo" style="margin-bottom:16px;display:inline-flex">' +
              '<img src="' + logoSrc + '" alt="Microbis" class="logo__mark">' +
            '</a>' +
            '<p style="max-width:32ch;font-size:.9rem">' + t.about + '</p>' +
            '<a href="https://casastudentilorsibiu.ro/" target="_blank" rel="noopener" class="footer-ccs">' + t.ccs + '</a>' +
          '</div>' +
          '<div class="footer-col"><h4>' + t.colSite + '</h4><ul>' +
            '<li><a href="' + pfx + 'index.html#despre">' + t.nav.despre + '</a></li>' +
            '<li><a href="' + spectacoleHref + '">' + t.nav.spectacole + '</a></li>' +
            '<li><a href="' + pfx + 'membri.html">' + t.nav.membri + '</a></li>' +
          '</ul></div>' +
          '<div class="footer-col"><h4>' + t.colInv + '</h4><ul>' +
            /* Calendar ascuns temporar: '<li><a href="' + pfx + 'calendar.html">' + t.calendar + '</a></li>' + */
            '<li><a href="' + pfx + 'auditii.html">' + t.auditii + '</a></li>' +
            '<li><a href="' + pfx + 'presa.html">' + t.presa + '</a></li>' +
            '<li><a href="' + pfx + 'contact.html">' + t.contact + '</a></li>' +
          '</ul></div>' +
          '<div class="footer-col"><h4>' + t.colContact + '</h4><ul>' +
            '<li>' + t.address + '</li>' +
            '<li><a href="mailto:contact@microbis.ro">contact@microbis.ro</a></li>' +
            '<li><a href="tel:+40269212883">+40 269 212 883</a></li>' +
          '</ul></div>' +
        '</div>' +
        '<div class="footer-bottom">' +
          '<span>© <span data-year>2026</span> ' + t.copy +
            '<span class="footer-credit">' + t.credit + '</span></span>' +
          '<div class="footer-social">' +
            '<a href="' + pfx + 'confidentialitate.html">' + t.privacy + '</a>' +
            '<a href="https://www.instagram.com/microbisdancecompany/" target="_blank" rel="noopener">Instagram</a>' +
            '<a href="https://www.facebook.com/MicrobisDanceCompany/" target="_blank" rel="noopener">Facebook</a>' +
          '</div>' +
        '</div>' +
      '</div></footer>'
    );
  };

})();
