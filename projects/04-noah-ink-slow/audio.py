"""노아의 방주 (잉크 일러스트판 1.5x Slow, 15초) — warm piano/strings score + pen & paper foley, synced to index.html."""
import numpy as np, wave, sys
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000; DUR = 15.0; SCALE = 1.5; N = int(SR * (DUR + 2.0))
rng = np.random.default_rng(11)
mus, sfx, amb = np.zeros(N), np.zeros(N), np.zeros(N)
tN = np.arange(N) / SR

def tt(d): return np.arange(int(d * SR)) / SR
def put(b, t0, sig, g=1.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]; b[i:i + len(sig)] += sig * g
def filt(x, kind, fr, order=2):
    fr = [v / (SR / 2) for v in fr] if isinstance(fr, (list, tuple)) else fr / (SR / 2)
    return sosfilt(butter(order, fr, btype=kind, output='sos'), x)
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def midi(n): return 440 * 2 ** ((n - 69) / 12)

def piano(n, d=3.0, g=0.22):
    t = tt(d); fr = midi(n); s = np.zeros_like(t)
    for k, a in enumerate([1, .55, .3, .18, .1, .06], 1):
        s += a * np.sin(2*np.pi*fr*k*(1 + 0.0004*k*k)*t) * np.exp(-t*(1.6 + k*0.9)/SCALE)
    s += filt(noise(d), 'band', [min(fr*3, 8000), min(fr*6, 16000)]) * np.exp(-t*80) * 0.08
    return s * np.minimum(1, t*1500) * g
def strings(notes, d, g=0.07, atk=1.2, cut=2200):
    t = tt(d); s = np.zeros_like(t)
    for n in notes:
        for c in (-8, 0, 8):
            ph = 2*np.pi*np.cumsum(midi(n)*2**(c/1200)*(1 + 0.003*np.sin(2*np.pi*5.2*t)))/SR
            s += 2*((ph/(2*np.pi)) % 1) - 1
    s = filt(s/(3*len(notes)), 'low', cut)
    return s * np.minimum(1, t/atk) * np.minimum(1, (d-t)/0.8) * g
def scribble(d, g=0.12, seed=0):   # pen on paper
    r = np.random.default_rng(seed); n = r.uniform(-1, 1, int(d*SR)); t = tt(d)
    s = filt(n, 'band', [2500, 7000])
    strokes = 0.55 + 0.45*np.sign(np.sin(2*np.pi*(7 + 4*r.random())*t + r.random()*6))
    return s * strokes * np.minimum(1, t*40) * np.minimum(1, (d-t)*30) * g
def tap(g=0.25, f=900):
    t = tt(0.12)
    return (filt(noise(0.12), 'band', [f*0.6, f*2]) * np.exp(-t*70) + np.sin(2*np.pi*f*0.4*t)*np.exp(-t*45)*0.5) * g
def paper_whoosh(d, g=0.18):
    t = tt(d); s = filt(noise(d), 'band', [400, 5000])
    crackle = (rng.random(len(t)) > 0.995) * rng.uniform(-1, 1, len(t)) * 3
    return (s + filt(crackle, 'high', 2000)) * np.sin(np.pi*t/d)**2 * g
def knock(g=0.4, f0=170):
    t = tt(0.3)
    return (np.sin(2*np.pi*f0*t)*np.exp(-t*20) + filt(noise(0.3), 'band', [700, 2800])*np.exp(-t*40)*0.6) * g
def thunder(g=0.8, d=3.6):
    t = tt(d); n = filt(noise(d), 'low', 240, 3)
    crack = filt(noise(d), 'band', [500, 4500]) * np.exp(-t*8) * 0.4
    return np.tanh((n*5 + crack) * np.exp(-t*1.0) * (1 + 0.5*np.sin(2*np.pi*1.8*t)**2)) * g
def bell(n, d=2.7, g=0.1):
    t = tt(d); fr = midi(n)
    return np.sin(2*np.pi*fr*t + 1.2*np.sin(2*np.pi*fr*3.5*t)*np.exp(-t*3.5)) * np.exp(-t*1.5) * np.minimum(1, t*900) * g
def flutter(d, g=0.18):
    t = tt(d); return filt(noise(d), 'band', [300, 2400]) * (0.5 + 0.5*np.sign(np.sin(2*np.pi*10*t))) * np.sin(np.pi*t/d) * g
def trumpet(g=0.12):
    d = 0.5 * SCALE; t = tt(d); f = 500 + 150*np.sin(np.pi*t/d) + 15*np.sin(2*np.pi*14*t)
    s = filt(2*((np.cumsum(f)/SR) % 1) - 1, 'band', [500, 3000])
    return s * np.sin(np.pi*t/d)**0.6 * g

# ── score: D major, piano arpeggios over strings (1.5x stretched timing)
CH = [(0.0, 1.25, [50, 57, 62, 66], [62, 66, 69, 74]),      # D
      (1.25, 1.35, [43, 55, 59, 62], [67, 71, 74, 71]),     # G
      (2.6, 1.3, [45, 57, 61, 64], [69, 73, 76, 73]),       # A
      (3.9, 1.4, [47, 54, 59, 62], [59, 62, 66, 62]),       # Bm (flood)
      (5.3, 1.25, [42, 54, 57, 61], [61, 64, 66, 69]),      # F#m (40 days)
      (6.55, 1.25, [43, 55, 59, 62], [67, 71, 74, 79]),     # G (hope)
      (7.8, 1.25, [45, 57, 61, 64], [73, 76, 81, 76]),      # A
      (9.0, 2.0, [38, 50, 57, 62, 66], [74, 78, 81, 86])]   # D (resolve)

