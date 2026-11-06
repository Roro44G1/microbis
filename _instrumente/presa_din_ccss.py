#!/usr/bin/env python3
"""
Actualizează pagina „MICROBIS în presă” (presa.html + en/presa.html) direct din datele
dosarului de presă CCS Sibiu (https://casastudentilorsibiu.ro/noutati/ccss-in-presa/),
fără export PDF. Folosește aceleași reguli de selecție și același HTML ca presa_din_pdf.py.

Sursa de adevăr a paginii e  _instrumente/presa_fise.json  (toate fișele din pagină).
Fișele existente NU se rescriu: se adaugă doar cele noi.

Comenzi (din orice folder):

  python3 presa_din_ccss.py init
        O singură dată: citește fișele din presa.html actual și scrie presa_fise.json.
  python3 presa_din_ccss.py noi [--sursa pagina.html --sursa rest.json]
        Descarcă datele CCSS (JSON-ul pr-data din pagină + articolele din categoria 114)
        sau le ia din fișiere salvate, aplică filtrul de cuvinte-cheie
        și scrie în presa_noi.json fișele care NU sunt încă în pagină. Afișează lista.
  python3 presa_din_ccss.py aplica
        Adaugă fișele din presa_noi.json în pagină. Fiecare fișă nouă trebuie să aibă
        traducerea în presa_en.json (titlu, rezumat; opțional subiect). Descarcă imaginile
        (dacă rețeaua permite) și regenerează presa.html și en/presa.html.
  python3 presa_din_ccss.py imagini
        Descarcă imaginile care lipsesc (fișe cu img_url, dar fără imagine locală) și
        regenerează paginile. Rulat automat de GitHub Actions după fiecare push.
  python3 presa_din_ccss.py pagini
        Doar regenerează paginile din presa_fise.json.

Necesită Pillow pentru imagini (pip install pillow). Nu se urcă pe serverul web.
"""

import datetime
import hashlib
import html
import io
import json
import re
import sys
import time
import types
import urllib.request
from pathlib import Path

AICI = Path(__file__).resolve().parent
sys.path.insert(0, str(AICI))
try:
    import pdfplumber  # noqa: F401  (presa_din_pdf îl importă; aici nu e nevoie de el)
except ImportError:
    sys.modules["pdfplumber"] = types.ModuleType("pdfplumber")
import presa_din_pdf as P  # noqa: E402

FISE = AICI / "presa_fise.json"
NOI = AICI / "presa_noi.json"
URL_CCSS = "https://casastudentilorsibiu.ro/noutati/ccss-in-presa/"
# Subiectele (din dosarul CCSS) care intră în pagina Microbis, ca la exportul PDF filtrat.
# O fișă cu cuvânt-cheie, dar cu alt subiect (de ex. „Finanțări pentru proiecte”), NU se adaugă:
# apare doar în raport, la „de verificat”.
SUBIECTE_PAGINA = {
    "Festivalul de Dans „Hugo Wolff”",
    "Microbis · Hugo Wolff",
    "Festivalul studențesc de dans",
    "Premii și distincții",
}
TIPURI = {"comunicat": "Comunicat de presă", "eveniment": "Eveniment"}
UA = "Mozilla/5.0 (compatible; microbis-presa/1.0)"


# --------------------------------------------------------------------------
# utilitare
# --------------------------------------------------------------------------

def url_norm(u):
    u = u.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^(www|m|amp)\.", "", u).split("#")[0]
    baza, _, q = u.partition("?")
    q = "&".join(sorted(k for k in q.split("&") if k and not re.match(r"(utm_|fbclid=|gclid=)", k)))
    baza = re.sub(r"/amp/?$", "", baza).rstrip("/")
    return baza + ("?" + q if q else "")


def citeste(cale, implicit):
    return json.loads(cale.read_text(encoding="utf-8")) if cale.exists() else implicit


