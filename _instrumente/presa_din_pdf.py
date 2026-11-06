#!/usr/bin/env python3
"""
Generează pagina „MICROBIS în presă” (presa.html) din dosarul de presă PDF
al Casei de Cultură a Studenților Sibiu
(https://casastudentilorsibiu.ro/noutati/ccss-in-presa/ → butonul de export PDF).

Utilizare (din folderul _instrumente, sau de oriunde):

    python3 presa_din_pdf.py dosar-de-presa.pdf

Ce face, în ordine:
  1. citește toate fișele din PDF (titlu, publicație, dată, autor, subiect, rezumat, link, imagine);
  2. păstrează doar fișele care conțin cel puțin unul dintre cuvintele-cheie de mai jos;
  3. elimină dublurile: același titlu + aceeași publicație + aceeași zi;
  4. salvează imaginile în assets/img/presa/;
  5. scrie presa.html și en/presa.html (înlocuiesc complet paginile vechi) și, în assets/css/presa.css,
     înălțimile barelor graficului pe ani (între marcajele GENERAT).
     Versiunea engleză ia titlurile și rezumatele traduse din presa_en.json (cheia = linkul articolului);
     linkurile rămân către articolele originale, în română. Un articol nou fără traducere oprește scriptul.

Stilurile sunt în assets/css/presa.css. Acest script NU trebuie urcat pe serverul web.
Necesită:  pip install pdfplumber
"""

import collections
import hashlib
import html
import re
import sys
import unicodedata
from pathlib import Path

import pdfplumber

# --------------------------------------------------------------------------
# SETĂRI — aici se schimbă ce intră în pagină
# --------------------------------------------------------------------------

# O fișă intră în pagină dacă în titlu, rezumat sau adresa articolului apare
# cel puțin unul dintre aceste tipare (căutare fără diacritice, fără diferență
# mare/mic). „Sibiu Dans Festival” e numele mai vechi al festivalului.
CUVINTE_CHEIE = re.compile(
    r"microbis"
    r"|hugo[\s\-]*wolff"
    r"|festivaluri\w*\s+(?:\w+\s+){0,3}de\s+dans"
    r"|festivalul\s+(?:\w+\s+){0,3}de\s+dans"
    r"|festival\w*\s+(?:\w+\s+){0,3}dans"
    r"|dans\w*\s+festival"
)

# Dosarul mai etichetează fișele cu „Subiect: …”. Dacă o fișă nu are cuvântul-cheie
# în text, dar are una dintre aceste etichete, intră totuși (de ex. articole vechi
# despre „Sibiu Dancing Days”).
SUBIECTE_ACCEPTATE = re.compile(r"microbis|hugo[\s\-]*wolff|festivalul\s+studentesc\s+de\s+dans")

SITE = Path(__file__).resolve().parent.parent  # rădăcina site-ului
FOLDER_IMG = SITE / "assets" / "img" / "presa"
CALE_IMG = "assets/img/presa"  # cum apar imaginile în HTML
CSS = SITE / "assets" / "css" / "presa.css"
CSS_START = "/* ===== GENERAT de presa_din_pdf.py — nu edita între marcaje ===== */"
CSS_END = "/* ===== SFÂRȘIT GENERAT ===== */"

# --------------------------------------------------------------------------
# 1. CITIREA PDF-ULUI
# --------------------------------------------------------------------------

# Dosarul are 3 coloane de fișe pe pagină; poziții în puncte PDF.
COLOANE = [34, 214, 395]
LATIME = 172
SUS_FISA = 117  # cât de sus față de linia cu data începe imaginea fișei

