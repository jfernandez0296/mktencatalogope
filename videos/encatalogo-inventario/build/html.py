# EnCatalogo.pe — inventario y traslados, vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "stock", "tienda", "traslado", "reponer", "celular", "agotando", "facturas", "comprobante", "whatsapp",
      "yape", "plin", "catálogo", "claude", "ciento", "cincuenta", "gratis", "orden", "control", "vendido", "sola"}
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
for s in segs:
    ph, iv = align(s); lst = []
    for words, (a, b) in zip(ph, iv):
        tot, acc = chars(words), 0
        for w_ in words: lst.append((w_.lower().strip("¿¡,.:;?!"), s["start"] + a + (b - a) * acc / tot)); acc += len(w_) + 1
        n = min(len(words), max(1, math.ceil(chars(words) / 22)))
        best = None
        for cut in itertools.combinations(range(1, len(words)), n - 1):
            gs = [words[i:j] for i, j in zip((0,) + cut, cut + (len(words),))]
            sc = max(chars(x) for x in gs) + (8 if any(len(x) == 1 and len(x[0]) < 6 for x in gs) else 0)
            if best is None or sc < best[0]: best = (sc, gs)
        t0 = a
        for x in best[1]:
            d = (b - a) * chars(x) / tot; caps.append([s["start"] + t0, s["start"] + t0 + d, x]); t0 += d
    WT[s["id"]] = lst
def W(i, word, off=0.0, nth=0):
    hits = [t for w_, t in WT[i] if w_.startswith(word)]
    if not hits: raise SystemExit(f"palabra no encontrada: {i} {word}")
    return round(hits[min(nth, len(hits) - 1)] + off, 3)
for i in range(len(caps)):
    nxt = caps[i + 1][0] if i + 1 < len(caps) else caps[i][1] + 0.4
    caps[i][1] = min(nxt, caps[i][1] + 0.35) if nxt - caps[i][1] > 0.7 else nxt
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

HL.clear(); HL.update({"encatalogo", "stock", "tienda", "almacén", "talla", "color", "traslado", "alerta", "reponer", "gratis",
                       "orden", "celular", "solo", "quiebres", "recibido", "ventas", "inventario", "variante", "tres"})

