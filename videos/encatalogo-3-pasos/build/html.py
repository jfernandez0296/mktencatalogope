# EnCatalogo.pe — tutorial vertical 9:16 "Empiezas en 3 pasos" (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "pasos", "cuenta", "gratis", "tarjeta", "whatsapp", "api", "minutos", "catálogo", "excel", "fotos",
      "vender", "stock", "precio", "ciento", "cincuenta", "noventa", "almacenes", "permanencia", "operación", "hoy", "uno", "dos", "tres"}
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


# ---------------------------------------------------------------- step pieces
STEPS = [("Cuenta", "user"), ("WhatsApp", None), ("Catálogo", "upload")]
def numbox(sid, n):
    return f'<div class="abs numbox" id="{sid}n" style="left:770px;top:226px"><span>{n}</span></div>'
def stephead(sid, n, title, size=92):
    return (f'<div class="abs badge" id="{sid}k" style="left:70px;top:250px">PASO {n} DE 3</div>'
            f'<div class="abs ttl" id="{sid}t" style="left:70px;top:330px;width:660px;font-size:{size}px;color:{INK}">{title}</div>'
            + numbox(sid, n))
def progress(sid, cur):
    out = []
    for i, (name, _) in enumerate(STEPS):
        cls = "done" if i < cur else ("cur" if i == cur else "next")
        mark = icon("check", 30, TERRAD, 3) if i < cur else f"<i>{i + 1}</i>"
        out.append(f'<div class="abs pstep {cls}" style="left:{70 + i * 320}px;top:1380px">{mark}<span>{name}</span></div>')
    return f'<div class="abs" id="{sid}pg" style="left:0;top:0">{"".join(out)}</div>'
def field(sid, ic, label, value, y):
    return (f'<div class="abs flab" style="left:44px;top:{y}px">{label}</div>'
            f'<div class="abs field" id="{sid}" style="left:44px;top:{y + 46}px;width:852px">{icon(ic, 38, MUTED)}'
            f'<span class="fv" id="{sid}v">{value}</span><span class="caret" id="{sid}c"></span></div>')

