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

  var NAV_ITEMS = [
    { key: 'acasa',      label: 'Acasă',        href: 'index.html' },
    { key: 'despre',     label: 'Despre trupă', href: 'despre-trupa.html' },
    { key: 'spectacole', label: 'Spectacole',   href: 'spectacole/index.html' },
    { key: 'trupa',      label: 'Trupă',        href: 'trupa.html' },
    { key: 'calendar',   label: 'Calendar',     href: 'calendar.html' },
    { key: 'galerie',    label: 'Galerie',      href: 'galerie.html' },
    { key: 'presa',      label: 'Presă',        href: 'presa.html' },
    { key: 'contact',    label: 'Contact',      href: 'contact.html' }
  ];

  // calea unui link din rădăcina site-ului, ajustată după unde suntem
  function pathFromRoot(root, href) {
    if (href === 'spectacole/index.html') return root ? href : 'index.html';
    return root ? href : '../' + href;
  }

  function esc(s) { return s; }

  /**
   * Generează utility-bar + header.
   * @param {string} active - cheia din NAV_ITEMS activă pe pagina curentă,
   *                           sau 'auditii' (caz special: butonul CTA, nu
   *                           un item din meniu), sau null/undefined (nicio
   *                           pagină din meniu, ex. confidențialitate).
   * @param {boolean} root - true dacă pagina e în rădăcina site-ului,
   *                          false dacă e în /spectacole/.
   */
  window.microbisHeader = function (active, root) {
    var logoSrc = pathFromRoot(root, 'assets/img/logo.png');
    var homeHref = pathFromRoot(root, 'index.html');
    var auditiiHref = pathFromRoot(root, 'auditii.html');

    var linksHtml = NAV_ITEMS.map(function (item) {
      var current = item.key === active ? ' aria-current="page"' : '';
      return '<li><a href="' + pathFromRoot(root, item.href) + '"' + current + '>' + esc(item.label) + '</a></li>';
    }).join('');

    var auditiiCurrent = active === 'auditii' ? ' aria-current="page"' : '';

    return (
      '<div class="utility-bar"><div class="container">' +
        '<a href="https://casastudentilorsibiu.ro/" target="_blank" rel="noopener">Sub egida Casei de Cultură a Studenților Sibiu ↗</a>' +
        '<div class="utility-bar__social">' +
          '<a href="https://www.instagram.com/microbisdancecompany/" target="_blank" rel="noopener">Instagram</a>' +
          '<a href="https://www.facebook.com/MicrobisDanceCompany/" target="_blank" rel="noopener">Facebook</a>' +
        '</div>' +
      '</div></div>' +
      '<header class="site-header"><div class="container">' +
        '<a href="' + homeHref + '" class="logo">' +
          '<img src="' + logoSrc + '" alt="Microbis" class="logo__mark">' +
          '<span><span class="logo__sub">Teatru-dans · CCS Sibiu</span></span>' +
        '</a>' +
        '<nav class="nav">' +
          '<ul class="nav__links">' + linksHtml + '</ul>' +
          '<a href="' + auditiiHref + '" class="btn btn-primary nav__cta"' + auditiiCurrent + '>Audiții</a>' +
          '<button class="nav__toggle" aria-label="Deschide meniul" aria-expanded="false"><span></span><span></span><span></span></button>' +
        '</nav>' +
      '</div></header>'
    );
  };

  /**
   * Generează footer-ul.
   * @param {boolean} root - true în rădăcină, false în /spectacole/.
   */
  window.microbisFooter = function (root) {
    var pfx = root ? '' : '../';
    var logoSrc = pfx + 'assets/img/logo.png';
    var spectacoleHref = root ? 'spectacole/index.html' : 'index.html';

    return (
      '<footer class="site-footer"><div class="container">' +
        '<div class="footer-grid">' +
          '<div class="footer-col">' +
            '<a href="' + pfx + 'index.html" class="logo" style="margin-bottom:16px;display:inline-flex">' +
              '<img src="' + logoSrc + '" alt="Microbis" class="logo__mark">' +
            '</a>' +
            '<p style="max-width:32ch;font-size:.9rem">Compania de teatru-dans a Casei de Cultură a Studenților Sibiu. Din 1993, corpul ca limbaj.</p>' +
            '<a href="https://casastudentilorsibiu.ro/" target="_blank" rel="noopener" class="footer-ccs">Casa de Cultură a Studenților Sibiu ↗</a>' +
          '</div>' +
          '<div class="footer-col"><h4>Site</h4><ul>' +
            '<li><a href="' + pfx + 'despre-trupa.html">Despre trupă</a></li>' +
            '<li><a href="' + spectacoleHref + '">Spectacole</a></li>' +
            '<li><a href="' + pfx + 'trupa.html">Trupă</a></li>' +
            '<li><a href="' + pfx + 'galerie.html">Galerie</a></li>' +
          '</ul></div>' +
          '<div class="footer-col"><h4>Implică-te</h4><ul>' +
            '<li><a href="' + pfx + 'calendar.html">Calendar spectacole</a></li>' +
            '<li><a href="' + pfx + 'auditii.html">Audiții</a></li>' +
            '<li><a href="' + pfx + 'presa.html">Presă &amp; critică</a></li>' +
            '<li><a href="' + pfx + 'contact.html">Contact</a></li>' +
          '</ul></div>' +
          '<div class="footer-col"><h4>Contact</h4><ul>' +
            '<li>Calea Dumbrăvii nr. 34, Sibiu</li>' +
            '<li><a href="mailto:contact@microbis.ro">contact@microbis.ro</a></li>' +
            '<li><a href="tel:+40269212883">+40 269 212 883</a></li>' +
          '</ul></div>' +
        '</div>' +
        '<div class="footer-bottom">' +
          '<span>© <span data-year>2026</span> Microbis — Casa de Cultură a Studenților Sibiu</span>' +
          '<div class="footer-social">' +
            '<a href="' + pfx + 'confidentialitate.html">Confidențialitate &amp; GDPR</a>' +
            '<a href="https://www.instagram.com/microbisdancecompany/" target="_blank" rel="noopener">Instagram</a>' +
            '<a href="https://www.facebook.com/MicrobisDanceCompany/" target="_blank" rel="noopener">Facebook</a>' +
          '</div>' +
        '</div>' +
      '</div></footer>'
    );
  };

})();
