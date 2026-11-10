"""노아의 방주 — procedural score + SFX, synced to index.html timeline (10 s)."""
import numpy as np, wave, sys
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000; DUR = 10.0; N = int(SR * (DUR + 1))
rng = np.random.default_rng(3)
mus, sfx, amb = np.zeros(N), np.zeros(N), np.zeros(N)

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

# ── instruments
def marimba(n, d=0.5, g=0.3):
    t = tt(d); fr = midi(n)
    s = np.sin(2*np.pi*fr*t) + 0.35*np.sin(2*np.pi*fr*4*t)*np.exp(-t*30) + 0.15*np.sin(2*np.pi*fr*10*t)*np.exp(-t*60)
    return s * np.exp(-t * 7) * np.minimum(1, t * 3000) * g
def pluck(n, d=0.8, g=0.25):  # harp-ish
    t = tt(d); fr = midi(n)
    s = sum(np.sin(2*np.pi*fr*k*t) / k**1.3 * np.exp(-t * (3 + k*1.5)) for k in range(1, 6))
    return s * np.minimum(1, t * 2000) * g
def bell(n, d=1.5, g=0.15):
    t = tt(d); fr = midi(n)
    s = np.sin(2*np.pi*fr*t + 1.4*np.sin(2*np.pi*fr*3.5*t)*np.exp(-t*5))
    return s * np.exp(-t * 2.5) * np.minimum(1, t * 800) * g
def pad(notes, d, g=0.1, atk=0.4, cut=1500):
    t = tt(d); s = np.zeros_like(t)
    for n in notes:
        for c in (-6, 6): s += 2 * ((t * midi(n) * 2 ** (c / 1200)) % 1) - 1
    s = filt(s / (2 * len(notes)), 'low', cut)
    return s * np.minimum(1, t / atk) * np.minimum(1, (d - t) / 0.4) * g
def knock(g=0.6, f0=180):   # hammer on wood
    t = tt(0.25); s = np.sin(2*np.pi*f0*t) * np.exp(-t*30) + filt(noise(0.25), 'band', [800, 3000]) * np.exp(-t*60) * 0.7
    return s * g
def thud(g=0.6, f0=70, dec=12):
    t = tt(0.5); f = f0 + 60*np.exp(-t*25)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*dec) * g
def pop(g=0.4, f0=500, f1=1100):
    t = tt(0.15); f = f0 + (f1 - f0) * (t / 0.15)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*30) * g
def thunder(g=1.0, d=2.2):
    t = tt(d); n = filt(noise(d), 'low', 260, 3)
    crack = filt(noise(d), 'band', [600, 5000]) * np.exp(-t*14) * 0.5
    env = np.exp(-t*1.6) * (1 + 0.6*np.sin(2*np.pi*3.3*t)**2)
    return np.tanh((n*5 + crack) * env) * g
def trumpet(g=0.3):  # elephant
    d = 0.55; t = tt(d); f = 520 + 160*np.sin(np.pi*t/d) + 18*np.sin(2*np.pi*22*t)
    s = 2*((np.cumsum(f)/SR) % 1) - 1
    s = filt(s, 'band', [500, 3500]) + filt(noise(d), 'band', [1000, 3000])*0.25
    return s * np.sin(np.pi*t/d)**0.6 * g
def roar(g=0.25):
    d = 0.5; t = tt(d); f = 110 + 30*np.sin(2*np.pi*31*t)
    s = filt(2*((np.cumsum(f)/SR) % 1)-1, 'low', 900) + filt(noise(d), 'band', [200, 1200])*0.5
    return s * np.sin(np.pi*t/d) * g
def flutter(d=0.5, g=0.25):
    t = tt(d); n = filt(noise(d), 'band', [300, 2500])
    return n * (0.5 + 0.5*np.sign(np.sin(2*np.pi*15*t))) * np.sin(np.pi*t/d) * g
def coo(g=0.2):
    d = 0.45; t = tt(d); f = 520 - 90*(t/d) + 25*np.sin(2*np.pi*9*t)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.sin(np.pi*t/d)**2 * g
def creak(g=0.15):
    d = 0.4; t = tt(d); f = 140 + 50*np.sin(np.pi*t/d)
    s = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))
    return filt(s, 'band', [300, 2500]) * np.sin(np.pi*t/d) * g
def whoosh(d, f0, f1, g=0.3):
    n = noise(d); out = np.zeros_like(n); seg = 512
    for i in range(0, len(n), seg):
        fc = f0 * (f1/f0) ** (i/len(n)); ch = n[max(0, i-2048):i+seg]
        out[i:i+seg] = filt(ch, 'band', [fc*0.7, min(fc*1.4, 20000)])[-len(n[i:i+seg]):]
    return out * np.sin(np.pi*tt(d)/d)**2 * g

