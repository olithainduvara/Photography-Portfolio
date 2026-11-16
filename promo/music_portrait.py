"""Synthesise the soundtrack for the portrait film -> promo/music_portrait.wav (60 s, stereo, 44.1 kHz).

Energetic house-style track, 120 BPM (one bar = 2 s), generated entirely with numpy/scipy:
no samples, no copyrighted material. Scene cuts fall on bar lines: 4, 8, 18, 28, 38, 46, 54 s.

    intro 0-4 | montage hits 4-8 | groove 8-18 | bigger groove 18-28 (build) |
    drop 28-38 | lighter 38-46 (build) | drop 46-54 | outro 54-60

    python promo/music_portrait.py
"""
import os, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BEAT = 0.5
BAR = 2.0
rng = np.random.default_rng(5)


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
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw(f, n, ph0=0.0):
    """Band-limited (polyBLEP) sawtooth."""
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


def supersaw(m, length, voices=7, detune=16):
    n = int(length * SR)
    out = np.zeros((n, 2))
    for k in range(voices):
        u = k / (voices - 1) * 2 - 1
        s = saw(hz(m) * 2 ** (u * detune / 1200), n, rng.random())
        out[:, 0] += s * np.cos((u * .8 + 1) * np.pi / 4)
        out[:, 1] += s * np.sin((u * .8 + 1) * np.pi / 4)
    return out / np.sqrt(voices)


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


KICK, DRUM, BASS, CHORD, PLUCK, LEAD, PAD, FX = (Bus() for _ in range(8))
kick_times = []


# ------------------------------------------------------------------ drums
def kick():
    n = int(.42 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (47 * t + (170 - 47) / 36 * (1 - np.exp(-36 * t)))) * np.exp(-t * 7.5)
    click = hp(rng.standard_normal(n), 2500) * np.exp(-t * 260) * .22
    return np.tanh((body + click) * 1.5) * env(n, .001, .06)


def clap():
    n = int(.3 * SR)
    t = np.arange(n) / SR
    e = sum(np.exp(-np.maximum(t - d, 0) * 190) * (t >= d) for d in (0, .011, .023)) * .6 + np.exp(-np.maximum(t - .03, 0) * 24) * (t >= .03)
    out = np.stack([bp(rng.standard_normal(n), 900, 7500) for _ in range(2)], 1)
    return out * e[:, None]


def snare():
    n = int(.16 * SR)
    t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1500, 9000) * np.exp(-t * 42) + .5 * np.sin(2 * np.pi * 195 * t) * np.exp(-t * 34)


def hat(open_=False):
    n = int((.24 if open_ else .05) * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 6500 if open_ else 7500, 4) * np.exp(-t * (15 if open_ else 95))


def crash(length=2.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    return np.stack([hp(rng.standard_normal(n), 3200, 3) for _ in range(2)], 1) * (np.exp(-t * 2.3) * env(n, .002, .2))[:, None]


def shutter():
    n = int(.2 * SR)
    out = np.zeros(n)
    for dt, g in ((0, 1.0), (.07, .8)):
        m = int(.06 * SR)
        t = np.arange(m) / SR
        out[int(dt * SR):int(dt * SR) + m] += (bp(rng.standard_normal(m), 1400, 7500) * np.exp(-t * 95) + .6 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 60)) * g
    return out


