"""프로젝트 폴더(index.html + audio.py)를 MP4로 렌더링합니다.

사용법:
  python tools/render.py projects/03-noah-ink --dur 10
  python tools/render.py projects/01-designingi-showreel --dur 15 --grain 6 --crf 16

과정: audio.py → out/music.wav 생성 → 헤드리스 Chromium으로 index.html의 grab(t)을
fps(기본 120)로 캡처 → ffmpeg tmix로 2프레임 합성(모션 블러) → 60fps H.264 + AAC(−14 LUFS).
"""
import argparse, base64, pathlib, subprocess, sys, time
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('project'); ap.add_argument('--dur', type=float, required=True)
ap.add_argument('--fps', type=int, default=120); ap.add_argument('--crf', type=int, default=18)
ap.add_argument('--grain', type=int, default=0, help='ffmpeg noise 세기 (0=끔)')
ap.add_argument('--out', default=None)
a = ap.parse_args()

proj = pathlib.Path(a.project).resolve(); outdir = proj / 'out'; outdir.mkdir(exist_ok=True)
wav = outdir / 'music.wav'; mp4 = pathlib.Path(a.out) if a.out else outdir / f'{proj.name}.mp4'
has_audio = (proj / 'audio.py').exists()
if has_audio:
    subprocess.run([sys.executable, str(proj / 'audio.py'), str(wav)], check=True, cwd=proj)
else:
    print('audio.py 없음 → 무음으로 렌더합니다')

vf = 'tmix=frames=2,fps=60' + (f',noise=alls={a.grain}:allf=t' if a.grain else '') + ',format=yuv420p'
cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
       '-f', 'image2pipe', '-framerate', str(a.fps), '-c:v', 'png', '-i', '-']
if has_audio:
    cmd += ['-i', str(wav), '-filter_complex', f'[0:v]{vf}[v];[1:a]loudnorm=I=-14:TP=-1:LRA=7[a]',
            '-map', '[v]', '-map', '[a]', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000']
else:
    cmd += ['-filter_complex', f'[0:v]{vf}[v]', '-map', '[v]']
cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf), '-pix_fmt', 'yuv420p',
        '-t', str(a.dur), '-movflags', '+faststart', str(mp4)]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

nf = int(a.fps * a.dur)
with sync_playwright() as p:
    b = p.chromium.launch()  # GPU 플래그를 켜면 캔버스 읽기가 검게 나올 수 있어 기본값 사용
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    pg.goto((proj / 'index.html').as_uri() + '?capture=1'); pg.evaluate('window.ready')
    t0 = time.time()
    for i in range(nf):
        ff.stdin.write(base64.b64decode(pg.evaluate(f'grab({i / a.fps})').split(',', 1)[1]))
        if i % a.fps == 0: print(f'{i}/{nf}  {time.time() - t0:.0f}s', flush=True)
    b.close()
ff.stdin.close(); ff.wait()
print('done' if ff.returncode == 0 else f'ffmpeg 실패 {ff.returncode}', mp4)
