#!/usr/bin/env python3
"""make_sounds.py [out_dir] — generate the skill's own sound-effect pack as 48 kHz stereo wavs (default: ../sounds).

Roles (see references/sound.md): pop, click, whoosh, bell, low, ding, static, tick, tap, bass, sparkle, riser, hit,
typing (a ~1 s keystroke recording that render.slice_transients() cuts into single keys), plus a few variants so
repeated sounds don't feel copy-pasted. Pure numpy; deterministic. The user's own sounds always win: drop wavs named
sfx_<role>.wav into work/assets and example_make.py uses those instead.
"""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import (SR_HZ, tone_n, snd_tap, snd_click, snd_pop, snd_sparkle, snd_bass, snd_whoosh, snd_tick, write_wav)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sounds")
os.makedirs(out, exist_ok=True)
def tt(n): return np.arange(n) / SR_HZ
def bell():
    n = int(SR_HZ * 1.6); t = tt(n); x = sum(tone_n(f, n, tau, a) for f, tau, a in [(1568, .55, .5), (2349, .35, .3), (3136, .22, .2), (4700, .12, .1)])
    return x * 0.7
def low():
    n = int(SR_HZ * 1.8); t = tt(n); env = np.sin(np.pi * np.clip(t / 1.8, 0, 1)) ** 1.5
    x = np.sin(2 * np.pi * 55 * t) * 0.7 + np.sin(2 * np.pi * 82.4 * t) * 0.4 + np.sin(2 * np.pi * 110 * t) * 0.2
    return x * env * 0.9
def ding():
    n = int(SR_HZ * 1.4); return (tone_n(1318.5, n, .35, .6) + tone_n(1975.5, n, .25, .35) + tone_n(2637, n, .15, .15)) * 0.7
def static():
    n = int(SR_HZ * 0.4); rnd = np.random.RandomState(9); t = tt(n); x = rnd.randn(n) * 0.5
    x = x - np.convolve(x, np.ones(6) / 6, "same") * 0.7; return x * np.exp(-t / 0.25) * np.clip(t / 0.01, 0, 1)
def riser():
    n = int(SR_HZ * 1.5); t = tt(n); rnd = np.random.RandomState(12); x = rnd.randn(n)
    k = 40; x = x - np.convolve(x, np.ones(k) / k, "same"); env = (t / 1.5) ** 2.2; f = 300 + 2400 * (t / 1.5) ** 2
    return (x * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR_HZ) * 0.35) * env * np.clip((1.5 - t) / 0.03, 0, 1)
def hit():
    n = int(SR_HZ * 0.9); t = tt(n); rnd = np.random.RandomState(14); f = 90 * np.exp(-t / 0.08) + 45
    return (np.sin(2 * np.pi * np.cumsum(f) / SR_HZ) * np.exp(-t / 0.3) + rnd.randn(n) * np.exp(-t / 0.012) * 0.6) * 0.9
def pop2():
    n = int(SR_HZ * 0.14); t = tt(n); rnd = np.random.RandomState(16)
    f = 420 * np.exp(-t / 0.03) + 160; return (np.sin(2 * np.pi * np.cumsum(f) / SR_HZ) * np.exp(-t / 0.035) + rnd.randn(n) * np.exp(-t / 0.003) * 0.4) * 0.8
def whoosh2():
    n = int(SR_HZ * 0.4); t = tt(n); rnd = np.random.RandomState(18); x = rnd.randn(n); k = 12
    x = np.convolve(x, np.ones(k) / k, "same") - np.convolve(x, np.ones(k * 8) / (k * 8), "same"); return x * np.sin(np.pi * np.clip(t / 0.4, 0, 1)) ** 1.6 * 3.0
def typing():
    """~10 distinct keystrokes (mixed pitch / thock) spread over ~1 s, so slice_transients() finds individual keys."""
    rnd = np.random.RandomState(21); out = np.zeros(int(SR_HZ * 1.2))
    for i in range(10):
        n = int(SR_HZ * 0.05); t = tt(n); f = rnd.uniform(1100, 2300); k = (rnd.randn(n) * np.exp(-t / 0.0015) * 0.5 + tone_n(f, n, 0.004, 0.35) + tone_n(rnd.uniform(220, 380), n, 0.012, 0.4))
        j = int(SR_HZ * (0.05 + i * 0.105 + rnd.uniform(-0.01, 0.01))); out[j:j + n] += k * rnd.uniform(0.7, 1.0)
    return out * 0.6
PACK = {"pop": snd_pop, "pop2": pop2, "click": snd_click, "tap": snd_tap, "tick": snd_tick, "whoosh": snd_whoosh, "whoosh2": whoosh2, "bell": bell,
        "low": low, "ding": ding, "static": static, "bass": snd_bass, "sparkle": snd_sparkle, "riser": riser, "hit": hit, "typing": typing}
for name, fn in PACK.items():
    x = np.asarray(fn(), dtype=np.float64); x = x / (np.abs(x).max() + 1e-9) * 0.9          # each file peak-normalised; levels are set per role in make.py
    write_wav(os.path.join(out, f"sfx_{name}.wav"), x, master=1.0); print(f"  sfx_{name}.wav  {len(x) / SR_HZ:.2f}s")
print(f"{len(PACK)} sounds → {os.path.abspath(out)}")
