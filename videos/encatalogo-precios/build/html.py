# EnCatalogo.pe — precios transparentes, vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "plan", "ciento", "cincuenta", "tienda", "tiendas", "noventa", "almacenes", "gratis", "veinte", "céntimos", "mensaje",
      "facturación", "claude", "treinta", "año", "mil", "quinientos", "permanencia", "igv", "letra", "chica"}
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

# A · hook: "¿Cuánto cuesta?" + fine print that disappears
FINE = "".join(f'<div class="fl" style="width:{w}px"></div>' for w in (780, 820, 700, 840, 760, 610, 800, 720))
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "PRECIOS", "¿Cuánto cuesta EnCatalogo?", top=290, size=104)}
        <div class="abs card" id="Adoc" style="left:70px;top:720px;width:940px;height:560px">
          <div class="abs eyebrow" style="left:50px;top:50px;color:{MUTED}">CONDICIONES</div>
          <div class="abs flines" id="Afl" style="left:50px;top:120px">{FINE}</div>
          <div class="abs lupa" id="Alupa" style="left:520px;top:150px"><span>letra chica</span></div>
          <div class="abs nofine" id="Ano" style="left:50px;top:400px">{icon("circle-check", 44, OK)} Sin letra chica</div>
        </div>
      </div>'''

# B · one plan, S/ 150
B = f'''      <div class="sc" id="sB" style="background:{LIGHT}">
        {head("B", "UN SOLO PLAN", "Todo en un plan. Pagas por tienda.", size=88)}
        <div class="abs card" id="Bcard" style="left:70px;top:600px;width:940px;height:560px">
          <div class="abs eyebrow" style="left:50px;top:50px">ENCATALOGO</div>
          <div class="abs price" style="left:50px;top:120px"><small>S/</small><span id="Bp">150</span><i>/mes</i></div>
          <div class="abs tagx" id="Bt1" style="left:50px;top:340px">{icon("store", 38, TERRAD)} Con 1 tienda</div>
          <div class="abs fine" style="left:50px;top:470px">Precios en soles · IGV incluido</div>
        </div>
      </div>'''

# C · what's included
INC = [("shirt", "Catálogo", "catálogo"), ("store", "Tienda online con enlace propio", "tienda"), ("wallet", "Caja (POS)", "caja"),
       ("package", "Inventario", "inventario"), ("receipt", "Pedidos", "pedidos"), ("wa", "Vendedor IA en WhatsApp", "vendedor")]
def incrow(i, ic, t):
    g = logo("whatsapp", 40, WA) if ic == "wa" else icon(ic, 40, TERRAD)
    return (f'<div class="abs inc" id="Ci{i}" style="left:50px;top:{110 + i * 108}px;width:840px"><span class="ii">{g}</span>'
            f'<span class="it">{t}</span><span class="ok" id="Co{i}">{icon("check", 30, WHITE, 3)}</span></div>')
C = f'''      <div class="sc" id="sC" style="background:{CREAM}">
        {head("C", "INCLUYE", "Todo lo que necesitas para vender", size=88)}
        <div class="abs card" id="Ccard" style="left:70px;top:620px;width:940px;height:800px">
          <div class="abs eyebrow" style="left:50px;top:46px">PLAN S/ 150/MES</div>
          {"".join(incrow(i, ic, t) for i, (ic, t, _) in enumerate(INC))}
        </div>
      </div>'''

# D · extra stores + free warehouses
D = f'''      <div class="sc" id="sD" style="background:{LIGHT}">
        {head("D", "MÁS SEDES", "Creces sin cambiar de plan", size=92)}
        {"".join(f'<div class="abs tile{" inc0" if i == 0 else ""}" id="Ds{i}" style="left:{70 + i * 320}px;top:600px">{icon("store", 56, TERRAD if i else INK, 1.8)}<b>Tienda {i + 1}</b><span>{"Incluida" if i == 0 else "+ S/ 90/mes"}</span></div>' for i in range(3))}
        <div class="abs card wh" id="Dw" style="left:70px;top:1000px;width:940px;height:300px">
          <div class="abs ich big2" style="left:44px;top:84px">{icon("warehouse", 64, TERRAD, 1.8)}</div>
          <div class="abs eyebrow" style="left:220px;top:54px">ALMACENES</div>
          <div class="abs whp" style="left:220px;top:132px">S/ <span id="Dz">0</span></div>
          <div class="abs gratis" id="Dg" style="left:640px;top:140px">Gratis</div>
        </div>
      </div>'''

# E · AI price (dark)
E = f'''      <div class="sc" id="sE" style="background:{INK}">
        {head("E", "PRECIO DE LA IA", "Pagas por cliente, no por mensaje", True, size=88)}
        <div class="abs card" id="Ecard" style="left:70px;top:600px;width:940px;height:460px">
          <div class="abs eyebrow" style="left:50px;top:50px">VENDEDOR IA EN WHATSAPP</div>
          <div class="abs price" style="left:50px;top:110px"><small>S/</small><span id="Ep">0.20</span></div>
          <div class="abs per" id="Eper" style="left:50px;top:320px">por cliente atendido cada 30 días</div>
        </div>
        <div class="abs strike dk" id="Ex" style="left:70px;top:1110px"><span class="sx">{icon("x", 30, WHITE, 3)}</span><span class="st">Cobro por mensaje<em id="Exl"></em></span></div>
      </div>'''

# F · optional modules
MOD = [("receipt", "Facturación electrónica", "S/ 50", "/mes por RUC · 500 comprobantes"),
       ("sparkles", "Asistente conectado a Claude", "S/ 50", "/mes"),
       ("wa", "Número de WhatsApp extra", "S/ 30", "/mes")]
def modrow(i, ic, t, p_, sub):
    g = logo("whatsapp", 44, WA) if ic == "wa" else icon(ic, 44, TERRAD)
    return (f'<div class="abs card mod" id="Fm{i}" style="left:70px;top:{600 + i * 250}px;width:940px;height:220px">'
            f'<div class="abs ich" style="left:40px;top:64px">{g}</div><div class="abs mt" style="left:170px;top:48px">{t}</div>'
            f'<div class="abs mp" style="left:170px;top:112px"><b>{p_}</b><span>{sub}</span></div></div>')
F = f'''      <div class="sc" id="sF" style="background:{CREAM}">
        {head("F", "MÓDULOS OPCIONALES", "¿Necesitas más? Solo si lo usas", size=88)}
        {"".join(modrow(i, *m) for i, m in enumerate(MOD))}
        <div class="abs illu" style="left:70px;top:1360px">Claude es una marca de Anthropic</div>
      </div>'''

# G · annual plan + no lock-in
G = f'''      <div class="sc" id="sG" style="background:{LIGHT}">
        {head("G", "PLAN ANUAL", "Paga el año y ahorra dos meses", size=88)}
        <div class="abs card" id="Gcard" style="left:70px;top:600px;width:940px;height:520px">
          <div class="abs eyebrow" style="left:50px;top:50px">PAGO ANUAL</div>
          <div class="abs price" style="left:50px;top:110px"><small>S/</small><span id="Gp">1500</span><i>/año</i></div>
          <div class="abs months" style="left:50px;top:330px">{"".join(f'<i id="Gm{i}" class="{"free" if i >= 10 else ""}">{"EFMAMJJASOND"[i]}</i>' for i in range(12))}</div>
          <div class="abs gratis" id="Gg" style="left:50px;top:430px">2 meses gratis</div>
        </div>
        <div class="abs callout" id="Gsp" style="left:70px;top:1170px;width:940px">
          <div class="ich">{icon("circle-check", 48, OK)}</div>
          <div><b>Sin permanencia</b><span>Cancelas cuando quieras</span></div>
        </div>
      </div>'''

# H · close
H = f'''      <div class="sc" id="sH" style="background:{CREAM}">
        <div class="abs" id="Hlg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Hwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Ht1" style="left:0;top:770px;width:1080px">Precios en soles.</div>
        <div class="abs tag2" id="Ht2" style="left:0;top:880px;width:1080px">IGV incluido.</div>
        <div class="abs cta" id="Hcta" style="left:240px;top:1060px;width:600px">Probar 7 días gratis</div>
        <div class="abs ctas" id="Hsub" style="left:0;top:1190px;width:1080px">Sin tarjeta · encatalogo.pe</div>
      </div>'''
I = ""
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
def strike_in(sid, t, t_line):
    slide(f"#{sid}x", t, -60, False)
    js(f'tl.fromTo("#{sid}xl", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.35, ease: "power2.out" }}, {t_line:.3f});'); ev("click", t_line)

# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
show("#Adoc", W("e1", "te", -0.2), 0.5, 60)
popin("#Alupa", W("e1", "letra", -0.4), 0.4)
js(f'tl.to("#Afl", {{ autoAlpha: 0.15, duration: 0.4 }}, {W("e1", "chica", 0.2):.3f});')
js(f'tl.to("#Alupa", {{ autoAlpha: 0, scale: 0.6, duration: 0.3 }}, {W("e1", "chica", 0.25):.3f});')
popin("#Ano", W("e1", "chica", 0.35), 0.45); ev("chime2", W("e1", "chica", 0.35))
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
show("#Bcard", W("e2", "plan", -0.1), 0.5, 60)
count("#Bp", W("e2", "ciento", -0.1), 0, 150, 0.9); ev("pop", W("e2", "ciento", 0.8))
slide("#Bt1", W("e2", "una", -0.1), -60)
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
show("#Ccard", W("e3", "incluye", -0.1), 0.5, 60)
for i, (_, _, w_) in enumerate(INC):
    slide(f"#Ci{i}", W("e3", w_, -0.15), -50, False); popin(f"#Co{i}", W("e3", w_, 0.1), 0.3)
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
popin("#Ds0", W("e4", "tienes", -0.1), 0.4)
popin("#Ds1", W("e4", "noventa", -0.15), 0.4); popin("#Ds2", W("e4", "cada", -0.1), 0.4)
show("#Dw", W("e4", "almacenes", -0.3), 0.5, 60)
popin("#Dg", W("e4", "gratis", -0.1), 0.45); ev("chime", W("e4", "gratis", -0.1))
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
show("#Ecard", W("e5", "ia", -0.1), 0.5, 60)
popin("#Ep", W("e5", "veinte", -0.05), 0.5)
show("#Eper", W("e5", "cliente", -0.1), 0.4, 20)
slide("#Ex", W("e5", "no", -0.2, 0), -60, False)
js(f'tl.fromTo("#Exl", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.35, ease: "power2.out" }}, {W("e5", "mensaje", 0.1):.3f});'); ev("click", W("e5", "mensaje", 0.1))
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
for i, w_ in enumerate(["facturación", "asistente", "número"]): slide(f"#Fm{i}", W("e6", w_, -0.2), 80)
js(f'tl.to(["#Fm0 .mp b", "#Fm1 .mp b"], {{ color: "{TERRAD}", duration: 0.3 }}, {W("e6", "cincuenta", -0.05):.3f});'); ev("pop", W("e6", "cincuenta", -0.05))
js(f'tl.to("#Fm2 .mp b", {{ color: "{TERRAD}", duration: 0.3 }}, {W("e6", "treinta", -0.05):.3f});'); ev("pop", W("e6", "treinta", -0.05))
# G
wipe("#sG", "#sF", S[6]); heading("G", S[6])
show("#Gcard", W("e7", "pagas", -0.1), 0.5, 60)
count("#Gp", W("e7", "mil", -0.1), 0, 1500, 1.0)
js(f'tl.fromTo("#Gcard .months i", {{ autoAlpha: 0, y: 14 }}, {{ autoAlpha: 1, y: 0, duration: 0.25, stagger: 0.05 }}, {W("e7", "mil", 0.1):.3f});')
js(f'tl.to(".months i.free", {{ backgroundColor: "{TERRAD}", color: "#FFFFFF", duration: 0.3, stagger: 0.12 }}, {W("e7", "dos", -0.05):.3f});')
popin("#Gg", W("e7", "gratis", -0.1), 0.45); ev("chime2", W("e7", "gratis", -0.1))
slide("#Gsp", W("e8", "permanencia", -0.3), 0)
# H
wipe("#sH", "#sG", S[7])
popin("#Hlg", S[7] + 0.35, 0.6); show("#Hwm", W("e9", "encatalogo", 0.2), 0.45, 20)
show("#Ht1", W("e9", "precios", -0.1), 0.5, 30); show("#Ht2", W("e9", "igv", -0.2), 0.5, 30)
popin("#Hcta", W("e9", "prueba", -0.15), 0.5); ev("chime", W("e9", "prueba", -0.15))
show("#Hsub", W("e9", "sin", -0.1), 0.4, 15)
js(f'tl.to("#Hcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e9", "sin", 0.6):.3f});')

json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — precios</title>
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
{H}
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