# A · hook
rowsA = [("Crea tu cuenta", "7 días gratis, sin tarjeta", icon("user", 52, TERRAD)),
         ("Conecta tu WhatsApp", "API oficial de WhatsApp Business", logo("whatsapp", 48, WA)),
         ("Sube tu catálogo", "Desde Excel o fotos del celular", icon("upload", 52, TERRAD))]
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        <div class="abs badge" id="Ak" style="left:70px;top:290px">TUTORIAL · EMPIEZA HOY</div>
        <div class="abs ttl" id="At" style="left:70px;top:370px;width:940px;font-size:104px;color:{INK}">Empieza a vender en <em>3 pasos</em></div>
        {"".join(f'<div class="abs srow" id="Ar{i}" style="left:70px;top:{660 + i * 230}px;width:940px"><div class="snum">{i + 1}</div><div class="stx"><b>{a}</b><span>{b}</span></div><div class="sic">{c}</div></div>' for i, (a, b, c) in enumerate(rowsA))}
      </div>'''

# B · paso 1
B = f'''      <div class="sc" id="sB" style="background:{LIGHT}">
        {stephead("B", 1, "Crea tu cuenta")}
        <div class="abs card" id="Bcard" style="left:70px;top:620px;width:940px;height:560px">
          <div class="abs eyebrow" style="left:44px;top:44px">CREAR MI CUENTA</div>
          {field("Bf0", "store", "Nombre de tu tienda", "Tienda Demo", 100)}
          {field("Bf1", "mail", "Correo", "hola@tiendademo.pe", 250)}
          <div class="abs btn" id="Bbtn" style="left:44px;top:430px;width:852px">Crear mi cuenta</div>
        </div>
        {chip("Bc0", "circle-check", "7 días gratis", 70, 1220, extra="")}
        {chip("Bc1", "credit-card", "Sin tarjeta", 470, 1220)}
        {progress("B", 0)}
      </div>'''

# C · paso 2
C = f'''      <div class="sc" id="sC" style="background:{CREAM}">
        {stephead("C", 2, "Conecta tu WhatsApp", 88)}
        <div class="abs card" id="Ccard" style="left:70px;top:620px;width:940px;height:560px">
          <div class="abs tile" id="Cl" style="left:70px;top:60px">{MARK(150)}</div>
          <div class="abs wtile" id="Cw" style="left:670px;top:60px">{logo("whatsapp", 120, WHITE)}</div>
          <div class="abs track" style="left:290px;top:154px;width:360px"><div id="Cfill"></div></div>
          <div class="abs lnk" id="Clk" style="left:430px;top:120px">{icon("link", 40, TERRAD)}</div>
          <div class="abs api" id="Capi" style="left:44px;top:330px;width:852px">{icon("shield-check", 46, TERRAD)}<span>API oficial de WhatsApp Business</span></div>
          <div class="abs stamp" id="Cok" style="left:44px;top:440px">{icon("circle-check", 34, OK)} Conectado</div>
        </div>
        {chip("Cc0", "check", "Listo en minutos", 70, 1220)}
        {progress("C", 1)}
      </div>'''

# D · paso 3
prods = ["Vestido Emilia", "Blazer Siena", "Pantalón Nara"]
D = f'''      <div class="sc" id="sD" style="background:{LIGHT}">
        {stephead("D", 3, "Sube tu catálogo")}
        <div class="abs src" id="Ds0" style="left:70px;top:620px">{icon("file-spreadsheet", 64, OK, 1.8)}<span>Desde Excel</span></div>
        <div class="abs src" id="Ds1" style="left:555px;top:620px">{icon("camera", 64, TERRAD, 1.8)}<span>Fotos del celular</span></div>
        <div class="abs card" id="Dcard" style="left:70px;top:870px;width:940px;height:470px">
          <div class="abs eyebrow" style="left:44px;top:40px">TU CATÁLOGO</div>
          <div class="abs today" id="Dcnt" style="left:700px;top:34px"><span id="Dcn">0</span> productos</div>
          {"".join(f'<div class="abs prod" id="Dp{i}" style="left:{44 + i * 290}px;top:110px"><div class="pimg">{icon("shirt", 96, TERRAD, 1.5)}</div><b>{n}</b><span>S · M · L</span></div>' for i, n in enumerate(prods))}
        </div>
        {progress("D", 2)}
      </div>'''

# E · vender (dark)
E = f'''      <div class="sc" id="sE" style="background:{INK}">
        {head("E", "VENDEDOR IA · WHATSAPP", "Y listo: ya puedes vender", True, size=92)}
        <div class="abs chat" id="Echat" style="left:70px;top:620px;width:940px;height:720px">
          <div class="abs chd"><span class="wa">{logo("whatsapp", 40, WHITE)}</span><div><b>Tienda Demo</b><i>en línea</i></div></div>
          <div class="abs bub in" id="Em0" style="top:160px">¿Tienes el Vestido Emilia en talla M?</div>
          <div class="abs bub out" id="Em1" style="top:290px">Sí, nos quedan 5 en talla M <span class="mono">Tallas S · M · L</span></div>
          <div class="abs bub out ph" id="Em2" style="top:460px"><div class="thumb">{icon("shirt", 64, TERRAD, 1.6)}</div><div><b>Vestido Emilia</b><span><i id="Epr">S/ 189.00 · </i>3 fotos</span></div></div>
        </div>
        <div class="abs illu dk" style="left:70px;top:1370px">Recreación ilustrativa</div>
      </div>'''

# F · ¿es para ti?
checks = ["Vendes productos con precio", "Tus clientes te escriben por WhatsApp", "Tienes catálogo, aunque sea en fotos"]
F = f'''      <div class="sc" id="sF" style="background:{CREAM}">
        {head("F", "¿ES PARA TI?", "Es para ti si…", size=100)}
        {"".join(f'<div class="abs crow" id="Fr{i}" style="left:70px;top:{600 + i * 220}px;width:940px"><div class="cdot" id="Fd{i}">{icon("check", 44, WHITE, 3)}</div><span>{t}</span></div>' for i, t in enumerate(checks))}
      </div>'''

# G · precio + sin permanencia
G = f'''      <div class="sc" id="sG" style="background:{LIGHT}">
        {head("G", "PRECIOS", "Un solo plan. Pagas por tienda.")}
        <div class="abs card" id="Gcard" style="left:70px;top:560px;width:940px;height:560px">
          <div class="abs eyebrow" style="left:50px;top:50px">ENCATALOGO</div>
          <div class="abs price" style="left:50px;top:110px"><small>S/</small><span id="Gp">150</span><i>/mes con 1 tienda</i></div>
          {"".join(f'<div class="abs hl" id="Gl{i}" style="left:50px;top:{325 + i * 72}px">{icon("circle-check", 38, TERRAD)}<span>{t}</span></div>' for i, t in enumerate(["S/ 90 cada tienda extra", "Almacenes gratis", "Vendedor IA en WhatsApp incluido"]))}
        </div>
        <div class="abs callout" id="Gsp" style="left:70px;top:1160px;width:940px">
          <div class="ich">{icon("x", 48, TERRAD, 2.5)}</div>
          <div><b>Sin permanencia</b><span>Cancelas cuando quieras</span></div>
        </div>
        <div class="abs fine" style="left:70px;top:1370px">Precios en soles · IGV incluido</div>
      </div>'''

# H · close
H = f'''      <div class="sc" id="sH" style="background:{CREAM}">
        <div class="abs" id="Hlg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Hwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Ht1" style="left:0;top:770px;width:1080px">Ordena tu operación.</div>
        <div class="abs tag2" id="Ht2" style="left:0;top:880px;width:1080px">Empieza gratis hoy.</div>
        <div class="abs cta" id="Hcta" style="left:240px;top:1060px;width:600px">Crear mi cuenta</div>
        <div class="abs ctas" id="Hsub" style="left:0;top:1190px;width:1080px">7 días gratis · sin tarjeta · encatalogo.pe</div>
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
def tap(sel, t): js(f'tl.to("{sel}", {{ scale: 0.94, duration: 0.09, yoyo: true, repeat: 1 }}, {t:.3f});'); ev("click", t)
def wipe(sel, prev, t):
    js(f'tl.set("{sel}", {{ autoAlpha: 1 }}, {t:.3f});')
    js(f'tl.fromTo("{sel}", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "power3.inOut" }}, {t:.3f});')
    js(f'tl.set("{prev}", {{ autoAlpha: 0 }}, {t + 0.65:.3f});')