# A · hook: the notebook lies
nb_rows = [("Polo Lima · M", "3"), ("Polo Lima · L", "5"), ("Jean Nara · 30", "2"), ("Blazer Siena · S", "4")]
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "INVENTARIO Y TRASLADOS", "¿Tu stock dice la verdad?", top=290, size=100)}
        <div class="abs nb" id="Anb" style="left:70px;top:640px;width:560px;height:700px">
          <div class="abs nbt" style="left:56px;top:40px">Cuaderno de stock</div>
          {"".join(f'<div class="abs nbr" id="Ar{i}" style="left:56px;top:{150 + i * 120}px;width:460px"><span>{a}</span><b id="Ab{i}">{b}</b></div>' for i, (a, b) in enumerate(nb_rows))}
          <div class="abs strike" id="Ast" style="left:450px;top:186px"></div>
        </div>
        <div class="abs ticket" id="Atk" style="left:660px;top:640px;width:350px">
          <div class="eyebrow" style="color:{TERRA}">VENTA</div>
          <div class="tkp">Polo Lima</div>
          <div class="tkm">Talla M</div>
          <div class="tkl">Última unidad</div>
        </div>
        <div class="abs real" id="Areal" style="left:660px;top:1010px;width:350px">
          <div class="eyebrow" style="color:{MUTED}">EN LA TIENDA</div>
          <b>0</b>
        </div>
        <div class="abs qmark sm" id="Aq" style="left:860px;top:1200px">?</div>
      </div>'''

# B · updates itself with every movement
moves = [("receipt", "Venta", "−1", "7"), ("package", "Recepción", "+12", "19"), ("arrow-right", "Devolución", "+1", "20"), ("truck", "Traslado", "−6", "14")]
B = f'''      <div class="sc" id="sB" style="background:{LIGHT}">
        {head("B", "STOCK EN TIEMPO REAL", "Se actualiza solo")}
        <div class="abs card" id="Bcard" style="left:70px;top:520px;width:940px;height:330px">
          <div class="abs pic" style="left:40px;top:40px">{icon("shirt", 120, TERRAD, 1.6)}</div>
          <div class="abs ptitle" style="left:290px;top:60px">Vestido Emilia</div>
          <div class="abs pmeta" style="left:290px;top:148px">Talla M · Negro</div>
          <div class="abs eyebrow" style="left:290px;top:226px;color:{MUTED}">STOCK</div>
          <div class="abs bnum" style="left:640px;top:96px;width:260px">{"".join(f'<b class="abs bn" id="Bn{k}">{v}</b>' for k, v in enumerate(["8"] + [m[3] for m in moves]))}</div>
        </div>
        {"".join(f'<div class="abs mv" id="Bm{i}" style="left:70px;top:{900 + i * 132}px;width:940px"><div class="ich">{icon(ic, 46, TERRAD)}</div><span>{t}</span><b class="{"pos" if d.startswith("+") else "neg"}">{d}</b></div>' for i, (ic, t, d, _) in enumerate(moves))}
      </div>'''

# C · matrix by store / warehouse / variant
sizes = ["S", "M", "L", "XL"]
places = [("store", "Miraflores"), ("store", "San Isidro"), ("warehouse", "Almacén")]
vals = [[[3, 0, 4, 2], [5, 2, 1, 0], [12, 18, 9, 6]], [[1, 4, 2, 0], [0, 3, 3, 1], [8, 10, 14, 5]]]
CX, CW, RY, RH = 380, 130, 250, 116
def grid(k):
    out = ""
    for r, row in enumerate(vals[k]):
        for c, v in enumerate(row):
            out += f'<div class="abs cell{" zero" if v == 0 else ""}" style="left:{CX + c * CW}px;top:{RY + r * RH}px;width:{CW}px">{v}</div>'
    tot = sum(sum(r) for r in vals[k])
    out += f'<div class="abs ctot" style="left:{CX}px;top:{RY + 3 * RH + 20}px;width:{4 * CW}px">{tot} unidades</div>'
    return out
C = f'''      <div class="sc" id="sC" style="background:{CREAM}">
        {head("C", "POR TIENDA · ALMACÉN · VARIANTE", "Cada talla y color, en cada sede", size=86)}
        <div class="abs card" id="Ccard" style="left:70px;top:590px;width:940px;height:780px">
          <div class="abs ptitle" style="left:44px;top:36px;font-size:54px">Blazer Siena</div>
          <div class="abs sw" id="Csw0" style="left:560px;top:44px"><i style="background:#1C1B1A"></i>Negro</div>
          <div class="abs sw" id="Csw1" style="left:740px;top:44px"><i style="background:#D8C3A5"></i>Arena</div>
          <div class="abs band" id="Chr" style="left:20px;top:{RY - 10}px;width:900px;height:{2 * RH}px"></div>
          <div class="abs band" id="Cha" style="left:20px;top:{RY - 10 + 2 * RH}px;width:900px;height:{RH}px"></div>
          <div class="abs band" id="Chc" style="left:{CX + CW}px;top:{RY - 100}px;width:{CW}px;height:{3 * RH + 90}px"></div>
          {"".join(f'<div class="abs chd2" style="left:{CX + c * CW}px;top:{RY - 80}px;width:{CW}px">{s}</div>' for c, s in enumerate(sizes))}
          {"".join(f'<div class="abs plc" id="Cp{r}" style="left:44px;top:{RY + r * RH}px">{icon(ic, 38, TERRAD)}<span>{n}</span></div>' for r, (ic, n) in enumerate(places))}
          <div class="abs" id="Cg0" style="left:0;top:0">{grid(0)}</div>
          <div class="abs" id="Cg1" style="left:0;top:0">{grid(1)}</div>
        </div>
      </div>'''

# D · create a transfer
D = f'''      <div class="sc" id="sD" style="background:{LIGHT}">
        {head("D", "TRASLADOS", "Mueve stock a donde se vende", size=88)}
        <div class="abs card st" id="Dl" style="left:70px;top:560px;width:450px;height:400px">
          <div class="abs plc" style="left:36px;top:36px">{icon("store", 40, TERRAD)}<span>Miraflores</span></div>
          <div class="abs pmeta" style="left:36px;top:110px">Talla M</div>
          <b class="abs snum" id="Dn0" style="left:36px;top:180px;color:{TERRAD}">0</b>
          <div class="abs pill bad" id="Dp0" style="left:36px;top:318px">Sin stock</div>
        </div>
        <div class="abs card st" id="Dr" style="left:560px;top:560px;width:450px;height:400px">
          <div class="abs plc" style="left:36px;top:36px">{icon("warehouse", 40, TERRAD)}<span>Almacén</span></div>
          <div class="abs pmeta" style="left:36px;top:110px">Talla M</div>
          <b class="abs snum" style="left:36px;top:180px">42</b>
          <div class="abs pill good" id="Dp1" style="left:36px;top:318px">Disponible</div>
        </div>
        <div class="abs card" id="Df" style="left:70px;top:990px;width:940px;height:420px">
          <div class="abs eyebrow" style="left:44px;top:40px">NUEVO TRASLADO</div>
          <div class="abs route" style="left:44px;top:96px">Almacén {icon("arrow-right", 44, TERRAD)} Miraflores</div>
          <div class="abs pmeta" style="left:44px;top:200px">18 prendas · Polo Lima · Talla M</div>
          <div class="abs btn" id="Dbtn" style="left:44px;top:290px;width:852px">Crear traslado</div>
          <div class="abs btn ok" id="Dok" style="left:44px;top:290px;width:852px">{icon("circle-check", 40, WHITE)} Traslado creado</div>
        </div>
      </div>'''

# E · track it (dark)
steps = [("Preparado", "Almacén"), ("En camino", "18 prendas en ruta"), ("Recibido", "Miraflores")]
E = f'''      <div class="sc" id="sE" style="background:{INK}">
        {head("E", "TRASLADO TRAZABLE", "Síguelo paso a paso", True)}
        <div class="abs dcard" id="Ecard" style="left:70px;top:540px;width:940px;height:560px">
          <div class="abs eyebrow" style="left:50px;top:44px;color:{TERRA}">TRASLADO #0187</div>
          <div class="abs vtrack" style="left:97px;top:150px;height:320px"><div id="Efill"></div></div>
          {"".join(f'<div class="abs vstep" id="Es{i}" style="left:60px;top:{125 + i * 160}px"><div class="vdot" id="Ed{i}">{icon("check", 34, WHITE, 3)}</div><div><b>{a}</b><span>{b}</span></div></div>' for i, (a, b) in enumerate(steps))}
          <div class="abs etruck" id="Etr" style="left:760px;top:{125}px">{icon("truck", 80, TERRA, 1.8)}</div>
        </div>
        {"".join(f'<div class="abs know" id="Ek{i}" style="left:{70 + i * 320}px;top:1150px">{icon(ic, 40, TERRAD)}<span>{t}</span></div>' for i, (ic, t) in enumerate([("package", "Qué tienes"), ("map-pin", "Dónde está"), ("bell-ring", "Qué falta")]))}
      </div>'''

# F · restock alert
F = f'''      <div class="sc" id="sF" style="background:{CREAM}">
        {head("F", "ALERTAS DE STOCK", "Repón antes de quedarte sin talla", size=86)}
        <div class="abs card" id="Fcard" style="left:70px;top:600px;width:940px;height:400px">
          <div class="abs ptitle" style="left:44px;top:40px;font-size:54px">Blazer Siena · Talla S</div>
          <div class="abs eyebrow" style="left:44px;top:124px;color:{MUTED}">STOCK</div>
          <b class="abs gnum" id="Fn" style="left:44px;top:184px">14</b>
          <div class="abs gauge" style="left:44px;top:330px;width:852px"><div id="Fbar"></div></div>
          <div class="abs gmin" style="left:{44 + 852 * 4 // 14}px;top:300px"></div>
          <div class="abs gml" style="left:{44 + 852 * 4 // 14 + 14}px;top:262px">Mínimo 4</div>
        </div>
        <div class="abs notif" id="Fnt" style="left:70px;top:1050px;width:940px">
          <span class="nlogo">{MARK(64)}</span>
          <div><i>EnCatalogo · ahora</i><b>Reponer pronto</b><span>Blazer Siena · Talla S · quedan 3</span></div>
        </div>
        <div class="abs stamp" id="Fok" style="left:70px;top:1300px">{icon("circle-check", 34, OK)} Sin ventas perdidas</div>
      </div>'''

# G · mobile app
G = f'''      <div class="sc" id="sG" style="background:{LIGHT}">
        {head("G", "APP MÓVIL", "Tus quiebres, en el celular")}
        <div class="abs phone" id="Gph" style="left:240px;top:570px;height:860px">
          <div class="abs hi" style="left:44px;top:56px">Inventario</div>
          <div class="abs eyebrow" style="left:44px;top:140px;font-size:22px">QUIEBRES DE STOCK</div>
          {"".join(f'<div class="abs qr" id="Gq{i}" style="left:44px;top:{190 + i * 86}px;width:484px"><span>{a}</span><b class="{c}">{b}</b></div>' for i, (a, b, c) in enumerate([("Jean Nara · 30", "Agotado", "bad"), ("Polo Lima · M", "Agotado", "bad"), ("Blazer Siena · S", "Quedan 3", "warn")]))}
          <div class="abs eyebrow" style="left:44px;top:480px;font-size:22px">LOS QUE MÁS SE MUEVEN</div>
          {"".join(f'<div class="abs mrow" style="left:44px;top:{530 + i * 100}px;width:484px"><span>{n}</span><div class="mtrack"><div class="mfill" id="Gm{i}" style="width:{w}%"></div></div></div>' for i, (n, w) in enumerate([("Vestido Emilia", 100), ("Polo Lima", 78), ("Pantalón Nara", 58)]))}
        </div>
      </div>'''

# H · warehouses free (dark)
H = f'''      <div class="sc" id="sH" style="background:{INK}">
        {head("H", "UN SOLO PLAN", "Almacenes gratis", True, size=100)}
        <div class="abs zero0" id="Hz" style="left:0;top:520px;width:1080px"><small>S/</small><span>0</span></div>
        <div class="abs zl" id="Hzl" style="left:0;top:890px;width:1080px">por cada almacén</div>
        {"".join(f'<div class="abs wh" id="Hw{i}" style="left:{70 + i * 320}px;top:1000px">{icon("warehouse", 70, TERRA, 1.6)}<span>Almacén {i + 1}</span><b>S/ 0</b></div>' for i in range(3))}
        <div class="abs fine" id="Hf" style="left:70px;top:1300px;color:#B9B2A8">Plan desde S/ 150/mes con 1 tienda · IGV incluido</div>
      </div>'''

# I · close
I = f'''      <div class="sc" id="sI" style="background:{CREAM}">
        <div class="abs" id="Ilg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Iwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="It1" style="left:0;top:770px;width:1080px">Tu mercadería en orden.</div>
        <div class="abs tag2" id="It2" style="left:0;top:880px;width:1080px">Tu negocio bajo control.</div>
        <div class="abs cta" id="Icta" style="left:240px;top:1060px;width:600px">Probar 7 días gratis</div>
        <div class="abs ctas" id="Isub" style="left:0;top:1190px;width:1080px">Sin tarjeta · encatalogo.pe</div>
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
def count(sel, t, frm, to, d=1.0, fmt="comma"):
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v).toLocaleString("en-US"); }} }}, {t:.3f}); }})();')
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)
# A
js('gsap.set(["#Aq", "#Ast", "#Areal"], { autoAlpha: 0 });')
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
slide("#Atk", W("e1", "vendiste", -0.1), 80)
js(f'tl.fromTo("#Atk .tkl", {{ color: "#FFFFFF" }}, {{ color: "{TERRA}", duration: 0.3 }}, {W("e1", "última"):.3f});')
show("#Anb", W("e1", "cuaderno", -0.35), 0.5, 60)
js(f'tl.fromTo("#sA .nbr", {{ autoAlpha: 0, x: -20 }}, {{ autoAlpha: 1, x: 0, duration: 0.3, stagger: 0.08 }}, {W("e1", "cuaderno", -0.1):.3f});')
js(f'tl.to("#Ab0", {{ scale: 1.4, color: "{TERRAD}", duration: 0.25, yoyo: true, repeat: 1 }}, {W("e1", "tres", -0.05):.3f});'); ev("pop", W("e1", "tres", -0.05))
js(f'tl.fromTo("#Ast", {{ autoAlpha: 1, scaleX: 0 }}, {{ autoAlpha: 1, scaleX: 1, transformOrigin: "0% 50%", duration: 0.3, ease: "power2.out" }}, {W("e1", "tres", 0.45):.3f});')
popin("#Areal", W("e1", "tres", 0.55), 0.45)
popin("#Aq", W("e1", "suena", -0.15), 0.45)
js(f'tl.to("#Aq", {{ rotation: 12, duration: 0.12, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e1", "suena", 0.35):.3f});')
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
js('gsap.set(["#Bn1", "#Bn2", "#Bn3", "#Bn4"], { autoAlpha: 0 });')
show("#Bcard", W("e2", "inventario", -0.2), 0.5, 60)
for i, w_ in enumerate(["vendes", "recibes", "devuelves", "trasladas"]):
    t = W("e2", w_, -0.1)
    slide(f"#Bm{i}", t, -80)
    js(f'tl.set("#Bn{i}", {{ autoAlpha: 0 }}, {t + 0.12:.3f});')
    js(f'tl.fromTo("#Bn{i + 1}", {{ autoAlpha: 0, y: -40 }}, {{ autoAlpha: 1, y: 0, duration: 0.25, ease: "back.out(2)" }}, {t + 0.12:.3f});')
    js(f'tl.fromTo("#Bm{i}", {{ backgroundColor: "{SOFT}" }}, {{ backgroundColor: "{WHITE}", duration: 0.8, immediateRender: false }}, {t + 0.3:.3f});')
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
js('gsap.set(["#Cg1", "#Chr", "#Cha", "#Chc"], { autoAlpha: 0 });')
show("#Ccard", W("e3", "ves", -0.1), 0.5, 60)
js(f'tl.fromTo("#Cg0 .cell", {{ autoAlpha: 0, scale: 0.6 }}, {{ autoAlpha: 1, scale: 1, duration: 0.25, stagger: 0.03, ease: "back.out(2)" }}, {W("e3", "stock"):.3f});')
js(f'tl.fromTo("#Cg0 .ctot", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, duration: 0.3 }}, {W("e3", "producto"):.3f});')
for sel, w_, nxt in [("#Chr", "tienda", "almacén"), ("#Cha", "almacén", "variante"), ("#Chc", "talla", "color")]:
    js(f'tl.fromTo("{sel}", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, duration: 0.25 }}, {W("e3", w_, -0.1):.3f});')
    js(f'tl.to("{sel}", {{ autoAlpha: 0, duration: 0.25 }}, {W("e3", nxt, -0.1):.3f});'); ev("pop", W("e3", w_, -0.1))
