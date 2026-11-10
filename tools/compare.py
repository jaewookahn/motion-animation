"""여러 버전의 HTML 애니메이션을 같은 시각에 캡처해 한 장의 비교 이미지(JPG)로 만듭니다.

사용법:
  python tools/compare.py --out projects/09-daniel-nutshell/versions/compare.jpg \
      --times 1,2.5,4.2,7.2,9.2,12.9,14.6 \
      projects/07-daniel-kurzgesagt/index.html \
      projects/09-daniel-nutshell/versions/v1.html projects/09-daniel-nutshell/versions/v2.html

  - 열 = 버전(인자 순서), 행 = 시각
  - 열 제목은 파일 경로에서 자동 생성 (versions/v1.html → "09 v1")
  - 버전 하나만 주면 그 버전의 컨택트 시트가 됩니다.
"""
import argparse, base64, io, pathlib
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('htmls', nargs='+'); ap.add_argument('--out', required=True)
ap.add_argument('--times', required=True); ap.add_argument('--cell', type=int, default=640)
a = ap.parse_args()
times = [float(x) for x in a.times.split(',')]
cw, ch = a.cell, a.cell * 9 // 16; head = 44; side = 90

def label(p):
    p = pathlib.Path(p).resolve()
    proj = next((q.name for q in p.parents if q.parent.name == 'projects'), p.parent.name)
    tag = p.stem if p.stem != 'index' else 'latest'
    return f'{proj[:2]} {tag}' if p.parent.name == 'versions' else f'{proj} ({tag})'

font_path = pathlib.Path(__file__).resolve().parent.parent / 'fonts' / 'Pretendard-Bold.otf'
font = ImageFont.truetype(str(font_path), 24) if font_path.exists() else ImageFont.load_default()
sheet = Image.new('RGB', (side + cw * len(a.htmls), head + ch * len(times)), (24, 22, 30))
dr = ImageDraw.Draw(sheet)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    for ci, h in enumerate(a.htmls):
        pg.goto(pathlib.Path(h).resolve().as_uri() + '?capture=1'); pg.evaluate('window.ready')
        dr.text((side + ci * cw + 12, 10), label(h), fill=(255, 230, 150), font=font)
        for ri, t in enumerate(times):
            d = pg.evaluate(f'grab({t})')
            im = Image.open(io.BytesIO(base64.b64decode(d.split(',', 1)[1]))).convert('RGB').resize((cw, ch))
            sheet.paste(im, (side + ci * cw, head + ri * ch))
            if ci == 0: dr.text((12, head + ri * ch + ch // 2 - 12), f'{t:.1f}s', fill=(220, 220, 220), font=font)
    b.close()
sheet.save(a.out, quality=82)
print('saved', a.out, sheet.size)
