# EnCatalogo.pe — app móvil y analítica, vertical 9:16 (~57 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "app", "bolsillo", "vendiste", "hoy", "ayer", "tendencias", "funcionando", "mueven", "quiebres", "stock", "alertas",
      "talla", "tiendas", "almacén", "inventario", "celular", "control", "gratis", "nadie"}
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
def apphead(title):
    return f'<div class="abs aph"><span class="apl">{MARK(40)}</span><b>{title}</b><span class="apb">{icon("bell-ring", 30, INK)}</span></div>'

# A · hook: calling the store
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "APP MÓVIL", "¿Cuánto vendiste hoy?", top=290, size=108)}
        <div class="abs card" id="Acall" style="left:70px;top:640px;width:940px;height:300px">
          <div class="abs ring" id="Aring" style="left:50px;top:60px">{icon("smartphone", 90, WHITE, 1.8)}</div>
          <div class="abs eyebrow" style="left:260px;top:74px;color:{MUTED}">LLAMANDO…</div>
          <div class="abs ptitle" style="left:260px;top:114px">Tienda Miraflores</div>
          <div class="abs dots" style="left:262px;top:218px">{"".join(f'<i id="Ad{i}"></i>' for i in range(3))}</div>
        </div>
        <div class="abs ask" id="Aq" style="left:70px;top:990px">¿Cuánto vendimos hoy?</div>
        <div class="abs wait" id="Await" style="left:70px;top:1110px">{icon("clock", 34, TERRAD)} Esperando respuesta…</div>
      </div>'''

# B · app reveal
tiles = [("trending-up", "Ventas"), ("package", "Stock"), ("bell-ring", "Alertas"), ("store", "Tiendas")]
B = f'''      <div class="sc" id="sB" style="background:{LIGHT}">
        {head("B", "ENCATALOGO EN TU CELULAR", "Tu tienda en el bolsillo", size=96)}
        <div class="abs phone" id="Bph" style="left:240px;top:560px">
          {apphead("Mi negocio")}
          <div class="abs eyebrow" style="left:40px;top:150px">RESUMEN DE HOY</div>
          {"".join(f'<div class="abs tile" id="Bt{i}" style="left:{40 + (i % 2) * 256}px;top:{205 + (i // 2) * 256}px">{icon(ic, 56, TERRAD, 1.8)}<span>{t}</span></div>' for i, (ic, t) in enumerate(tiles))}
          <div class="abs synced" id="Bsy" style="left:40px;top:745px">{icon("circle-check", 30, OK)} Datos de todas tus tiendas</div>
        </div>
      </div>'''

# C · today's sales vs yesterday (dark)
C = f'''      <div class="sc" id="sC" style="background:{INK}">
        {head("C", "VENTAS DE HOY", "Cuánto vendiste, sin llamar a nadie", True, size=84)}
        <div class="abs phone" id="Cph" style="left:240px;top:560px">
          {apphead("Ventas")}
          <div class="abs eyebrow" style="left:40px;top:150px">VENTAS DE HOY</div>
          <div class="abs big" style="left:40px;top:195px">S/ <span id="Csales">4,820</span></div>
          <div class="abs up" id="Cup" style="left:40px;top:320px">{icon("trending-up", 34, OK)} +18% frente a ayer</div>
          <div class="abs cmp" style="left:40px;top:420px">
            <div class="cr"><span>Ayer</span><div class="cb"><i id="Cb0" style="width:70%;background:{BORDER}"></i></div><b>S/ 4,085</b></div>
            <div class="cr"><span>Hoy</span><div class="cb"><i id="Cb1" style="width:82%;background:{TERRA}"></i></div><b>S/ 4,820</b></div>
          </div>
          <div class="abs nocall" id="Cnc" style="left:40px;top:690px">{icon("x", 30, WHITE, 3)}<span>0 llamadas a la tienda</span></div>
        </div>
      </div>'''

# D · trends + top movers
top = [("Vestido Emilia", 48), ("Blazer Siena", 36), ("Jean Araña", 29), ("Polo Lima", 21)]
D = f'''      <div class="sc" id="sD" style="background:{LIGHT}">
        {head("D", "VENTAS Y TENDENCIAS", "Entiende qué está funcionando", size=90)}
        <div class="abs card" id="Dcard" style="left:70px;top:560px;width:940px;height:860px">
          <div class="abs eyebrow" style="left:44px;top:44px">VENTAS · ÚLTIMOS 7 DÍAS</div>
          <svg class="abs" style="left:44px;top:100px" width="852" height="230" viewBox="0 0 852 230" aria-label="tendencia">
            <path d="M0 229 H852" stroke="{BORDER}" stroke-width="2"/>
            <path id="Dline" d="M0 190 L142 170 L284 178 L426 130 L568 120 L710 70 L852 30" fill="none" stroke="{TERRAD}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
            <circle id="Ddot" cx="852" cy="30" r="13" fill="{TERRAD}"/>
          </svg>
          <div class="abs eyebrow" style="left:44px;top:380px">LOS QUE MÁS SE MUEVEN</div>
          {"".join(f'<div class="abs rk" id="Dr{i}" style="left:44px;top:{440 + i * 96}px;width:852px"><em>{i + 1}</em><span>{n}</span><div class="rb"><i id="Drb{i}" style="width:{v / 48 * 100:.0f}%"></i></div><b>{v} u.</b></div>' for i, (n, v) in enumerate(top))}
        </div>
        <div class="abs illu" style="left:70px;top:1440px">Datos de ejemplo</div>
      </div>'''

# E · stock-outs + restock alert
outs = [("Jean Araña · Talla 30", "Agotado", "ag"), ("Polo Lima · Talla M", "Agotado", "ag"), ("Blazer Siena · Talla S", "Quedan 3", "lo")]
E = f'''      <div class="sc" id="sE" style="background:{CREAM}">
        {head("E", "QUIEBRES DE STOCK", "Actúa antes de quedarte sin talla", size=86)}
        <div class="abs card" id="Ecard" style="left:70px;top:610px;width:940px;height:440px">
          <div class="abs eyebrow" style="left:44px;top:44px">QUIEBRES DE STOCK</div>
          {"".join(f'<div class="abs lr2" id="Er{i}" style="left:44px;top:{110 + i * 104}px;width:852px"><span>{n}</span><b class="{c}">{t}</b></div>' for i, (n, t, c) in enumerate(outs))}
        </div>
        <div class="abs callout" id="Ealert" style="left:70px;top:1090px;width:940px">
          <div class="ich">{icon("bell-ring", 48, TERRAD)}</div>
          <div><b>Reponer pronto</b><span>Blazer Siena · Talla S · quedan 3</span></div>
        </div>
      </div>'''

# F · several stores
stores = [("store", "Miraflores", "Ventas hoy", "S/ 2,140", "Stock", "412 u."),
          ("store", "San Isidro", "Ventas hoy", "S/ 1,690", "Stock", "358 u."),
          ("warehouse", "Almacén", "Stock", "1,860 u.", "Traslados", "2 en camino")]
F = f'''      <div class="sc" id="sF" style="background:{LIGHT}">
        {head("F", "VARIAS TIENDAS", "Cada sede, desde donde estés", size=90)}
        {"".join(f"""<div class="abs card st" id="Fs{i}" style="left:70px;top:{570 + i * 250}px;width:940px;height:220px">
          <div class="abs ich" style="left:40px;top:64px;background:{SOFT}">{icon(ic, 50, TERRAD, 1.8)}</div>
          <div class="abs sn" style="left:170px;top:52px">{n}</div>
          <div class="abs sm" style="left:170px;top:128px">{icon("map-pin", 26, MUTED)} Lima</div>
          <div class="abs kv" style="left:520px;top:48px"><span>{k1}</span><b>{v1}</b></div>
          <div class="abs kv" style="left:740px;top:48px"><span>{k2}</span><b>{v2}</b></div>
        </div>""" for i, (ic, n, k1, v1, k2, v2) in enumerate(stores))}
        <div class="abs illu" style="left:70px;top:1330px">Datos de ejemplo</div>
      </div>'''

# G · inventory updates itself (dark)
moves = [("Venta", "−1"), ("Recepción", "+12"), ("Devolución", "+1"), ("Traslado", "−6")]
vals = [24, 23, 35, 36, 30]
G = f'''      <div class="sc" id="sG" style="background:{INK}">
        {head("G", "INVENTARIO CONECTADO", "Lo que ves es lo que hay", True, size=92)}
        {"".join(f'<div class="abs mv" id="Gm{i}" style="left:{70 + (i % 2) * 480}px;top:{560 + (i // 2) * 140}px"><span>{t}</span><b class="{"neg" if d[0] == "−" else "pos"}">{d}</b></div>' for i, (t, d) in enumerate(moves))}
        <div class="abs card" id="Gcard" style="left:70px;top:880px;width:940px;height:400px">
          <div class="abs eyebrow" style="left:50px;top:50px">STOCK · VESTIDO EMILIA · TALLA M</div>
          {"".join(f'<div class="abs gnum" id="Gn{i}" style="left:50px;top:118px">{v}</div>' for i, v in enumerate(vals))}
          <div class="abs synced" id="Gsy" style="left:50px;top:300px">{icon("smartphone", 30, OK)} Actualizado en tu celular</div>
        </div>
      </div>'''

# H · close
H = f'''      <div class="sc" id="sH" style="background:{CREAM}">
        <div class="abs" id="Hlg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Hwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Ht1" style="left:0;top:770px;width:1080px">Tu negocio bajo control,</div>
        <div class="abs tag2" id="Ht2" style="left:0;top:880px;width:1080px">desde el celular.</div>
        <div class="abs cta" id="Hcta" style="left:240px;top:1060px;width:600px">Probar 7 días gratis</div>
        <div class="abs ctas" id="Hsub" style="left:0;top:1190px;width:1080px">Sin tarjeta · encatalogo.pe</div>
      </div>'''
SCENES_HTML = "\n".join([A, B, C, D, E, F, G, H])

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

def count2(sel, t, frm, to, d=1.0):
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v).toLocaleString("en-US"); }} }}, {t:.3f}); }})();')
def grow(sel, t, d=0.6, axis="X", origin="0% 50%"):
    js(f'tl.fromTo("{sel}", {{ scale{axis}: 0 }}, {{ scale{axis}: 1, transformOrigin: "{origin}", duration: {d}, ease: "power2.out" }}, {t:.3f});')

# A
js('gsap.set(["#Aq", "#Await"], { autoAlpha: 0 });')
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
show("#Acall", W("e1", "llamar", -0.3), 0.5, 60); ev("click", W("e1", "llamar"))
js(f'tl.to("#Aring", {{ rotation: 10, duration: 0.08, yoyo: true, repeat: 11, ease: "sine.inOut" }}, {W("e1", "llamar", 0.1):.3f});')
js(f'tl.fromTo("#Acall .dots i", {{ opacity: 0.2 }}, {{ opacity: 1, duration: 0.3, stagger: 0.2, repeat: 4, yoyo: true }}, {W("e1", "llamar", 0.2):.3f});')
popin("#Aq", W("e1", "tienda", -0.1), 0.4)
popin("#Await", W("e1", "esperar", -0.1), 0.4)
js(f'tl.to("#Await", {{ x: 10, duration: 0.07, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {W("e1", "responda"):.3f});')
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
js(f'tl.fromTo("#Bph", {{ autoAlpha: 0, y: 500 }}, {{ autoAlpha: 1, y: 0, duration: 0.8, ease: "power3.out" }}, {W("e2", "app", -0.3):.3f});'); ev("pop", W("e2", "app", -0.3))
for i in range(4): popin(f"#Bt{i}", W("e2", "tienes", -0.1 + i * 0.12), 0.35, i == 0)
show("#Bsy", W("e2", "bolsillo", -0.1), 0.4, 15); ev("chime2", W("e2", "bolsillo"))
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
show("#Cph", W("e3", "abres", -0.2), 0.6, 120)
count2("#Csales", W("e3", "vendiste", -0.2), 0, 4820, 1.2)
show("#Cup", W("e3", "frente", -0.15), 0.35, 15); ev("pop", W("e3", "frente", -0.15))
grow("#Cb0", W("e3", "ayer", -0.2)); grow("#Cb1", W("e3", "ayer", 0.1))
popin("#Cnc", W("e3", "sin", -0.1), 0.4)
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
show("#Dcard", W("e4", "ventas", -0.1), 0.5, 60)
tl0, tl1 = W("e4", "tendencias", -0.2), W("e4", "funcionando", 0.3)
js(f'tl.fromTo("#Dline", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {tl1 - tl0:.2f}, ease: "power1.inOut" }}, {tl0:.3f});')
popin("#Ddot", tl1, 0.35)
for i in range(4):
    t0 = W("e4", "productos", -0.2 + i * 0.22)
    slide(f"#Dr{i}", t0, -40, i == 0); grow(f"#Drb{i}", t0 + 0.15)
js(f'tl.to("#Dr0", {{ scale: 1.03, duration: 0.25, yoyo: true, repeat: 1 }}, {W("e4", "mueven"):.3f});')
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
js('gsap.set("#Ealert", { autoAlpha: 0 });')
show("#Ecard", W("e5", "también", 0.0), 0.5, 60)
for i in range(3): slide(f"#Er{i}", W("e5", "quiebres", -0.1 + i * 0.25), 60, i < 2)
js(f'tl.fromTo("#Ealert", {{ autoAlpha: 0, y: -60 }}, {{ autoAlpha: 1, y: 0, duration: 0.5, ease: "back.out(1.6)" }}, {W("e5", "alertas", -0.15):.3f});'); ev("chime", W("e5", "alertas", -0.15))
js(f'tl.to("#Ealert .ich", {{ rotation: 14, duration: 0.1, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {W("e5", "alertas", 0.3):.3f});')
js(f'tl.to("#Er2 b", {{ scale: 1.15, duration: 0.2, yoyo: true, repeat: 1 }}, {W("e5", "talla", -0.1):.3f});')
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
slide("#Fs0", W("e6", "estado", -0.2), 80); slide("#Fs1", W("e6", "una", -0.1), 80)
slide("#Fs2", W("e6", "almacén", -0.2), 80)
js(f'tl.to("#sF .st", {{ y: -8, duration: 0.25, stagger: 0.1, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {W("e6", "moverte"):.3f});')
# G
wipe("#sG", "#sF", S[6]); heading("G", S[6])
js('gsap.set(["#Gn1", "#Gn2", "#Gn3", "#Gn4", "#Gsy"], { autoAlpha: 0 });')
show("#Gcard", S[6] + 0.6, 0.5, 60)
for i, w_ in enumerate(["venta", "recepción", "devolución", "traslado"]):
    t0 = W("e7", w_, -0.1)
    popin(f"#Gm{i}", t0, 0.35)
    js(f'tl.set("#Gn{i}", {{ autoAlpha: 0 }}, {t0 + 0.2:.3f});')
    js(f'tl.fromTo("#Gn{i + 1}", {{ autoAlpha: 0, y: -30 }}, {{ autoAlpha: 1, y: 0, duration: 0.25, ease: "power2.out" }}, {t0 + 0.2:.3f});')
popin("#Gsy", W("e7", "celular", -0.2), 0.4); ev("chime2", W("e7", "celular", -0.2))
# H
wipe("#sH", "#sG", S[7])
popin("#Hlg", S[7] + 0.35, 0.6); show("#Hwm", W("e8", "encatalogo", 0.2), 0.45, 20)
show("#Ht1", W("e8", "tu", -0.1), 0.5, 30); show("#Ht2", W("e8", "desde", -0.1), 0.5, 30)
popin("#Hcta", W("e8", "prueba", -0.15), 0.5); ev("chime", W("e8", "prueba", -0.15))
show("#Hsub", W("e8", "sin", -0.1, 1), 0.4, 15)
js(f'tl.to("#Hcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e8", "sin", 0.6, 1):.3f});')

json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — app móvil</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-fps="30" data-width="1080" data-height="1920">
{SCENES_HTML}
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
