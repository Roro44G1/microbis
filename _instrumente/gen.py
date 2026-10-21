import os, re, html, json
from data import SHOWS
import data
FOLD={'margot':'2026_margot','ritual-si-mere-rosii':'2025_ritual_si_mere_rosii','clipe-de-luciditate':'2024_clipe_de_luciditate','tinerete-fara-batranete':'2023_tinerete_fara_batranete','romeo-si-julieta':'2019_romeo_si_julieta','fetita-cu-chibrituri':'2018_fetita_cu_chibrituri','colectionarul':'2017_colectionarul','bonnie-clyde':'2016_bonnie_clyde','damnatul':'2014_damnatul','interviu-cu-un-ego':'2013_interviu_cu_un_ego','hurem-conditia-umana':'2012_hurem_conditia_umana','ultima-imbucatura-din-dragoste':'2011_ultima_imbucatura_din_dragoste','regina-margot':'2009_regina_margot','teodora-imparateasa-bizantului':'2008_teodora_imparateasa_bizantului','adam-si-eva':'2005_adam_si_eva','curtea-miracolelor':'2004_curtea_miracolelor','clipe-de-luciditate-1997':'1997_clipe_de_luciditate'}
SHOWS=sorted(SHOWS,key=lambda s:(s['slug']!='margot', -int(s['year'])))
for s in SHOWS:
    s['folder']=FOLD[s['slug']]
    VID={'2025_ritual_si_mere_rosii':'YdlM_1LQA74','2024_clipe_de_luciditate':'jSqcRChi0iA','2023_tinerete_fara_batranete':'dBlye_PlkGw','2019_romeo_si_julieta':'mQRtN62sLm8','2018_fetita_cu_chibrituri':'J9nZtOsWduQ','2017_colectionarul':'-kseIRkjH0w','2014_damnatul':'SxuLArnWC58','2011_ultima_imbucatura_din_dragoste':'aRFUlFCXCT8'}
    s['video']=VID.get(s['folder'], 'YT_'+s['folder'])
ROOT = os.path.expanduser('~/mnt/microbis'); SP = ROOT + '/spectacole'
FONTS = open(SP+'/damnatul.html', encoding='utf-8').read() if False else None
def head(title, desc, canon, ogdesc, ogtype='article'):
    return f'''<!doctype html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{{kw}}">
<link rel="canonical" href="https://microbis.ro/spectacole/{canon}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Microbis">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{ogdesc}">
<meta property="og:image" content="{{ogimg}}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" hreflang="ro" href="https://microbis.ro/spectacole/{canon}">
<link rel="alternate" hreflang="en" href="https://microbis.ro/en/spectacole/{canon}">
<link rel="alternate" hreflang="x-default" href="https://microbis.ro/spectacole/{canon}">
<link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;0,6..96,600;0,6..96,700;0,6..96,800;1,6..96,500;1,6..96,600;1,6..96,700&family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
<script src="../assets/js/partials.js"></script>
</head>
<body>

<script>document.write(microbisHeader('spectacole', false));</script>
'''
FOOT_SHOW = '''
<script>document.write(microbisFooter(false));</script>

<div class="lightbox" id="lightbox"><div class="lightbox__inner"></div><button class="lightbox__close">✕ Închide</button></div>
<script src="../assets/js/main.js"></script>
</body>
</html>
'''
def plain(s): return s.get('plain') or html.unescape(s['title'])
def attr(t): return html.escape(html.unescape(t), quote=True)
def imgs(slug):
    fo = FOLD[slug]; d = f'{SP}/{fo}'
    fs = sorted(f for f in os.listdir(d) if re.fullmatch(re.escape(fo)+r'_\d\d\.jpg', f))
    return fs, os.path.exists(f'{d}/{fo}_afis.jpg')
