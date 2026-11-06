# Instrumente de generare (nu fac parte din site-ul public)

Scripturi Python folosite pentru a genera paginile. Nu e nevoie să fie urcate pe serverul web.

- `gen.py` + `data.py` — paginile RO de spectacol (`spectacole/*.html`) și hub-ul
- `gen_en.py` + `data_en.py` — paginile EN de spectacol (`en/spectacole/*.html`)
- `common.py` — folderele spectacolelor și ID-urile YouTube
- `membri.txt` + `membri_gen.py` — lista de membri (ordonată după nume)
- `en/conv.py` + `en/p_*.py` — traducerea paginilor principale (`en/*.html`) din paginile RO:
  `python3 conv.py p_index p_membri p_calendar p_contact p_auditii p_presa p_conf`
  Dacă se modifică un text pe o pagină RO, trebuie actualizată și perechea RO→EN din `p_*.py`.
  Scriptul semnalează („NEGĂSITE”) orice text care nu mai corespunde.
- `en/check_ro.py` — verifică dacă a rămas text românesc într-o pagină EN

Căile din scripturi presupun site-ul în `~/mnt/microbis` (mediul de lucru Claude). Pentru rulare locală, se ajustează `ROOT`/`SITE` la începutul fișierelor.

## Pagina de presă (`presa.html`, `en/presa.html`) — actualizare din dosarul CCSS

Actualizarea rulează automat săptămânal, ca sarcină programată Claude (o singură sarcină pentru microbis.ro
și ansamblulardealul.ro). Pagina se actualizează direct din dosarul de presă CCSS (https://casastudentilorsibiu.ro/noutati/ccss-in-presa/),
fără export PDF. Scriptul: `presa_din_ccss.py` (folosește regulile și HTML-ul din `presa_din_pdf.py`).

- `presa_fise.json` — sursa de adevăr: toate fișele din pagină. Fișele existente nu se rescriu.
- Intră doar fișele cu subiectele din `SUBIECTE_PAGINA` (Festivalul de Dans „Hugo Wolff”, Microbis · Hugo Wolff,
  Festivalul studențesc de dans, Premii și distincții). Celelalte apar în raport la „de verificat”.

Pași, din rădăcina depozitului:

1. `python3 _instrumente/presa_din_ccss.py noi` — fișele noi → `presa_noi.json` (afișează și lista „de verificat”).
   Sau, cu o singură descărcare pentru ambele site-uri: `descarca /tmp/ccss`, apoi
   `noi --sursa /tmp/ccss/pagina.html --sursa /tmp/ccss/rest.json`.
2. Pentru fiecare fișă nouă se adaugă traducerea în `presa_en.json` (cheia = linkul; `titlu`, `rezumat`, opțional `subiect`).
3. `python3 _instrumente/presa_din_ccss.py aplica` — adaugă fișele și regenerează ambele pagini.
4. Commit + push. Workflow-ul `.github/workflows/presa-imagini.yml` descarcă imaginile lipsă
   (`presa_din_ccss.py imagini`) și face singur un commit cu ele.

Site-ul CCSS răspunde uneori cu pagina anti-bot „One moment, please…”: se reîncearcă după 1–2 minute.
Dacă descărcarea nu merge, datele se pot salva manual și date scriptului cu `--sursa pagina.html --sursa rest.json`.
