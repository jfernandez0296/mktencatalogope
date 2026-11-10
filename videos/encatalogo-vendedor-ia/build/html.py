# EnCatalogo.pe — vendedor IA en WhatsApp, vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "whatsapp", "chatbot", "vendedor", "recomienda", "fotos", "tallas", "precios", "stock", "valida", "yape", "plin",
      "transferencia", "escribir", "nadie", "intervenir", "equipo", "setecientos", "diecisiete", "veinte", "céntimos", "mensaje", "gratis"}
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

# A · hook
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "VENDEDOR IA · WHATSAPP", "¿Quién le responde a tu cliente?", top=290, size=100)}
        <div class="abs chat" id="Achat" style="left:70px;top:660px;width:940px;height:660px">
          {chathead("Cliente nuevo", "escribiendo…")}
          <div class="abs bub in" id="Am0" style="top:160px">Hola, ¿tienes el Vestido Emilia en talla M?</div>
          <div class="abs bub in" id="Am1" style="top:320px">¿Cuánto cuesta?</div>
          <div class="abs bub in" id="Am2" style="top:420px">¿Me mandas una foto?</div>
          <div class="abs wait" id="Await" style="top:560px">{icon("clock", 34, TERRAD)} 3 mensajes sin responder</div>
        </div>
      </div>'''

# B · chatbot vs vendedor
B = f'''      <div class="sc" id="sB" style="background:{INK}">
        {head("B", "LA DIFERENCIA", "No es un chatbot. Es tu vendedor.", True, size=92)}
        <div class="abs vs bot" id="Bc0" style="left:70px;top:620px;width:940px">
          <div class="vh">{icon("x", 34, MUTED, 3)} UN CHATBOT</div>
          <div class="vt">Contesta lo que le preguntan<em id="Bxl"></em></div>
        </div>
        <div class="abs vs ai" id="Bc1" style="left:70px;top:900px;width:940px">
          <div class="vh">{icon("circle-check", 34, TERRAD)} VENDEDOR IA DE ENCATALOGO</div>
          <div class="vt">Pregunta para qué lo quiere y recomienda prendas de tu catálogo</div>
          <div class="recs">{"".join(f'<div class="rec" id="Br{i}"><span class="rt">{icon("shirt", 44, TERRAD, 1.6)}</span>{t}</div>' for i, t in enumerate(["Vestido Emilia", "Blazer Siena"]))}</div>
        </div>
      </div>'''

# C · photos, sizes, prices in the chat
C = f'''      <div class="sc" id="sC" style="background:{LIGHT}">
        {head("C", "FOTOS · TALLAS · PRECIOS", "Todo en el mismo chat")}
        {strike("C", "manda un link y espera", 550)}
        <div class="abs chat" id="Cchat" style="left:70px;top:640px;width:940px;height:800px">
          {chathead()}
          <div class="abs bub in" id="Cm0" style="top:150px">¿Tienes el Vestido Emilia?</div>
          <div class="abs bub out ph" id="Cm1" style="top:250px"><div class="thumb">{icon("shirt", 64, TERRAD, 1.6)}</div><div><b>Vestido Emilia</b><span>3 fotos</span></div><div class="pics">{"".join(f'<i id="Cp{i}">{icon("camera", 30, TERRAD)}</i>' for i in range(3))}</div></div>
          <div class="abs bub out" id="Cm2" style="top:430px">Tallas disponibles <span class="sizes">{"".join(f'<i id="Cz{i}">{t}</i>' for i, t in enumerate("SML"))}</span></div>
          <div class="abs bub out" id="Cm3" style="top:580px">Precio: <b class="pr">S/ 189.00</b></div>
          <div class="abs paid" id="Cstock" style="top:700px">{icon("package", 34, OK)} Stock real · quedan 4 en talla M</div>
        </div>
      </div>'''

# D · payment validation
D = f'''      <div class="sc" id="sD" style="background:{CREAM}">
        {head("D", "PAGOS", "Valida el pago por ti")}
        {strike("D", "te pasa el pago a ti", 550)}
        <div class="abs chat" id="Dchat" style="left:70px;top:640px;width:940px;height:500px">
          {chathead()}
          <div class="abs bub in" id="Dm0" style="top:150px">Listo, ya te pagué</div>
          <div class="abs bub in ph" id="Dm1" style="top:250px"><div class="thumb">{icon("receipt", 56, TERRAD, 1.8)}</div><div><b>Comprobante de pago</b><span>S/ 189.00</span></div></div>
          <div class="abs paid" id="Dok" style="top:400px;left:auto;right:36px">{icon("circle-check", 34, OK)} Pago validado</div>
        </div>
        {"".join(f'<div class="abs chip" id="Dp{i}" style="left:{x}px;top:1190px">{icon(ic, 40, TERRAD)}<span>{t}</span></div>' for i, (ic, t, x) in enumerate([("smartphone", "Yape", 70), ("smartphone", "Plin", 340), ("credit-card", "Transferencia", 600)]))}
      </div>'''

# E · follow-up
E = f'''      <div class="sc" id="sE" style="background:{LIGHT}">
        {head("E", "SEGUIMIENTO", "No se olvida de ningún cliente", size=88)}
        {strike("E", "se olvida del cliente", 550)}
        <div class="abs chat" id="Echat" style="left:70px;top:640px;width:940px;height:800px">
          {chathead()}
          <div class="abs day" style="top:150px">Ayer</div>
          <div class="abs bub in" id="Em0" style="top:220px">Déjame pensarlo</div>
          <div class="abs wait" id="Ewait" style="top:330px">{icon("clock", 34, TERRAD)} Sin respuesta</div>
          <div class="abs day" id="Ed1" style="top:430px">Hoy</div>
          <div class="abs bub out" id="Em1" style="top:500px">¡Hola! ¿Aún te interesa el Vestido Emilia? Todavía hay en talla M.</div>
          <div class="abs bub in" id="Em2" style="top:690px">¡Sí! Lo quiero</div>
        </div>
      </div>'''

# F · hand-off to the team
F = f'''      <div class="sc" id="sF" style="background:{INK}">
        {head("F", "TU EQUIPO AL MANDO", "Te avisa cuando necesitas intervenir", True, size=88)}
        {strike("F", "responde aunque no sepa", 550, True)}
        <div class="abs card" id="Fn" style="left:70px;top:660px;width:940px;height:300px">
          <div class="abs ich big2" style="left:44px;top:44px">{icon("bell-ring", 64, TERRAD)}</div>
          <div class="abs eyebrow" style="left:220px;top:56px">AVISO DEL VENDEDOR IA</div>
          <div class="abs ntitle" style="left:220px;top:100px">Necesitas intervenir</div>
          <div class="abs nmeta" style="left:220px;top:190px">Esta consulta la debe ver tu equipo</div>
        </div>
        <div class="abs hand" id="Fh0" style="left:70px;top:1010px">{icon("sparkles", 44, TERRA)}<span>Vendedor IA</span></div>
        <div class="abs harr" id="Fha" style="left:470px;top:1040px">{icon("arrow-right", 64, TERRA, 2.4)}</div>
        <div class="abs hand tm" id="Fh1" style="left:600px;top:1010px">{icon("users", 44, INK)}<span>Tu equipo</span></div>
        <div class="abs paid" id="Fok" style="left:70px;top:1190px">{icon("circle-check", 34, OK)} Conversación pasada a tu equipo</div>
      </div>'''

# G · proof stats
G = f'''      <div class="sc" id="sG" style="background:{CREAM}">
        {head("G", "EN NÚMEROS", "La IA ya está atendiendo")}
        <div class="abs card bigstat" id="Gs0" style="left:70px;top:560px;width:940px;height:340px">
          <div class="abs ich" style="left:50px;top:50px">{icon("message-circle", 50, TERRAD)}</div>
          <div class="abs num" style="left:200px;top:46px">+<span id="Gn0">2.700</span></div>
          <div class="abs lbl" style="left:50px;top:250px">chats atendidos por la IA</div>
        </div>
        <div class="abs card bigstat" id="Gs1" style="left:70px;top:960px;width:940px;height:340px">
          <div class="abs ich" style="left:50px;top:50px">{logo("whatsapp", 50, WA)}</div>
          <div class="abs num" style="left:200px;top:46px">+<span id="Gn1">117</span> mil</div>
          <div class="abs lbl" style="left:50px;top:250px">mensajes de WhatsApp</div>
        </div>
      </div>'''

# H · pricing
H = f'''      <div class="sc" id="sH" style="background:{LIGHT}">
        {head("H", "PRECIO DE LA IA", "Pagas por cliente atendido")}
        <div class="abs card" id="Hcard" style="left:70px;top:560px;width:940px;height:580px">
          <div class="abs eyebrow" style="left:50px;top:50px">VENDEDOR IA EN WHATSAPP</div>
          <div class="abs price" style="left:50px;top:110px"><small>S/</small><span id="Hp">0.20</span></div>
          <div class="abs per" id="Hper" style="left:50px;top:300px">por cliente atendido cada 30 días</div>
          {"".join(f'<div class="abs hl" id="Hl{i}" style="left:50px;top:{400 + i * 80}px">{icon("circle-check", 38, TERRAD)}<span>{t}</span></div>' for i, t in enumerate(["Sin cobro por mensaje", "Incluido en el plan de S/ 150/mes"]))}
        </div>
        <div class="abs fine" style="left:70px;top:1180px">Precios en soles · IGV incluido</div>
      </div>'''

# I · close
I = f'''      <div class="sc" id="sI" style="background:{CREAM}">
        <div class="abs" id="Ilg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Iwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="It1" style="left:0;top:770px;width:1080px">No es un chatbot.</div>
        <div class="abs tag2" id="It2" style="left:0;top:880px;width:1080px">Es tu vendedor.</div>
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
show("#Achat", W("e1", "whatsapp", -0.3), 0.5, 60)
for sel, w_ in [("#Am0", "talla"), ("#Am1", "precio"), ("#Am2", "foto")]: popin(sel, W("e1", w_, -0.15), 0.35)
popin("#Await", W("e1", "foto", 0.35), 0.4)
js(f'tl.to("#Await", {{ x: 10, duration: 0.07, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {W("e1", "quién"):.3f});')
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
show("#Bc0", W("e2", "chatbot", -0.3), 0.45, 40)
js(f'tl.fromTo("#Bxl", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.4, ease: "power2.out" }}, {W("e2", "preguntan", 0.3):.3f});'); ev("click", W("e2", "preguntan", 0.3))
js(f'tl.to("#Bc0", {{ opacity: 0.55, duration: 0.4 }}, {W("e2", "preguntan", 0.5):.3f});')
popin("#Bc1", W("e2", "vendedor", -0.2), 0.5)
for i in range(2): popin(f"#Br{i}", W("e2", "recomienda", i * 0.25), 0.35, i == 0)
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
strike_in("C", S[2] + 0.6, W("e3", "espera", -0.1))
show("#Cchat", W("e3", "envía", -0.6), 0.5, 60)
popin("#Cm0", W("e3", "envía", -0.3), 0.3, False)
popin("#Cm1", W("e3", "fotos", -0.1), 0.35)
js(f'tl.fromTo("#Cm1 .pics i", {{ autoAlpha: 0, y: 10 }}, {{ autoAlpha: 1, y: 0, duration: 0.25, stagger: 0.1 }}, {W("e3", "fotos", 0.2):.3f});')
popin("#Cm2", W("e3", "tallas", -0.1), 0.35)
js(f'tl.fromTo("#Cm2 .sizes i", {{ autoAlpha: 0, scale: 0.5 }}, {{ autoAlpha: 1, scale: 1, duration: 0.25, stagger: 0.08, ease: "back.out(2)" }}, {W("e3", "tallas", 0.2):.3f});')
popin("#Cm3", W("e3", "precios", -0.1), 0.35)
popin("#Cstock", W("e3", "stock", -0.1), 0.4); ev("chime2", W("e3", "stock", -0.1))
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
slide("#Dx", S[3] + 0.6, -60, False)
show("#Dchat", W("e4", "cuando", 0.1), 0.5, 60)
popin("#Dm0", W("e4", "paga", -0.1), 0.35); popin("#Dm1", W("e4", "paga", 0.3), 0.35)
popin("#Dok", W("e4", "valida", -0.05), 0.45); ev("chime", W("e4", "valida", -0.05))
for i, w_ in enumerate(["yape", "plin", "transferencia"]): popin(f"#Dp{i}", W("e4", w_, -0.1), 0.35)
js(f'tl.fromTo("#Dxl", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.35, ease: "power2.out" }}, {W("e4", "pasa"):.3f});'); ev("click", W("e4", "pasa"))
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
show("#Echat", S[4] + 0.6, 0.5, 60)
popin("#Em0", W("e5", "cliente", -0.1), 0.35)
popin("#Ewait", W("e5", "responder", -0.1), 0.4)
show("#Ed1", W("e5", "vuelve", -0.3), 0.3, 10)
popin("#Em1", W("e5", "escribir", -0.2), 0.4); ev("chime2", W("e5", "escribir", 0.1))
strike_in("E", W("e5", "olvida", -0.3), W("e5", "nadie", -0.1))
popin("#Em2", W("e5", "olvida", 0.1), 0.35)
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
strike_in("F", S[5] + 0.6, W("e6", "responder", 0.1))
popin("#Fn", W("e6", "avisa", -0.15), 0.45)
js(f'tl.to("#Fn .ich", {{ rotation: 14, duration: 0.1, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {W("e6", "avisa", 0.2):.3f});')
slide("#Fh0", W("e6", "pasa", -0.3), -60)
popin("#Fha", W("e6", "pasa", 0.1), 0.35, False)
slide("#Fh1", W("e6", "conversación", 0.1), 60)
popin("#Fok", W("e6", "equipo", -0.15), 0.4); ev("chime2", W("e6", "equipo", -0.15))
# G
wipe("#sG", "#sF", S[6]); heading("G", S[6])
show("#Gs0", W("e7", "más", -0.2), 0.5, 60); count("#Gn0", W("e7", "dos", -0.1), 0, 2700, 1.3)
show("#Gs1", W("e7", "más", -0.2, 1), 0.5, 60); count("#Gn1", W("e7", "ciento", -0.1), 0, 117, 1.1)
ev("chime", W("e7", "whatsapp", 0.1))
# H
wipe("#sH", "#sG", S[7]); heading("H", S[7])
show("#Hcard", W("e8", "veinte", -0.5), 0.5, 60)
popin("#Hp", W("e8", "veinte", -0.05), 0.5)
show("#Hper", W("e8", "cliente", -0.1), 0.4, 20)
slide("#Hl0", W("e8", "sin", -0.1), -60); slide("#Hl1", W("e8", "sin", 0.35), -60)
# I
wipe("#sI", "#sH", S[8])
popin("#Ilg", S[8] + 0.35, 0.6); show("#Iwm", W("e9", "encatalogo", 0.2), 0.45, 20)
show("#It1", W("e9", "no", -0.1), 0.5, 30); show("#It2", W("e9", "es", -0.1, 1), 0.5, 30)
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
    <title>EnCatalogo.pe — vendedor IA</title>
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
