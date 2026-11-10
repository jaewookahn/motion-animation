import sys, base64, pathlib, time
from playwright.sync_api import sync_playwright
root = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]); out.mkdir(exist_ok=True)
times = [float(x) for x in sys.argv[3].split(',')]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width':1920,'height':1080})
    errs=[]; pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto((root/'index.html').as_uri()+'?capture=1'); pg.evaluate('window.ready')
    t0=time.time()
    for t in times:
        d = pg.evaluate(f'grab({t})')
        (out/f'{t:06.2f}.png').write_bytes(base64.b64decode(d.split(',')[1]))
    print('per frame', (time.time()-t0)/len(times)); print('errors', errs[:5])
    b.close()
