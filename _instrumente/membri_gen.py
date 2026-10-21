import html, re, os
ALPH = ' -aăâbcdefghiîjklmnopqrsștțuvwxyz'
def key(s):
    s = s.lower().replace('(', '').replace(')', '')
    return [ALPH.index(c) if c in ALPH else 0 for c in s]
def cap(s): return re.sub(r"[^\s-]+", lambda m: m.group(0)[0] + m.group(0)[1:].lower(), s)
rows = [l.strip().split('|') for l in open(os.path.expanduser('~/work/membri.txt'), encoding='utf-8') if l.strip()]
rows.sort(key=lambda r: (key(r[1]), key(r[0])))
groups = {}
for p, n in rows: groups.setdefault(n[0], []).append((p, n))
parts = []
for L, items in groups.items():
    lis = '\n'.join(f'            <li><span class="members-index__surname">{html.escape(cap(n))}</span> {html.escape(p)}</li>' for p, n in items)
    parts.append(f'        <div class="members-index__group">\n          <div class="members-index__letter">{L}</div>\n          <ul class="members-index__list">\n{lis}\n          </ul>\n        </div>')
f = os.path.expanduser('~/mnt/microbis/membri.html'); s = open(f, encoding='utf-8').read()
a = s.index('      <div class="members-index" data-reveal>\n') + len('      <div class="members-index" data-reveal>\n')
b = s.index('\n      </div>\n    </div>\n  </section>', a)
s = s[:a] + '\n'.join(parts) + s[b:]
open(f, 'w', encoding='utf-8', newline='').write(s)
print(len(rows), 'nume;', ''.join(groups))