# ------------------------------------------------------------------ tonal
def bass_note(m, length, bright=1.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = saw(hz(m), n) * .7 + .35 * saw(hz(m) * 1.005, n, .5)
    e = np.exp(-t * 10)
    s = lp(s, 220) * (1 - e) + lp(s, 1500 * bright) * e
    return (s + np.sin(2 * np.pi * hz(m) * t) * .6) * env(n, .004, .03)


def stab(tones, length, cutoff):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = sum(supersaw(m, length) for m in tones) / len(tones) ** .5
    e = np.exp(-t * 7)[:, None]
    s = lp(s, cutoff * .45) * (1 - e) + lp(s, cutoff) * e
    return s * (env(n, .006, .07) * (.75 + .25 * np.exp(-t * 6)))[:, None]


def pluck(m, length=.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = saw(hz(m), n) + .5 * np.sign(np.sin(2 * np.pi * hz(m) * 2 * t))
    e = np.exp(-t * 20)
    s = lp(s, 450) * (1 - e) + lp(s, 6000) * e
    return s * np.exp(-t * 9) * env(n, .002, .02)


def lead_note(m, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    vib = 1 + .004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(t / .25, 1)
    f = hz(m) * vib
    ph = np.cumsum(f) / SR
    s = (2 * (ph % 1) - 1) * .5 + (2 * ((ph * 1.007) % 1) - 1) * .5 + np.sin(2 * np.pi * ph * 2) * .3
    return lp(s, 5200) * env(n, .012, .09)


def bell(m, length=2.4):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    return np.sin(2 * np.pi * f * t + 1.7 * np.exp(-t * 3.5) * np.sin(2 * np.pi * f * 3.01 * t)) * np.exp(-t * 2.1) * env(n, .004, .1)


def riser(length, tone=True):
    n = int(length * SR)
    u = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for k, (lo, hi) in enumerate(((200, 700), (700, 2200), (2200, 6000), (6000, 14000))):
        out += bp(noise, lo, hi) * np.clip((u - k * .17) / (1 - k * .17), 0, 1) ** 2.2
    if tone:
        f = 180 * 2 ** (3.2 * u ** 1.6)
        ph = np.cumsum(f) / SR
        out += lp(2 * (ph % 1) - 1, 6000) * u ** 2 * .5
    return out * env(n, .05, .012)


def impact():
    n = int(2.6 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (34 * t + (110 - 34) / 8 * (1 - np.exp(-8 * t)))) * np.exp(-t * 2.4) * env(n, .003, .3)


def roll(t0, t1, gain0=.2, gain1=.75):
    """Snare roll that speeds up: 8ths, then 16ths, then 32nds over the last beat."""
    t = t0
    while t < t1 - 1e-6:
        left = t1 - t
        step = .25 if left > (t1 - t0) * .5 else .125 if left > .5 else .0625
        k = (t - t0) / (t1 - t0)
        DRUM.add(t, snare(), gain0 + (gain1 - gain0) * k ** 1.5, (-.2, .2)[int(t / step) % 2])
        t += step


# ------------------------------------------------------------------ arrangement
CH = {  # bass root, chord tones
    'Am': (45, [57, 60, 64, 67]), 'F': (41, [57, 60, 65, 69]), 'C': (48, [55, 60, 64, 67]), 'G': (43, [55, 59, 62, 67]),
}
MELODY = {  # (beat, note, length in beats)
    'Am': [(0, 76, .7), (.75, 81, .5), (1.5, 79, .45), (2, 76, .9), (3, 74, .45), (3.5, 76, .45)],
    'F': [(0, 72, .7), (.75, 77, .5), (1.5, 76, .45), (2, 72, .9), (3, 69, .45), (3.5, 72, .45)],
    'C': [(0, 76, .7), (.75, 79, .5), (1.5, 76, .45), (2, 74, .9), (3, 72, .45), (3.5, 74, .45)],
    'G': [(0, 74, .7), (.75, 79, .5), (1.5, 74, .45), (2, 71, .9), (3, 74, .45), (3.5, 71, .45)],
}
BARS = (['Am', 'Am'] + ['F', 'G'] + ['Am', 'F', 'C', 'G', 'Am'] + ['F', 'C', 'G', 'Am', 'G']
        + ['Am', 'F', 'C', 'G', 'Am'] + ['F', 'C', 'G', 'G'] + ['Am', 'F', 'C', 'G'] + ['F', 'G', 'Am'])
SEC = ['intro'] * 2 + ['hits'] * 2 + ['g1'] * 5 + ['g2'] * 5 + ['drop'] * 5 + ['mid'] * 4 + ['drop'] * 4 + ['outro'] * 3
STAB_AT = [(0, .6), (.75, .6), (1.5, .8), (2.5, .6), (3.25, .6)]
ARP = [0, 2, 1, 3, 2, 3, 1, 2, 0, 2, 3, 1, 2, 3, 1, 3]


def add_kick(t, g=1.0):
    KICK.add(t, kick(), g)
    kick_times.append(t)


def delay(bus, t, sig, gain, pan, time=.375, taps=3, fb=.42):
    bus.add(t, sig, gain, pan)
    for k in range(1, taps + 1):
        bus.add(t + time * k, sig, gain * fb ** k, -pan if k % 2 else pan)


for b, (name, sec) in enumerate(zip(BARS, SEC)):
    t0 = b * BAR
    root, tones = CH[name]
    last_of = b + 1 == len(SEC) or SEC[b + 1] != sec           # last bar of its section
    breakdown = sec == 'g2' and last_of                       # bar before the first drop: drums drop out

    if sec == 'intro':
        PAD.add(t0, lp(sum(supersaw(m, BAR + .6) for m in tones) / 2, 700 + 500 * b) * env(int((BAR + .6) * SR), .8, .6)[:, None], .5)
        FX.add(t0 + 1.0, bell(81 if b == 0 else 88), .22, -.3 if b == 0 else .3)
        continue

    if sec == 'hits':                                          # one hit per beat, under the photo cuts
        for k in range(4):
            t = t0 + k * BEAT
            add_kick(t, 1.0)
            FX.add(t - .012, shutter(), .5, (-.3, .3)[k % 2])
            BASS.add(t, bass_note(root - 12, BEAT * .8, 1.2), .8)
            CHORD.add(t, stab(tones, BEAT * .7, 1800 + (b - 2) * 1600 + k * 350), .6)
        continue

    if sec == 'outro':
        n = int((BAR + .8) * SR)
        PAD.add(t0, lp(sum(supersaw(m, BAR + .8) for m in tones) / 2, 1500) * env(n, .5, .8)[:, None], .5)
        BASS.add(t0, bass_note(root - 12, BAR * .9, .6), .55)
        for k, idx in enumerate([3, 2, 1, 0, 3, 2, 1, 2]):
            delay(FX, t0 + k * BEAT / 2, bell(tones[idx] + 24, 1.6), .15, (-.5, .5)[k % 2], taps=2)
        if b == 27:
            for k in (0, 1, 2, 3):
                DRUM.add(t0 + k * BEAT + .25, hat(True), .14 * (1 - k / 5))
        continue

    drop, g2, mid = sec == 'drop', sec == 'g2', sec == 'mid'
    # ---- drums
    if not breakdown:
        for k in range(4):
            if last_of and k == 3 and not drop:
                continue                                       # leave a gap before the next section
            add_kick(t0 + k * BEAT, 1.0)
        if drop or g2 or (sec == 'g1' and b >= 6) or (mid and b >= 21):
            for k in (1, 3):
                DRUM.add(t0 + k * BEAT, clap(), .5 if drop else .4)
        for k in range(4):                                     # off-beat hats
            DRUM.add(t0 + k * BEAT + .25, hat(drop or g2), .3 if drop else .24 if g2 else .2, .15)
        if drop or g2 or mid:
            for k in range(16):                                # 16th shaker
                if k % 4 != 2:
                    DRUM.add(t0 + k * .125, hat(), (.11 if k % 2 else .07) * (1.2 if drop else 1), (-.35, .35)[k % 2])
    # ---- bass: off-beats, with pick-ups in the drops
    if not breakdown:
        for k in range(4):
            BASS.add(t0 + k * BEAT + .25, bass_note(root - 12, .21, 1.3 if drop else .9), .8)
        if drop:
            for bt in (1.75, 3.75):
                BASS.add(t0 + bt * BEAT, bass_note(root, .11, 1.4), .55)
    # ---- chords
    cut = 5200 if drop else 2600 if g2 else 1500 if mid else 1150
    for bt, ln in STAB_AT:
        CHORD.add(t0 + bt * BEAT, stab(tones, ln * BEAT, cut * (.5 if breakdown else 1)), .62 if drop else .5)
    if drop:                                                   # sustained supersaw that pumps with the kick
        n = int(BAR * SR)
        PAD.add(t0, lp(sum(supersaw(m + 12, BAR) for m in tones) / 2, 6500) * env(n, .01, .05)[:, None], .5)
    elif g2 or mid:
        n = int((BAR + .3) * SR)
        PAD.add(t0, lp(sum(supersaw(m, BAR + .3) for m in tones) / 2, 1700) * env(n, .2, .3)[:, None], .34)
    # ---- arpeggio
    pg = .34 if (mid or drop) else .3 if g2 else .22
    for k, idx in enumerate(ARP):
        delay(PLUCK, t0 + k * .125, pluck(tones[idx] + 12 + (12 if (mid and k % 4 == 3) else 0)), pg * (1 if k % 2 == 0 else .7), (-.5, .5)[k % 2], taps=2)
    # ---- lead
    if drop:
        for bt, m, ln in MELODY[name]:
            delay(LEAD, t0 + bt * BEAT, lead_note(m, ln * BEAT), .42, .1, taps=2, fb=.35)
    if mid or g2:
        FX.add(t0, bell(tones[3] + 12), .16, (-.3, .3)[b % 2])
    # ---- builds into the next section
    if breakdown:
        roll(t0, t0 + BAR)
    elif last_of and sec == 'mid':
        roll(t0 + 1.0, t0 + BAR, .2, .6)
    elif last_of and not drop:
        roll(t0 + 1.5, t0 + BAR, .25, .5)

# section changes: risers before, crash + impact on the downbeat
for t, big in ((4, 1), (8, 2), (18, 1), (28, 3), (38, 1), (46, 3), (54, 2)):
    L = (1.0, 1.9, 3.6)[big - 1]
    FX.add(t - L, riser(L), (.22, .3, .42)[big - 1])
    c = crash()
    FX.add(t - 1.5, c[::-1][-int(1.5 * SR):], .16 * big / 2)       # reverse cymbal swell
    FX.add(t, c, (.3, .4, .5)[big - 1])
    FX.add(t, impact(), (.3, .45, .6)[big - 1])
FX.add(.5 - .012, shutter(), .7)
FX.add(48.0, bell(93, 2.0), .3)                               # light / dark switch
FX.add(48.0, bell(88, 2.0), .25, .4)
FX.add(58.6 - .012, shutter(), .5)

# ------------------------------------------------------------------ mix
t = np.arange(N) / SR
duck = np.ones(N)
for kt in kick_times:                                         # side-chain: everything breathes around the kick
    i = int(kt * SR)
    seg = np.arange(min(int(.36 * SR), N - i)) / SR
    duck[i:i + len(seg)] = np.minimum(duck[i:i + len(seg)], 1 - np.exp(-seg * 9))
duck = np.clip(duck, 0, 1)
strong, light = (.25 + .75 * duck)[:, None], (.6 + .4 * duck)[:, None]

music = (hp(BASS.a, 32) * .4 * strong + CHORD.a * .66 * strong + PAD.a * .52 * strong
         + PLUCK.a * .88 * light + LEAD.a * .86 * light)
send = CHORD.a * .3 * strong + PLUCK.a * .4 + LEAD.a * .5 + DRUM.a * .12 + FX.a * .5 + PAD.a * .2 * strong
ir_n = int(1.9 * SR)
tt = np.arange(ir_n) / SR
rev = np.stack([fftconvolve(send[:, ch], bp(rng.standard_normal(ir_n), 250, 7500) * np.exp(-tt / .5), mode='full')[:N] for ch in range(2)], 1)
mix = KICK.a * .5 + hp(DRUM.a, 250) * .7 + music + hp(FX.a, 30) * .5 + rev * .013
mix = hp(mix, 26)

fade = np.ones(N)
fade[:int(.12 * SR)] = np.linspace(0, 1, int(.12 * SR))
fo = int(2.3 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.6
mix *= fade[:, None]
mix /= np.abs(mix).max()
mix = np.tanh(mix * 2.3) / np.tanh(2.3)                       # glue + soft limiting for a loud, even master
mix *= .94 / np.abs(mix).max()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_portrait.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())

db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
print(f'> promo/music_portrait.wav  {DUR:.0f}s  peak {np.abs(mix).max():.2f}  rms {db(mix):.1f} dBFS')
for a, b_, nm in ((0, 4, 'intro'), (4, 8, 'hits'), (8, 18, 'groove'), (18, 26, 'groove 2'), (26, 28, 'build'), (28, 38, 'drop'), (38, 46, 'lighter'), (46, 54, 'drop 2'), (54, 60, 'outro')):
    print(f'   {a:4.0f}-{b_:2.0f}s {nm:9s} rms {db(mix[int(a * SR):int(b_ * SR)]):6.1f} dB')
m = mix.mean(1)
X = np.abs(np.fft.rfft(m)) ** 2
f = np.fft.rfftfreq(len(m), 1 / SR)
print('   bands: ' + '  '.join(f'{nm} {10 * np.log10(X[(f >= lo) & (f < hi)].sum() / X.sum()):.1f}' for nm, lo, hi in
                                (('sub', 0, 70), ('bass', 70, 250), ('lowmid', 250, 800), ('mid', 800, 3000), ('high', 3000, 8000), ('air', 8000, 22050))))
