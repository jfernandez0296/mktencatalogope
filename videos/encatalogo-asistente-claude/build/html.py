# EnCatalogo.pe — asistente conectado a Claude, vertical 9:16 (~57 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
import json, os, re, math, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
plan = json.load(open(os.path.join(ROOT, "build", "plan.json")))
segs = json.load(open(os.path.join(ROOT, "audio", "segmentos.json")))
SEG = {s["id"]: s for s in segs}
S, T = plan["S"], plan["T"]
CREAM, LIGHT, WHITE, INK = "#F2EDE4", "#FAF9F5", "#FFFFFF", "#0F0F10"
TERRA, TERRAD, SOFT, BORDER = "#D99873", "#A65353", "#F2E6CE", "#E7DDD1"
OK, BODY, MUTED, WA = "#3F7A4F", "#57534E", "#8A8178", "#25D366"

def p(i, k=0, off=0.0):
    s = SEG[i]; iv = s["speech"]; k = min(k, len(iv) - 1)
    return round(s["start"] + iv[k][0] + off, 3)
EV = []
def ev(kind, t): EV.append([kind, round(t, 3)])
def icon(name, size, color=INK, sw=2):
    src = open(os.path.join(IMG, f"icon-{name}.svg")).read()
    inner = src[src.index(">", src.index("<svg")) + 1: src.rindex("</svg>")]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-label="{name}">{inner}</svg>')
def logo(name, size, color):
    d = re.search(r'<path d="([^"]+)"', open(os.path.join(IMG, f"logo-{name}.svg")).read()).group(1)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" aria-label="{name}"><path d="{d}" fill="{color}"/></svg>'
MARK = lambda h: f'<img src="assets/img/encatalogo-logo.svg" alt="EnCatalogo.pe" style="height:{h}px;width:auto;display:block">'

# ---------------------------------------------------------------- captions (same engine as earlier projects)
HL = {"encatalogo", "reponer", "excel", "asistente", "claude", "inventario", "ventas", "productos", "talla", "tienda", "quedan",
      "resumen", "resultados", "vendiste", "moviendo", "reporte", "decidiendo", "números", "módulo", "cincuenta", "negocio", "gratis"}
def phrases(text):
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if re.search(r"[,.:;?!]$", w): out.append(cur); cur = []
    if cur: out.append(cur)
    return out
def chars(ws): return sum(len(w) + 1 for w in ws)
def align(s):
    ph, iv = phrases(s["text"]), [list(x) for x in s["speech"]]
    while len(ph) > len(iv):
        k = min(range(len(ph) - 1), key=lambda i: chars(ph[i]) + chars(ph[i + 1])); ph[k:k + 2] = [ph[k] + ph[k + 1]]
    while len(iv) > len(ph):
        k = min(range(len(iv) - 1), key=lambda i: iv[i + 1][0] - iv[i][1]); iv[k:k + 2] = [[iv[k][0], iv[k + 1][1]]]
    return ph, iv
caps, WT = [], {}
# word timings come from forced alignment (audio/alinear-palabras.py): s["words"] = [[w, start, end], ...]
for s in segs:
    wd = s["words"]; WT[s["id"]] = [(w_.lower().strip("¿¡,.:;?!"), s["start"] + a) for w_, a, b in wd]
    ph, cur = [], []
    for k, (w_, a, b) in enumerate(wd):
        cur.append(k)
        gap = wd[k + 1][1] - b if k + 1 < len(wd) else 9
        if re.search(r"[,.:;?!]$", w_) or gap > 0.25: ph.append(cur); cur = []
    if cur: ph.append(cur)
    for idx in ph:
        words = [wd[k][0] for k in idx]
        n = min(len(words), max(1, math.ceil(chars(words) / 22)))
        best = None
        for cut in itertools.combinations(range(1, len(words)), n - 1):
            gs = [list(range(i, j)) for i, j in zip((0,) + cut, cut + (len(words),))]
            sc = max(chars([words[q] for q in x]) for x in gs) + (8 if any(len(x) == 1 and len(words[x[0]]) < 6 for x in gs) else 0)
            if best is None or sc < best[0]: best = (sc, gs)
        for x in best[1]:
            caps.append([s["start"] + wd[idx[x[0]]][1], s["start"] + wd[idx[x[-1]]][2], [words[q] for q in x]])
def W(i, word, off=0.0, nth=0):
    hits = [t for w_, t in WT[i] if w_.startswith(word)]
    if not hits: raise SystemExit(f"palabra no encontrada: {i} {word}")
    return round(hits[min(nth, len(hits) - 1)] + off, 3)