def para(ps): return '\n'.join(f'            <p>{p}</p>' for p in ps)
VAR = ['', ' v2', ' v3']
def page(i, s, nxt):
    slug, pt = s['slug'], plain(s)
    fo = s['folder']
    photos, afis = imgs(slug)
    desc = f"{pt} ({s['year']}) — spectacol din repertoriul Companiei de Teatru-Dans Microbis, Casa de Cultură a Studenților Sibiu."
    h = head(f"{attr(pt)} — Microbis", attr(desc), f'{slug}.html', attr(html.unescape(re.sub('<[^>]+>','',s['card']))))
    h = h.replace('{kw}', attr(f"{pt}, Microbis, teatru dans Sibiu, Hugo Wolff")).replace('{ogimg}', f"https://microbis.ro/spectacole/{fo}/{fo}_afis.jpg" if afis else "https://microbis.ro/assets/img/og-cover.jpg")
    o = [h, '<main>', '  <section class="theme-ink page-header pb-0">', '    <div class="container">',
         '      <a href="index.html" class="back-link">← Repertoriu</a>',
         f'      <p class="eyebrow eyebrow--red mt-22">{s["year"]} · {s["eyebrow"]}</p>',
         f'      <h1 class="h-display mt-18 mb-10">{s["h1"]}</h1>']
    if s.get('subtitle'): o.append(f'      <p class="h-md page-subtitle max-34ch">{s["subtitle"]}</p>')
    o += ['    </div>', '  </section>', '', '  <section class="section theme-ink pt-48">', '    <div class="container">',
          '      <div class="grid grid-3 gap-24 pb-48 border-bottom-ink" data-reveal>']
    for lab, val in s['credits']:
        o.append(f'        <div><div class="eyebrow eyebrow--muted mb-8">{lab}</div><div class="h-sm">{val}</div></div>')
    o += ['      </div>', '', '      <div class="grid grid-2 mt-xl items-start">', '        <div data-reveal>']
    first = True
    if s['about']:
        o += ['          <h2 class="h-md mb-18">Despre spectacol</h2>', '          <div class="prose opacity-80">', para(s['about']), '          </div>']; first = False
    if s['context']:
        o += [f'          <h2 class="h-md {"mb-18" if first else "mt-36 mb-18"}">{"Context" if not first else "Despre spectacol"}</h2>', '          <div class="prose opacity-80">', para(s['context']), '          </div>']; first = False
    if s.get('quotes'):
        o.append(f'          <h2 class="h-md {"mb-18" if first else "mt-36 mb-18"}">Din presă</h2>'); first = False
        for qt, qs in s['quotes']:
            o += ['          <blockquote class="press-quote mb-24">', f'            <p class="prose opacity-90">„{qt}”</p>', f'            <p class="press-source">{qs}</p>', '          </blockquote>']
        o.append('          <a href="../presa.html" class="btn btn-outline btn-arrow mt-10">Toate cronicile</a>')
    if s.get('press'): o.append('          <a href="../presa.html" class="btn btn-outline btn-arrow mt-26">Citește cronicile</a>')
    if s.get('related'): o.append(f'          <a href="{s["related"][0]}.html" class="btn btn-outline btn-arrow mt-26">{s["related"][1]}</a>')
    if False and s.get('missing'):
        o += [f'          <div class="notice {"mt-26" if not first else ""}">'.replace(' "', '"'), '            <span class="notice__icon">i</span>',
              f'            <span>Prezentarea completă a spectacolului „{html.escape(pt)}” este în curs de completare din arhiva companiei. Ai materiale, amintiri sau fotografii de la acest spectacol? <a href="../contact.html">Scrie-ne</a>.</span>', '          </div>']
    o.append('        </div>')
    alt = attr(f'Afișul spectacolului „{pt}”')
    if afis:
        o += ['        <div data-reveal>', f'          <div class="ph-photo ph-photo--poster" data-img="{fo}/{fo}_afis.jpg" data-img-alt="{alt}">',
              '            <div class="ph-photo__mark"><div class="ph-photo__label">Afiș</div></div>', '          </div>', '        </div>']
    else:
        o += ['        <div data-reveal>', f'          <div class="ph-photo ar-3-4">',
              '            <div class="ph-photo__mark"><span class="ring-decor ring-decor--44"></span><div class="ph-photo__label">Afiș</div><div class="ph-photo__sub">[ de completat ]</div></div>', '          </div>', '        </div>']
    o += ['      </div>']
    if s['cast'] or s.get('musicians') or s['team']:
        o += ['', '      <h2 class="h-md mt-xl mb-l" data-reveal>Distribuție</h2>', '      <div class="grid grid-2" data-reveal>']
        if s['cast']:
            o += ['        <div>', f'          <div class="eyebrow eyebrow--muted mb-14">{"Dansează" if len(s["cast"])>1 else "Cu"}</div>', f'          <p class="opacity-80">{", ".join(s["cast"])}.</p>']
            if s.get('musicians'):
                o += ['          <div class="eyebrow eyebrow--muted mt-26 mb-14">Muzicieni live</div>', f'          <p class="opacity-80">{", ".join(s["musicians"])}.</p>']
            o.append('        </div>')
        if s['team']:
            o += ['        <div>', '          <div class="eyebrow eyebrow--muted mb-14">Echipa</div>']
            o += [f'          <p class="opacity-80 mb-10"><strong>{l}:</strong> {v}</p>' for l, v in s['team']]
            o.append('        </div>')
        o.append('      </div>')
    if s['video']:
        has = not s['video'].startswith('YT_')
        sub = f'{html.escape(pt)} · {s["year"]}' if has else 'Video în curând'
        o += ['', '      <h2 class="h-md mt-xl mb-l" data-reveal>Video</h2>',
              f'      <div class="ph-video ph-photo{VAR[i%3]} ar-16-10 video-block" data-lightbox="video" data-video-id="{s["video"]}" data-reveal>',
              f'        <div class="ph-photo__mark"><div class="ph-photo__label">Extras spectacol</div><div class="ph-photo__sub">{sub}</div></div>',
              '        <div class="ph-video__play"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>', '      </div>']
    o += ['', '      <h2 class="h-md mt-xl mb-l" data-reveal>Din spectacol</h2>',
          f'      <div class="prod-gallery-wrap" data-gallery data-gallery-folder="{fo}/" data-gallery-files="{",".join(photos)}" data-reveal>',
          '        <button class="prod-gallery-arrow prev" aria-label="Anterior">‹</button>', '        <div class="prod-gallery-track"></div>',
          '        <button class="prod-gallery-arrow next" aria-label="Următor">›</button>', '      </div>', '    </div>', '  </section>', '',
          '  <section class="section theme-paper alt cta-band">', '    <div class="container">']
    if nxt:
        o += ['      <p class="eyebrow eyebrow--red justify-center">Următorul spectacol</p>', f'      <h2 class="h-lg mt-16 mb-26">{nxt["title"]}</h2>', f'      <a href="{nxt["slug"]}.html" class="btn btn-primary btn-arrow">Vezi spectacolul</a>']
    else:
        o += ['      <p class="eyebrow eyebrow--red justify-center">Repertoriu</p>', '      <h2 class="h-lg mt-16 mb-26">Vezi și celelalte spectacole</h2>', '      <a href="index.html" class="btn btn-primary btn-arrow">Toate spectacolele</a>']
    o += ['    </div>', '  </section>', '</main>', FOOT_SHOW]
    open(f'{SP}/{slug}.html', 'w', encoding='utf-8', newline='\n').write('\n'.join(o))
