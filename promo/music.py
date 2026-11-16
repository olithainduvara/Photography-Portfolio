"""Synthesise the soundtrack for the reveal film -> promo/music.wav (45 s, stereo, 44.1 kHz).

Everything is generated here with numpy: no samples, no copyrighted material.
90 BPM, so one bar is 2.667 s and the scene cuts (5.33, 13.33, 21.33, 29.33, 34.67, 40 s) fall on bar lines.

    python promo/music.py
"""
import os, wave
import numpy as np

SR = 44100
DUR = 45.0
N = int(SR * DUR)
BEAT = 60 / 90
BAR = BEAT * 4
CUTS = [5.333, 13.333, 21.333, 29.333, 34.667, 40.0]
rng = np.random.default_rng(11)

dry = np.zeros((N, 2))      # goes straight to the mix
wet = np.zeros((N, 2))      # also sent to the reverb


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(buf, t, sig, gain=1.0, pan=0.0):
    """Mix a mono signal in at time t (seconds). pan: -1 left .. 1 right."""
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0:
        return
    sig = sig[:N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l
    buf[i:i + len(sig), 1] += sig * gain * r


def band(x, lo, hi):
    """Zero-phase band-pass with soft edges (FFT)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / (1 + (lo / np.maximum(f, 1e-6)) ** 6) / (1 + (f / hi) ** 6)
    return np.fft.irfft(X * g, len(x))


def env(n, a, r, curve=1.0):
    """Attack / release envelope over n samples."""
    e = np.ones(n)
    na, nr = min(int(a * SR), n), min(int(r * SR), n)
    if na:
        e[:na] = np.linspace(0, 1, na) ** curve
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e


# ------------------------------------------------------------------ instruments
def pad(notes, length, bright=1.0):
    """Warm detuned pad: stacked soft-saw voices, slow attack."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in notes:
        f0 = hz(m)
        for det, pan in ((-7, -.6), (0, 0), (7, .6)):
            f = f0 * 2 ** (det / 1200)
            v = np.zeros(n)
            for h in range(1, 9):
                if f * h > 7500 * bright:
                    break
                v += np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.28)) / h ** 1.4
            v *= 1 + .12 * np.sin(2 * np.pi * (.17 + m * .003) * t)
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            out[:, 0] += v * l
            out[:, 1] += v * r
    return out * env(n, min(.9, length * .35), min(1.1, length * .4))[:, None] / (len(notes) * 2.2)


def pluck(m, length=.9):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    v = np.sin(2 * np.pi * f * t) * np.exp(-t * 5.5) + .45 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 9) \
        + .2 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 14)
    v[:int(.004 * SR)] *= np.linspace(0, 1, int(.004 * SR))
    return v


def bell(m, length=2.6):
    """Soft FM bell."""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    v = np.sin(2 * np.pi * f * t + 1.6 * np.exp(-t * 3.5) * np.sin(2 * np.pi * f * 3.01 * t)) * np.exp(-t * 1.9)
    v[:int(.006 * SR)] *= np.linspace(0, 1, int(.006 * SR))
    return v


