# EnCatalogo.pe — No es para todos (para quién es), vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "todos", "medida", "persona", "tampoco", "precio", "whatsapp", "catálogo", "fotos", "caja", "sí", "inventario", "ventas", "lugar", "stock", "excel", "celular", "ciento", "cincuenta", "permanencia", "gratis", "reconociste"}
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
    kc = TERRA if dark else TERRAD
    tc = WHITE if dark else INK
    badge = f'<div class="abs badge{" dk" if dark else ""}" id="{sid}k" style="left:70px;top:{top}px">{kick}</div>'
    return badge + f'<div class="abs ttl" id="{sid}t" style="left:70px;top:{top + 80}px;width:940px;font-size:{size}px;color:{tc}">{title}</div>'
BRAND = lambda sid, dark=False: (f'<div class="abs brand" id="{sid}br" style="left:70px;top:130px;color:{WHITE if dark else INK}">'
                                 f'<span class="bchip{" dk" if dark else ""}">{MARK(54)}</span>EnCatalogo.pe</div>')
def chip(sid, ic, text, x, y, bg=WHITE, fg=INK, icc=TERRAD, extra=""):
    return f'<div class="abs chip" id="{sid}" style="left:{x}px;top:{y}px;background:{bg};color:{fg}">{icon(ic, 40, icc)}<span>{text}</span>{extra}</div>'

def strike(sid, text, top, dark=False):
    return (f'<div class="abs strike{" dk" if dark else ""}" id="{sid}x" style="left:70px;top:{top}px">'
            f'<span class="sx">{icon("x", 30, WHITE, 3)}</span><span class="st"><i>Un chatbot:</i> {text}<em id="{sid}xl"></em></span></div>')
def chathead(name="Tienda Demo", status="en línea"):
    return f'<div class="abs chd"><span class="wa">{logo("whatsapp", 40, WHITE)}</span><div><b>{name}</b><i>{status}</i></div></div>'

