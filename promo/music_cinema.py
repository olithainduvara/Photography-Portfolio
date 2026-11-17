"""Synthesise the soundtrack for the cinematic film -> promo/music_cinema.wav (60 s, stereo, 44.1 kHz).

A cinematic trailer cue at 80 BPM (one bar = 3 s), generated entirely with numpy/scipy:
no samples, no copyrighted material. Every chapter is three bars, so cuts land on bar lines.

    0-6   cold open: felt piano alone, a string swell
    6-15  Portraits: piano motif + strings
    15-24 Blooming Beauty: + cello ostinato, warmer strings
    24-33 Reels: + pulse, rising strings, first low hits
    33-42 Culture: taiko drums enter, brass stabs
    42-51 From above: full climax (drums, ostinato, high strings, brass)
    51-54 the last swell, then silence  |  54-60 end card: piano alone + a final low boom

    python promo/music_cinema.py
"""
import os, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BEAT = .75
BAR = 3.0
rng = np.random.default_rng(23)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * .45) / (SR / 2), 'low', output='sos'), x, axis=0)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc / (SR / 2), 'high', output='sos'), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo / (SR / 2), min(hi, SR * .45) / (SR / 2)], 'band', output='sos'), x, axis=0)


def env(n, a, r):
    e = np.ones(n)
    na, nr = min(int(a * SR), n), min(int(r * SR), n)
    if na:
        e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def saw(f, n, ph0=0.0):
    dt = f / SR
    ph = (ph0 + dt * np.arange(n)) % 1.0
    s = 2 * ph - 1
    a = ph < dt
    x = ph[a] / dt
    s[a] -= x + x - x * x - 1
    b = ph > 1 - dt
    x = (ph[b] - 1) / dt
    s[b] -= x * x + x + x + 1
    return s


class Bus:
    def __init__(self):
        self.a = np.zeros((N, 2))

    def add(self, t, sig, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        if i >= N or i < 0:
            return
        sig = sig[:N - i]
        if sig.ndim == 1:
            self.a[i:i + len(sig), 0] += sig * gain * np.cos((pan + 1) * np.pi / 4) * 1.414
            self.a[i:i + len(sig), 1] += sig * gain * np.sin((pan + 1) * np.pi / 4) * 1.414
        else:
            self.a[i:i + len(sig)] += sig * gain


PIANO, STR, CELLO, BRASS, DRUM, LOW, FX = (Bus() for _ in range(7))


# ------------------------------------------------------------------ instruments
def piano(m, length=3.5, vel=1.0):
    """Soft felt piano: slightly inharmonic partials, brighter and shorter when played harder."""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + .00035 * k * k)
        if fk > 9000:
            break
        s += np.sin(2 * np.pi * fk * t + rng.random() * 6.28) * (vel ** (k * .25)) / k ** 1.5 * np.exp(-t * (1.1 + k * .55) * (1 + (m - 60) / 60))
    hammer = lp(rng.standard_normal(n), 2500) * np.exp(-t * 60) * .08 * vel
    s = (s + hammer) * env(n, .004, .3)
    return lp(s, 3600 + 3400 * vel) * vel