def count(sel, t, frm, to, d=1.0):
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v).toLocaleString("en-US"); }} }}, {t:.3f}); }})();')
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)
def stepin(sid, t, nword):
    heading(sid, t)
    js(f'tl.fromTo("#{sid}n", {{ autoAlpha: 0, scale: 0.5, rotation: -8 }}, {{ autoAlpha: 1, scale: 1, rotation: 0, duration: 0.55, ease: "back.out(1.7)" }}, {nword:.3f});'); ev("pop", nword)
    show(f"#{sid}pg", t + 0.5, 0.4, 20)
def typeit(sel, t, d):
    js(f'tl.fromTo("{sel}v", {{ clipPath: "inset(0% 100% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: {d}, ease: "steps(14)" }}, {t:.3f});')
    js(f'tl.fromTo("{sel}", {{ borderColor: "{BORDER}" }}, {{ borderColor: "{TERRAD}", duration: 0.2 }}, {t - 0.1:.3f});')
    js(f'tl.to("{sel}", {{ borderColor: "{BORDER}", duration: 0.2 }}, {t + d + 0.2:.3f});')

# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
for i in range(3): slide(f"#Ar{i}", W("e1", "ordenar", -0.2 + i * 0.3), 80, i == 0)
js(f'tl.fromTo("#sA .snum", {{ scale: 1 }}, {{ scale: 1.18, backgroundColor: "{TERRA}", color: "{INK}", duration: 0.2, stagger: 0.18, yoyo: true, repeat: 1 }}, {W("e1", "tres", -0.1):.3f});'); ev("pop", W("e1", "tres", -0.1))
js(f'tl.to("#At em", {{ color: "{TERRAD}", duration: 0.3 }}, {W("e1", "tres"):.3f});')
# B
wipe("#sB", "#sA", S[1]); stepin("B", S[1], W("e2", "uno", -0.1))
js('gsap.set(["#Bf0v", "#Bf1v"], { clipPath: "inset(0% 100% 0% 0%)" });')
show("#Bcard", W("e2", "crea", -0.2), 0.5, 60)
typeit("#Bf0", W("e2", "crea", 0.2), 0.6); typeit("#Bf1", W("e2", "cuenta", 0.1), 0.7)
tap("#Bbtn", W("e2", "tienes", -0.2))
popin("#Bc0", W("e2", "gratis", -0.2), 0.4); ev("chime2", W("e2", "gratis", -0.2))
popin("#Bc1", W("e2", "tarjeta", -0.2), 0.4)
# C
wipe("#sC", "#sB", S[2]); stepin("C", S[2], W("e3", "dos", -0.1))
js('gsap.set(["#Cok", "#Cc0"], { autoAlpha: 0 });')
show("#Ccard", W("e3", "conecta", -0.2), 0.5, 60)
c0, c1 = W("e3", "whatsapp", -0.1), W("e3", "usamos", 0.0)
js(f'tl.fromTo("#Cfill", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: {max(0.5, c1 - c0):.2f}, ease: "power1.inOut" }}, {c0:.3f});')
popin("#Clk", c1, 0.35)
show("#Capi", W("e3", "api", -0.2), 0.45, 30); ev("pop", W("e3", "api", -0.2))
js(f'tl.to("#Cw", {{ scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {W("e3", "business"):.3f});')
popin("#Cok", W("e3", "listo", -0.1), 0.4, False); ev("chime2", W("e3", "listo", -0.1))
popin("#Cc0", W("e3", "minutos", -0.1), 0.4)
# D
wipe("#sD", "#sC", S[3]); stepin("D", S[3], W("e4", "tres", -0.1))
show("#Dcard", W("e4", "sube", -0.1), 0.5, 60)
popin("#Ds0", W("e4", "excel", -0.15), 0.4); popin("#Ds1", W("e4", "fotos", -0.15), 0.4)
for i in range(3): popin(f"#Dp{i}", W("e4", "excel", 0.3 + i * 0.35), 0.35, i == 0)
count("#Dcn", W("e4", "excel", 0.3), 0, 48, 1.6)
js(f'tl.to("#Ds1", {{ y: -12, duration: 0.18, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {W("e4", "celular"):.3f});')
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
show("#Echat", W("e5", "ya", -0.1), 0.5, 60)
popin("#Em0", W("e5", "vendedor", -0.1), 0.35)
popin("#Em1", W("e5", "stock", -0.2), 0.35)
popin("#Em2", W("e5", "fotos", -0.15), 0.35)
js('gsap.set("#Epr", { autoAlpha: 0 });')
js(f'tl.fromTo("#Epr", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, duration: 0.3 }}, {W("e5", "precios", -0.05):.3f});'); ev("pop", W("e5", "precios", -0.05))
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
for i, w_ in enumerate(["vendes", "clientes", "tienes"]):
    slide(f"#Fr{i}", W("e6", w_, -0.25), -60, False); popin(f"#Fd{i}", W("e6", w_, 0.15), 0.35)