# A · hook — honest disclaimer
ROWS = 6
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "¿ES PARA TI?", "No es para todos.", top=290, size=128)}
        <div class="abs card" id="Acard" style="left:70px;top:620px;width:940px;height:760px">
          <div class="abs eyebrow" style="left:50px;top:50px">ANTES DE PROBAR, REVISA ESTO</div>
          {"".join(f'<div class="abs prow" id="Ar{i}" style="left:50px;top:{120 + i * 100}px"><i class="pdot"></i><span class="pline" style="width:{[620, 520, 700, 460, 580, 640][i]}px"></span></div>' for i in range(ROWS))}
        </div>
        <div class="abs clock" id="Aclk" style="left:70px;top:1410px">{icon("clock", 34, TERRAD)} Te ahorramos tiempo</div>
      </div>'''

# B · not for you (dark)
def nocard(sid, top, title, sub_html):
    return (f'<div class="abs vs bot nocard" id="{sid}" style="left:70px;top:{top}px;width:940px">'
            f'<div class="vh">{icon("x", 34, MUTED, 3)} NO ES PARA TI</div>'
            f'<div class="vt">{title}<em id="{sid}l"></em></div>{sub_html}'
            f'<div class="abs nox" id="{sid}x">{icon("x", 70, WHITE, 3.2)}</div></div>')
B = f'''      <div class="sc" id="sB" style="background:{INK}">
        {head("B", "NO ES PARA TI SI…", "Mejor te lo decimos antes.", True, size=90)}
        {nocard("Bn0", 600, "Cotizas cada trabajo a medida", f'<div class="qrow"><span class="qtag">{icon("receipt", 30, MUTED)} Cotización</span><span class="qtag">Precio: a convenir</span></div>')}
        {nocard("Bn1", 1000, "Cierras tus ventas solo en persona", f'<div class="qrow"><span class="qtag">{icon("users", 30, MUTED)} Solo cara a cara</span></div>')}
      </div>'''

# C · yes for you
YES = [("receipt", "Vendes productos con precio"), ("whatsapp", "Tus clientes te escriben por WhatsApp"),
       ("camera", "Tienes catálogo, aunque sea en fotos"), ("store", "Quieres vender en tienda física con caja")]
def yicon(n): return logo("whatsapp", 46, WA) if n == "whatsapp" else icon(n, 46, TERRAD)
C = f'''      <div class="sc" id="sC" style="background:{LIGHT}">
        {head("C", "SÍ ES PARA TI SI…", "¿Te reconoces?")}
        {"".join(f'<div class="abs yrow" id="Cy{i}" style="left:70px;top:{580 + i * 205}px;width:940px"><span class="yi">{yicon(n)}</span><span class="yt">{t}</span><span class="yc" id="Cc{i}">{icon("check", 40, WHITE, 3.2)}</span></div>' for i, (n, t) in enumerate(YES))}
      </div>'''

# D · then yes: all in one place
TILES = [("package", "Inventario"), ("wallet", "Caja"), ("trending-up", "Ventas")]
D = f'''      <div class="sc" id="sD" style="background:{CREAM}">
        {head("D", "ENTONCES SÍ", "Todo en un solo lugar")}
        <div class="abs hub" id="Dhub" style="left:340px;top:590px">{MARK(250)}</div>
        <svg class="abs" id="Dln" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920">
          {"".join(f'<path id="Dl{i}" d="M540 880 L{225 + i * 315} 1010" stroke="{TERRA}" stroke-width="5" stroke-linecap="round" fill="none" stroke-dasharray="180" stroke-dashoffset="180"/>' for i in range(3))}
        </svg>
        {"".join(f'<div class="abs upd" id="Du{i}" style="left:{70 + i * 315}px;top:1020px;width:300px"><div class="ich">{icon(ic, 46, TERRAD)}</div><span>{t}</span><div class="tick" id="Dt{i}">{icon("check", 26, WHITE, 3)}</div></div>' for i, (ic, t) in enumerate(TILES))}
        <div class="abs dsub" id="Dsub" style="left:0;top:1250px;width:1080px">Tu mercadería en orden. Tu negocio bajo control.</div>
      </div>'''

# E · AI seller + catalog upload (dark)
E = f'''      <div class="sc" id="sE" style="background:{INK}">
        {head("E", "VENDEDOR IA · CATÁLOGO", "Vende por WhatsApp desde tu catálogo", True, size=84)}
        <div class="abs chat" id="Echat" style="left:70px;top:600px;width:940px;height:560px">
          {chathead()}
          <div class="abs bub in" id="Em0" style="top:150px">¿Tienes el Vestido Emilia en talla M?</div>
          <div class="abs bub out ph" id="Em1" style="top:270px"><div class="thumb">{icon("shirt", 64, TERRAD, 1.6)}</div><div><b>Vestido Emilia</b><span>S/ 189.00 · Tallas S · M · L</span></div></div>
          <div class="abs paid" id="Eok" style="top:450px">{icon("package", 34, OK)} Stock real · quedan 4 en talla M</div>
        </div>
        <div class="abs eyebrow" id="Eey" style="left:70px;top:1210px;color:{TERRA}">SUBE TU CATÁLOGO</div>
        <div class="abs chip" id="Es0" style="left:70px;top:1270px;background:#FFFFFF;color:#0F0F10">{icon("receipt", 40, TERRAD)}<span>Desde Excel</span></div>
        <div class="abs chip" id="Es1" style="left:440px;top:1270px;background:#FFFFFF;color:#0F0F10">{icon("camera", 40, TERRAD)}<span>Con fotos del celular</span></div>
        <div class="abs illu" style="left:70px;top:1410px;color:#B9B2A8">Recreación ilustrativa</div>
      </div>'''

# F · pricing
F = f'''      <div class="sc" id="sF" style="background:{LIGHT}">
        {head("F", "PRECIO", "Un solo plan. Sin permanencia.")}
        <div class="abs card" id="Fcard" style="left:70px;top:580px;width:940px;height:640px">
          <div class="abs eyebrow" style="left:50px;top:50px">ENCATALOGO</div>
          <div class="abs price" style="left:50px;top:110px"><small>S/</small><span id="Fp">150</span><i>/mes con 1 tienda</i></div>
          {"".join(f'<div class="abs hl" id="Fl{i}" style="left:50px;top:{330 + i * 82}px">{icon("circle-check", 38, TERRAD)}<span>{t}</span></div>' for i, t in enumerate(["IGV incluido", "Sin permanencia", "Cancelas cuando quieras"]))}
        </div>
        <div class="abs fine" style="left:70px;top:1260px">Precios en soles · S/ 90 cada tienda extra · almacenes gratis</div>
      </div>'''

# G · close
G = f'''      <div class="sc" id="sG" style="background:{CREAM}">
        <div class="abs" id="Glg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Gwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Gt1" style="left:0;top:770px;width:1080px">¿Te reconociste?</div>
        <div class="abs tag2" id="Gt2" style="left:0;top:880px;width:1080px">Empieza gratis hoy.</div>
        <div class="abs cta" id="Gcta" style="left:240px;top:1060px;width:600px">Crear mi cuenta</div>
        <div class="abs ctas" id="Gsub" style="left:0;top:1190px;width:1080px">7 días gratis · sin tarjeta · encatalogo.pe</div>
      </div>'''

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
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v); }} }}, {t:.3f}); }})();')
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)
def line(sel, t, d=0.4): js(f'tl.fromTo("{sel}", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: {d}, ease: "power2.out" }}, {t:.3f});')

# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.6, 50)
js(f'tl.to("#At", {{ scale: 1.04, transformOrigin: "0% 50%", duration: 0.25, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {W("e1", "todos", -0.1):.3f});'); ev("click", W("e1", "todos", -0.1))
show("#Acard", W("e1", "preferimos", -0.2), 0.5, 60)
js(f'tl.fromTo("#sA .prow", {{ autoAlpha: 0, x: -30 }}, {{ autoAlpha: 1, x: 0, duration: 0.35, stagger: 0.12, ease: "power3.out" }}, {W("e1", "decírtelo", -0.1):.3f});')
popin("#Aclk", W("e1", "tiempo", -0.25), 0.4)
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
js('gsap.set([".nox"], { autoAlpha: 0 });')
show("#Bn0", W("e2", "cotizas", -0.3), 0.5, 50)
line("#Bn0l", W("e2", "precios", -0.1)); ev("click", W("e2", "precios", -0.1))
popin("#Bn0x", W("e2", "ti", -0.25), 0.4)
js(f'tl.to("#Bn0", {{ opacity: 0.6, duration: 0.4 }}, {W("e2", "ti", 0.3):.3f});')
show("#Bn1", W("e3", "si", -0.25), 0.5, 50)
line("#Bn1l", W("e3", "persona", 0.0)); ev("click", W("e3", "persona", 0.0))
popin("#Bn1x", W("e3", "tampoco", -0.1), 0.4)
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
js('gsap.set(["#sC .yc"], { autoAlpha: 0 });')
for i, (w_, sid, nth) in enumerate([("productos", "e4", 0), ("clientes", "e4", 0), ("catálogo", "e5", 0), ("tienda", "e5", 0)]):
    slide(f"#Cy{i}", W(sid, w_, -0.45), -60, False)
for i, (w_, sid) in enumerate([("precio", "e4"), ("whatsapp", "e4"), ("fotos", "e5"), ("caja", "e5")]):
    popin(f"#Cc{i}", W(sid, w_, 0.0), 0.35)
    js(f'tl.to("#Cy{i}", {{ borderColor: "{OK}", duration: 0.3 }}, {W(sid, w_, 0.0):.3f});')
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
js('gsap.set(["#sD .tick"], { autoAlpha: 0 });')
popin("#Dhub", W("e6", "sí", -0.1), 0.55); ev("chime", W("e6", "sí", -0.1))
for i, w_ in enumerate(["inventario", "caja", "ventas"]):
    js(f'tl.to("#Dl{i}", {{ strokeDashoffset: 0, duration: 0.35, ease: "power2.out" }}, {W("e6", w_, -0.35):.3f});')
    slide(f"#Du{i}", W("e6", w_, -0.2), 0, False); popin(f"#Dt{i}", W("e6", w_, 0.15), 0.3)
show("#Dsub", W("e6", "solo", -0.2), 0.45, 20)
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
show("#Echat", W("e7", "vendedor", -0.2), 0.5, 60)
popin("#Em0", W("e7", "responde", -0.1), 0.35)
popin("#Em1", W("e7", "fotos", -0.2), 0.4)
popin("#Eok", W("e7", "stock", -0.1), 0.4); ev("chime2", W("e7", "stock", -0.1))
show("#Eey", W("e7", "catálogo", -0.3), 0.4, 15)
slide("#Es0", W("e7", "excel", -0.15), -60); slide("#Es1", W("e7", "celular", -0.4), 60)
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
show("#Fcard", W("e8", "plan", -0.1), 0.5, 60)
count("#Fp", W("e8", "ciento", -0.1), 0, 150, 0.9)
for i, (w_, nth) in enumerate([("igv", 0), ("permanencia", 0), ("cancelas", 0)]): slide(f"#Fl{i}", W("e8", w_, -0.15, nth), -60)
# G
wipe("#sG", "#sF", S[6])
popin("#Glg", S[6] + 0.35, 0.6); show("#Gwm", S[6] + 0.7, 0.45, 20)
show("#Gt1", W("e9", "te", -0.15), 0.5, 30); show("#Gt2", W("e9", "prueba", -0.15), 0.5, 30)
popin("#Gcta", W("e9", "crea", -0.1), 0.5); ev("chime", W("e9", "crea", -0.1))
show("#Gsub", W("e9", "siete", -0.1), 0.4, 15)
js(f'tl.to("#Gcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e9", "tarjeta", 0.3):.3f});')

json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — no es para todos</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-fps="30" data-width="1080" data-height="1920">
{A}
{B}
{C}
{D}
{E}
{F}
{G}
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