for i, s in enumerate(SHOWS):
    page(i, s, SHOWS[i+1] if i+1 < len(SHOWS) else None)
# --- hub ---
h = head('Spectacole &amp; Repertoriu — Microbis', attr('Repertoriul Companiei de Teatru-Dans Microbis, Casa de Cultură a Studenților Sibiu: ' + ', '.join(plain(s) if s['slug']!='clipe-de-luciditate-1997' else 'Clipe de luciditate (1997)' for s in SHOWS) + '.'), 'index.html', 'Producțiile care au marcat peste treizeci de ani de teatru-dans Microbis, la Sibiu.', 'website')
h = h.replace('{kw}', 'spectacole Microbis, repertoriu teatru-dans, Compania de Teatru-Dans Microbis, Sibiu, Hugo Wolff').replace('{ogimg}', 'https://microbis.ro/assets/img/og-cover.jpg').replace('<meta property="og:title" content="Spectacole &amp; Repertoriu — Microbis">','<meta property="og:title" content="Spectacole & Repertoriu — Microbis">')
o = [h, '<main>', '  <section class="theme-ink page-header">', '    <div class="container">', '      <p class="eyebrow eyebrow--red">Repertoriu</p>', '      <h1 class="h-display mt-18">Spectacole</h1>',
     f'      <p class="lede max-w-prose mt-24 opacity-85">{len(SHOWS)} producții din arhiva companiei, de la primele spectacole semnate de Hugo Wolff până la cea mai recentă premieră, din 2025.</p>',
     '    </div>', '  </section>', '', '  <section class="section theme-ink">', '    <div class="container">', '      <div class="grid grid-2">', '']