tc = W("e3", "color", -0.1)
js(f'tl.to("#Cg0", {{ autoAlpha: 0, duration: 0.25 }}, {tc:.3f});')
js(f'tl.fromTo("#Cg1", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, duration: 0.3 }}, {tc + 0.1:.3f});')
js(f'tl.to("#Csw0", {{ backgroundColor: "{WHITE}", color: "{MUTED}", duration: 0.25 }}, {tc:.3f});')
js(f'tl.to("#Csw1", {{ backgroundColor: "{INK}", color: "{WHITE}", duration: 0.25 }}, {tc:.3f});'); tap("#Csw1", tc)
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
js('gsap.set(["#Dok", "#Df"], { autoAlpha: 0 });')
slide("#Dl", W("e4", "miraflores", -0.2), -80)
js(f'tl.to("#Dp0", {{ scale: 1.12, duration: 0.18, yoyo: true, repeat: 3 }}, {W("e4", "talla"):.3f});')
slide("#Dr", W("e4", "almacén", -0.2), 80)
show("#Df", W("e4", "creas", -0.4), 0.45, 60)
tap("#Dbtn", W("e4", "traslado", 0.1))
popin("#Dok", W("e4", "segundos", -0.1), 0.4); ev("chime2", W("e4", "segundos", -0.1))
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
js('gsap.set(["#Ed0", "#Ed1", "#Ed2"], { autoAlpha: 0.25 });')
show("#Ecard", W("e5", "sigues", -0.2), 0.5, 60)
for i, w_ in enumerate(["preparado", "camino", "recibido"]):
    t = W("e5", w_, -0.05)
    js(f'tl.to("#Ed{i}", {{ autoAlpha: 1, backgroundColor: "{OK}", scale: 1.15, duration: 0.2, yoyo: true, repeat: 1 }}, {t:.3f});')
    js(f'tl.set("#Ed{i}", {{ autoAlpha: 1, backgroundColor: "{OK}" }}, {t + 0.41:.3f});')
    js(f'tl.to("#Etr", {{ y: {i * 160}, duration: 0.35, ease: "power2.inOut", overwrite: "auto" }}, {t - 0.2:.3f});')
    ev("chime2" if i == 2 else "pop", t)