for (orig_t0, orig_d, low, arp) in CH:
    t0 = orig_t0 * SCALE
    d = orig_d * SCALE
    put(mus, t0, strings(low[1:], d + 0.6, 0.06 if orig_t0 < 3.9 or orig_t0 > 6 else 0.085, atk=0.75))
    put(mus, t0, piano(low[0], 3.6, 0.26))
    for i, n in enumerate(arp):
        put(mus, t0 + 0.12 + i * d / len(arp), piano(n, 2.7, 0.16 if i else 0.2))

put(mus, 3.9 * SCALE, strings([35, 42], 2.4, 0.09, atk=0.3, cut=500))   # low swell under flood
put(mus, 9.0 * SCALE, strings([74, 78, 81], 2.4, 0.05, atk=0.9, cut=3500))

# ── foley
for i in range(6): put(sfx, (0.15 + i*0.1 + 0.12) * SCALE, tap(0.3, 700 + i*40))
put(sfx, 0.55 * SCALE, scribble(0.35 * SCALE, 0.1, 1))
for k, s in enumerate([1.25, 2.6, 3.9, 5.3, 6.55, 7.8]):
    put(sfx, (s - 0.25) * SCALE, scribble(0.4 * SCALE, 0.09, 10 + k))                # panel frame
    put(sfx, (s + 0.1) * SCALE, tap(0.22, 600))                                      # badge pop
for a, b in [(1.0, 1.45), (2.45, 2.85), (3.75, 4.15), (5.15, 5.55), (6.4, 6.8), (7.65, 8.05)]:
    put(sfx, a * SCALE, paper_whoosh((b - a + 0.1) * SCALE, 0.16))
put(sfx, 9.0 * SCALE, paper_whoosh(1.2, 0.22))

# P1
put(sfx, 1.4 * SCALE, scribble(0.9 * SCALE, 0.07, 30))
for k in range(4): put(sfx, (1.53 + k*0.34) * SCALE, knock(0.35, 165 + k*8))
put(sfx, 1.9 * SCALE, scribble(0.35 * SCALE, 0.08, 31))
put(sfx, 2.25 * SCALE, scribble(0.3 * SCALE, 0.08, 32))

# P2
for i in range(6): put(sfx, (2.75 + i*0.08 + 0.12) * SCALE, tap(0.18, 400 + i*30))
put(sfx, 2.95 * SCALE, trumpet(0.14))
put(sfx, 3.15 * SCALE, scribble(0.4 * SCALE, 0.08, 33))
for j in range(3): put(sfx, (3.42 + j*0.08) * SCALE, tap(0.2, 1100))

# P3
put(sfx, 3.95 * SCALE, scribble(0.5 * SCALE, 0.07, 34))
put(sfx, 4.3 * SCALE, thunder(0.7, 3.6))
rain_env = np.clip((tN - 3.95 * SCALE) / (0.45), 0, 1) * np.clip((5.6 * SCALE - tN) / (0.6), 0, 1)
amb += filt(rng.uniform(-1, 1, N), 'band', [1500, 8000]) * rain_env * 0.12
amb += filt(rng.uniform(-1, 1, N), 'low', 450) * rain_env * (0.6 + 0.4*np.sin(2*np.pi*0.4*tN)) * 0.25

# P4
for i in range(3): put(sfx, (5.32 + i*0.1 + 0.12) * SCALE, tap(0.28, 500))
for k in range(40): put(sfx, (5.55 + k*0.019) * SCALE, tap(0.07, 2200 + (k % 5)*120))

# P5
put(sfx, 6.6 * SCALE, scribble(0.4 * SCALE, 0.07, 35))
put(sfx, 6.82 * SCALE, flutter(0.85 * SCALE, 0.16))
put(sfx, 7.3 * SCALE, scribble(0.3 * SCALE, 0.07, 36))

# P6
for i in range(6): put(sfx, (7.9 + i*0.05) * SCALE, bell(86 - i*2, 2.4, 0.06))
put(sfx, 8.35 * SCALE, tap(0.2, 700))
put(sfx, 8.55 * SCALE, scribble(0.6 * SCALE, 0.07, 37))

# arrows
for i in range(5): put(sfx, (9.25 + i*0.07) * SCALE, scribble(0.22 * SCALE, 0.07, 40 + i))

# ── mix
ir_t = np.arange(int(2.4*SR))/SR
ir = rng.uniform(-1, 1, len(ir_t)) * np.exp(-ir_t*2.2); ir = filt(ir, 'low', 5500); ir /= np.sqrt(np.sum(ir**2))
verb = fftconvolve(mus*0.7 + sfx*0.15, ir)[:N] * 0.35
mix = mus + sfx + amb + verb
fade = np.clip((DUR - tN)/0.9, 0, 1) * np.clip(tN/0.08, 0, 1)
mix = np.tanh(mix*fade*1.1)/np.tanh(1.1); mix = filt(mix, 'high', 30); mix = mix/np.max(np.abs(mix))*0.9
st = np.stack([mix, np.roll(mix, 11)*0.96 + verb*0.06], 1)[:int(DUR*SR)]
st = (np.clip(st, -1, 1)*32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok')