for i in range(len(caps)):
    nxt = caps[i + 1][0] if i + 1 < len(caps) else caps[i][1] + 0.4
    caps[i][1] = min(nxt, caps[i][1] + 0.35) if nxt - caps[i][1] > 0.7 else nxt
    caps[i][1] = min(caps[i][1], nxt - 0.05)
def cw(w):
    k = re.sub(r"[^\wáéíóúñ]", "", w.lower())
    w = w.replace("EnCatalogo", "EnCatalogo")
    return f"<b>{w}</b>" if k in HL else w
CAPS = "\n".join(f'      <div class="cap" id="cap{i}" data-layout-allow-overlap="true"><span>{" ".join(cw(w) for w in c[2])}</span></div>' for i, c in enumerate(caps))
CAPJS = "\n".join(f'      capShow("#cap{i}", {c[0]:.3f}, {c[1]:.3f});' for i, c in enumerate(caps))

# ---------------------------------------------------------------- pieces
def head(sid, kick, title, dark=False, top=250, size=92):
    tc = WHITE if dark else INK
    badge = f'<div class="abs badge{" dk" if dark else ""}" id="{sid}k" style="left:70px;top:{top}px">{kick}</div>'
    return badge + f'<div class="abs ttl" id="{sid}t" style="left:70px;top:{top + 80}px;width:940px;font-size:{size}px;color:{tc}">{title}</div>'
BRAND = lambda sid, dark=False: (f'<div class="abs brand" id="{sid}br" style="left:70px;top:130px;color:{WHITE if dark else INK}">'
                                 f'<span class="bchip{" dk" if dark else ""}">{MARK(54)}</span>EnCatalogo.pe</div>')
TM = lambda top, dark=False: f'<div class="abs illu{" dk" if dark else ""}" style="left:70px;top:{top}px">Recreación ilustrativa · Claude es una marca de Anthropic</div>'
def asst(status="conectado a Claude"):
    return (f'<div class="abs ahd"><span class="cl">{logo("claude", 40, TERRA)}</span>'
            f'<div><b>Asistente EnCatalogo</b><i>{status}</i></div></div>')

