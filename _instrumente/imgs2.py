import os, re, sys, json
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None
SP = os.path.expanduser('~/mnt/microbis/spectacole'); A = SP + '/Album/'
R = A + '09 - Ritual si mere rosii/POZE RITUAL SI MERE ROSII/'
ALB = {
 '2014_damnatul': ([A+'02-Damnatul/POZE DAMNATUL/New folder'], None),
 '2016_bonnie_clyde': ([A+'03-Bonie & Clayde/POZE BONNIE SI CLYDE/FotoBonnie&Clay'], None),
 '2017_colectionarul': ([A+'04-Colectionarul/POZE COLECTIONARUL/Mici'], None),
 '2018_fetita_cu_chibrituri': ([A+'05-Fetita cu chibrituri/POZE FETITA CU CHIBRITURI'], None),
 '2019_romeo_si_julieta': ([A+'06-Romeo si Julieta/POZE ROMEO SI JULIETA'], None),
 '2023_tinerete_fara_batranete': ([], A+'07- Tinerete fara Batranete/AFIS TINERETE FARA BATRANETE/afis TINERETE FARA BATRANETE.jpg'),
 '2024_clipe_de_luciditate': ([A+'08 - Clipe de luciditate/POZE CLIPE DE LUCIDITATE'], A+'08 - Clipe de luciditate/AFIS CLIPE DE LUCIDITATE/afis CLIPE DE LUCIDITATE.jpg'),
 '2025_ritual_si_mere_rosii': ([R+'foto-KAMNER/ALESE', R+'foto-KAMNER', R+'foto-vecerdea', R+'POZE AUGUSTINA - MERE ROSII', R+'POZE LILI/25_10_Hugo_Wolff_Festival_Dans-1-001/25_10_Hugo_Wolff_Festival_Dans'],
                               A+'09 - Ritual si mere rosii/AFIS RITUAL SI MERE ROSII/afis MERE ROSII 400x600 copy.jpg'),
}
MAX = 30
def isimg(f): return f.lower().endswith(('.jpg', '.jpeg', '.png'))
def load(p, size=None):
    im = Image.open(p)
    if size: im.draft('RGB', (size*4, size*4))
    return ImageOps.exif_transpose(im).convert('RGB')
def ahash(p):
    im = load(p, 32).convert('L').resize((16, 16), Image.BILINEAR)
    px = list(im.getdata()); m = sum(px)/len(px)
    return sum(1 << i for i, v in enumerate(px) if v > m)
def close(a, b): return bin(a ^ b).count('1') <= 26
def res(p):
    w, h = Image.open(p).size; return w*h
def save(src, dst, edge):
    im = load(src); im.thumbnail((edge, edge), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=82, optimize=True, progressive=True)
def run(folder):
    d = f'{SP}/{folder}'
    gen = re.compile(re.escape(folder) + r'_(\d\d|afis)\.jpg$')
    files = sorted(f for f in os.listdir(d) if isimg(f) and not gen.match(f))
    af = [f for f in files if re.match(r'(afis|poster)', f, re.I)]
    yphotos = [os.path.join(d, f) for f in files if f not in af]
    afsrc = os.path.join(d, af[0]) if af else (ALB.get(folder, ([], None))[1])
    hashes = [ahash(afsrc)] if afsrc else []
    chosen = []
    def add(p):
        h = ahash(p)
        if any(close(h, x) for x in hashes): return False
        hashes.append(h); chosen.append(p); return True
    for p in yphotos:
        if len(chosen) < MAX: add(p)
    srcs = []
    for sd in ALB.get(folder, ([], None))[0]:
        fs = [os.path.join(sd, f) for f in os.listdir(sd) if isimg(f) and not re.match(r'(afis|poster)', f, re.I)]
        stem = lambda p: os.path.splitext(os.path.basename(p))[0].replace('+', '').lower()
        edited = {stem(p) for p in fs if '+' in os.path.basename(p)}
        fs = [p for p in fs if '+' in os.path.basename(p) or stem(p) not in edited]
        fs.sort(key=lambda p: (res(p), '++' in p), reverse=True)
        srcs.append(fs)
    i = 0
    while len(chosen) < MAX and any(srcs):
        q = srcs[i % len(srcs)]
        if q: add(q.pop(0))
        i += 1
        if i > 100000: break
    for old in os.listdir(d):
        if gen.match(old): os.remove(os.path.join(d, old))
    out = []
    for n, p in enumerate(chosen, 1):
        name = f'{folder}_{n:02d}.jpg'; save(p, f'{d}/{name}', 1600); out.append((name, os.path.relpath(p, SP)))
    if afsrc: save(afsrc, f'{d}/{folder}_afis.jpg', 1400)
    json.dump({'photos': out, 'afis': os.path.relpath(afsrc, SP) if afsrc else None}, open(os.path.expanduser(f'~/work/sel_{folder}.json'), 'w'), ensure_ascii=False, indent=1)
    print(folder, 'an:', len([o for o in out if not o[1].startswith('Album')]), 'album:', len([o for o in out if o[1].startswith('Album')]), 'afis:', bool(afsrc), flush=True)
for f in sys.argv[1:]: run(f)
