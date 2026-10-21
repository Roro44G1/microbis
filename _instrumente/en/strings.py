import sys, re
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=False); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style'): s.skip+=1
        for k,v in a:
            if k in ('alt','content','placeholder','aria-label','title','data-img-alt','value') and v and re.search('[A-Za-zĂÂÎȘȚăâîșț]{3}',v) and not v.startswith(('http','width','summary','website','article','#','Microbis —')) :
                s.out.append(f'@{k}: {v}')
    def handle_endtag(s,t):
        if t in ('script','style'): s.skip-=1
    def handle_data(s,d):
        if s.skip: return
        d=d.strip()
        if d and re.search('[A-Za-zăâîșț]{2}',d): s.out.append(d)
    def handle_entityref(s,n): pass
f=sys.argv[1]; p=P(); p.feed(open(f,encoding='utf-8').read())
seen=set()
for x in p.out:
    if x not in seen: seen.add(x); print(x)