# ── MUSIC (100 BPM, eighth = 0.3 s)
E = 0.3
# Act 1 · playful C-major pentatonic (0 – 2.4)
mel1 = [72, 76, 79, 76, 81, 79, 76, 74]
for i, n in enumerate(mel1): put(mus, 0.12 + i*E, marimba(n, 0.5, 0.28))
for i, n in enumerate([48, 55, 53, 55]): put(mus, 0.12 + i*0.6, marimba(n, 0.7, 0.32))
put(mus, 0.12, pad([60, 64, 67], 2.4, 0.05))
# Act 2 · darkening to A minor (2.4 – 3.4)
for i, n in enumerate([69, 72, 76, 72]): put(mus, 2.52 + i*E*0.9, marimba(n, 0.5, 0.22))
put(mus, 2.4, pad([45, 57, 60, 64], 1.4, 0.07, atk=0.6, cut=900))
# Act 3 · storm drone (3.4 – 5.4)
put(mus, 3.3, pad([33, 40, 45, 48], 2.4, 0.14, atk=0.3, cut=600))
for k in range(4): put(mus, 3.6 + k*0.45, thud(0.35, 55, 6))
# Act 4 · 40 days, mystic pulse (5.4 – 7.0)
put(mus, 5.4, pad([45, 52, 57, 60], 1.7, 0.09, atk=0.3, cut=1100))
for k in range(8):  # one tick per 5 days
    put(mus, 5.5 + k*0.2, marimba(84 if k % 2 == 0 else 81, 0.25, 0.12))
# Act 5 · hope: harp arpeggio (7.0 – 8.6)
arp = [60, 64, 67, 72, 76, 79, 84, 79, 76, 72, 74, 79]
for i, n in enumerate(arp): put(mus, 7.05 + i*0.13, pluck(n, 1.0, 0.2))
put(mus, 7.0, pad([48, 55, 60, 64], 1.7, 0.08, atk=0.5, cut=2000))
# Act 6 · rainbow (8.6 – 10)
for i, n in enumerate([72, 76, 79, 83, 86, 88]): put(mus, 8.6 + i*0.07, bell(n, 1.6, 0.13))
for i, n in enumerate([79, 81, 84, 88]): put(mus, 9.15 + i*0.15, marimba(n, 0.6, 0.18))
put(mus, 8.6, pad([48, 55, 60, 64, 71, 74], 1.6, 0.11, atk=0.15, cut=2600))
put(mus, 8.6, marimba(36, 1.2, 0.35))

# ── SFX
for k in range(4): put(sfx, 0.12 + k*0.22 + 0.2, knock(0.55, 170 + k*12))       # planks land
for k in range(4): put(sfx, 0.15 + k*0.3 + 0.15, knock(0.25, 260))              # noah hammer taps
put(sfx, 1.05, pop(0.35, 300, 700)); put(sfx, 1.3, thud(0.5, 90, 16)); put(sfx, 1.3, knock(0.3, 140))
put(sfx, 1.32, pop(0.25, 600, 1200)); put(sfx, 1.38, creak(0.15))
for i in range(12): put(sfx, 1.75 + i*0.14, thud(0.18 if i % 2 else 0.25, 60, 18))  # footsteps
put(sfx, 2.0, trumpet(0.28)); put(sfx, 2.6, roar(0.22)); put(sfx, 2.3, pop(0.2, 700, 1300))
put(sfx, 3.42, creak(0.18)); put(sfx, 3.68, thud(0.6, 80, 14)); put(sfx, 3.68, knock(0.35, 150))
for h in (3.55, 4.42, 5.05): put(sfx, h + 0.03, thunder(0.75 if h != 4.42 else 0.9))
# rain bed + waves
t = np.arange(N)/SR
rain_env = np.clip((t-3.2)/0.4, 0, 1) * np.where(t > 5.4, np.interp(t, [5.4, 5.7], [1, 0.6]), 1) * np.clip((7.05-t)/0.35, 0, 1)
amb += filt(rng.uniform(-1, 1, N), 'band', [1500, 9000]) * rain_env * 0.22
wave_env = np.clip((t-4.3)/0.6, 0, 1) * np.clip((8.6-t)/0.8, 0, 1)
amb += filt(rng.uniform(-1, 1, N), 'low', 500) * wave_env * (0.6 + 0.4*np.sin(2*np.pi*0.45*t)) * 0.5
put(sfx, 5.35, whoosh(0.7, 300, 1500, 0.25))
for k in range(3): put(sfx, 5.6 + k*0.5, creak(0.1))
put(sfx, 7.67, thud(0.55, 65, 9)); put(sfx, 7.67, creak(0.2))
put(sfx, 7.1, flutter(0.55, 0.28)); put(sfx, 7.85, flutter(0.62, 0.28)); put(sfx, 8.52, coo(0.2)); put(sfx, 8.85, coo(0.15))
put(sfx, 8.75, creak(0.15)); put(sfx, 8.85, pop(0.2, 400, 900))
for i in range(10): put(sfx, 9.0 + i*0.11, thud(0.14, 70, 20))
put(sfx, 9.25, trumpet(0.18))
for i in range(4): put(sfx, 8.75 + i*0.1, pluck(96 - i*3, 0.3, 0.05))  # bird chirps
put(sfx, 0.08, whoosh(0.5, 2000, 6000, 0.12))

# ── mix
ir_t = np.arange(int(1.4*SR))/SR
ir = rng.uniform(-1, 1, len(ir_t)) * np.exp(-ir_t*3.5); ir = filt(ir, 'low', 5000); ir /= np.sqrt(np.sum(ir**2))
verb = fftconvolve(mus*0.6 + sfx*0.25, ir)[:N] * 0.3
mix = mus + sfx*0.9 + amb + verb
fade = np.clip((10.0 - t)/0.35, 0, 1) * np.clip(t/0.05, 0, 1)
mix = np.tanh(mix*fade*1.2) / np.tanh(1.2)
mix = filt(mix, 'high', 30) / np.max(np.abs(mix)) * 0.9
L = mix; R = np.roll(mix, 9)*0.95 + verb*0.08
st = (np.clip(np.stack([L, R], 1)[:int(DUR*SR)], -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok')
