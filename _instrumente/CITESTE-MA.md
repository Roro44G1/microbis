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
