# Timing plan + music bed + SFX for the EnCatalogo.pe vertical promo. Run from the project folder.
import json, os, re, subprocess, wave
import numpy as np
SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "audio")
SCENES = [["e1"], ["e2"], ["e3"], ["e4"], ["e5"], ["e6"], ["e7"], ["e8"], ["e9"]]
IN_GAP, SCENE_GAP, HEAD, TAIL = 0.3, 0.25, 0.5, 2.0

def sh(*a): return subprocess.run(a, check=True, capture_output=True, text=True)
def dur(p): return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p).stdout)
def speech(p, d):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=n=-35dB:d=0.22", "-f", "null", "-"], capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    out, cur = [], 0.0
    for a, b in zip(ss, se + [d] * (len(ss) - len(se))):
        if a - cur > 0.05: out.append([round(cur, 3), round(a, 3)])
        cur = b
    if d - cur > 0.05: out.append([round(cur, 3), round(d, 3)])
    return out

segs = {s["id"]: s for s in json.load(open(os.path.join(A, "segmentos.json")))}
t, scene_start, order = HEAD, [], []
for si, ids in enumerate(SCENES):
    if si: t += SCENE_GAP
    scene_start.append(round(t - (0.6 if si else HEAD), 3))
    for k, i in enumerate(ids):
        if k: t += IN_GAP
        p = os.path.join(A, "seg", i + ".wav"); d = dur(p)
        s = segs[i]; s["start"], s["dur"], s["speech"], s["scene"] = round(t, 3), round(d, 3), speech(p, d), si
        order.append(s); t += d
T = round(t + TAIL, 2)
json.dump(order, open(os.path.join(A, "segmentos.json"), "w"), ensure_ascii=False, indent=1)
plan = {"S": scene_start, "V": {s["id"]: s["start"] for s in order}, "D": {s["id"]: s["dur"] for s in order}, "T": T}
json.dump(plan, open(os.path.join(ROOT, "build", "plan.json"), "w"), indent=1)
print("T", T, "scenes", scene_start)

N = int(T * SR)
rng = np.random.default_rng(3)
def tt(d): return np.arange(int(d * SR)) / SR
def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf) or i < 0: return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += g * x
def smooth(x, k): return np.convolve(x, np.ones(k) / k, mode="same")
def pluck(f, d=1.0):
    x = tt(d); return np.exp(-x * 5) * (1 - np.exp(-x * 300)) * (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x))
def pad(fs, d, amp):
    x = tt(d); y = sum(np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 1.004 * x) for f in fs)
    return amp * y * np.minimum(1, x / 0.5) * np.minimum(1, (d - x) / 0.5)
def kick():
    x = tt(0.3); return np.sin(2 * np.pi * (45 + 55 * np.exp(-x * 30)) * x) * np.exp(-x * 10)
def hat():
    return smooth(rng.uniform(-1, 1, int(0.04 * SR)), 2) * np.exp(-tt(0.04) * 90)

# warm upbeat retail bed: Dmaj7 - Bm7 - Gmaj7 - A6 at 104 bpm
beat = 60 / 104; bar = 4 * beat
prog = [[146.83, 185.0, 220.0, 277.18], [123.47, 146.83, 185.0, 220.0], [98.0, 123.47, 146.83, 185.0], [110.0, 138.59, 164.81, 185.0]]
mus = np.zeros(N)
for b in range(int(T / bar) + 1):
    t0 = b * bar; ch = prog[b % 4]
    add(mus, pad(ch, bar + 0.5, 0.03), t0)
    for e in range(8):
        if e in (0, 2, 3, 5, 6):
            add(mus, pluck(ch[[0, 2, 1, 3, 2, 3, 1, 2][e]] * 4, 0.8), t0 + e * beat / 2, 0.05)
    for q in range(4):
        if q in (0, 2): add(mus, kick(), t0 + q * beat, 0.2)
        add(mus, hat(), t0 + q * beat + beat / 2, 0.035)
fi = int(1.5 * SR); mus[:fi] *= np.linspace(0, 1, fi)
fo = int(3.0 * SR); mus[-fo:] *= np.linspace(1, 0, fo)

fx = np.zeros(N)
def whoosh(d=0.6):
    x = tt(d); return smooth(rng.uniform(-1, 1, len(x)), 16) * np.sin(np.pi * x / d) ** 2 * 2
def pop(f0=520, f1=860):
    x = tt(0.09); return np.sin(2 * np.pi * (f0 + (f1 - f0) * x / 0.09) * x) * np.exp(-x * 40)
def click():
    x = tt(0.04); return np.sin(2 * np.pi * 2000 * x) * np.exp(-x * 120)
def chime(b=880):
    x = tt(2.0); return sum(a * np.sin(2 * np.pi * b * m * x) for a, m in ((1, 1), (0.5, 1.5), (0.25, 2))) * np.exp(-x * 2.5)
for s in scene_start[1:]:
    add(fx, whoosh(), s - 0.1, 0.4)
json.dump({"fx": "events in html.py"}, open(os.path.join(ROOT, "build", "fx.json"), "w"))
ev = json.load(open(os.path.join(ROOT, "build", "events.json"))) if os.path.exists(os.path.join(ROOT, "build", "events.json")) else []
for kind, at in ev:
    add(fx, {"pop": pop(), "click": click(), "chime": chime(), "chime2": chime(1046.5)}[kind], at, {"pop": 0.25, "click": 0.5, "chime": 0.3, "chime2": 0.3}[kind])

def save(path, x, peak):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    st = np.repeat((x * 32767).astype(np.int16)[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
save(os.path.join(A, "musica-raw.wav"), mus, 0.6)
sh("ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(A, "musica-raw.wav"), "-af", "loudnorm=I=-25:TP=-3:LRA=7", "-ar", "44100", os.path.join(A, "musica.wav"))
os.remove(os.path.join(A, "musica-raw.wav"))
save(os.path.join(A, "efectos.wav"), fx, 0.7)
sh("python3", os.path.join(A, "ducking.py"), os.path.join(A, "musica.wav"), os.path.join(A, "musica-duck.wav"), os.path.join(A, "segmentos.json"), os.path.join(A, "seg"))
print("audio ok")