def strings(notes, length, bright=1.0, attack=.9):
    """String ensemble: many detuned saws, slow attack, gentle vibrato, warm low-pass."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in notes:
        for k in range(5):
            u = k / 4 * 2 - 1
            vib = 1 + .0035 * np.sin(2 * np.pi * (5.2 + k * .3) * t + k)
            f = hz(m) * 2 ** (u * 9 / 1200) * vib
            ph = np.cumsum(f) / SR + rng.random()
            s = 2 * (ph % 1) - 1
            out[:, 0] += s * np.cos((u * .7 + 1) * np.pi / 4)
            out[:, 1] += s * np.sin((u * .7 + 1) * np.pi / 4)
    out = lp(out, 1500 + 4300 * bright, 3) / (len(notes) * 2.2)
    return out * env(n, attack, min(.9, length * .3))[:, None]


def cello(m, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = saw(hz(m), n) + .6 * saw(hz(m) * 1.004, n, .3)
    return lp(s, 1300) * env(n, .015, .06) * np.exp(-t * 2.5)


def brass(notes, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = sum(saw(hz(m), n) + .5 * saw(hz(m) * 1.006, n, .4) for m in notes) / len(notes)
    cut = 600 + 2400 * np.exp(-t * 5)
    s = lp(s, 1600) * (1 - np.exp(-t * 5)) + lp(s, 3000) * np.exp(-t * 5)
    del cut
    return np.tanh(s * 1.4) * env(n, .03, .4)


def taiko(pitch=1.0, length=1.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (52 * pitch * t + (140 - 52) * pitch / 22 * (1 - np.exp(-22 * t)))) * np.exp(-t * 5.5)
    skin = bp(rng.standard_normal(n), 120, 1800) * np.exp(-t * 26) * .5
    return np.tanh((body + skin) * 1.3) * env(n, .002, .1)


def rim():
    n = int(.25 * SR)
    t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 900, 6000) * np.exp(-t * 30) + .4 * np.sin(2 * np.pi * 330 * t) * np.exp(-t * 40)


def boom(length=3.5):
    """Trailer hit: sub drop + distant metallic tail."""
    n = int(length * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (30 * t + (90 - 30) / 6 * (1 - np.exp(-6 * t)))) * np.exp(-t * 1.6)
    metal = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (3 + i)) for i, f in enumerate((211, 347, 523, 761))) * .08
    noise = bp(rng.standard_normal(n), 400, 4000) * np.exp(-t * 5) * .25
    return (sub + metal + noise) * env(n, .003, .5)


def braam(root, length=2.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = sum(saw(hz(m), n, rng.random()) for m in (root, root + 7, root + 12, root + 12.08))
    cut = 300 + 1700 * np.exp(-t * 1.2)
    s = lp(s, 2000) * np.exp(-t * .9)
    del cut
    return np.tanh(s * .7) * env(n, .01, .6)


def swell(length):
    """Reverse-cymbal style swell into a cut."""
    n = int(length * SR)
    u = np.linspace(0, 1, n)
    return np.stack([hp(rng.standard_normal(n), 2500) for _ in range(2)], 1) * (u ** 3)[:, None] * env(n, .05, .01)[:, None]


def riser(length):
    n = int(length * SR)
    u = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = sum(bp(noise, lo, hi) * np.clip((u - k * .2) / (1 - k * .2), 0, 1) ** 2 for k, (lo, hi) in enumerate(((300, 900), (900, 2600), (2600, 7000), (7000, 14000))))
    return out * env(n, .05, .01)


# ------------------------------------------------------------------ the score
# one chord per bar (3 s): Am F C G | Am F C Em | F G Am Am ...
PROG = ['Am', 'Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'Em', 'F', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'G', 'Am', 'Am']
CH = {'Am': (45, [57, 60, 64]), 'F': (41, [57, 60, 65]), 'C': (48, [55, 60, 64]), 'G': (43, [55, 59, 62]), 'Em': (40, [55, 59, 64])}
# piano motif per bar: (beat, note offset into the chord stack, velocity)
MOTIF = [(0, 0, .8), (.5, 1, .55), (1, 2, .6), (1.5, 1, .5), (2, 3, .7), (2.5, 2, .5), (3, 1, .55), (3.5, 2, .45)]
CUTS = [6, 15, 24, 33, 42, 51, 54]


def stack(tones):
    return [tones[0], tones[1], tones[2], tones[0] + 12]


for b, name in enumerate(PROG):
    t0 = b * BAR
    root, tones = CH[name]
    st = stack([m + 12 for m in tones])
    sec = 0 if t0 < 6 else 1 if t0 < 15 else 2 if t0 < 24 else 3 if t0 < 33 else 4 if t0 < 42 else 5 if t0 < 51 else 6 if t0 < 54 else 7

    # ---- piano: always there; sparse in the cold open and the end card
    if sec in (0, 7):
        for bt, idx, v in MOTIF[::2]:
            PIANO.add(t0 + bt * BEAT, piano(st[idx], 4, v * .85), .5, (-.3, .3)[idx % 2])
        PIANO.add(t0, piano(root + 12, 5, .6), .45)
    elif sec != 6:
        for bt, idx, v in MOTIF:
            PIANO.add(t0 + bt * BEAT, piano(st[idx] + (12 if sec == 5 and idx == 3 else 0), 2.6, v), .42 if sec < 4 else .34, (-.35, .35)[idx % 2])
        PIANO.add(t0, piano(root + 12, 3.5, .7), .4)

    # ---- strings
    if sec == 0 and b == 1:
        STR.add(t0, strings(tones, BAR + .8, .4, 2.2), .55)
    elif 1 <= sec <= 6:
        bright = (.45, .6, .75, .9, 1.0, 1.0)[sec - 1]
        notes = tones + ([tones[0] + 12, tones[1] + 12] if sec >= 4 else [])
        STR.add(t0, strings(notes, BAR + .6, bright, .7 if sec < 4 else .35), .6 if sec < 5 else .72)
        LOW.add(t0, strings([root, root + 12], BAR + .6, .3, .5), .45 if sec >= 2 else .3)

    # ---- cello ostinato (8ths), from Blooming Beauty on
    if 2 <= sec <= 5:
        for k in range(8):
            m = root + (0, 0, 7, 0, 12, 7, 0, 7)[k] if sec >= 4 else root + (0, 7)[k % 2]
            CELLO.add(t0 + k * BEAT / 2, cello(m, BEAT / 2 * .9), (.32 if sec < 4 else .42) * (1.2 if k % 4 == 0 else .9), (-.2, .2)[k % 2])

    # ---- drums
    if sec == 3:                                               # a pulse: low hits on 1 and 3
        for bt in (0, 2):
            DRUM.add(t0 + bt * BEAT, taiko(.8, 1.5), .45)
    if sec in (4, 5):
        pattern = (0, 1.5, 2, 3, 3.5) if sec == 4 else (0, .75, 1.5, 2, 2.75, 3, 3.5)
        for bt in pattern:
            DRUM.add(t0 + bt * BEAT, taiko(1.0 if bt % 1 == 0 else 1.25, 1.2), .65 if bt in (0, 2) else .45, (-.3, .3)[int(bt * 2) % 2])
        for bt in (1, 3):
            DRUM.add(t0 + bt * BEAT, rim(), .25 if sec == 4 else .32, .2)
        if sec == 5:
            for k in range(16):
                DRUM.add(t0 + k * BEAT / 4, rim() * .35, .12 + .06 * (k % 4 == 0), (-.4, .4)[k % 2])
    # ---- brass stabs in the big sections
    if sec in (4, 5):
        BRASS.add(t0, brass([m - 12 for m in tones] + [tones[0]], 1.2), .45 if sec == 4 else .55)
        if sec == 5:
            BRASS.add(t0 + 2 * BEAT, brass([m - 12 for m in tones], .9), .4)

# ---- the end of the climax: everything drops out at 54 for the end card
FX.add(51.0, braam(45, 3.0), .55)
FX.add(51.0, boom(3), .7)
for k in range(8):                                             # snare-roll build 52.5 -> 54
    t = 52.5 + k * .1875
    DRUM.add(t, rim(), .2 + k * .06)
FX.add(52.0, riser(2.0), .35)

# ---- transitions: swell into each cut, a trailer hit on the big ones
for c, big in zip(CUTS, (1, 1, 2, 3, 3, 0, 3)):
    if big == 0:
        continue
    FX.add(c - 1.4, swell(1.4), (.08, .12, .16)[big - 1])
    FX.add(c, boom(3.2 if big == 3 else 2.5), (.35, .55, .8)[big - 1])
    if big >= 2:
        FX.add(c, braam(CH[PROG[int(c // BAR)]][0], 2.6), (.3, .45)[big - 2])
FX.add(4.5, riser(1.5), .12)
FX.add(31.5, riser(1.5), .2)
FX.add(40.5, riser(1.5), .26)

# ------------------------------------------------------------------ mix
music = PIANO.a * .9 + STR.a * .8 + LOW.a * .5 + hp(CELLO.a, 50) * .7 + BRASS.a * .55
send = PIANO.a * .7 + STR.a * .5 + CELLO.a * .3 + BRASS.a * .4 + DRUM.a * .35 + FX.a * .5
ir_n = int(3.6 * SR)
tt = np.arange(ir_n) / SR
rev = np.stack([fftconvolve(send[:, ch], bp(rng.standard_normal(ir_n), 200, 7000) * np.exp(-tt / 1.05), mode='full')[:N] for ch in range(2)], 1)
mix = music + hp(DRUM.a, 35) * .85 + hp(send, 5000) * .18 + hp(FX.a, 25) * .6 + rev * .0075
mix = hp(mix, 24)
fade = np.ones(N)
fade[:int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
fo = int(2.6 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade[:, None]
mix /= np.abs(mix).max()
mix = np.tanh(mix * 1.9) / np.tanh(1.9)
mix *= .94 / np.abs(mix).max()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_cinema.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
print(f'> promo/music_cinema.wav  {DUR:.0f}s  peak {np.abs(mix).max():.2f}  rms {db(mix):.1f} dBFS')
for a, b_, nm in ((0, 6, 'cold open'), (6, 15, 'portraits'), (15, 24, 'blooming'), (24, 33, 'reels'), (33, 42, 'culture'), (42, 51, 'climax'), (51, 54, 'last swell'), (54, 60, 'end card')):
    print(f'   {a:4.0f}-{b_:2.0f}s {nm:11s} rms {db(mix[int(a * SR):int(b_ * SR)]):6.1f} dB')
m = mix.mean(1)
X = np.abs(np.fft.rfft(m)) ** 2
f = np.fft.rfftfreq(len(m), 1 / SR)
print('   bands: ' + '  '.join(f'{nm} {10 * np.log10(X[(f >= lo) & (f < hi)].sum() / X.sum()):.1f}' for nm, lo, hi in
                                (('sub', 0, 70), ('bass', 70, 250), ('lowmid', 250, 800), ('mid', 800, 3000), ('high', 3000, 8000), ('air', 8000, 22050))))