# A · hook: an afternoon of Excel
cols = ["Producto", "Talla", "Tienda", "Stock", "Vend."]
sheet_rows = "".join(
    f'<div class="srow" id="Ar{r}">' + "".join(f'<span class="scell{" w" if c == 0 else ""}"></span>' for c in range(5)) + '</div>'
    for r in range(18))
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "ASISTENTE CON CLAUDE", "¿Qué debo reponer esta semana?", top=290, size=100)}
        <div class="abs card sheet" id="Asheet" style="left:70px;top:700px;width:940px;height:640px">
          <div class="abs xlbar"><span class="xl">X</span>inventario_semana_final_v3.xlsx</div>
          <div class="abs shead">{"".join(f'<span class="scell{" w" if i == 0 else ""}">{c}</span>' for i, c in enumerate(cols))}</div>
          <div class="abs sview"><div class="sbody">{sheet_rows}</div></div>
        </div>
        <div class="abs clockpill" id="Aclk" style="left:640px;top:630px">{icon("clock", 44, WHITE)}<span id="Ahr">14:00</span></div>
      </div>'''

# B · ask the assistant
B = f'''      <div class="sc" id="sB" style="background:{INK}">
        {head("B", "PREGÚNTALE A TU NEGOCIO", "Ahora se lo preguntas a tu asistente", True, size=88)}
        <div class="abs achat" id="Bchat" style="left:70px;top:620px;width:940px;height:460px">
          {asst()}
          <div class="abs ask" id="Bq" style="right:36px;top:170px">¿Qué debo reponer esta semana?</div>
          <div class="abs typing" id="Bty" style="left:36px;top:300px"><i></i><i></i><i></i></div>
        </div>
        <div class="abs cbadge" id="Bcl" style="left:70px;top:1130px"><span class="cl">{logo("claude", 46, TERRA)}</span>Conectado a <b>Claude</b></div>
        {TM(1270, True)}
      </div>'''

# C · concrete answer
rows = [("Blazer Siena", "Talla S", "Miraflores", "3"), ("Vestido Mía", "Talla M", "San Isidro", "2"), ("Jean Araña", "Talla 30", "Almacén", "4")]
C = f'''      <div class="sc" id="sC" style="background:{LIGHT}">
        {head("C", "CON TUS DATOS", "Te responde con productos concretos", size=86)}
        <div class="abs achat lt" id="Cchat" style="left:70px;top:610px;width:940px;height:780px">
          {asst("respondiendo")}
          <div class="abs ask sm" style="right:36px;top:150px">¿Qué debo reponer esta semana?</div>
          <div class="abs ansc" id="Cans" style="left:36px;top:260px;width:868px">
            <div class="alead">Te recomiendo reponer:</div>
            {"".join(f'<div class="arow" id="Cr{i}"><span class="an">{icon("shirt", 40, TERRAD, 1.6)}</span><b>{p}</b><span class="tz" id="Cz{i}">{t}</span><span class="tg" id="Ct{i}">{icon("store", 26, MUTED)}{s}</span><em id="Cq{i}">quedan {q}</em></div>' for i, (p, t, s, q) in enumerate(rows))}
          </div>
        </div>
        {TM(1420)}
      </div>'''

# D · weekly summary
bars = [48, 62, 55, 70, 84, 100, 66]
D = f'''      <div class="sc" id="sD" style="background:{CREAM}">
        {head("D", "RESUMEN DE RESULTADOS", "Pídele un resumen. Sin reportes.", size=86)}
        <div class="abs ask" id="Dq" style="right:70px;top:600px">Dame un resumen de la semana</div>
        <div class="abs card" id="Dcard" style="left:70px;top:720px;width:940px;height:600px">
          <div class="abs eyebrow" style="left:44px;top:44px">VENDISTE ESTA SEMANA</div>
          <div class="abs big" style="left:44px;top:90px">S/ <span id="Dsales">18.450</span></div>
          {"".join(f'<div class="abs bar" id="Db{i}" style="left:{560 + i * 52}px;top:{230 - h * 1.5:.0f}px;height:{h * 1.5:.0f}px;width:36px{";background:" + TERRAD if i == 5 else ""}"></div>' for i, h in enumerate(bars))}
          <div class="abs eyebrow" style="left:44px;top:290px">LO QUE MÁS SE MUEVE</div>
          {"".join(f'<div class="abs mv" id="Dm{i}" style="left:44px;top:{340 + i * 110}px;width:852px"><span class="rk">{i + 1}</span><b>{n}</b><i>{u} uds.</i></div>' for i, (n, u) in enumerate([("Vestido Emilia", 64), ("Polo Lima", 51)]))}
        </div>
        <div class="abs nope" id="Dno" style="left:70px;top:1360px">{icon("x", 30, WHITE, 3)}<span>Armar el reporte a mano<em id="Dnol"></em></span></div>
      </div>'''

# E · you decide
E = f'''      <div class="sc" id="sE" style="background:{INK}">
        <div class="abs badge dk" id="Ek" style="left:70px;top:330px">TÚ AL MANDO</div>
        <div class="abs bigline" id="E1" style="left:70px;top:460px;color:{WHITE}">Tú decides.</div>
        <div class="abs bigline it" id="E2" style="left:70px;top:620px;color:{TERRA}">El asistente busca los números.</div>
        <div class="abs dec" id="Edec" style="left:70px;top:1000px;width:940px">
          <div><b>Reponer Blazer Siena · Talla S</b><span>Sugerido por tu asistente</span></div>
          <div class="okbtn" id="Eok">{icon("check", 34, WHITE, 3)} Aprobar</div>
        </div>
      </div>'''

# F · price
F = f'''      <div class="sc" id="sF" style="background:{LIGHT}">
        {head("F", "MÓDULO", "Asistente conectado a Claude")}
        <div class="abs card" id="Fcard" style="left:70px;top:560px;width:940px;height:640px">
          <div class="abs cl" style="left:50px;top:50px;width:90px;height:90px;background:{SOFT};border-radius:24px">{logo("claude", 54, TERRAD)}</div>
          <div class="abs price" style="left:50px;top:180px"><small>S/</small><span id="Fp">50</span><i>/mes</i></div>
          {"".join(f'<div class="abs hl" id="Fl{i}" style="left:50px;top:{400 + i * 72}px">{icon("circle-check", 38, TERRAD)}<span>{t}</span></div>' for i, t in enumerate(["Pregúntale qué reponer", "Pídele un resumen de resultados", "Se suma a tu plan de EnCatalogo"]))}
        </div>
        <div class="abs fine" style="left:70px;top:1240px">Precios en soles · IGV incluido · Claude es una marca de Anthropic</div>
      </div>'''

# G · close
G = f'''      <div class="sc" id="sG" style="background:{CREAM}">
        <div class="abs" id="Glg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Gwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Gt1" style="left:0;top:770px;width:1080px">Pregúntale</div>
        <div class="abs tag2" id="Gt2" style="left:0;top:880px;width:1080px">a tu negocio.</div>
        <div class="abs cta" id="Gcta" style="left:240px;top:1060px;width:600px">Probar 7 días gratis</div>
        <div class="abs ctas" id="Gsub" style="left:0;top:1190px;width:1080px">Sin tarjeta · encatalogo.pe</div>
        <div class="abs illu" style="left:0;top:1300px;width:1080px;text-align:center">Claude es una marca de Anthropic</div>
      </div>'''
SCENES_HTML = [A, B, C, D, E, F, G]

# ---------------------------------------------------------------- timeline
J = []
def js(s): J.append("      " + s)
def show(sel, t, d=0.45, y=30): js(f'tl.fromTo("{sel}", {{ autoAlpha: 0, y: {y} }}, {{ autoAlpha: 1, y: 0, duration: {d}, ease: "power3.out" }}, {t:.3f});')
def popin(sel, t, d=0.4, snd=True):
    js(f'tl.fromTo("{sel}", {{ autoAlpha: 0, scale: 0.7 }}, {{ autoAlpha: 1, scale: 1, duration: {d}, ease: "back.out(1.8)" }}, {t:.3f});')
    if snd: ev("pop", t)
def slide(sel, t, x=-80, snd=True):
    js(f'tl.fromTo("{sel}", {{ autoAlpha: 0, x: {x} }}, {{ autoAlpha: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {t:.3f});')
    if snd: ev("pop", t)
def wipe(sel, prev, t):
    js(f'tl.set("{sel}", {{ autoAlpha: 1 }}, {t:.3f});')
    js(f'tl.fromTo("{sel}", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "power3.inOut" }}, {t:.3f});')
    js(f'tl.set("{prev}", {{ autoAlpha: 0 }}, {t + 0.65:.3f});')
def count(sel, t, frm, to, d=1.0):
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v).toLocaleString("en-US").replace(/,/g, "."); }} }}, {t:.3f}); }})();')
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)

# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
show("#Asheet", W("e1", "antes", -0.3), 0.5, 60)
js(f'tl.fromTo("#Asheet .srow", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, duration: 0.12, stagger: 0.08 }}, {W("e1", "antes", 0.1):.3f});')
popin("#Aclk", W("e1", "tarde", -0.2), 0.4)
tc0, tc1 = W("e1", "tarde", 0.1), W("e1", "excel", 0.6)
js(f'(() => {{ const o = {{ v: 0 }}; tl.to(o, {{ v: 300, duration: {tc1 - tc0:.2f}, ease: "power1.in", onUpdate: () => {{ const m = 14 * 60 + Math.round(o.v); document.querySelector("#Ahr").textContent = Math.floor(m / 60) + ":" + String(m % 60).padStart(2, "0"); }} }}, {tc0:.3f}); }})();')
js(f'tl.to("#Asheet .sbody", {{ y: -480, duration: {tc1 - tc0:.2f}, ease: "power1.inOut" }}, {tc0:.3f});')
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
show("#Bchat", W("e2", "ahora", 0.0), 0.5, 60)
popin("#Bq", W("e2", "preguntas", -0.1), 0.4); ev("click", W("e2", "preguntas", -0.1))
show("#Bty", W("e2", "asistente", 0.1), 0.3, 10)
js(f'tl.fromTo("#Bty i", {{ y: 0 }}, {{ y: -10, duration: 0.25, stagger: 0.1, yoyo: true, repeat: 7, ease: "sine.inOut" }}, {W("e2", "asistente", 0.2):.3f});')
popin("#Bcl", W("e2", "claude", -0.2), 0.45); ev("chime2", W("e2", "claude", -0.2))
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
show("#Cchat", S[2] + 0.6, 0.5, 60)
show("#Cans", W("e3", "responde", -0.2), 0.45, 30)
for i in range(3): slide(f"#Cr{i}", W("e3", "productos", -0.1 + i * 0.2), -60, i == 0)
js(f'tl.fromTo(["#Cz0", "#Cz1", "#Cz2"], {{ backgroundColor: "{SOFT}" }}, {{ backgroundColor: "{TERRA}", color: "{WHITE}", duration: 0.3, stagger: 0.08 }}, {W("e3", "talla", -0.05):.3f});'); ev("pop", W("e3", "talla", -0.05))
js(f'tl.fromTo(["#Ct0", "#Ct1", "#Ct2"], {{ color: "{MUTED}" }}, {{ color: "{INK}", duration: 0.3, stagger: 0.08 }}, {W("e3", "tienda", -0.05):.3f});'); ev("pop", W("e3", "tienda", -0.05))
js(f'tl.fromTo(["#Cq0", "#Cq1", "#Cq2"], {{ autoAlpha: 0, scale: 0.6 }}, {{ autoAlpha: 1, scale: 1, duration: 0.3, stagger: 0.1, ease: "back.out(2)" }}, {W("e3", "cuántas", -0.05):.3f});'); ev("chime2", W("e3", "cuántas", 0.1))
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
popin("#Dq", W("e4", "resumen", -0.3), 0.4); ev("click", W("e4", "resumen", -0.3))
show("#Dcard", W("e4", "resultados", -0.1), 0.5, 60)
count("#Dsales", W("e4", "cuánto", -0.1), 0, 18450, 1.2)
js(f'tl.fromTo("#sD .bar", {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 0.45, stagger: 0.05, ease: "power2.out" }}, {W("e4", "vendiste"):.3f});')
for i in range(2): slide(f"#Dm{i}", W("e4", "moviendo", -0.5 + i * 0.25), -60, i == 0)
slide("#Dno", W("e4", "sin", -0.1), -60, False)
js(f'tl.fromTo("#Dnol", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.35, ease: "power2.out" }}, {W("e4", "reporte", 0.0):.3f});'); ev("click", W("e4", "reporte"))
# E
wipe("#sE", "#sD", S[4])
show("#Ek", S[4] + 0.5, 0.4, 20)
show("#E1", W("e5", "tú", -0.1), 0.5, 40)
show("#E2", W("e5", "asistente", -0.1), 0.5, 40)
show("#Edec", W("e5", "ahorra", -0.2), 0.45, 40)
js(f'tl.to("#Eok", {{ scale: 0.92, duration: 0.09, yoyo: true, repeat: 1 }}, {W("e5", "números", 0.2):.3f});'); ev("click", W("e5", "números", 0.2))
js(f'tl.to("#Eok", {{ backgroundColor: "{OK}", duration: 0.25 }}, {W("e5", "números", 0.3):.3f});'); ev("chime2", W("e5", "números", 0.3))
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
show("#Fcard", W("e6", "módulo", -0.4), 0.5, 60)
count("#Fp", W("e6", "cincuenta", -0.1), 0, 50, 0.8); ev("pop", W("e6", "cincuenta", -0.1))
for i, (w_, off) in enumerate([("mes", 0.3), ("suma", -0.6), ("suma", -0.1)]): slide(f"#Fl{i}", W("e6", w_, off), -60)
# G
wipe("#sG", "#sF", S[6])
popin("#Glg", S[6] + 0.35, 0.6); show("#Gwm", W("e7", "encatalogo", 0.2), 0.45, 20)
show("#Gt1", W("e7", "pregúntale", -0.1), 0.5, 30); show("#Gt2", W("e7", "negocio", -0.2), 0.5, 30)
popin("#Gcta", W("e7", "prueba", -0.15), 0.5); ev("chime", W("e7", "prueba", -0.15))
show("#Gsub", W("e7", "sin", -0.1), 0.4, 15)
js(f'tl.to("#Gcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e7", "sin", 0.6):.3f});')


json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — asistente Claude</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-fps="30" data-width="1080" data-height="1920">
{chr(10).join(SCENES_HTML)}
{CAPS}
{"".join(f'      <audio id="v_{s["id"]}" src="audio/seg/{s["id"]}.wav" data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="12" data-volume="1"></audio>{chr(10)}' for s in segs)}      <audio id="musica-fondo" src="audio/musica-duck.wav" data-start="0" data-duration="{T}" data-track-index="13" data-volume="0.8"></audio>
      <audio id="efectos-sonido" src="audio/efectos.wav" data-start="0" data-duration="{T}" data-track-index="14" data-volume="0.45"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const capShow = (sel, a, b) => {{
        tl.fromTo(sel, {{ autoAlpha: 0, y: 12, scale: 0.96 }}, {{ autoAlpha: 1, y: 0, scale: 1, duration: 0.15, ease: "back.out(2)" }}, a - 0.04);
        tl.set(sel, {{ autoAlpha: 0 }}, b);
      }};
{chr(10).join(J)}
{CAPJS}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("captions", len(caps), "events", len(EV))