t0, t2 = W("e5", "preparado"), W("e5", "recibido")
js(f'tl.fromTo("#Efill", {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 0%", duration: {t2 - t0:.2f}, ease: "none" }}, {t0:.3f});')
for i, w_ in enumerate(["tienes", "dónde", "falta"]): popin(f"#Ek{i}", W("e5", w_, -0.1), 0.35)
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
js('gsap.set(["#Fnt", "#Fok"], { autoAlpha: 0 });')
show("#Fcard", W("e6", "antes", 0.0), 0.5, 60)
ta, tb = W("e6", "antes", 0.3), W("e6", "talla", 0.2)
count("#Fn", ta, 14, 3, tb - ta)
js(f'tl.fromTo("#Fbar", {{ scaleX: 1 }}, {{ scaleX: {3 / 14:.3f}, transformOrigin: "0% 50%", duration: {tb - ta:.2f}, ease: "power2.out" }}, {ta:.3f});')
js(f'tl.to(["#Fbar"], {{ backgroundColor: "{TERRAD}", duration: 0.3 }}, {tb - 0.2:.3f});')
js(f'tl.to("#Fn", {{ color: "{TERRAD}", duration: 0.3 }}, {tb - 0.2:.3f});')
js(f'tl.fromTo("#Fnt", {{ autoAlpha: 0, y: -120 }}, {{ autoAlpha: 1, y: 0, duration: 0.5, ease: "back.out(1.4)" }}, {W("e6", "alerta", -0.3):.3f});'); ev("chime", W("e6", "alerta", -0.3))
js(f'tl.to("#Fnt .nlogo", {{ rotation: 10, duration: 0.1, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {W("e6", "alerta", 0.2):.3f});')
popin("#Fok", W("e6", "pierdes", -0.1), 0.4)
# G
wipe("#sG", "#sF", S[6]); heading("G", S[6])
show("#Gph", W("e7", "celular", -0.4), 0.6, 120)
js(f'tl.fromTo("#sG .qr", {{ autoAlpha: 0, x: 40 }}, {{ autoAlpha: 1, x: 0, duration: 0.3, stagger: 0.12 }}, {W("e7", "quiebres", -0.1):.3f});'); ev("pop", W("e7", "quiebres", -0.1))
js(f'tl.fromTo("#sG .mfill", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.6, stagger: 0.1, ease: "power2.out" }}, {W("e7", "productos", -0.1):.3f});')
js(f'tl.to("#Gm0", {{ backgroundColor: "{TERRAD}", duration: 0.3 }}, {W("e7", "mueven"):.3f});'); ev("pop", W("e7", "mueven"))
# H
wipe("#sH", "#sG", S[7]); heading("H", S[7])
popin("#Hz", W("e8", "almacenes", 0.1), 0.5)
show("#Hzl", W("e8", "cuestan", -0.1), 0.4, 20)
for i in range(3): popin(f"#Hw{i}", W("e8", "extra", -0.1) + i * 0.15, 0.35, i == 0)
js(f'tl.to("#Hz span", {{ scale: 1.12, color: "{WHITE}", duration: 0.2, yoyo: true, repeat: 1 }}, {W("e8", "gratis"):.3f});'); ev("chime", W("e8", "gratis"))
show("#Hf", W("e8", "gratis", 0.4), 0.4, 15)
# I
wipe("#sI", "#sH", S[8])
popin("#Ilg", S[8] + 0.35, 0.6); show("#Iwm", W("e9", "encatalogo", 0.2), 0.45, 20)
show("#It1", W("e9", "tu", -0.1), 0.5, 30); show("#It2", W("e9", "orden", 0.4), 0.5, 30)
popin("#Icta", W("e9", "prueba", -0.15), 0.5); ev("chime", W("e9", "prueba", -0.15))
show("#Isub", W("e9", "sin", -0.1), 0.4, 15)
js(f'tl.to("#Icta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e9", "sin", 0.6):.3f});')
json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — inventario y traslados</title>
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
{I}
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
