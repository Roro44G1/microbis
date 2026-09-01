# Microbis — README tehnic de predare

Acest document însoțește site-ul de prezentare al companiei Microbis (Casa de Cultură a Studenților Sibiu) și e scris pentru persoana care va prelua conținutul mai departe — fie Radu, fie un dezvoltator angajat ulterior. Explică ce e placeholder și ce e conținut real, cum se înlocuiește fiecare tip de placeholder, cum se activează formularele, ce rămâne de rezolvat pe partea legală/GDPR, cum se optimizează imaginile, și câteva note despre migrarea la CMS și publicarea pe microbis.ro.

Site-ul e HTML/CSS/JS static, fără build step, fără dependențe — orice server web poate să-l servească așa cum e.

## 1. Structura fișierelor

```
microbis-site/
├── index.html                 Acasă
├── despre-trupa.html          Despre trupă (istoric, Hugo Wolff, noua generație)
├── trupa.html                 Trupă / Membri
├── calendar.html               Calendar / Bilete (informativ)
├── galerie.html                Galerie foto + video
├── presa.html                  Presă / Critică
├── auditii.html                 Audiții (formular înscriere)
├── contact.html                 Contact (formular + hartă)
├── confidentialitate.html       Politica de confidențialitate / GDPR (noindex)
├── robots.txt
├── sitemap.xml
├── spectacole/
│   ├── index.html                Hub repertoriu
│   ├── ritual-si-mere-rosii.html  Spectacolul curent (2025)
│   ├── clipe-de-luciditate.html   2024
│   ├── tinerete-fara-batranete.html  2023
│   └── romeo-si-julieta.html      Repertoriu istoric, pagină minimală
└── assets/
    ├── css/style.css             Tot sistemul de design (un singur fișier)
    ├── js/main.js                 Navigație mobilă, lightbox, galerie, formulare
    ├── js/partials.js             Header, meniu, footer — sursă unică (vezi mai jos)
    └── img/
        ├── logo.png               Logo-ul real, transparent (vezi §2.1)
        ├── favicon.svg            Favicon provizoriu (vezi §2.1)
        └── og-cover.jpg            Imagine de previzualizare pentru social media
```

Nu există CSS separat per pagină — tot ce ține de design e în `assets/css/style.css`. Header-ul, bara de sus și footer-ul **nu mai sunt copiate în fiecare pagină** — fiecare fișier HTML conține doar un rând care le cere din `assets/js/partials.js`:

```html
<script>document.write(microbisHeader('acasa', true));</script>
…
<script>document.write(microbisFooter(true));</script>
```

Tot ce ține de logo, meniu sau footer se editează **o singură dată**, în `assets/js/partials.js` — nu mai există 14 fișiere de umblat pentru o schimbare de genul ăsta. Vedeți comentariul din capul fișierului `partials.js` pentru ce anume se schimbă unde. (Restul conținutului fiecărei pagini — titluri, text, fotografii — rămâne, ca înainte, direct în fișierul HTML al paginii respective; doar chenarul comun de sus/jos vine din `partials.js`.)

Pentru a rula site-ul local, din interiorul folderului `microbis-site/`:

```
python3 -m http.server 8000
```

apoi deschideți `http://localhost:8000/`. (Deschiderea directă a fișierelor cu dublu-click, prin `file://`, funcționează parțial, dar formularele și unele verificări JS se comportă altfel decât pe un server real — recomandăm testarea printr-un server local, ca mai sus.)

## 2. Inventarul conținutului placeholder

Tot ce e placeholder e marcat vizual și consistent, ca să fie ușor de găsit fără să căutați prin cod: text între paranteze pătrate (`[ de înlocuit ]`, `[ Nume Prenume ]`) pe fotografii, un buton de play pe casetele video, și câte o casetă `.notice` cu chenar punctat auriu lângă orice secțiune cu conținut de completat. Nimic din ce vedeți pe site nu e prezentat ca fiind conținut final decât dacă provine direct din materialul de documentare.

### 2.1 Logo — REZOLVAT

