"""Procedural soundtrack for the 디자인하는AI showreel — 120 BPM, synced to index.html events."""
import numpy as np, wave, sys
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 15.0
N = int(SR * DUR) + SR  # tail room
rng = np.random.default_rng(7)

def buf(): return np.zeros(N)
drums, bass, pad, fx, sfx = buf(), buf(), buf(), buf(), buf()   # sfx → reverb send too

def tt(d): return np.arange(int(d * SR)) / SR
def put(b, t0, sig, g=1.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]
    b[i:i + len(sig)] += sig * g
def filt(x, kind, f, order=2):
    if isinstance(f, (list, tuple)): f = [v / (SR / 2) for v in f]
    else: f = f / (SR / 2)
    return sosfilt(butter(order, f, btype=kind, output='sos'), x)
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def midi(n): return 440 * 2 ** ((n - 69) / 12)

# ── instruments
def kick(g=1.0, dec=7.0):
    t = tt(0.5); f = 48 + 140 * np.exp(-t * 38)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * dec)
    s[:150] += noise(150 / SR) * np.linspace(1, 0, 150) * 0.6
    return np.tanh(s * 1.6) * g
def clap():
    t = tt(0.35); n = filt(noise(0.35), 'band', [900, 4200])
    e = np.zeros_like(t)
    for o in (0, 0.011, 0.022): e += (t >= o) * np.exp(-np.clip(t - o, 0, None) * (60 if o < .02 else 16))
    return n * e * 0.8
def hat(open_=False):
    d = 0.18 if open_ else 0.05; t = tt(d)
    return filt(noise(d), 'high', 7000) * np.exp(-t * (18 if open_ else 70)) * 0.5
def blip(freq, d=0.12, g=0.4, wave='sine'):
    t = tt(d); s = np.sin(2 * np.pi * freq * t)
    if wave == 'sq': s = np.sign(s) * 0.5 + np.sin(2 * np.pi * freq * 2 * t) * 0.2
    return s * np.exp(-t * 28) * g * np.minimum(1, t * 2000)
def click(g=0.3, f=3200):
    t = tt(0.03)
    return (filt(noise(0.03), 'band', [f * 0.6, f * 1.6]) * np.exp(-t * 180) + np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t * 250) * 0.4) * g
def whoosh(d, f0, f1, g=0.5, shape='bell'):
    n = noise(d); t = tt(d); out = np.zeros_like(n); seg = 256
    for i in range(0, len(n), seg):
        p = i / len(n); fc = f0 * (f1 / f0) ** p
        out[i:i + seg] = filt(n[max(0, i - 2048):i + seg], 'band', [fc * 0.7, min(fc * 1.4, 22000)])[-len(n[i:i + seg]):]
    env = np.sin(np.pi * t / d) ** 2 if shape == 'bell' else (t / d) ** 2.5
    return out * env * g
def riser(d, g=0.5):
    t = tt(d); w = whoosh(d, 300, 9000, 1.0, 'up')
    f = 220 * 2 ** (3 * t / d); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.25
    return (w + s) * g
def impact(g=1.0, d=2.2):
    t = tt(d); f = 32 + 90 * np.exp(-t * 10)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crash = filt(noise(d), 'high', 1500) * np.exp(-t * 3.5) * 0.35
    return np.tanh(sub * 1.3 + crash) * g
def saw(freq, d, detune=(0, -7, 7)):
    t = tt(d); s = np.zeros_like(t)
    for c in detune:
        fr = freq * 2 ** (c / 1200); s += 2 * ((t * fr) % 1) - 1
    return s / len(detune)
def bass_note(n, d, g=0.5):
    t = tt(d); fr = midi(n)
    s = saw(fr, d, (0, 5)) * 0.6 + np.sin(2 * np.pi * fr * t) * 0.9
    s = filt(s, 'low', 380 + 1400 * 0)  # warm
    env = np.minimum(1, t * 300) * np.exp(-t * 3.0) * np.minimum(1, (d - t) * 60)
    return s * env * g