DATA = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def citeste_fise(pdf_path):
    """Returnează toate fișele din PDF, în ordinea în care apar în dosar."""
    fise = []
    with pdfplumber.open(pdf_path) as pdf:
        for nr_pag, pagina in enumerate(pdf.pages, start=1):
            cuvinte = pagina.extract_words(extra_attrs=["size", "fontname"])
            cuvinte = [w for w in cuvinte if w["top"] < 800]  # fără subsolul paginii
            fise_pagina = []

            for nr_col, x in enumerate(COLOANE):
                coloana = [w for w in cuvinte if x - 3 <= w["x0"] < x + LATIME]
                date = sorted(
                    (w for w in coloana if DATA.match(w["text"]) and abs(w["size"] - 6.6) < 0.3),
                    key=lambda w: w["top"],
                )
                for i, d in enumerate(date):
                    sus = d["top"] - SUS_FISA
                    jos = date[i + 1]["top"] - SUS_FISA if i + 1 < len(date) else 800
                    fisa = fisa_din_cuvinte(pagina, coloana, x, sus, jos, d["top"])
                    fisa["pozitie"] = (nr_pag, round(d["top"]) // 30, nr_col)
                    fise_pagina.append(fisa)

            fise.extend(fise_pagina)

    fise.sort(key=lambda f: f["pozitie"])  # ordinea de citire: pagină, rând, coloană
    return fise


def fisa_din_cuvinte(pagina, coloana, x, sus, jos, top_data):
    """Construiește o fișă din cuvintele aflate între `sus` și `jos` în coloana ei."""
    regiune = [w for w in coloana if sus <= w["top"] < jos - 1]
    linii = collections.defaultdict(list)
    for w in regiune:
        linii[round(w["top"])].append(w)

    rânduri = []
    for top in sorted(linii):
        l = sorted(linii[top], key=lambda w: w["x0"])
        rânduri.append(
            {
                "top": top,
                "size": round(l[0]["size"], 1),
                "text": " ".join(w["text"] for w in l),
            }
        )

    # Mărimile fonturilor din dosar: 8.6 = titlu, 7.1 = rezumat, 6.6 = dată/autor/subiect,
    # 6.4 = „Citește articolul în …”, 5.4 = eticheta publicației de pe imagine,
    # 10.0 + 6.0 = numele publicației și subiectul, la fișele fără imagine.
    deasupra = [r for r in rânduri if r["top"] < top_data - 1]
    corp = [r for r in rânduri if r["top"] >= top_data - 1]
    prima_linie_titlu = min([r["top"] for r in corp if r["size"] == 8.6] or [9999])

    def text(rânduri_, size):
        return " ".join(r["text"] for r in rânduri_ if r["size"] == size)

    meta = " ".join(r["text"] for r in corp if r["size"] == 6.6 and r["top"] < prima_linie_titlu)
    subiect = " ".join(r["text"] for r in corp if r["size"] == 6.6 and r["top"] > prima_linie_titlu)
    cta = text(corp, 6.4)
    publicatie = re.sub(r"^CITE.TE ARTICOLUL .N\s+|\s*»\s*$", "", cta).strip()

    zi, luna, an = meta.split(" ")[0].split(".")
    autor = meta.split("·", 1)[1].strip() if "·" in meta else ""

    # Imaginea fișei (dacă există) și linkul articolului.
    imagine = None
    for im in pagina.images:
        if x - 3 <= im["x0"] < x + LATIME and sus - 4 <= im["top"] <= sus + 8:
            date_img = im["stream"].get_rawdata()
            if date_img[:2] == b"\xff\xd8":  # e JPEG
                imagine = date_img
    link = next(
        h["uri"]
        for h in pagina.hyperlinks
        if x - 3 <= h["x0"] < x + LATIME and sus <= h["top"] < jos - 1
    )

    # La fișele fără imagine, dosarul scrie numele publicației mare, pe fundal închis.
    nume_mare = " ".join(r["text"] for r in deasupra if r["size"] == 10.0)
    eticheta_mica = " ".join(r["text"] for r in deasupra if r["size"] == 6.0)

    return {
        "iso": f"{an}-{luna}-{zi}",
        "data": f"{zi}.{luna}.{an}",
        "autor": autor,
        "titlu": text(corp, 8.6),
        "subiect": subiect.replace("Subiect:", "").strip(),
        "rezumat": text(corp, 7.1),
        "publicatie": publicatie,  # MAJUSCULE, ca în dosar
        "nume_mare": nume_mare,  # doar la fișele fără imagine
        "eticheta_mica": eticheta_mica,  # doar la fișele fără imagine
        "link": link,
        "imagine": imagine,
    }


# --------------------------------------------------------------------------
# 2. SELECȚIA ȘI DUBLURILE
# --------------------------------------------------------------------------


def fara_diacritice(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def cheie(s):
    return re.sub(r"[^a-z0-9]+", "", fara_diacritice(s))


def alege(fise):
    pastrate = []
    for f in fise:
        in_text = fara_diacritice(" ".join([f["titlu"], f["rezumat"], f["link"]]))
        in_subiect = fara_diacritice(f["subiect"])
        if CUVINTE_CHEIE.search(in_text) or SUBIECTE_ACCEPTATE.search(in_subiect):
            pastrate.append(f)

    # dubluri = același titlu + aceeași publicație + aceeași zi
    vazute, unice, dubluri = set(), [], []
    for f in pastrate:
        k = (cheie(f["titlu"]), cheie(f["publicatie"]), f["iso"])
        if k in vazute:
            dubluri.append(f)
        else:
            vazute.add(k)
            unice.append(f)

    unice.sort(key=lambda f: f["iso"], reverse=True)  # cele mai noi primele; la zi egală, ordinea din dosar
    return unice, dubluri


# --------------------------------------------------------------------------
# 3. IMAGINILE
# --------------------------------------------------------------------------


def salveaza_imagini(fise):
    """Scrie imaginile în assets/img/presa/ și adaugă fiecărei fișe `cale_img`."""
    FOLDER_IMG.mkdir(parents=True, exist_ok=True)
    for vechi in FOLDER_IMG.glob("*.jpg"):  # folderul e gestionat de acest script
        vechi.unlink()

    dupa_continut = {}  # aceeași imagine folosită de mai multe fișe → un singur fișier
    for f in fise:
        if not f["imagine"]:
            f["cale_img"] = None
            continue
        amprenta = hashlib.md5(f["imagine"]).hexdigest()
        if amprenta not in dupa_continut:
            nume = f"{f['iso']}_{cheie(f['publicatie'])}_{amprenta[:6]}.jpg"
            (FOLDER_IMG / nume).write_bytes(f["imagine"])
            dupa_continut[amprenta] = nume
        f["cale_img"] = f"{CALE_IMG}/{dupa_continut[amprenta]}"
    return len(dupa_continut)


# --------------------------------------------------------------------------
# 4. PAGINA HTML
# --------------------------------------------------------------------------

# Nume „frumoase” ale publicațiilor (cele din dosar sunt scrise cu majuscule).
MICI = {"de", "din", "în", "la", "și", "a", "cu", "pe"}


def nume_publicatie(f, nume_cunoscute):
    if f["publicatie"] in nume_cunoscute:
        return nume_cunoscute[f["publicatie"]].split(" · ")[0]  # „AGERPRES · Comunicate” → „AGERPRES”
    cuvinte = f["publicatie"].lower().split()
    return " ".join(
        c.upper() if c == "fm" else c if (i and c in MICI) else c.capitalize() for i, c in enumerate(cuvinte)
    )


# --------------------------------------------------------------------------
# 5. LIMBILE (RO = presa.html, EN = en/presa.html)
# --------------------------------------------------------------------------

# Traducerile cardurilor (titlu + rezumat) stau în presa_en.json, cu cheia = linkul articolului.
# Linkul rămâne mereu cel către articolul original, în română.
JSON_EN = Path(__file__).resolve().parent / "presa_en.json"

LuniEN = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]

SUBIECTE_EN = {
    "Festivalul de Dans „Hugo Wolff”": "Hugo Wolff Dance Festival",
    "Microbis · Hugo Wolff": "Microbis · Hugo Wolff",
    "Festivalul studențesc de dans": "Student Dance Festival",
    "Premii și distincții": "Awards and distinctions",
}

LIMBI = {
    "ro": {
        "fisier": SITE / "presa.html",
        "pfx": "",
        "pfx_site": "",
        "titlu_pagina": "MICROBIS în presă — Microbis",
        "descriere": "Apariții în presă despre Compania de Teatru-Dans Microbis și Festivalul de Dans „Hugo Wolff”, {an_min}–{an_max}: {numar} articole, cu link către sursa originală.",
        "cuvinte_cheie": "Microbis presă, Microbis în presă, Festivalul de Dans Hugo Wolff, teatru dans Sibiu",
        "og_descriere": "Ce s-a scris în presă despre Microbis și Festivalul de Dans „Hugo Wolff”.",
        "og_locale": "",
        "eticheta": "Presă",
        "h1": "MICROBIS în presă",
        "lead": "{numar} apariții în presă · {an_min}–{an_max}",
        "grafic_aria": "Apariții în presă pe ani",
        "stare_toate": "{numar} articole. Alege un an din grafic ca să le filtrezi.",
        "stare_an": "Se afișează {numar} din {an}.",
        "reset": "Arată toate",
        "nota": ("Selecție din dosarul de presă al Casei de Cultură a Studenților Sibiu, actualizat la {generat}. "
                 "Imaginile și textele integrale aparțin publicațiilor citate. Fiecare fișă trimite la articolul original."),
        "subiect": "Subiect:",
        "cta": "Citește articolul în {nume} »",
    },
    "en": {
        "fisier": SITE / "en" / "presa.html",
        "pfx": "../",
        "pfx_site": "",
        "titlu_pagina": "MICROBIS in the press — Microbis",
        "descriere": "Press coverage of the Microbis Theatre-Dance Company and the Hugo Wolff Dance Festival, {an_min}–{an_max}: {numar} articles, each linking to the original source.",
        "cuvinte_cheie": "Microbis press, Microbis in the press, Hugo Wolff Dance Festival, theatre dance Sibiu",
        "og_descriere": "What the press has written about Microbis and the Hugo Wolff Dance Festival.",
        "og_locale": '<meta property="og:locale" content="en_GB">\n',
        "eticheta": "Press",
        "h1": "MICROBIS in the press",
        "lead": "{numar} press appearances · {an_min}–{an_max}",
        "grafic_aria": "Press appearances by year",
        "stare_toate": "{numar} articles. Pick a year in the chart to filter them.",
        "stare_an": "Showing {numar} from {an}.",
        "reset": "Show all",
        "nota": ("Selection from the press archive of the Sibiu Student Cultural Centre (CCS Sibiu), updated on {generat}. "
                 "Images and full texts belong to the publications cited. Each card links to the original article, "
                 "which opens in Romanian; the titles and summaries here are translated."),
        "subiect": "Subject:",
        "cta": "Read the article in {nume} »",
    },
}


def numar_articole(n, limba):
    """„1 articol”, „12 articole”, „23 de articole” / „1 article”, „12 articles”."""
    if limba == "en":
        return f"{n} article" + ("" if n == 1 else "s")
    if n == 1:
        return "1 articol"
    return f"{n} {cu_de(n)}articole"


def data_en(iso):
    a, l, z = iso.split("-")
    return f"{int(z)} {LuniEN[int(l) - 1]} {a}"


AUTOR_EN = {  # părțile „Autor: …” care nu sunt nume de persoane
    "nesemnat": "unsigned",
    "autor": "not stated",
    "comunicat de presa": "Press release",
    "eveniment": "Event",
    "publicitate": "Advertising",
    "redactie stiri": "News desk",
    "redactia": "Editorial staff",
}


def autor_en(autor):
    """„Autor: Redacția Alba24.ro · Comunicat de presă” → „Author: Alba24.ro editorial staff · Press release”."""
    parti = []
    for parte in autor.replace("Autor:", "").split("·"):
        parte = parte.strip()
        cheie_parte = fara_diacritice(parte).lower()
        if cheie_parte in AUTOR_EN:
            parte = AUTOR_EN[cheie_parte]
        elif re.match(r"redacti[ae]\s+\S", cheie_parte):
            parte = re.sub(r"^\S+\s+", "", parte) + " editorial staff"
        elif cheie_parte.startswith("comunicat "):
            parte = parte.split(" ", 1)[1] + " press release"
        if parte and parte not in parti:
            parti.append(parte)
    if any(p.endswith(" press release") for p in parti):
        parti = [p for p in parti if p != "Press release"]  # „CCS Sibiu press release · Press release” → o singură dată
    return "Author: " + (" · ".join(parti) if parti else "not stated")


def traduceri_en(fise):
    """Încarcă presa_en.json și verifică că fiecare fișă are traducere (altfel oprește scriptul)."""
    import json

    tr = json.loads(JSON_EN.read_text(encoding="utf-8"))
    lipsa = [f["link"] for f in fise if f["link"] not in tr]
    if lipsa:
        sys.exit(f"Lipsesc traduceri în {JSON_EN.name} pentru {len(lipsa)} articole, de ex.:\n  " + "\n  ".join(lipsa[:5]))
    return tr


def card_html(f, nume, limba, tr):
    e = html.escape
    t = LIMBI[limba]
    atribute_link = f'href="{e(f["link"])}" target="_blank" rel="noopener noreferrer"'
    pfx = t["pfx"]

    if limba == "en":
        titlu, rezumat = tr[f["link"]]["titlu"], tr[f["link"]]["rezumat"]
        data = data_en(f["iso"])
        autor = autor_en(f["autor"])
        subiect = SUBIECTE_EN.get(f["subiect"], f["subiect"])
        eticheta_mica = SUBIECTE_EN_MARI.get(f["eticheta_mica"], f["eticheta_mica"])
    else:
        titlu, rezumat = f["titlu"], f["rezumat"]
        data, autor, subiect, eticheta_mica = f["data"], f["autor"], f["subiect"], f["eticheta_mica"]

    if f["cale_img"]:
        media = f"""        <a class="presa-card__media" {atribute_link} tabindex="-1" aria-hidden="true">
          <img src="{pfx}{f['cale_img']}" alt="" width="400" height="250" loading="lazy">
          <span class="presa-card__badge">{e(f['publicatie'])}</span>
        </a>"""
    else:
        media = f"""        <a class="presa-card__media presa-card__media--ph" {atribute_link} tabindex="-1" aria-hidden="true">
          <span class="presa-card__ph-name">{e(f['nume_mare'] or nume)}</span>
          <span class="presa-card__ph-tag">{e(eticheta_mica)}</span>
        </a>"""

    return f"""      <li class="presa-card" data-an="{f['iso'][:4]}">
{media}
        <div class="presa-card__body">
          <p class="presa-card__meta"><time datetime="{f['iso']}">{data}</time> · {e(autor)}</p>
          <h2 class="presa-card__title">{e(titlu)}</h2>
          <p class="presa-card__subject"><strong>{t['subiect']}</strong> <span>{e(subiect)}</span></p>
          <p class="presa-card__text">{e(rezumat)}</p>
          <a class="presa-card__cta" {atribute_link}>{e(t['cta'].format(nume=nume))}</a>
        </div>
      </li>"""


SUBIECTE_EN_MARI = {
    "FESTIVALUL DE DANS „HUGO WOLFF”": "HUGO WOLFF DANCE FESTIVAL",
    "MICROBIS · HUGO WOLFF": "MICROBIS · HUGO WOLFF",
    "FESTIVALUL STUDENȚESC DE DANS": "STUDENT DANCE FESTIVAL",
    "PREMII ȘI DISTINCȚII": "AWARDS AND DISTINCTIONS",
}


PAGINA_HTML = """<!doctype html>
<html lang="{limba}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t[titlu_pagina]}</title>
<meta name="description" content="{descriere}">
<meta name="keywords" content="{t[cuvinte_cheie]}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
{t[og_locale]}<meta property="og:site_name" content="Microbis">
<meta property="og:title" content="{t[titlu_pagina]}">
<meta property="og:description" content="{t[og_descriere]}">
<meta property="og:image" content="https://microbis.ro/assets/img/og-cover.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" hreflang="ro" href="https://microbis.ro/presa.html">
<link rel="alternate" hreflang="en" href="https://microbis.ro/en/presa.html">
<link rel="alternate" hreflang="x-default" href="https://microbis.ro/presa.html">
<link rel="icon" href="{t[pfx]}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;0,6..96,600;0,6..96,700;0,6..96,800;1,6..96,500;1,6..96,600;1,6..96,700&family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{t[pfx]}assets/css/style.css">
<link rel="stylesheet" href="{t[pfx]}assets/css/presa.css">
<script src="{t[pfx]}assets/js/partials.js"></script>
</head>
<body>

<script>document.write(microbisHeader('presa', true));</script>

<main>
  <section class="theme-ink page-header presa-head">
    <div class="container">
      <p class="eyebrow eyebrow--red">{t[eticheta]}</p>
      <h1 class="h-lg mt-18">{t[h1]}</h1>
      <p class="presa-lead">{lead}</p>
    </div>
  </section>

  <section class="section theme-ink presa">
    <div class="container">

      <div class="presa-chart" role="group" aria-label="{t[grafic_aria]}">
        <div class="presa-chart__scroll">
          <div class="presa-chart__bars">
{grafic}
          </div>
        </div>
      </div>

      <div class="presa-filter">
        <p class="presa-filter__text" role="status" aria-live="polite" data-all="{stare_toate}">{stare_toate}</p>
        <button type="button" class="presa-filter__reset" hidden>{t[reset]}</button>
      </div>

      <ul class="presa-grid">
{carduri}
      </ul>

      <p class="presa-note">
        {nota}
      </p>

    </div>
  </section>
</main>

<script>document.write(microbisFooter(true));</script>

<script src="{t[pfx]}assets/js/main.js"></script>
<script src="{t[pfx]}assets/js/presa.js"></script>
</body>
</html>
"""


def cu_de(n):
    """„de ” pentru numeralele românești de la 20 în sus (23 de articole), altfel nimic (12 articole)."""
    return "de " if n % 100 >= 20 or n % 100 == 0 else ""


def numara_pe_ani(fise):
    """Câte articole sunt în fiecare an, de la cel mai vechi la cel mai nou (ani fără articole = 0)."""
    ani = [int(f["iso"][:4]) for f in fise]
    return collections.OrderedDict((an, ani.count(an)) for an in range(min(ani), max(ani) + 1))


def grafic_html(pe_ani, limba):
    """Barele graficului: câte un buton pe an. Înălțimea vine din clasa .presa-h-N (din presa.css)."""
    t = LIMBI[limba]
    bare = []
    for an, n in pe_ani.items():
        dezactivat = " disabled" if n == 0 else ""
        eticheta = f"{an}: {numar_articole(n, limba)}"
        mesaj = t["stare_an"].format(numar=numar_articole(n, limba), an=an)
        bare.append(
            f"""            <button type="button" class="presa-bar" data-an="{an}" data-msg="{mesaj}" aria-pressed="false"{dezactivat} aria-label="{eticheta}">
              <span class="presa-bar__count">{n}</span>
              <span class="presa-bar__col"><span class="presa-bar__fill presa-h-{n}"></span></span>
              <span class="presa-bar__year">{an}</span>
            </button>"""
        )
    return "\n".join(bare)


def scrie_css_inaltimi(pe_ani):
    """Scrie în presa.css clasele .presa-h-0 … .presa-h-N (înălțimea barelor, în % din cea mai înaltă)."""
    maxim = max(pe_ani.values())
    reguli = "\n".join(f".presa-h-{n} {{ height: {n * 100 / maxim:.1f}%; }}" for n in range(maxim + 1))
    bloc = f"{CSS_START}\n{reguli}\n{CSS_END}"
    css = CSS.read_text(encoding="utf-8")
    if CSS_START in css:
        css = re.sub(re.escape(CSS_START) + r".*?" + re.escape(CSS_END), lambda m: bloc, css, flags=re.S)
    else:
        css = css.rstrip() + "\n\n" + bloc + "\n"
    CSS.write_text(css, encoding="utf-8")


def scrie_pagina(fise, nume_cunoscute, generat, limba):
    t = LIMBI[limba]
    tr = traduceri_en(fise) if limba == "en" else None
    carduri = "\n\n".join(card_html(f, nume_publicatie(f, nume_cunoscute), limba, tr) for f in fise)
    pe_ani = numara_pe_ani(fise)
    if limba == "ro":
        scrie_css_inaltimi(pe_ani)  # aceeași înălțime în ambele limbi
    n = len(fise)
    cifre = {"an_min": min(pe_ani), "an_max": max(pe_ani), "generat": generat}
    numar = f"{n} {cu_de(n)}".strip() if limba == "ro" else str(n)  # „142 de” / „142”
    lead = t["lead"].format(numar=numar, **cifre)
    stare = t["stare_toate"].format(numar=numar)
    t["fisier"].parent.mkdir(parents=True, exist_ok=True)
    t["fisier"].write_text(
        PAGINA_HTML.format(
            limba=limba,
            t=t,
            descriere=t["descriere"].format(numar=numar, **cifre),
            canonical="https://microbis.ro/presa.html" if limba == "ro" else "https://microbis.ro/en/presa.html",
            lead=lead,
            grafic=grafic_html(pe_ani, limba),
            stare_toate=stare,
            carduri=carduri,
            nota=t["nota"].format(generat=generat),
        ),
        encoding="utf-8",
    )
    return t["fisier"]


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------


def main():
    if len(sys.argv) != 2:
        sys.exit("Utilizare: python3 presa_din_pdf.py dosar-de-presa.pdf")
    pdf_path = Path(sys.argv[1])

    toate = citeste_fise(pdf_path)
    with pdfplumber.open(pdf_path) as pdf:
        m = re.search(r"Generat la (\d{2}\.\d{2}\.\d{4})", pdf.pages[0].extract_text() or "")
    generat = m.group(1) if m else "data exportului"

    # nume corecte ale publicațiilor, luate de pe fișele fără imagine („Mesagerul de Sibiu” etc.)
    nume_cunoscute = {f["publicatie"]: f["nume_mare"] for f in toate if f["nume_mare"]}

    alese, dubluri = alege(toate)
    nr_img = salveaza_imagini(alese)
    pagini = [scrie_pagina(alese, nume_cunoscute, generat, limba) for limba in ("ro", "en")]

    print(f"Fișe în dosar:            {len(toate)}")
    print(f"Cu cuvintele-cheie:       {len(alese) + len(dubluri)}")
    print(f"Dubluri eliminate:        {len(dubluri)}")
    for d in dubluri:
        print(f"   - {d['data']} · {d['publicatie']} · {d['titlu'][:70]}")
    print(f"Articole în pagină:       {len(alese)}  ({sum(1 for f in alese if f['cale_img'])} cu imagine, "
          f"{sum(1 for f in alese if not f['cale_img'])} fără)")
    print(f"Imagini salvate:          {nr_img}  → {FOLDER_IMG}")
    for pagina in pagini:
        print(f"Pagina scrisă:            {pagina}")


if __name__ == "__main__":
    main()