def scrie(cale, date):
    cale.write_text(json.dumps(date, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def azi():
    return datetime.date.today().strftime("%d.%m.%Y")


# --------------------------------------------------------------------------
# init: fișele din presa.html actual
# --------------------------------------------------------------------------

CARD = re.compile(r'<li class="presa-card" data-an="\d{4}">(.*?)</li>', re.S)


def init():
    pagina = (P.SITE / "presa.html").read_text(encoding="utf-8")
    u = html.unescape
    fise = []
    for bloc in CARD.findall(pagina):
        g = lambda rx: re.search(rx, bloc, re.S)  # noqa: E731
        iso = g(r'<time datetime="([\d-]+)">')[1]
        meta = g(r'</time> · (.*?)</p>')[1]
        img = g(r'<img src="([^"]+)"')
        badge = g(r'presa-card__badge">(.*?)</span>')
        ph_nume = g(r'presa-card__ph-name">(.*?)</span>')
        ph_tag = g(r'presa-card__ph-tag">(.*?)</span>')
        cta = g(r'presa-card__cta" href="([^"]+)"[^>]*>(.*?)</a>')
        nume = re.sub(r"^Citește articolul în\s+|\s*»$", "", u(cta[2])).strip()
        a, l, z = iso.split("-")
        fise.append({
            "iso": iso, "data": f"{z}.{l}.{a}", "autor": u(meta),
            "titlu": u(g(r'presa-card__title">(.*?)</h2>')[1]),
            "subiect": u(g(r'presa-card__subject"><strong>.*?</strong> <span>(.*?)</span>')[1]),
            "rezumat": u(g(r'presa-card__text">(.*?)</p>')[1]),
            "publicatie": u(badge[1]) if badge else nume.upper(),
            "nume": nume,
            "nume_mare": u(ph_nume[1]) if ph_nume else "",
            "eticheta_mica": u(ph_tag[1]) if ph_tag else "",
            "link": u(cta[1]),
            "cale_img": img[1] if img else None,
            "img_url": "",
        })
    m = re.search(r"actualizat la (\d{2}\.\d{2}\.\d{4})", pagina)
    scrie(FISE, {"generat": m[1] if m else azi(), "fise": fise})
    print(f"presa_fise.json: {len(fise)} fișe citite din presa.html")


# --------------------------------------------------------------------------
# noi: ce e în dosarul CCSS și nu e încă în pagină
# --------------------------------------------------------------------------

URL_REST = ("https://casastudentilorsibiu.ro/wp-json/wp/v2/posts?categories=114&per_page=100"
            "&_fields=id,title,content&page={}")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8")


def _din_pagina(text):
    """Fișele din JSON-ul pr-data al paginii „CCSS în presă”."""
    m = re.search(r'<script type="application/json" class="pr-data">(.*?)</script>', text, re.S)
    if not m:
        sys.exit("Nu găsesc datele pr-data (posibil pagina anti-bot „One moment, please…”). Reîncearcă peste 1–2 minute.")
    return json.loads(m.group(1))


def _din_rest(posts):
    """Fișele din articolele categoriei 114 (adăugate de agentul de presă, încărcate pe pagină prin JS)."""
    u = html.unescape
    out = []
    for post in posts:
        c = post["content"]["rendered"]
        m = re.search(r'<div class="ccss-presa-fisa"([^>]*)>', c)
        if not m:
            continue
        at = {k: u(v) for k, v in re.findall(r'data-([a-z-]+)="([^"]*)"', m.group(1))}
        rez = re.search(r"<p>(.*?)</p>", c, re.S)
        out.append({
            "d": at.get("date", ""), "p": at.get("pub", ""), "a": at.get("author", ""),
            "t": u(post["title"]["rendered"]), "u": at.get("url", ""), "i": at.get("img", ""),
            "y": at.get("type", "articol"), "tp": at.get("topic-ro", ""),
            "s": u(re.sub(r"<[^>]+>", "", rez.group(1))).strip() if rez else "",
            "s_en": at.get("subject-en", ""), "tp_en": at.get("topic-en", ""),
        })
    return out


def date_ccss(surse=()):
    """Toate fișele dosarului CCSS: JSON-ul pr-data din pagină + articolele categoriei 114.
    `surse` = fișiere locale (pagina HTML salvată și/sau JSON-ul REST), dacă nu se descarcă."""
    fise, rest = [], []
    if surse:
        for cale in surse:
            text = Path(cale).read_text(encoding="utf-8")
            if text.lstrip().startswith("["):
                rest += json.loads(text)
            else:
                fise += _din_pagina(text)
    else:
        fise = _din_pagina(_get(URL_CCSS))
        pag = 1
        while True:
            time.sleep(20)  # site-ul CCSS răspunde cu anti-bot la cereri dese
            lot = json.loads(_get(URL_REST.format(pag)))
            rest += lot
            if len(lot) < 100:
                break
            pag += 1
    fise += _din_rest(rest)
    unice, vazute = [], set()
    for x in fise:
        k = url_norm(x["u"])
        if x.get("u") and x.get("d") and k not in vazute:
            vazute.add(k)
            unice.append(x)
    return unice


def fisa_din_ccss(x):
    """Transformă o fișă din JSON-ul CCSS (d,p,a,t,u,i,y,tp,s) în formatul paginii."""
    pub_scurt = x["p"].split(" · ")[0].split(" (")[0]
    autor = "Autor: " + (x.get("a") or "nesemnat")
    if x.get("y") in TIPURI:
        autor += " · " + TIPURI[x["y"]]
    a, l, z = x["d"].split("-")
    return {
        "iso": x["d"], "data": f"{z}.{l}.{a}", "autor": autor,
        "titlu": x["t"], "subiect": x.get("tp", ""), "rezumat": x.get("s", ""),
        "publicatie": pub_scurt.upper(), "nume": pub_scurt,
        "nume_mare": x["p"], "eticheta_mica": (x.get("tp") or "").upper(),
        "link": x["u"], "cale_img": None, "img_url": x.get("i") or "",
        "rezumat_en_ccss": x.get("s_en", ""), "subiect_en_ccss": x.get("tp_en", ""),
    }


def noi(surse=()):
    stare = citeste(FISE, None)
    if stare is None:
        sys.exit("Lipsește presa_fise.json: rulează întâi  python3 presa_din_ccss.py init")
    existente = {url_norm(f["link"]) for f in stare["fise"]}
    chei = {(P.cheie(f["titlu"]), P.cheie(f["publicatie"]), f["iso"]) for f in stare["fise"]}
    candidate = [fisa_din_ccss(x) for x in date_ccss(surse)]
    alese, _ = P.alege(candidate)
    gasite = [f for f in alese
              if url_norm(f["link"]) not in existente
              and (P.cheie(f["titlu"]), P.cheie(f["publicatie"]), f["iso"]) not in chei]
    de_verificat = [f for f in gasite if f["subiect"] not in SUBIECTE_PAGINA]
    gasite = [f for f in gasite if f["subiect"] in SUBIECTE_PAGINA]
    scrie(NOI, gasite)
    print(f"Fișe în dosarul CCSS: {len(candidate)} · cu cuvintele-cheie: {len(alese)} · NOI: {len(gasite)}"
          f" · de verificat (alt subiect): {len(de_verificat)}")
    for f in gasite:
        print(f"  + {f['iso']} · {f['nume']} · {f['titlu'][:80]}\n    {f['link']}")
    for f in de_verificat:
        print(f"  ? {f['iso']} · {f['nume']} · [{f['subiect']}] {f['titlu'][:70]}")
    return gasite


# --------------------------------------------------------------------------
# imagini
# --------------------------------------------------------------------------

def descarca_imagine(f):
    """Salvează imaginea fișei (400×250, decupată ca în dosar). Întoarce True dacă a reușit."""
    if not f.get("img_url") or f.get("cale_img"):
        return False
    try:
        from PIL import Image
        req = urllib.request.Request(f["img_url"], headers={"User-Agent": UA})
        brut = urllib.request.urlopen(req, timeout=30).read()
        im = Image.open(io.BytesIO(brut)).convert("RGB")
        r = max(400 / im.width, 250 / im.height)
        im = im.resize((max(400, round(im.width * r)), max(250, round(im.height * r))), Image.LANCZOS)
        st, sus = (im.width - 400) // 2, (im.height - 250) // 2
        im = im.crop((st, sus, st + 400, sus + 250))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
        date = buf.getvalue()
    except Exception as e:  # rețea blocată, imagine lipsă etc. → fișa rămâne cu placeholder
        print(f"  ! imagine nedescărcată ({type(e).__name__}): {f['img_url'][:90]}")
        return False
    nume = f"{f['iso']}_{P.cheie(f['publicatie'])}_{hashlib.md5(date).hexdigest()[:6]}.jpg"
    P.FOLDER_IMG.mkdir(parents=True, exist_ok=True)
    (P.FOLDER_IMG / nume).write_bytes(date)
    f["cale_img"] = f"{P.CALE_IMG}/{nume}"
    return True


# --------------------------------------------------------------------------
# pagini
# --------------------------------------------------------------------------

def pagini(stare):
    tr = json.loads(P.JSON_EN.read_text(encoding="utf-8"))
    for f in stare["fise"]:  # subiecte noi: traducerea vine din presa_en.json („subiect”: …)
        sub_en = tr.get(f["link"], {}).get("subiect")
        if sub_en and f["subiect"] not in P.SUBIECTE_EN:
            P.SUBIECTE_EN[f["subiect"]] = sub_en
            P.SUBIECTE_EN_MARI.setdefault(f["subiect"].upper(), sub_en.upper())
    P.nume_publicatie = lambda f, _nc: f["nume"]
    fise = sorted(stare["fise"], key=lambda f: f["iso"], reverse=True)  # stabil: la zi egală, ordinea existentă
    for limba in ("ro", "en"):
        print("Pagina scrisă:", P.scrie_pagina(fise, {}, stare["generat"], limba))


def aplica():
    stare = citeste(FISE, None)
    noi_ = citeste(NOI, [])
    if not noi_:
        print("Nimic de adăugat (presa_noi.json e gol).")
        return
    tr = json.loads(P.JSON_EN.read_text(encoding="utf-8"))
    lipsa = [f["link"] for f in noi_ if f["link"] not in tr]
    if lipsa:
        sys.exit("Lipsesc traducerile EN în presa_en.json pentru:\n  " + "\n  ".join(lipsa))
    for f in noi_:
        descarca_imagine(f)
    stare["fise"] = noi_ + stare["fise"]
    stare["generat"] = azi()
    scrie(FISE, stare)
    scrie(NOI, [])
    pagini(stare)
    print(f"Adăugate: {len(noi_)} · total în pagină: {len(stare['fise'])}")


def imagini():
    stare = citeste(FISE, None)
    n = sum(descarca_imagine(f) for f in stare["fise"])
    print(f"Imagini descărcate: {n}")
    if n:
        scrie(FISE, stare)
        pagini(stare)


def main():
    a = sys.argv[1:]
    cmd = a[0] if a else ""
    if cmd == "init":
        init()
    elif cmd == "noi":
        noi([a[i + 1] for i, v in enumerate(a) if v == "--sursa"])
    elif cmd == "aplica":
        aplica()
    elif cmd == "imagini":
        imagini()
    elif cmd == "pagini":
        pagini(citeste(FISE, None))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
