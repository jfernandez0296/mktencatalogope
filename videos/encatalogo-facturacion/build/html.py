# EnCatalogo.pe — «¿Todavía facturas a mano?» facturación y caja, vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "vendes", "cobras", "facturas", "flujo", "caja", "inventario", "comprobante", "sunat", "igv", "dieciocho",
      "stock", "tienda", "cuaderno", "cuadra", "cuadrar", "cincuenta", "quinientos", "comprobantes", "gratis", "lugar"}
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

# A · hook: cuaderno + calculadora + otro sistema, nada cuadra
tools = [("book-open", "Cuaderno", "Ventas del día", 70, 640, -3), ("calculator", "Calculadora", "Suma a mano", 490, 850, 3), ("laptop", "Otro sistema", "Facturas aparte", 110, 1060, -2)]
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "CAJA Y FACTURACIÓN", "¿Todavía facturas a mano?", top=290, size=104)}
        {"".join(f'<div class="abs tool" id="At{i}" style="left:{x}px;top:{y}px;transform:rotate({r}deg)"><div class="ich big2">{icon(ic, 66, TERRAD, 1.7)}</div><div><b>{t}</b><span>{s}</span></div></div>' for i, (ic, t, s, x, y, r) in enumerate(tools))}
        <div class="abs mism" id="Amis" style="left:70px;top:1300px;width:940px">
          <div><span class="ml">Cuaderno</span><b>S/ 1,240</b></div><div class="neq">≠</div><div><span class="ml">Caja</span><b>S/ 1,185</b></div>
        </div>
        <div class="abs nostamp" id="Ano" style="left:700px;top:1150px">No cuadra</div>
      </div>'''

# B · un solo flujo
steps = [("shopping-bag", "Vendes"), ("wallet", "Cobras"), ("receipt", "Facturas")]
B = f'''      <div class="sc" id="sB" style="background:{LIGHT}">
        {head("B", "UN SOLO FLUJO", "Vendes, cobras y facturas sin cambiar de sistema", size=86)}
        <div class="abs flow" style="left:70px;top:660px;width:940px">
          <div class="abs fline" id="Bline" style="left:96px;top:96px;width:0;height:640px"></div>
          {"".join(f'<div class="abs fstep" id="Bs{i}" style="left:0;top:{i * 300}px"><div class="fn">{icon(ic, 70, WHITE, 1.8)}</div><div><small>PASO {i + 1}</small><b>{t}</b></div></div>' for i, (ic, t) in enumerate(steps))}
        </div>
      </div>'''

# C · POS sale updates caja, inventario, comprobante
C = f'''      <div class="sc" id="sC" style="background:{CREAM}">
        {head("C", "CAJA (POS)", "Una venta, tres cosas al día")}
        <div class="abs card" id="Cpos" style="left:70px;top:560px;width:560px;height:740px">
          <div class="abs eyebrow" style="left:40px;top:40px">CAJA · TIENDA MIRAFLORES</div>
          <div class="abs il" style="left:40px;top:120px;width:480px"><span>Vestido Emilia · M</span><b>S/ 189.00</b></div>
          <div class="abs il" style="left:40px;top:190px;width:480px"><span>Blazer Siena · S</span><b>S/ 200.00</b></div>
          <div class="abs il tot" style="left:40px;top:300px;width:480px"><span>Total</span><b>S/ 389.00</b></div>
          <div class="abs pays" style="left:40px;top:420px">{"".join(f'<i>{t}</i>' for t in ["Efectivo", "Tarjeta", "Yape"])}</div>
          <div class="abs cta sm" id="Cbtn" style="left:40px;top:560px;width:480px">Cobrar S/ 389.00</div>
        </div>
        {"".join(f'<div class="abs upd" id="Cu{i}" style="left:660px;top:{560 + i * 250}px;width:350px;height:210px"><div class="ich">{icon(ic, 46, TERRAD)}</div><span>{t}</span><div class="tick" id="Ct{i}">{icon("check", 26, WHITE, 3)}</div></div>' for i, (ic, t) in enumerate([("wallet", "Caja"), ("package", "Inventario"), ("receipt", "Comprobante")]))}
        <div class="abs illu" style="left:70px;top:1330px">Ejemplo ilustrativo</div>
      </div>'''

# D · factura electrónica SUNAT, IGV 18 %
D = f'''      <div class="sc" id="sD" style="background:{LIGHT}">
        {head("D", "FACTURA ELECTRÓNICA", "Aceptada por SUNAT, con el IGV calculado", size=84)}
        <div class="abs card" id="Dcard" style="left:70px;top:620px;width:940px;height:700px">
          <div class="abs eyebrow" style="left:50px;top:46px">FACTURA ELECTRÓNICA</div>
          <div class="abs inv" style="left:50px;top:90px">F001-00004218</div>
          <div class="abs il" style="left:50px;top:200px;width:840px"><span>1 × Vestido Emilia · M</span><b>S/ 189.00</b></div>
          <div class="abs il" style="left:50px;top:265px;width:840px"><span>1 × Blazer Siena · S</span><b>S/ 200.00</b></div>
          <div class="abs il sm" style="left:50px;top:360px;width:840px"><span>Subtotal</span><b>S/ 329.66</b></div>
          <div class="abs il sm igv" id="Digv" style="left:30px;top:405px;width:880px"><span>IGV 18%</span><b>S/ 59.34</b></div>
          <div class="abs il tot" style="left:50px;top:480px;width:840px"><span>Total</span><b>S/ 389.00</b></div>
          <div class="abs stamp" id="Dst" style="left:50px;top:600px">{icon("circle-check", 34, OK)} Aceptado por SUNAT</div>
        </div>
      </div>'''

# E · stock se descuenta por tienda
stores = [("store", "Miraflores", "11"), ("store", "San Isidro", "7"), ("warehouse", "Almacén", "24")]
E = f'''      <div class="sc" id="sE" style="background:{CREAM}">
        {head("E", "INVENTARIO AL DÍA", "Cada venta descuenta el stock")}
        <div class="abs card" id="Ecard" style="left:70px;top:560px;width:940px;height:330px">
          <div class="abs pic sm2" style="left:40px;top:40px">{icon("shirt", 110, TERRAD, 1.6)}</div>
          <div class="abs ptitle" style="left:290px;top:56px">Vestido Emilia</div>
          <div class="abs pmeta" style="left:290px;top:146px">Talla M · Miraflores</div>
          <div class="abs eyebrow" style="left:290px;top:226px;color:{MUTED}">STOCK</div>
          <div class="abs snum" style="left:740px;top:70px"><span id="En">12</span></div>
          <div class="abs minus" id="Em" style="left:630px;top:215px">−1</div>
        </div>
        {"".join(f'<div class="abs srow" id="Er{i}" style="left:70px;top:{940 + i * 130}px;width:940px"><span class="sic">{icon(ic, 40, TERRAD)}</span><span>{t}</span><b>{n}</b></div>' for i, (ic, t, n) in enumerate(stores))}
      </div>'''

# F · sin copiar datos, sin cuadrar a mano
F = f'''      <div class="sc" id="sF" style="background:{INK}">
        {head("F", "MENOS TRABAJO", "Se acabó el doble registro", True, size=92)}
        {"".join(f'<div class="abs nope" id="Fx{i}" style="left:70px;top:{600 + i * 200}px;width:940px"><span class="sx">{icon("x", 34, WHITE, 3)}</span><span class="st">{t}<em id="Fl{i}"></em></span></div>' for i, t in enumerate(["Pasar datos de un sistema a otro", "Cuadrar la caja a mano"]))}
        <div class="abs yes" id="Fok" style="left:70px;top:1060px;width:940px">{icon("circle-check", 46, OK)}<span>Venta, caja, stock y comprobante en un solo sistema</span></div>
      </div>'''

# G · precio del módulo
G = f'''      <div class="sc" id="sG" style="background:{LIGHT}">
        {head("G", "MÓDULO DE FACTURACIÓN", "Cuánto cuesta")}
        <div class="abs card" id="Gcard" style="left:70px;top:560px;width:940px;height:620px">
          <div class="abs eyebrow" style="left:50px;top:50px">FACTURACIÓN ELECTRÓNICA</div>
          <div class="abs price" style="left:50px;top:110px"><small>S/</small><span id="Gp">50</span><i>/mes por RUC</i></div>
          {"".join(f'<div class="abs hl" id="Gl{i}" style="left:50px;top:{330 + i * 80}px">{icon("circle-check", 38, TERRAD)}<span>{t}</span></div>' for i, t in enumerate(["500 comprobantes incluidos", "Aceptada por SUNAT", "Se suma a tu plan de EnCatalogo"]))}
        </div>
        <div class="abs fine" style="left:70px;top:1220px">Precios en soles · IGV incluido</div>
      </div>'''

# H · close
H = f'''      <div class="sc" id="sH" style="background:{CREAM}">
        <div class="abs" id="Hlg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Hwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1 sm" id="Ht1" style="left:0;top:780px;width:1080px">Vendes, cobras y facturas.</div>
        <div class="abs tag2" id="Ht2" style="left:0;top:880px;width:1080px">En un solo lugar.</div>
        <div class="abs cta" id="Hcta" style="left:240px;top:1060px;width:600px">Probar 7 días gratis</div>
        <div class="abs ctas" id="Hsub" style="left:0;top:1190px;width:1080px">Sin tarjeta · encatalogo.pe</div>
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
def tap(sel, t): js(f'tl.to("{sel}", {{ scale: 0.93, duration: 0.09, yoyo: true, repeat: 1 }}, {t:.3f});'); ev("click", t)
def wipe(sel, prev, t):
    js(f'tl.set("{sel}", {{ autoAlpha: 1 }}, {t:.3f});')
    js(f'tl.fromTo("{sel}", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "power3.inOut" }}, {t:.3f});')
    js(f'tl.set("{prev}", {{ autoAlpha: 0 }}, {t + 0.65:.3f});')