def chord(notes, d, g=0.15, atk=0.3, cut=1800):
    t = tt(d); s = sum(saw(midi(n), d) for n in notes) / len(notes)
    s = filt(s, 'low', cut)
    env = np.minimum(1, t / atk) * np.minimum(1, (d - t) / 0.3)
    return s * env * g
def bell(n, d=1.2, g=0.18):
    t = tt(d); fr = midi(n)
    s = np.sin(2 * np.pi * fr * t + 1.5 * np.sin(2 * np.pi * fr * 3.5 * t) * np.exp(-t * 6))
    return s * np.exp(-t * 3.2) * g * np.minimum(1, t * 800)

# ── event clock (mirrors index.html)
KICKS = [2.0 + 0.5 * i for i in range(23) if 2.0 + 0.5 * i < 13.3]
# 0–2 s · prompt
put(pad, 0.0, chord([45, 57, 64], 2.0, 0.10, atk=1.2, cut=700))
for i in range(13): put(sfx, 0.22 + i * 0.075, click(0.35, 2600 + rng.uniform(-500, 500)))
put(sfx, 1.42, click(0.6, 1800)); put(sfx, 1.42, blip(midi(81), 0.2, 0.25))
put(fx, 1.0, riser(1.0, 0.55))
for b in (0.0, 0.5, 1.0, 1.5): put(drums, b, kick(0.35, 12))
# 2.0 impact + groove
put(fx, 2.0, impact(1.2))
for k in KICKS: put(drums, k, kick(1.0 if k not in (2.0, 13.0) else 1.1))
for k in KICKS: put(drums, k + 0.25, hat(open_=(k >= 4.0 and int(k * 2) % 4 == 3)))
for i in range(int((13.25 - 4.0) / 0.125)):
    tq = 4.0 + i * 0.125
    if i % 2: put(drums, tq, hat(), 0.5)
for c in [4.5, 5.5, 6.5 + .5, 7.5 + .5, 9.5, 10.5, 11.0, 12.0, 13.0]:
    if c < 13.3: put(drums, c, clap(), 0.85)
put(fx, 2.5, whoosh(0.3, 400, 3000, 0.35))
# glitch stutter 3.5
for i in range(5): put(sfx, 3.5 + i * 0.026, filt(noise(0.02), 'band', [1500, 6000]) * 0.5)
put(sfx, 3.5, blip(midi(93), 0.1, 0.25, 'sq'))
put(fx, 3.7, whoosh(0.32, 200, 8000, 0.6, 'up'))
# bass line (8ths, octave bounce)
ROOTS = [(2.0, 33), (4.0, 29), (6.5, 36), (8.0, 31), (10.0, 33), (11.5, 29), (12.5, 31)]
def root_at(t):
    r = ROOTS[0][1]
    for s_, n in ROOTS:
        if t >= s_: r = n
    return r
for i in range(int((13.3 - 2.0) / 0.25)):
    tq = 2.0 + i * 0.25
    n = root_at(tq) + (12 if i % 2 else 0)
    put(bass, tq, bass_note(n, 0.24, 0.55))
# pads per section
for (t0, d, notes) in [(2.0, 2.0, [57, 60, 64]), (4.0, 2.5, [53, 57, 60, 64]), (6.5, 1.5, [48, 55, 60, 64]),
                       (8.0, 2.0, [55, 59, 62, 67]), (10.0, 1.5, [57, 60, 64, 71]), (11.5, 1.0, [53, 57, 60, 65]), (12.5, 0.85, [55, 59, 62, 67])]:
    put(pad, t0, chord(notes, d, 0.12, atk=0.05, cut=2400))
# S3 tool slots: rising pentatonic blips
PENTA = [69, 72, 74, 76, 79, 81, 84]
for k in range(7): put(sfx, 4.0 + 0.25 * k, blip(midi(PENTA[k]), 0.16, 0.28, 'sq'))
# reel ticks — crossing integer positions of eOutQuart * 17
def eOutQuart(x): return 1 - (1 - x) ** 4
prev = 0
for i in range(1, 600):
    v = i / 1000; pos = eOutQuart(min(1, v / 0.6)) * 17
    if int(pos) > prev:
        prev = int(pos); put(sfx, 5.75 + v, click(0.32, 4200))
