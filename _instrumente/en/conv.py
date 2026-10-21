import re, os, sys, importlib
SITE = os.path.expanduser('~/mnt/microbis')
BASE = 'https://microbis.ro/'
def tr_text(html, pairs, fname):
    missing = []
    for ro, en in sorted(pairs, key=lambda p: -len(p[0])):
        pat_t = re.compile(r'(?<=>)(\s*)' + re.escape(ro) + r'(\s*)(?=<)')
        pat_a = re.compile(r'(?<==")' + re.escape(ro) + r'(?=")')
        n1 = len(pat_t.findall(html)); n2 = len(pat_a.findall(html))
        if not n1 and not n2: missing.append(ro[:70]); continue
        html = pat_t.sub(lambda m: m.group(1) + en + m.group(2), html)
        html = pat_a.sub(lambda m: en.replace('"', '&quot;'), html)
    if missing: print(f'[{fname}] NEGĂSITE:', *missing, sep='\n   ')
    return html
def hreflang(rel):  # rel = cale RO relativă la rădăcina site-ului
    ro = BASE + ('' if rel == 'index.html' else rel); en = BASE + 'en/' + ('' if rel == 'index.html' else rel)
    return (f'<link rel="alternate" hreflang="ro" href="{ro}">\n<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{ro}">\n')
def add_hreflang(html, rel):
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n', '', html)
    return html.replace('<link rel="icon"', hreflang(rel) + '<link rel="icon"', 1)
def to_en(rel, pairs, post=()):
    src = os.path.join(SITE, rel); html = open(src, encoding='utf-8').read()
    # RO: doar hreflang
    ro_html = add_hreflang(html, rel)
    if ro_html != html: open(src, 'w', encoding='utf-8', newline='').write(ro_html)
    h = tr_text(ro_html, pairs, rel)
    h = h.replace('<html lang="ro">', '<html lang="en">', 1)
    depth_pfx = '../' * (rel.count('/') + 1)  # din en/<rel> spre rădăcina site-ului
    # fișiere comune (assets, imagini spectacole) — există o singură dată, în rădăcină
    sub_root = '../' * rel.count('/')
    def fix(m):
        attr, val = m.group(1), m.group(2)
        v = val
        if rel.count('/') == 0:
            if v.startswith('assets/') or re.match(r'spectacole/\d{4}_', v): v = '../' + v
        else:
            if v.startswith('../assets/'): v = '../' + v
            elif re.match(r'\d{4}_', v): v = '../../spectacole/' + v
        return f'{attr}="{v}"'
    h = re.sub(r'\b(src|href|data-img|data-gallery-folder)="([^"]*)"', fix, h)
    canon = BASE + 'en/' + ('' if rel == 'index.html' else rel)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canon}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canon}">', h)
    if 'og:locale' not in h:
        h = h.replace('<meta property="og:site_name"', '<meta property="og:locale" content="en_GB">\n<meta property="og:site_name"', 1)
    for a, b in post: h = h.replace(a, b)
    out = os.path.join(SITE, 'en', rel); os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8', newline='').write(h)
    return out
if __name__ == '__main__':
    for mod in sys.argv[1:]:
        m = importlib.import_module(mod); print('->', to_en(m.REL, m.PAIRS, getattr(m, 'POST', ())))