def count(sel, t, frm, to, d=1.0):
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v); }} }}, {t:.3f}); }})();')
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)
def line(sel, t, d=0.35):
    js(f'tl.fromTo("{sel}", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: {d}, ease: "power2.out" }}, {t:.3f});'); ev("click", t)

# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
for i, w_ in enumerate(["cuaderno", "después", "sistema"]): popin(f"#At{i}", W("e1", w_, -0.2), 0.4)
show("#Amis", W("e1", "final", -0.2), 0.45, 40)
popin("#Ano", W("e1", "cuadra", -0.15), 0.4, False); ev("click", W("e1", "cuadra", -0.15))
js(f'tl.to("#Ano", {{ rotation: -6, duration: 0.08, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e1", "cuadra", 0.3):.3f});')
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
for i, w_ in enumerate(["vendes", "cobras", "facturas"]): slide(f"#Bs{i}", W("e2", w_, -0.15), -60)
js('gsap.set("#Bline", { width: 6 });')
js(f'tl.fromTo("#Bline", {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 0%", duration: {max(0.4, W("e2", "facturas") - W("e2", "vendes")):.2f}, ease: "none" }}, {W("e2", "vendes"):.3f});')
js(f'tl.to("#sB .fn", {{ scale: 1.1, duration: 0.18, yoyo: true, repeat: 1, stagger: 0.12 }}, {W("e2", "flujo"):.3f});'); ev("chime2", W("e2", "flujo"))
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
js('gsap.set(".tick", { autoAlpha: 0 });')
show("#Cpos", W("e3", "registras", -0.1), 0.5, 60)
tap("#Cbtn", W("e3", "caja", -0.05))
for i, (w_, n) in enumerate([("caja", 1), ("inventario", 0), ("comprobante", 0)]):
    slide(f"#Cu{i}", W("e3", "tres", -0.1 + i * 0.15), 80, i == 0); popin(f"#Ct{i}", W("e3", w_, 0.05, n), 0.3)
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
js('gsap.set("#Dst", { autoAlpha: 0 });')
show("#Dcard", W("e4", "factura", -0.1), 0.5, 60)
popin("#Dst", W("e4", "sunat", -0.05), 0.45); ev("chime", W("e4", "sunat", -0.05))
js(f'tl.fromTo("#Digv", {{ backgroundColor: "rgba(242,230,206,0)" }}, {{ backgroundColor: "rgba(242,230,206,1)", duration: 0.3 }}, {W("e4", "igv", -0.1):.3f});'); ev("pop", W("e4", "igv", -0.1))
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
js('gsap.set("#Em", { autoAlpha: 0 });')
show("#Ecard", W("e5", "venta", -0.3), 0.5, 60)
js(f'tl.fromTo("#Em", {{ autoAlpha: 0, y: 20 }}, {{ autoAlpha: 1, y: -20, duration: 0.5, ease: "power2.out" }}, {W("e5", "descuenta", -0.1):.3f});')
js(f'tl.to("#Em", {{ autoAlpha: 0, duration: 0.3 }}, {W("e5", "descuenta", 0.7):.3f});')
count("#En", W("e5", "descuenta", 0.1), 12, 11, 0.3); ev("click", W("e5", "descuenta", 0.1))
for i in range(3): slide(f"#Er{i}", W("e5", "siempre", -0.1 + i * 0.2), -60, i == 0)
js(f'tl.to("#Er0", {{ borderColor: "{TERRAD}", duration: 0.3 }}, {W("e5", "tienda"):.3f});')
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
slide("#Fx0", W("e6", "pasar", -0.3), -60, False); line("#Fl0", W("e6", "otro", 0.1))
slide("#Fx1", W("e6", "cuadrar", -0.4), -60, False); line("#Fl1", W("e6", "mano", 0.1))
popin("#Fok", W("e6", "final", -0.1), 0.45); ev("chime2", W("e6", "final", -0.1))
# G
wipe("#sG", "#sF", S[6]); heading("G", S[6])
show("#Gcard", W("e7", "módulo", -0.3), 0.5, 60)
count("#Gp", W("e7", "cincuenta", -0.1), 0, 50, 0.8)
for i, (w_, off) in enumerate([("quinientos", -0.1), ("incluidos", 0.2), ("incluidos", 0.6)]): slide(f"#Gl{i}", W("e7", w_, off), -60, i == 0)
# H
wipe("#sH", "#sG", S[7])
popin("#Hlg", S[7] + 0.35, 0.6); show("#Hwm", W("e8", "encatalogo", 0.2), 0.45, 20)
show("#Ht1", W("e8", "vendes", -0.1), 0.5, 30); show("#Ht2", W("e8", "un", -0.1), 0.5, 30)
popin("#Hcta", W("e8", "prueba", -0.15), 0.5); ev("chime", W("e8", "prueba", -0.15))
show("#Hsub", W("e8", "sin", -0.1), 0.4, 15)
js(f'tl.to("#Hcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e8", "sin", 0.6):.3f});')

json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — facturación y caja</title>
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