put(sfx, 6.35, bell(88, 0.8, 0.25)); put(sfx, 6.35, bell(81, 0.8, 0.18))
# S4 system
put(fx, 6.5, whoosh(0.25, 3000, 300, 0.4))
for k in range(23): put(sfx, 6.75 + k * 0.032, click(0.18, 3000 + rng.uniform(-600, 600)))
put(sfx, 7.55, click(0.7, 1400)); put(sfx, 7.55, blip(midi(76), 0.15, 0.3))
for d in range(29): put(sfx, 7.0 + d * 0.026, blip(midi(72 + d % 12 + (d // 12) * 12 * 0), 0.06, 0.08))
put(fx, 7.85, whoosh(0.55, 500, 6000, 0.45))
put(sfx, 8.45, kick(0.5, 14)); put(sfx, 8.45, click(0.5, 900))
put(sfx, 8.58, click(0.35, 2400))
put(fx, 8.82, whoosh(0.4, 300, 9000, 0.75))
# S5 numbers — ratchets
for s0 in (9.0, 9.75, 10.5):
    tk = 0.0
    while tk < 0.5:
        put(sfx, s0 + tk, click(0.22, 5200)); tk += 0.012 + tk * 0.12
    put(sfx, s0 + 0.5, blip(midi(84), 0.12, 0.18))
for s0 in (9.65, 10.4): put(fx, s0, whoosh(0.25, 800, 4000, 0.3))
put(fx, 11.2, whoosh(0.3, 6000, 400, 0.5))
# S6 content + build up
put(sfx, 11.85, blip(midi(79), 0.14, 0.3, 'sq'))
put(fx, 12.4, riser(1.1, 0.75))
for i in range(16):
    tq = 12.5 + 0.85 * (1 - (1 - i / 16) ** 1.6)
    put(drums, tq, clap(), 0.25 + 0.5 * i / 16)
# 13.5 drop / end card
put(fx, 13.5, impact(1.6, 2.0))
put(drums, 13.5, kick(1.2, 4))
put(pad, 13.5, chord([45, 57, 64, 67, 71, 76], 1.5, 0.2, atk=0.02, cut=3200))
put(bass, 13.5, bass_note(33, 1.4, 0.7))
for i, n in enumerate([81, 88, 93, 100]): put(sfx, 13.62 + i * 0.09, bell(n, 1.0, 0.13))
for i in range(11): put(sfx, 13.95 + i * 0.023, click(0.12, 3000))

# ── mix
t = np.arange(N) / SR
side = np.ones(N)
for k in KICKS + [13.5]:
    m = t >= k; side[m] = np.minimum(side[m], 1 - 0.65 * np.exp(-(t[m] - k) * 9))
ir_t = np.arange(int(1.6 * SR)) / SR
ir = rng.uniform(-1, 1, len(ir_t)) * np.exp(-ir_t * 3.2); ir = filt(ir, 'low', 6000); ir /= np.sqrt(np.sum(ir ** 2))
send = fx * 0.4 + sfx * 0.5 + pad * 0.5
verb = fftconvolve(send, ir)[:N] * 0.35
mix = drums * 0.55 + filt(bass, 'low', 900) * side * 0.85 + pad * side * 0.9 + fx * 0.8 + sfx * 0.9 + verb
mix = filt(mix, 'high', 28)
# end fade
fade = np.ones(N); fs_, fe = int(14.4 * SR), int(15.0 * SR)
fade[fs_:fe] = np.linspace(1, 0, fe - fs_) ** 1.5; fade[fe:] = 0
mix = mix * fade
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.max(np.abs(mix)) * 0.93
st = np.stack([mix, np.roll(mix, 12) * 0.98 + verb * 0.05], 1)[: int(DUR * SR)]
st = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok', st.shape)
