import sys, re, subprocess
RO = re.compile(r'[ăâîșțĂÂÎȘȚ]|\b(și|în|din|pentru|este|sunt|spectacol\w*|dans\w*|cu|de|la|al|ale|vezi|despre)\b', re.I)
for f in sys.argv[1:]:
    out = subprocess.run(['python3', '/sessions/' + __import__('os').environ.get('USER','') , ], capture_output=True) if False else None
    import importlib.util
    spec = importlib.util.spec_from_file_location('s', __import__('os').path.expanduser('~/work/en/strings.py'))
    txt = subprocess.run(['python3', __import__('os').path.expanduser('~/work/en/strings.py'), f], capture_output=True, text=True).stdout.splitlines()
    hits = [t for t in txt if RO.search(t)]
    print(f'== {f}: {len(hits)} rânduri cu posibil text RO')
    for h in hits: print('   ', h[:160])
