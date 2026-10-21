import os, re, html, copy
import data, data_en
from common import FOLD, VID
ROOT = os.path.expanduser('~/mnt/microbis'); SP = ROOT + '/spectacole'; OUT = ROOT + '/en/spectacole'
os.makedirs(OUT, exist_ok=True)
SHOWS = []
for r in sorted(data.SHOWS, key=lambda s: (s['slug'] != 'regina-margot', -int(s['year']))):
    s = dict(r); e = data_en.E[s['slug']]
    s.update({k: v for k, v in e.items()})
    s['folder'] = FOLD[s['slug']]; s['video'] = VID.get(s['folder'], 'YT_' + s['folder'])
    s['missing'] = r.get('missing', False) and not e.get('quotes')
    s['press'] = r.get('press', False)
    SHOWS.append(s)
IMG = '../../spectacole/'
def plain(s): return s.get('plain') or html.unescape(s['title'])
def attr(t): return html.escape(html.unescape(t), quote=True)
def imgs(fo):
    d = f'{SP}/{fo}'
    return sorted(f for f in os.listdir(d) if re.fullmatch(re.escape(fo) + r'_\d\d\.jpg', f)), os.path.exists(f'{d}/{fo}_afis.jpg')
def para(ps): return '\n'.join(f'            <p>{p}</p>' for p in ps)
VAR = ['', ' v2', ' v3']
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;0,6..96,600;0,6..96,700;0,6..96,800;1,6..96,500;1,6..96,600;1,6..96,700&family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
def head(title, desc, canon, ogdesc, kw, ogimg, ogtype='article'):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<link rel="canonical" href="https://microbis.ro/en/spectacole/{canon}">
<meta property="og:type" content="{ogtype}">
<meta property="og:locale" content="en_GB">
<meta property="og:site_name" content="Microbis">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{ogdesc}">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" hreflang="ro" href="https://microbis.ro/spectacole/{canon}">
<link rel="alternate" hreflang="en" href="https://microbis.ro/en/spectacole/{canon}">
<link rel="alternate" hreflang="x-default" href="https://microbis.ro/spectacole/{canon}">
<link rel="icon" href="../../assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS}
<link rel="stylesheet" href="../../assets/css/style.css">
<script src="../../assets/js/partials.js"></script>
</head>
<body>

<script>document.write(microbisHeader('spectacole', false));</script>
'''
FOOT = '''
<script>document.write(microbisFooter(false));</script>