for i, s in enumerate(SHOWS):
    photos, afis = imgs(s['slug']); slug = s['slug']
    fo = s['folder']; src = f'{fo}/{photos[0]}' if photos else (f'{fo}/{fo}_afis.jpg' if afis else '')
    imgattr = f' data-img="{src}" data-img-alt="{attr("Din spectacolul „" + plain(s) + "”")}"' if src else ''
    meta = s['year'] + (' · Remake · Trailer 30–31 oct. 2026' if slug=='margot' else '') + (' · Versiunea originală' if slug=='clipe-de-luciditate-1997' else (' · Reinterpretare' if slug=='clipe-de-luciditate' else ''))
    o += [f'        <a class="card" href="{slug}.html" data-reveal>',
          f'          <div class="ph-photo{VAR[i%3]} ar-16-10"{imgattr}><div class="ph-photo__mark"><span class="ring-decor ring-decor--44"></span><div class="ph-photo__label">Foto spectacol</div><div class="ph-photo__sub">[ de completat ]</div></div></div>',
          '          <div class="card__body">', f'            <div class="card__meta">{meta}</div>', f'            <h3 class="card__title">{html.escape(plain(s)) if slug!="clipe-de-luciditate-1997" else "Clipe de luciditate"}</h3>',
          f'            <p class="card__text">{s["card"]}</p>', '          </div>', '        </a>', '']
o += ['      </div>', '    </div>', '  </section>', '</main>', '', "<script>document.write(microbisFooter(false));</script>", '', '<script src="../assets/js/main.js"></script>', '</body>', '</html>', '']
open(f'{SP}/index.html', 'w', encoding='utf-8', newline='\n').write('\n'.join(o))
# --- sitemap ---
sm = open(ROOT+'/sitemap.xml', encoding='utf-8').read()
sm = re.sub(r'\s*<url><loc>https://microbis\.ro/spectacole/(?!index)[^<]+</loc>.*?</url>', '', sm)
lines = ''.join(f'\n  <url><loc>https://microbis.ro/spectacole/{s["slug"]}.html</loc><priority>{"0.8" if int(s["year"])>=2023 else "0.6"}</priority></url>' for s in SHOWS)
sm = sm.replace('<loc>https://microbis.ro/spectacole/index.html</loc><priority>0.9</priority></url>', '<loc>https://microbis.ro/spectacole/index.html</loc><priority>0.9</priority></url>' + lines)
open(ROOT+'/sitemap.xml', 'w', encoding='utf-8', newline='\n').write(sm)
print('ok')