js(f'tl.to("#Fr2 span", {{ color: "{TERRAD}", duration: 0.3 }}, {W("e6", "aunque"):.3f});')
# G
wipe("#sG", "#sF", S[6]); heading("G", S[6])
js('gsap.set("#Gsp", { autoAlpha: 0 });')
show("#Gcard", W("e7", "plan", -0.2), 0.5, 60)
count("#Gp", W("e7", "ciento", -0.1), 0, 150, 0.9)
for i, w_ in enumerate(["noventa", "almacenes", "gratis"]): slide(f"#Gl{i}", W("e7", w_, 0.1 if i < 2 else 0.4), -60)
slide("#Gsp", W("e8", "sin", -0.1), 0, False); ev("chime2", W("e8", "sin", -0.1))
js(f'tl.to("#Gsp .ich", {{ rotation: 90, duration: 0.4, ease: "back.out(2)" }}, {W("e8", "cancelas"):.3f});')
# H
wipe("#sH", "#sG", S[7])
popin("#Hlg", S[7] + 0.35, 0.6); show("#Hwm", S[7] + 0.6, 0.45, 20)
show("#Ht1", W("e9", "ordena", -0.1), 0.5, 30); show("#Ht2", W("e9", "empieza", -0.1), 0.5, 30)
popin("#Hcta", W("e9", "crea", -0.15), 0.5); ev("chime", W("e9", "crea", -0.15))
show("#Hsub", W("e9", "hoy", 0.1), 0.4, 15)
js(f'tl.to("#Hcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e9", "hoy", 0.5):.3f});')
json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — empiezas en 3 pasos</title>
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