def bass(m, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    v = np.sin(2 * np.pi * f * t) + .28 * np.sin(2 * np.pi * 2 * f * t) + .08 * np.sin(2 * np.pi * 3 * f * t)
    return v * env(n, .012, min(.12, length * .3)) * np.exp(-t * 1.1)


def kick():
    n = int(.34 * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * (46 * t + (118 - 46) / 26 * (1 - np.exp(-26 * t)))
    return np.sin(ph) * np.exp(-t * 11) * env(n, .002, .05)


def rim():
    n = int(.16 * SR)
    t = np.arange(n) / SR
    return band(rng.standard_normal(n), 900, 5200) * np.exp(-t * 34) * env(n, .001, .02)


def hat(decay=70):
    n = int(.07 * SR)
    t = np.arange(n) / SR
    return band(rng.standard_normal(n), 6500, 15000) * np.exp(-t * decay)


def shutter():
    """Two quick mechanical clicks, like a camera shutter."""
    n = int(.22 * SR)
    out = np.zeros(n)
    for dt, g in ((0, 1.0), (.072, .8)):
        m = int(.06 * SR)
        t = np.arange(m) / SR
        c = band(rng.standard_normal(m), 1400, 7500) * np.exp(-t * 95) + .7 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 60)
        i = int(dt * SR)
        out[i:i + m] += c * g
    return out


def riser(length):
    """Air rising into a cut: bands of noise that open up from low to high."""
    n = int(length * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for k, (lo, hi) in enumerate(((180, 600), (600, 1800), (1800, 5000), (5000, 12000))):
        out += band(noise, lo, hi) * np.clip((t - k * .16) / (1 - k * .16), 0, 1) ** 2.4 * (1 - k * .12)
    return out * env(n, .05, .02)


def whoosh(length=.9):
    n = int(length * SR)
    t = np.linspace(-1, 1, n)
    return band(rng.standard_normal(n), 250, 7000) * np.exp(-(t / .34) ** 2)


def impact():
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (36 * t + (95 - 36) / 7 * (1 - np.exp(-7 * t)))) * np.exp(-t * 2.2)
    crash = band(rng.standard_normal(n), 2500, 13000) * np.exp(-t * 2.6) * .32
    return (sub + crash) * env(n, .003, .3)


def tick():
    n = int(.09 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (1250 * t + 700 / 30 * (1 - np.exp(-30 * t)))) * np.exp(-t * 38)


# ------------------------------------------------------------------ the arrangement
CH = {  # bass note, pad / arpeggio tones (MIDI)
    'Dm': (38, [50, 53, 57, 60, 64]),
    'Bb': (34, [46, 53, 57, 60, 62]),
    'F': (41, [48, 53, 57, 60, 64]),
    'C': (36, [48, 52, 55, 60, 62]),
}
BELL = {'Dm': [81, 77], 'Bb': [77, 74], 'F': [81, 79], 'C': [76, 79]}
bars = ['Dm', 'Dm'] + ['Dm', 'Bb', 'F', 'C'] * 3 + ['Dm', 'Bb', 'F']          # 17 bars = 45.3 s


def section(t):
    """Which scene the time belongs to: 0 intro .. 6 outro."""
    return sum(t >= c - 1e-3 for c in CUTS)


for b, name in enumerate(bars):
    t0 = b * BAR
    if t0 >= DUR:
        break
    root, tones = CH[name]
    s = section(t0)
    # pad: one chord per bar, overlapping its neighbours; brighter as the film builds
    p = pad(tones, BAR + 1.2, bright=(.55 if s == 0 else .8 if s in (1, 4) else 1.0))
    i = int(t0 * SR)
    seg = p[:max(0, N - i)]
    wet[i:i + len(seg)] += seg * (.5 if s == 0 else .62)
    if s == 0 or s == 6:
        if s == 6:                                             # outro: slow bell arpeggio over the last chords
            for k, m in enumerate([tones[1] + 12, tones[2] + 12, tones[3] + 12, tones[4] + 12]):
                add(wet, t0 + k * BEAT, bell(m, 3.2), .24, (-.5, .2, -.2, .5)[k])
            add(dry, t0, bass(root, BAR), .22)
        continue
    # bass: root on 1, a push before 3, octave lift at the end of the bar
    for bt, ln, m in ((0, 1.4, root), (1.5, .45, root), (2, 1.3, root), (3.5, .45, root + 12)):
        add(dry, t0 + bt * BEAT, bass(m, ln * BEAT), .27)
    # arpeggio: 8th notes through the chord tones, an octave up
    for k, idx in enumerate([0, 2, 1, 3, 2, 4, 3, 2]):
        add(wet, t0 + k * BEAT / 2, pluck(tones[idx] + 12), .25 if s != 4 else .3, (-.55, .55)[k % 2])
        add(wet, t0 + k * BEAT / 2 + BEAT * .75, pluck(tones[idx] + 12, .7), .09, (.55, -.55)[k % 2])     # echo
    # drums: build scene by scene, drop out for the tablet break (scene 4)
    if s != 4:
        for bt in ((0, 2) if s in (1, 2) else (0, 1, 2, 3)):
            add(dry, t0 + bt * BEAT, kick(), .46 if bt in (0, 2) else .37)
    if s in (2, 3, 5):
        for bt in (1, 3):
            add(wet, t0 + bt * BEAT, rim(), .3, .15)
    if s >= 2 and s != 4:
        step = .5 if s == 2 else .25
        for k in range(int(4 / step)):
            add(dry, t0 + k * step * BEAT, hat(60 if k % 2 else 95), (.075 if k % 2 == 0 else .115) * (1 if s != 2 else .8), (-.3, .3)[k % 2])
    # bells: a high note on 1 and 3 once the film opens up
    if s in (3, 5):
        add(wet, t0, bell(BELL[name][0]), .2, -.3)
        add(wet, t0 + 2 * BEAT, bell(BELL[name][1]), .16, .3)
    elif s in (2, 4):
        add(wet, t0, bell(BELL[name][0]), .14, .25)

# transitions and sound effects
for c, big in zip(CUTS, (True, False, True, False, False, True)):
    add(wet, c - (1.9 if big else 1.0), riser(1.9 if big else 1.0), .2 if big else .11)
    add(wet, c - .45, whoosh(), .3, -.4)
    if big:
        add(wet, c, impact(), .55)
add(wet, .55 - .012, shutter(), .85)                          # opening flash
add(wet, 44.05 - .012, shutter(), .6)                         # closing flash
for t, pan in ((36.52, 0), (36.72, -.6), (36.92, .6)):        # the three devices switch theme
    add(wet, t, tick(), .2, pan)

# ------------------------------------------------------------------ reverb, master
ir_n = int(2.3 * SR)
tt = np.arange(ir_n) / SR
mix = dry + wet * .82
for ch in range(2):
    ir = band(rng.standard_normal(ir_n), 180, 6500) * np.exp(-tt / .62)
    ir[:int(.012 * SR)] *= np.linspace(0, 1, int(.012 * SR))
    L = 1 << int(np.ceil(np.log2(N + ir_n)))
    rev = np.fft.irfft(np.fft.rfft(wet[:, ch], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, ch] += rev * .0105

mix *= env(N, .25, 1.15, 1.6)[:, None]                        # fade in, long fade out with the picture
mix /= np.abs(mix).max()
mix = np.tanh(mix * 1.55) / np.tanh(1.55)                     # gentle glue / soft limiting
mix *= .93 / np.abs(mix).max()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
rms = np.sqrt((mix ** 2).mean())
print(f'> promo/music.wav  {DUR:.0f}s  peak {np.abs(mix).max():.2f}  rms {20 * np.log10(rms):.1f} dBFS')
for a, b in zip([0] + CUTS, CUTS + [DUR]):
    seg = mix[int(a * SR):int(b * SR)]
    print(f'   {a:5.1f}-{b:5.1f}s  rms {20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9):6.1f} dB')