<div class="lightbox" id="lightbox"><div class="lightbox__inner"></div><button class="lightbox__close">✕ Close</button></div>
<script src="../../assets/js/main.js"></script>
</body>
</html>
'''
def page(i, s, nxt):
    slug, pt, fo = s['slug'], plain(s), s['folder']
    photos, afis = imgs(fo)
    desc = f"{pt} ({s['year']}) — a performance from the repertoire of the MICROBIS Theatre Dance Company, University Cultural Center of Sibiu."
    ogimg = f"https://microbis.ro/spectacole/{fo}/{fo}_afis.jpg" if afis else "https://microbis.ro/assets/img/og-cover.jpg"
    o = [head(f"{attr(pt)} — Microbis", attr(desc), f'{slug}.html', attr(re.sub('<[^>]+>', '', html.unescape(s['card']))), attr(f"{pt}, Microbis, theatre dance Sibiu, Hugo Wolff"), ogimg),
         '<main>', '  <section class="theme-ink page-header pb-0">', '    <div class="container">',
         '      <a href="index.html" class="back-link">← Repertoire</a>',
         f'      <p class="eyebrow eyebrow--red mt-22">{s["year"]} · {s["eyebrow"]}</p>',
         f'      <h1 class="h-display mt-18 mb-10">{s["h1"]}</h1>']
    if s.get('subtitle'): o.append(f'      <p class="h-md page-subtitle max-34ch">{s["subtitle"]}</p>')
    if s.get('orig'): o.append(f'      <p class="eyebrow eyebrow--muted mt-18" lang="ro">Original title: {s["orig"]}</p>')
    o += ['    </div>', '  </section>', '', '  <section class="section theme-ink pt-48">', '    <div class="container">',
          '      <div class="grid grid-3 gap-24 pb-48 border-bottom-ink" data-reveal>']
    o += [f'        <div><div class="eyebrow eyebrow--muted mb-8">{l}</div><div class="h-sm">{v}</div></div>' for l, v in s['credits']]
    o += ['      </div>', '', '      <div class="grid grid-2 mt-xl items-start">', '        <div data-reveal>']
    first = True
    if s['about']:
        o += ['          <h2 class="h-md mb-18">About the performance</h2>', '          <div class="prose opacity-80">', para(s['about']), '          </div>']; first = False
    if s['context']:
        o += [f'          <h2 class="h-md {"mb-18" if first else "mt-36 mb-18"}">{"Context" if not first else "About the performance"}</h2>', '          <div class="prose opacity-80">', para(s['context']), '          </div>']; first = False
    if s.get('quotes'):
        o.append(f'          <h2 class="h-md {"mb-18" if first else "mt-36 mb-18"}">From the press</h2>'); first = False
        for qt, qs in s['quotes']:
            o += ['          <blockquote class="press-quote mb-24">', f'            <p class="prose opacity-90">“{qt}”</p>', f'            <p class="press-source">{qs}</p>', '          </blockquote>']
        o.append('          <a href="../presa.html" class="btn btn-outline btn-arrow mt-10">All reviews</a>')
    if s.get('press'): o.append('          <a href="../presa.html" class="btn btn-outline btn-arrow mt-26">Read the reviews</a>')
    if s.get('related'): o.append(f'          <a href="{s["related"][0]}.html" class="btn btn-outline btn-arrow mt-26">{s["related"][1]}</a>')
    if s.get('missing'):
        o += [f'          <div class="notice{" mt-26" if not first else ""}">', '            <span class="notice__icon">i</span>',
              f'            <span>The full presentation of “{html.escape(pt)}” is being compiled from the company’s archive. Do you have materials, memories or photographs from this performance? <a href="../contact.html">Write to us</a>.</span>', '          </div>']
    o.append('        </div>')
    alt = attr(f'Poster for “{pt}”')
    if afis:
        o += ['        <div data-reveal>', f'          <div class="ph-photo ph-photo--poster" data-img="{IMG}{fo}/{fo}_afis.jpg" data-img-alt="{alt}">',
              '            <div class="ph-photo__mark"><div class="ph-photo__label">Poster</div></div>', '          </div>', '        </div>']
    else:
        o += ['        <div data-reveal>', '          <div class="ph-photo ar-3-4">',
              '            <div class="ph-photo__mark"><span class="ring-decor ring-decor--44"></span><div class="ph-photo__label">Poster</div><div class="ph-photo__sub">[ to be added ]</div></div>', '          </div>', '        </div>']
    o += ['      </div>']
    if s['cast'] or s.get('musicians') or s['team']:
        o += ['', '      <h2 class="h-md mt-xl mb-l" data-reveal>Cast</h2>', '      <div class="grid grid-2" data-reveal>']
        if s['cast']:
            o += ['        <div>', f'          <div class="eyebrow eyebrow--muted mb-14">{"Dancers" if len(s["cast"]) > 1 else "With"}</div>', f'          <p class="opacity-80">{", ".join(s["cast"])}.</p>']
            if s.get('musicians'):
                o += ['          <div class="eyebrow eyebrow--muted mt-26 mb-14">Live musicians</div>', f'          <p class="opacity-80">{", ".join(s["musicians"])}.</p>']
            o.append('        </div>')
        if s['team']:
            o += ['        <div>', '          <div class="eyebrow eyebrow--muted mb-14">Team</div>'] + [f'          <p class="opacity-80 mb-10"><strong>{l}:</strong> {v}</p>' for l, v in s['team']] + ['        </div>']
        o.append('      </div>')
    has = not s['video'].startswith('YT_')
    o += ['', '      <h2 class="h-md mt-xl mb-l" data-reveal>Video</h2>',
          f'      <div class="ph-video ph-photo{VAR[i % 3]} ar-16-10 video-block" data-lightbox="video" data-video-id="{s["video"]}" data-reveal>',
          f'        <div class="ph-photo__mark"><div class="ph-photo__label">Performance excerpt</div><div class="ph-photo__sub">{html.escape(pt) + " · " + s["year"] if has else "Video coming soon"}</div></div>',
          '        <div class="ph-video__play"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>', '      </div>',
          '', '      <h2 class="h-md mt-xl mb-l" data-reveal>From the performance</h2>',
          f'      <div class="prod-gallery-wrap" data-gallery data-gallery-folder="{IMG}{fo}/" data-gallery-files="{",".join(photos)}" data-reveal>',
          '        <button class="prod-gallery-arrow prev" aria-label="Previous">‹</button>', '        <div class="prod-gallery-track"></div>',
          '        <button class="prod-gallery-arrow next" aria-label="Next">›</button>', '      </div>', '    </div>', '  </section>', '',
          '  <section class="section theme-paper alt cta-band">', '    <div class="container">']
    if nxt:
        o += ['      <p class="eyebrow eyebrow--red justify-center">Next performance</p>', f'      <h2 class="h-lg mt-16 mb-26">{nxt["title"]}</h2>', f'      <a href="{nxt["slug"]}.html" class="btn btn-primary btn-arrow">See the performance</a>']
    else:
        o += ['      <p class="eyebrow eyebrow--red justify-center">Repertoire</p>', '      <h2 class="h-lg mt-16 mb-26">See the other performances</h2>', '      <a href="index.html" class="btn btn-primary btn-arrow">All performances</a>']
    o += ['    </div>', '  </section>', '</main>', FOOT]
    open(f'{OUT}/{slug}.html', 'w', encoding='utf-8', newline='\n').write('\n'.join(o))
for i, s in enumerate(SHOWS): page(i, s, SHOWS[i + 1] if i + 1 < len(SHOWS) else None)
# hub
titles = ', '.join(plain(s) if s['slug'] != 'clipe-de-luciditate-1997' else 'Moments of Awareness (1997)' for s in SHOWS)
o = [head('Performances &amp; Repertoire — Microbis', attr('The repertoire of the MICROBIS Theatre Dance Company, University Cultural Center of Sibiu: ' + titles + '.'), 'index.html', 'The productions that have marked more than thirty years of Microbis theatre dance in Sibiu.', 'Microbis performances, theatre dance repertoire, MICROBIS Theatre Dance Company, Sibiu, Hugo Wolff', 'https://microbis.ro/assets/img/og-cover.jpg', 'website').replace('content="Performances &amp; Repertoire — Microbis">', 'content="Performances & Repertoire — Microbis">'),
     '<main>', '  <section class="theme-ink page-header">', '    <div class="container">', '      <p class="eyebrow eyebrow--red">Repertoire</p>', '      <h1 class="h-display mt-18">Performances</h1>',
     f'      <p class="lede max-w-prose mt-24 opacity-85">{len(SHOWS)} productions from the company’s archive, from the first performances created by Hugo Wolff to the most recent premiere, in 2025.</p>',
     '    </div>', '  </section>', '', '  <section class="section theme-ink">', '    <div class="container">', '      <div class="grid grid-2">', '']
for i, s in enumerate(SHOWS):
    fo = s['folder']; photos, afis = imgs(fo)
    src = f'{IMG}{fo}/{photos[0]}' if photos else (f'{IMG}{fo}/{fo}_afis.jpg' if afis else '')
    ia = f' data-img="{src}" data-img-alt="{attr("From the performance “" + plain(s) + "”")}"' if src else ''
    meta = s['year'] + (f' · <span lang="ro">{s["orig"]}</span>' if s.get('orig') else '') + {'regina-margot': ' · Trailer 30–31 Oct. 2026', 'clipe-de-luciditate-1997': ' · Original version', 'clipe-de-luciditate': ' · Reinterpretation'}.get(s['slug'], '')
    o += [f'        <a class="card" href="{s["slug"]}.html" data-reveal>',
          f'          <div class="ph-photo{VAR[i % 3]} ar-16-10"{ia}><div class="ph-photo__mark"><span class="ring-decor ring-decor--44"></span><div class="ph-photo__label">Performance photo</div><div class="ph-photo__sub">[ to be added ]</div></div></div>',
          '          <div class="card__body">', f'            <div class="card__meta">{meta}</div>', f'            <h3 class="card__title">{html.escape(plain(s))}</h3>',
          f'            <p class="card__text">{s["card"]}</p>', '          </div>', '        </a>', '']
o += ['      </div>', '    </div>', '  </section>', '</main>', '', '<script>document.write(microbisFooter(false));</script>', '', '<script src="../../assets/js/main.js"></script>', '</body>', '</html>', '']
open(f'{OUT}/index.html', 'w', encoding='utf-8', newline='\n').write('\n'.join(o))
print('ok', len(SHOWS))