Logo-ul real (simbolul dansatorului + wordmark „MICROBIS") e activ pe site, în `assets/img/logo.png`. Fișierul primit era un JPEG cu fundal negru plin — l-am procesat (fundal eliminat, păstrat doar desenul alb, decupat strâns) și salvat ca PNG cu transparență, ca să se integreze fără chenar vizibil peste header-ul semi-transparent și footer-ul plin ale site-ului.

E cablat o singură dată, în `assets/js/partials.js` (header-ul și footer-ul comune — vezi §1), nu în fiecare pagină. Dimensiunea afișată e controlată de clasa `.logo__mark` din `style.css` (`height: 42px`) — dacă vreți logo-ul mai mare sau mai mic, acolo se schimbă o singură valoare și se vede peste tot, instant.

**Dacă vedeți vreodată logo-ul afișat foarte mare** (cât o parte semnificativă din pagină): aproape sigur browserul a păstrat în cache o versiune veche a `style.css`, de dinainte ca regula `.logo__mark` să existe — un refresh normal uneori nu detectează schimbarea unui fișier CSS. Soluție: reîncărcați forțat pagina (Ctrl+Shift+R pe Windows/Linux, Cmd+Shift+R pe Mac) sau deschideți site-ul într-o fereastră privată/incognito ca să confirmați. Nu e nevoie să schimbați nimic în cod pentru asta.

Rămâne opțional: `assets/img/favicon.svg` e încă simbolul geometric simplu (cerc roșu/auriu), nu logo-ul real — o versiune de favicon derivată din silueta dansatorului ar arăta mai fidel brandului, dar cere o simplificare suplimentară (un logo cu text „MICROBIS" nu se citește la 16px). Spuneți dacă vreți să încerc o variantă.

### 2.2 Fotografii — fotografia din hero-ul paginii Acasă lipsește momentan

`index.html` a fost actualizat (varianta primită de la Radu) să folosească `<img src="assets/img/hero-ritual-mere-rosii.jpg">` în loc de caseta placeholder din hero — dar **acest fișier nu există încă** în `assets/img/`. Până când e adăugat, hero-ul de pe Acasă va afișa o iconiță de imagine spartă în loc de fotografie. Salvați fotografia reală cu exact acest nume în `assets/img/`, sau schimbați `src`-ul din cod dacă preferați alt nume de fișier.

**181 de casete foto** (`.ph-photo`) sunt distribuite pe tot site-ul — hero-uri, cele patru pagini de spectacol, Trupă (12 carduri de membri), Galerie, Despre trupă. Fiecare e un gradient CSS cu textură de grain (definit în `style.css`, clasele `.ph-photo`, `.v2`, `.v3` pentru variații de nuanță) și o etichetă text („Foto" / „[ de înlocuit ]").

**Pentru a înlocui o fotografie NU mai trebuie să atingeți markup-ul din interior.** Adăugați doar atributul `data-img="cale/catre/poza.jpg"` (și, opțional, `data-img-alt="descriere"`) pe div-ul `.ph-photo` existent — restul (span-uri, etichete) rămâne exact cum e, JS-ul (`assets/js/main.js`) le înlocuiește automat la încărcarea paginii:

```html
<div class="ph-photo v2" style="--ar:4/5" data-reveal
     data-img="assets/img/hugo-wolff.jpg"
     data-img-alt="Hugo Wolff, fondatorul companiei Microbis">
  <div class="ph-photo__mark">...</div>
</div>
```

Un singur atribut adăugat, nimic șters. Fără `data-img`, caseta rămâne exact placeholder-ul de-acum.

Vezi §3 pentru dimensiunile recomandate și pipeline-ul de optimizare — brief-ul cere explicit un site rapid, cu galerie indexabilă și originale grele ținute separat, nu încărcate direct.

### 2.3 Video

**5 casete video** (`.ph-video`), toate gândite pentru embed YouTube sau Vimeo prin lightbox (nu fișiere video servite direct — corect, dat fiind că brief-ul cere site rapid):

- `spectacole/ritual-si-mere-rosii.html` — trailer
- `spectacole/clipe-de-luciditate.html` — extras
- `spectacole/tinerete-fara-batranete.html` — extras
- `galerie.html` — 2 casete video în grila foto

Fiecare are `data-video-id="ID_DE_INLOCUIT"`. Înlocuiți `ID_DE_INLOCUIT` cu ID-ul real din URL-ul YouTube (partea de după `v=`) sau Vimeo. Lightbox-ul din `main.js` construiește automat embed-ul `youtube.com/embed/{id}` — dacă alegeți Vimeo în loc de YouTube, trebuie ajustat acel fragment din `main.js` (căutați `data-video-id` în fișier) să construiască URL-ul de embed Vimeo (`player.vimeo.com/video/{id}`).

### 2.4 Membri și echipă tehnică (trupa.html)

12 carduri placeholder: 8 dansatori + 4 poziții tehnice (Lumini, Sunet, Scenografie & costume, Coordonare producție), fiecare cu `[ Nume Prenume ]` și o poză `.ph-photo`. Componența reală a companiei se schimbă anual (caracter studențesc), motiv pentru care nu am pus nume — vezi și caseta `.notice` de pe pagină, care trimite spre distribuția istorică (nume reale, datate) de pe pagina „Clipe de luciditate".

**Important — GDPR:** înainte de a publica nume și fotografii de membri actuali, aveți nevoie de consimțământ explicit, scris, de la fiecare persoană (secțiunea 5 din `confidentialitate.html` menționează deja acest lucru public). Vezi checklist-ul din §5.

### 2.5 Coregraf / coordonator artistic actual (despre-trupa.html)

O singură casetă, ușor de găsit — căutați `[ Nume de completat ]` în `despre-trupa.html` (în cardul „O nouă generație"). Materialul de documentare nu a putut confirma cine conduce artistic compania după 2023, dincolo de continuitatea asigurată de Florian Oros (regizor) și Alex Wolff (regie/coregrafie pentru „Ritual și Mere Roșii", 2025) — ambii au deja carduri proprii pe aceeași secțiune, cu ce s-a putut confirma despre fiecare.

### 2.6 Calendar (calendar.html)

Pagina conține un singur card-exemplu, badge-uit vizibil „EXEMPLU DE FORMAT — nu e un spectacol real", plus o notă care spune clar că nu există, la data predării, spectacole confirmate. Când aveți o dată reală: copiați structura `.event-card` a exemplului, completați data/ora/locul, și **ștergeți badge-ul „EXEMPLU DE FORMAT"** (căutați string-ul exact în `calendar.html`). Rețineți: conform răspunsului vostru din faza de brief, pagina rămâne informativă — fără bilete online — pentru lansare; secțiunea „Vrei vânzare online de bilete?" explică pe scurt opțiunile pentru mai târziu.

### 2.7 Audiții (auditii.html)

Similar cu Calendarul — un card-exemplu de sesiune, badge-uit „EXEMPLU DE FORMAT — nu e o dată reală", cu `[ Dată sesiune audiții ]` de completat când există o sesiune reală programată.

## 3. Pipeline de imagini — optimizare și arhivă

Brief-ul menționează explicit multe fotografii și materiale video nepublicate încă, și cere o arhitectură de galerie „serioasă", indexabilă, cu încărcare rapidă. Recomandarea tehnică, gândită să se potrivească cu ce e deja construit:

1. **Originale** (RAW/JPG mari, materiale brute video) — păstrate într-un depozit separat de codul site-ului: un Google Drive/folder partajat, sau un repo separat (ex. Git LFS, dacă echipa e confortabilă cu Git), niciodată încărcate direct în folderul `assets/img/` al site-ului. Brief-ul cere exact asta — „arhivă accesată la cerere", nu servită publicului.
2. **Versiuni web** — pentru fiecare fotografie care intră pe site: redimensionată la maximum ~1600px pe latura lungă pentru imaginile mari (hero-uri) și ~800px pentru cardurile din galerie/grile, exportată în JPG sau, ideal, **WebP** (fișiere semnificativ mai mici, suportate de toate browserele moderne) cu un JPG ca fallback dacă vreți compatibilitate maximă. Un instrument simplu ca [Squoosh](https://squoosh.app) (gratuit, în browser) sau `cwebp`/`sharp` în linie de comandă fac treaba fără cunoștințe tehnice avansate.
3. **Lazy loading** — deja pregătit structural: orice `<img>` care înlocuiește o casetă `.ph-photo` din Galerie sau din grilele de „Din spectacol" ar trebui să primească atributul `loading="lazy"` (nativ în HTML, fără JS suplimentar). Imaginile din hero (prima secțiune vizibilă a fiecărei pagini) fac excepție — acelea se încarcă imediat (`loading="eager"` sau fără atribut), ca să nu întârzie prima impresie.
4. **Indexare** — pentru ca imaginile din galerie să apară în Google Imagini, fiecare `<img>` are nevoie de un atribut `alt` descriptiv (ex. „Dansatori Microbis, scenă din Ritual și Mere Roșii, 2025" — nu doar „foto1.jpg"). Momentan casetele placeholder nu au `alt` fiindcă nu există încă imagine reală de descris; nu uitați să-l adăugați odată cu fiecare fotografie.

## 4. Activarea formularelor

Site-ul are două formulare — Contact (`contact.html`) și Audiții (`auditii.html`) — construite identic din punct de vedere tehnic. Amândouă au `action="https://formspree.io/f/ID_DE_INLOCUIT"` și un checkbox GDPR obligatoriu.

Codul din `main.js` (căutați comentariul „NOTĂ TEHNICĂ PENTRU BACKEND") e deja pregătit inteligent: **atâta timp cât `action` conține textul `ID_DE_INLOCUIT`**, JS-ul interceptează trimiterea și arată un mesaj clar că formularul e funcțional tehnic dar nu e conectat încă — nu lasă utilizatorul să creadă că a trimis ceva ce nu a ajuns nicăieri. În paralel, fiecare formular are un link „scrie-ne direct pe e-mail" care funcționează garantat, indiferent de stadiu.

Ca să activați trimiterea reală, cel mai simplu drum:

1. Creați un cont gratuit pe [Formspree.io](https://formspree.io) (sau alternative echivalente: Getform, Netlify Forms — dacă site-ul ajunge găzduit pe Netlify, acesta din urmă e cel mai simplu, fără cont separat).
2. Creați un „form endpoint" nou pentru fiecare formular (recomandăm două separate — unul pentru Contact, unul pentru Audiții — ca să le puteți distinge în inbox).
3. Înlocuiți `ID_DE_INLOCUIT` din `action="https://formspree.io/f/ID_DE_INLOCUIT"` cu ID-ul primit, în `contact.html` și, separat, în `auditii.html`.
4. Gata — din momentul ăsta, `action` nu mai conține `ID_DE_INLOCUIT`, deci JS-ul nu mai intervine și formularul trimite normal către Formspree, care vă retrimite datele pe e-mail.

Nu e nevoie de nicio altă modificare de cod pentru acest pas.

## 5. Checklist legal / GDPR — operațional (intern, nu pentru site-ul public)

Pagina publică `confidentialitate.html` acoperă ce colectăm prin formulare și de ce, dar câteva lucruri rămân de gestionat **intern, înainte de publicare**, și nu aparțin unei pagini publice:

- **Consimțământ foto/video pentru fiecare membru actual** — un formular scris simplu (poate fi pe hârtie sau un Google Form intern), semnat de fiecare dansator/membru al echipei tehnice, înainte de a le publica numele și fotografia pe pagina Trupă. Secțiunea 5 din `confidentialitate.html` promite deja public că acest consimțământ există separat — asigurați-vă că e adevărat înainte de lansare.
- **Verificare DPO** — textul din `confidentialitate.html` e un model standard, adaptat pentru acest site, dar recomandăm explicit (și pagina o spune) o trecere prin responsabilul cu protecția datelor al CCS Sibiu înainte de publicare finală — mai ales datele operatorului și temeiul legal exact.
- **Drepturi de autor muzică și coregrafie** — pentru extrasele video complete (nu doar teasere scurte): muzica folosită live sau înregistrată în spectacole poate necesita clarificare de drepturi (ex. printr-un organism de gestiune colectivă, sau confirmare că muzica e originală/compusă pentru spectacol) înainte de a publica înregistrări video complete pe YouTube/site. Teaserele scurte au, în general, o expunere legală mai mică, dar recomandăm verificare oricum.
- **Minori** — dacă vreun membru actual sau viitor al companiei e minor, fotografiile/numele lui necesită consimțământul unui părinte/tutore, nu doar consimțământul propriu.
- **Cookie-uri** — secțiunea 8 din `confidentialitate.html` spune corect că site-ul, în forma curentă, nu are cookie-uri de tracking. Dacă adăugați ulterior Google Analytics sau alt instrument similar, **trebuie** actualizat acel text și adăugat un banner de consimțământ cookie — altfel pagina de confidențialitate devine inexactă.

## 6. SEO tehnic — ce există deja

- Meta title/description unice pe fiecare pagină, Open Graph + Twitter Card pentru preview la distribuire pe social media (imaginea folosită: `assets/img/og-cover.jpg`).
- `sitemap.xml` cu toate cele 13 pagini publice; `confidentialitate.html` e exclusă intenționat (are `noindex` și e disallow-uită în `robots.txt`, fiind un document legal, nu conținut de indexat).
- Date structurate JSON-LD (schema.org, tip `PerformingGroup`) pe `index.html`, utile pentru rezultate îmbogățite în Google.
- Cuvintele cheie din brief sunt reflectate în title-uri, meta description și textul vizibil (teatru-dans Sibiu, dans contemporan Sibiu, audiții dans Sibiu etc.) — organic, nu înghesuit.

Ce mai rămâne, după publicare pe domeniul final:
- Înregistrarea site-ului în Google Search Console și trimiterea sitemap-ului.
- Actualizarea `<link rel="canonical">` și a URL-urilor `og:image`/`sitemap.xml` dacă domeniul final diferă de `microbis.ro` (folosit ca ipoteză de lucru în tot codul).

## 7. Note pentru migrarea la CMS

Brief-ul menționează „HTML+CSS+JS static, eventual și CMS" — site-ul actual e gândit să facă acest pas ușor, dar nu presupune niciunul anume. Câteva opțiuni realiste, de la cea mai simplă la cea mai completă:

- **CMS bazat pe Git (Decap CMS / Netlify CMS)** — cel mai apropiat de structura actuală: adaugă o interfață vizuală de editare peste fișiere Markdown/JSON, fără bază de date, găzduire în continuare statică. Cel mai puțin efort de migrare din punctul actual.
- **Generator static cu template-uri (Eleventy, Astro)** — ar rezolva duplicarea actuală a header-ului/footer-ului în fiecare fișier HTML (menționată în §1) transformând-o în componente reutilizabile, păstrând site-ul static și rapid.
- **WordPress (eventual headless)** — dacă echipa CCS Sibiu are deja experiență de administrare WordPress din alte proiecte, e o opțiune familiară, deși mai „grea" tehnic decât actuala arhitectură.

Oricare ar fi alegerea, sistemul de design (`style.css`) și structura de conținut (title-uri, secțiuni, ordinea paginilor) pot fi reutilizate aproape neschimbate — munca de migrare e în principal despre cum se editează conținutul, nu despre cum arată.

## 8. Publicare pe microbis.ro

Fiind un site 100% static, orice hosting de fișiere statice funcționează. Câteva opțiuni obișnuite, de la cea mai simplă la cea mai flexibilă:

1. **Netlify sau Vercel** (gratuit pentru acest volum de trafic) — se trage folderul `microbis-site/` (sau un repo Git conectat) și publicarea se face automat; formularele pot folosi chiar Netlify Forms în loc de Formspree, dacă alegeți Netlify. Recomandat dacă nu există deja un hosting.
2. **Hosting clasic cu cPanel/FTP** — dacă CCS Sibiu are deja găzduire web pentru alte site-uri, tot conținutul din `microbis-site/` (mai puțin `_qa/` și acest README) se încarcă prin FTP în directorul public al domeniului.

Pași generali, indiferent de hosting ales:
- Configurarea domeniului `microbis.ro` (sau subdomeniul ales) să indice spre hostingul respectiv (înregistrare DNS de tip A sau CNAME, în funcție de furnizor).
- Activarea HTTPS (certificat SSL) — Netlify/Vercel îl generează automat; hostingurile clasice au de obicei Let's Encrypt gratuit prin cPanel.
- După publicare: verificați `sitemap.xml` și `robots.txt` la adresa finală, și trimiteți sitemap-ul în Google Search Console (§6).

## 9. Verificări făcute înainte de predare

Toate cele 13 pagini publice au fost randate local și verificate vizual pe două rezoluții (desktop 1440px, mobil 390px) cu Chromium, în ambele teme ale sistemului de design (`theme-ink` — pagini de prezentare/spectacole; `theme-paper` — pagini utilitare, conform deciziei „hibrid pe secțiuni" din faza de brief). În acest proces au fost găsite și corectate câteva probleme de aliniere (suprapunere text pe casetele video, un link care se rupea pe două rânduri, o grilă de 3 coloane care nu se restrângea corect pe mobil pe cele trei pagini de spectacol cu dată).

Recomandăm totuși un test final chiar de către voi, pe dispozitive reale și în Chrome/Safari/Firefox, mai ales după ce înlocuiți placeholder-ele cu fotografii și video reale — dimensiunile fișierelor reale pot afecta viteza de încărcare într-un fel pe care testele cu placeholder nu-l pot arăta.

## 10. Ce nu e inclus în arhivă

Folderul `_qa/` (capturile de ecran folosite în procesul de verificare internă) nu face parte din livrarea finală — nu e conținut de site, doar artefact de proces.
