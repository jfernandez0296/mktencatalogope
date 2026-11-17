# EnCatalogo.pe — un día con EnCatalogo, vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "día", "nueve", "mediodía", "cuatro", "seis", "celular", "ventas", "avisa", "traslado", "whatsapp", "fotos", "tallas",
      "precios", "stock", "yape", "valida", "caja", "descuenta", "sunat", "recibido", "disponible", "sistema", "orden", "control", "gratis"}
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
def chathead(name="Tienda Demo", status="en línea"):
    return f'<div class="abs chd"><span class="wa">{logo("whatsapp", 40, WHITE)}</span><div><b>{name}</b><i>{status}</i></div></div>'

# persistent clock (scenes B–F)
TIMES = [("9:00", "Mañana"), ("12:00", "Mediodía"), ("16:00", "Tarde"), ("18:00", "Cierre")]
CLK = (f'      <div class="abs clk" id="clk" data-layout-allow-overlap="true" style="left:570px;top:112px">'
       f'<span class="cki">{icon("clock", 46, TERRAD, 2.2)}</span><div class="ckt">'
       + "".join(f'<div class="cks" id="ck{i}" data-layout-allow-overlap="true"><b>{t}</b><i>{l}</i></div>' for i, (t, l) in enumerate(TIMES))
       + '</div><div class="ckbar"><div id="ckfill"></div></div></div>')

# A · hook: the day as a timeline
stops = [("9:00", "smartphone", "Revisas tu negocio desde el celular"), ("12:00", "message-circle", "Vendes por WhatsApp con IA"),
         ("16:00", "wallet", "Vendes en caja y facturas"), ("18:00", "truck", "Recibes tu traslado")]
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "UN DÍA CON ENCATALOGO", "¿Cómo se ve un día en tu tienda?", top=290, size=100)}
        <div class="abs card" id="Acard" style="left:70px;top:690px;width:940px;height:700px">
          <div class="abs tline" id="Aline" style="left:150px;top:90px;height:520px"></div>
          {"".join(f'<div class="abs stop" id="As{i}" style="left:40px;top:{50 + i * 160}px"><div class="stt">{t}</div><div class="sdot">{icon(ic, 34, WHITE, 2)}</div><span>{d}</span></div>' for i, (t, ic, d) in enumerate(stops))}
        </div>
      </div>'''

# B · 9:00 phone with yesterday's close
bars = [48, 62, 55, 70, 58, 92, 80]
movers = [("Vestido Emilia", 100), ("Polo Lima", 78), ("Jean Nara", 56)]
B = f'''      <div class="sc" id="sB" style="background:{LIGHT}">
        {head("B", "9:00 · ANTES DE ABRIR", "Así cerró ayer tu tienda", size=88)}
        <div class="abs phone" id="Bph" style="left:240px;top:530px">
          <div class="abs eyebrow" style="left:44px;top:56px">RESUMEN DE AYER</div>
          <div class="abs big" style="left:44px;top:100px">S/ <span id="Bsales">3,960</span></div>
          <div class="abs up" id="Bup" style="left:44px;top:214px">{icon("trending-up", 34, OK)} Ventas de ayer</div>
          {"".join(f'<div class="abs bar" id="Bb{i}" style="left:{52 + i * 70}px;top:{470 - h * 1.8:.0f}px;height:{h * 1.8:.0f}px{";background:" + TERRAD if i == 6 else ""}"></div>' for i, h in enumerate(bars))}
          <div class="abs low" id="Blow" style="left:28px;top:500px">
            <div class="eyebrow" style="margin-bottom:10px">LOS QUE MÁS SE MUEVEN</div>
            {"".join(f'<div class="mv" id="Bm{i}"><span>{n}</span><div class="mvb"><div style="width:{w}%"></div></div></div>' for i, (n, w) in enumerate(movers))}
          </div>
        </div>
      </div>'''

# C · stock alert + create transfer
C = f'''      <div class="sc" id="sC" style="background:{CREAM}">
        {head("C", "ALERTA DE STOCK", "Se acaba la talla M en Miraflores", size=88)}
        <div class="abs callout" id="Calert" style="left:70px;top:560px;width:940px">
          <div class="ich">{icon("bell-ring", 48, TERRAD)}</div>
          <div><b>Reponer pronto</b><span>Vestido Emilia · Talla M · Miraflores</span></div>
        </div>
        <div class="abs st2" id="Cs0" style="left:70px;top:790px"><span>{icon("store", 36, TERRAD)} Miraflores</span><b class="lowq">2</b><i>Talla M</i></div>
        <div class="abs st2" id="Cs1" style="left:555px;top:790px"><span>{icon("warehouse", 36, TERRAD)} Almacén</span><b>18</b><i>Talla M</i></div>
        <div class="abs cta sm" id="Cbtn" style="left:70px;top:1070px;width:940px">{icon("truck", 40, WHITE, 2)}<span>Crear traslado</span></div>
        <div class="abs card" id="Ctr" style="left:70px;top:1070px;width:940px;height:330px">
          <div class="abs eyebrow" style="left:44px;top:40px">TRASLADO #0187 · 12 UNIDADES</div>
          <div class="abs route" style="left:44px;top:92px">Almacén {icon("arrow-right", 44, TERRAD)} Miraflores</div>
          <div class="abs pill ok" id="Cp0" style="left:44px;top:220px">{icon("check", 28, OK, 3)} Preparado</div>
          <div class="abs pill" style="left:330px;top:220px">En camino</div>
          <div class="abs pill" style="left:590px;top:220px">Recibido</div>
        </div>
      </div>'''

# D · 12:00 WhatsApp sale (dark)
D = f'''      <div class="sc" id="sD" style="background:{INK}">
        {head("D", "MEDIODÍA · WHATSAPP", "Tu vendedor IA atiende y cobra", True, size=86)}
        <div class="abs chat" id="Dchat" style="left:70px;top:580px;width:940px;height:880px">
          {chathead()}
          <div class="abs bub in" id="Dm0" style="top:150px">Hola, ¿tienes el Vestido Emilia en talla M?</div>
          <div class="abs bub out ph" id="Dm1" style="top:310px"><div class="thumb">{icon("shirt", 64, TERRAD, 1.6)}</div><div><b>Vestido Emilia</b><span>3 fotos</span></div><div class="pics">{"".join(f'<i>{icon("camera", 30, TERRAD)}</i>' for i in range(3))}</div></div>
          <div class="abs bub out" id="Dm2" style="top:490px">Tallas <span class="sizes">{"".join(f'<i>{t}</i>' for t in "SML")}</span> · <b class="pr" id="Dpr">S/ 189.00</b></div>
          <div class="abs paid" id="Dstk" style="top:610px;left:auto;right:36px">{icon("package", 32, OK)} Stock real · hay talla M</div>
          <div class="abs bub in" id="Dm3" style="top:700px">Listo, ya te yapeé</div>
          <div class="abs paid" id="Dok" style="top:790px">{icon("circle-check", 32, OK)} Pago validado · Yape</div>
        </div>
      </div>'''

# E · 16:00 in-store POS
E = f'''      <div class="sc" id="sE" style="background:{LIGHT}">
        {head("E", "16:00 · CAJA EN TIENDA", "Vendes en caja, y todo se actualiza", size=86)}
        <div class="abs card" id="Epos" style="left:70px;top:560px;width:940px;height:470px">
          <div class="abs eyebrow" style="left:44px;top:40px">CAJA · MIRAFLORES</div>
          <div class="abs il" style="left:44px;top:110px;width:852px"><span>1 × Polo Lima · Talla M</span><b>S/ 79.00</b></div>
          <div class="abs il" style="left:44px;top:180px;width:852px"><span>1 × Jean Nara · 30</span><b>S/ 129.00</b></div>
          <div class="abs il tot" style="left:44px;top:250px;width:852px"><span>Total</span><b>S/ 208.00</b></div>
          <div class="abs cta sm" id="Epay" style="left:44px;top:350px;width:852px;height:90px">{icon("wallet", 36, WHITE, 2)}<span>Cobrar</span></div>
        </div>
        <div class="abs card tile" id="Et0" style="left:70px;top:1070px;width:455px;height:340px">
          <div class="abs eyebrow" style="left:36px;top:36px">STOCK · POLO LIMA M</div>
          <div class="abs tnum" style="left:36px;top:96px"><span id="Eq">8</span></div>
          <div class="abs tmeta" id="Edn" style="left:36px;top:250px">{icon("package", 32, TERRAD)} Se descontó solo</div>
        </div>
        <div class="abs card tile" id="Et1" style="left:555px;top:1070px;width:455px;height:340px">
          <div class="abs eyebrow" style="left:36px;top:36px">FACTURA ELECTRÓNICA</div>
          <div class="abs inv" style="left:36px;top:96px;font-size:46px">F001-00004219</div>
          <div class="abs tmeta" style="left:36px;top:170px">IGV 18 % incluido</div>
          <div class="abs stamp" id="Estamp" style="left:36px;top:240px">{icon("circle-check", 32, OK)} Aceptada por SUNAT</div>
        </div>
      </div>'''

# F · 18:00 transfer received
steps = ["Preparado", "En camino", "Recibido"]
F = f'''      <div class="sc" id="sF" style="background:{CREAM}">
        {head("F", "18:00 · CIERRE DEL DÍA", "El traslado llegó a Miraflores", size=88)}
        <div class="abs card" id="Fcard" style="left:70px;top:560px;width:940px;height:480px">
          <div class="abs eyebrow" style="left:44px;top:44px">TRASLADO #0187 · 12 UNIDADES</div>
          <div class="abs route" style="left:44px;top:100px">Almacén {icon("arrow-right", 44, TERRAD)} Miraflores</div>
          <div class="abs track" style="left:84px;top:290px;width:772px"><div id="Ffill"></div></div>
          <div class="abs truck" id="Ftruck" style="left:40px;top:208px">{icon("truck", 70, INK, 1.8)}</div>
          {"".join(f'<div class="abs step" id="Fs{i}" style="left:{44 + i * 386}px;top:270px"><div class="dot" id="Fd{i}">{icon("check", 30, WHITE, 3)}</div><span>{t}</span></div>' for i, t in enumerate(steps))}
        </div>
        <div class="abs callout ok" id="Fok" style="left:70px;top:1090px;width:940px">
          <div class="ich">{icon("store", 48, OK)}</div>
          <div><b>Talla M disponible otra vez</b><span>Vestido Emilia · Miraflores · <em id="Fq">2</em> unidades</span></div>
        </div>
      </div>'''

# G · recap (dark)
mods = [("package", "Inventario"), ("truck", "Traslados"), ("message-circle", "Ventas por WhatsApp"), ("wallet", "Caja"), ("receipt", "Facturación")]
G = f'''      <div class="sc" id="sG" style="background:{INK}">
        {head("G", "TODO CONECTADO", "Un solo sistema, todo el día", True, size=90)}
        {"".join(f'<div class="abs mod" id="Gm{i}" style="left:{70 if i % 2 == 0 else 555}px;top:{580 + (i // 2) * 170}px;width:{940 if i == 4 else 455}px">{icon(ic, 44, TERRA, 2)}<span>{t}</span></div>' for i, (ic, t) in enumerate(mods))}
        <div class="abs one" id="Gone" style="left:70px;top:1110px;width:940px"><span class="bchip dk">{MARK(70)}</span><b>EnCatalogo.pe</b></div>
      </div>'''

# H · close
H = f'''      <div class="sc" id="sH" style="background:{CREAM}">
        <div class="abs" id="Hlg" style="left:390px;top:300px">{MARK(300)}</div>
        <div class="abs wm" id="Hwm" style="left:0;top:650px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Ht1" style="left:0;top:770px;width:1080px">Tu mercadería en orden.</div>
        <div class="abs tag2" id="Ht2" style="left:0;top:880px;width:1080px">Tu negocio bajo control.</div>
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
def tap(sel, t): js(f'tl.to("{sel}", {{ scale: 0.94, duration: 0.09, yoyo: true, repeat: 1 }}, {t:.3f});'); ev("click", t)
def wipe(sel, prev, t):
    js(f'tl.set("{sel}", {{ autoAlpha: 1 }}, {t:.3f});')
    js(f'tl.fromTo("{sel}", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.6, ease: "power3.inOut" }}, {t:.3f});')
    js(f'tl.set("{prev}", {{ autoAlpha: 0 }}, {t + 0.65:.3f});')
def count(sel, t, frm, to, d=1.0):
    js(f'(() => {{ const o = {{ v: {frm} }}; tl.to(o, {{ v: {to}, duration: {d}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = Math.round(o.v).toLocaleString("en-US"); }} }}, {t:.3f}); }})();')
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)
def clock(i, t):
    if i == 0:
        js(f'tl.fromTo("#clk", {{ autoAlpha: 0, y: -30 }}, {{ autoAlpha: 1, y: 0, duration: 0.5, ease: "back.out(1.6)" }}, {t:.3f});')
        js(f'tl.set("#ck0", {{ autoAlpha: 1 }}, {t:.3f});')
    else:
        js(f'tl.to("#ck{i - 1}", {{ autoAlpha: 0, y: -40, duration: 0.3, ease: "power2.in" }}, {t:.3f});')
        js(f'tl.fromTo("#ck{i}", {{ autoAlpha: 0, y: 40 }}, {{ autoAlpha: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {t + 0.2:.3f});')
        js(f'tl.to("#clk .cki", {{ rotation: 360, duration: 0.6, ease: "power2.inOut" }}, {t:.3f});')
    js(f'tl.to("#ckfill", {{ scaleX: {[0.1, 0.4, 0.75, 1.0][i]}, duration: 0.6, ease: "power2.out" }}, {t:.3f});')
    ev("click", t)

js('gsap.set(["#ck1", "#ck2", "#ck3"], { autoAlpha: 0 });')
js('gsap.set("#ckfill", { scaleX: 0, transformOrigin: "0% 50%" });')
# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
show("#Acard", W("e1", "tienda", -0.2), 0.5, 60)
js(f'tl.fromTo("#Aline", {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 0%", duration: 1.6, ease: "power1.inOut" }}, {W("e1", "mostramos", -0.2):.3f});')
for i in range(4): slide(f"#As{i}", W("e1", "mostramos", -0.2) + i * 0.4, -50, True)
# B · 9:00
wipe("#sB", "#sA", S[1]); clock(0, W("e2", "nueve", 0.0)); heading("B", S[1])
show("#Bph", W("e2", "revisas", -0.4), 0.6, 120)
count("#Bsales", W("e2", "ayer", -0.3), 0, 3960, 1.1)
js(f'tl.fromTo("#sB .bar", {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 0.5, stagger: 0.06, ease: "power2.out" }}, {W("e2", "ventas", -0.3):.3f});')
show("#Bup", W("e2", "ventas"), 0.35, 15)
show("#Blow", W("e2", "productos", -0.3), 0.45, 40)
js(f'tl.fromTo("#Blow .mvb div", {{ scaleX: 0 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: 0.6, stagger: 0.12, ease: "power2.out" }}, {W("e2", "más", -0.1):.3f});'); ev("pop", W("e2", "más", -0.1))
# C · alert + transfer
wipe("#sC", "#sB", S[2]); heading("C", S[2])
js('gsap.set("#Ctr", { autoAlpha: 0 });')
slide("#Calert", W("e3", "avisa", -0.2), 0)
js(f'tl.to("#Calert .ich", {{ rotation: 14, duration: 0.1, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {W("e3", "avisa", 0.2):.3f});')
popin("#Cs0", W("e3", "miraflores", -0.1), 0.4)
js(f'tl.to("#Cs0 .lowq", {{ scale: 1.2, color: "{TERRAD}", duration: 0.2, yoyo: true, repeat: 3 }}, {W("e3", "acabando"):.3f});')
popin("#Cs1", W("e3", "así", -0.1), 0.4)
show("#Cbtn", W("e3", "así", 0.2), 0.4, 30)
tap("#Cbtn", W("e3", "traslado", -0.1))
js(f'tl.to("#Cbtn", {{ autoAlpha: 0, duration: 0.2 }}, {W("e3", "traslado", 0.15):.3f});')
popin("#Ctr", W("e3", "traslado", 0.2), 0.45, False)
popin("#Cp0", W("e3", "almacén", -0.1), 0.35); ev("chime2", W("e3", "almacén", -0.1))
# D · 12:00 WhatsApp
wipe("#sD", "#sC", S[3]); clock(1, W("e4", "mediodía", 0.0)); heading("D", S[3])
show("#Dchat", W("e4", "cliente", -0.3), 0.5, 60)
popin("#Dm0", W("e4", "escribe", -0.1), 0.35)
popin("#Dm1", W("e4", "fotos", -0.15), 0.35)
js(f'tl.fromTo("#Dm1 .pics i", {{ autoAlpha: 0, y: 10 }}, {{ autoAlpha: 1, y: 0, duration: 0.25, stagger: 0.1 }}, {W("e4", "fotos", 0.15):.3f});')
popin("#Dm2", W("e4", "tallas", -0.1), 0.35)
js(f'tl.fromTo("#Dm2 .sizes i", {{ autoAlpha: 0, scale: 0.5 }}, {{ autoAlpha: 1, scale: 1, duration: 0.25, stagger: 0.08, ease: "back.out(2)" }}, {W("e4", "tallas", 0.15):.3f});')
js(f'tl.fromTo("#Dpr", {{ autoAlpha: 0 }}, {{ autoAlpha: 1, duration: 0.3 }}, {W("e4", "precios", -0.1):.3f});')
popin("#Dstk", W("e4", "stock", -0.1), 0.4)
popin("#Dm3", W("e5", "paga", -0.1), 0.35)
popin("#Dok", W("e5", "valida", -0.05), 0.45); ev("chime", W("e5", "valida", -0.05))
# E · 16:00 POS
wipe("#sE", "#sD", S[4]); clock(2, W("e6", "cuatro", 0.0)); heading("E", S[4])
js('gsap.set(["#Edn", "#Estamp"], { autoAlpha: 0 });')
show("#Epos", W("e6", "tienda", -0.3), 0.5, 60)
tap("#Epay", W("e6", "caja", -0.05))
show("#Et0", W("e6", "el", -0.2), 0.45, 40)
count("#Eq", W("e6", "descuenta", -0.1), 8, 7, 0.4); show("#Edn", W("e6", "descuenta", 0.2), 0.35, 15); ev("pop", W("e6", "descuenta", -0.1))
show("#Et1", W("e6", "factura", -0.2), 0.45, 40)
popin("#Estamp", W("e6", "sunat", -0.1), 0.45); ev("chime", W("e6", "sunat", -0.1))
# F · 18:00 received
wipe("#sF", "#sE", S[5]); clock(3, W("e7", "seis", 0.0)); heading("F", S[5])
js('gsap.set(["#Fd1", "#Fd2", "#Fok"], { autoAlpha: 0 });')
show("#Fcard", W("e7", "traslado", -0.3), 0.5, 60)
ts, te = W("e7", "traslado", 0.1), W("e7", "recibido", 0.1)
js(f'tl.fromTo("#Ffill", {{ scaleX: 0.5 }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: {te - ts:.2f}, ease: "power1.inOut" }}, {ts:.3f});')
js(f'tl.fromTo("#Ftruck", {{ x: 386 }}, {{ x: 772, duration: {te - ts:.2f}, ease: "power1.inOut" }}, {ts:.3f});')
popin("#Fd1", ts, 0.3, False); popin("#Fd2", te, 0.35); ev("chime2", te)
slide("#Fok", W("e7", "vuelve", -0.3), 0)
count("#Fq", W("e7", "disponible", -0.3), 2, 14, 0.8)
# G · recap
wipe("#sG", "#sF", S[6]); heading("G", S[6])
js(f'tl.to("#clk", {{ autoAlpha: 0, y: -30, duration: 0.3 }}, {S[6]:.3f});')
for i, w_ in enumerate(["inventario", "traslados", "ventas", "caja", "facturación"]): popin(f"#Gm{i}", W("e8", w_, -0.1), 0.35)
popin("#Gone", W("e8", "solo", -0.1), 0.5, False); ev("chime", W("e8", "solo", -0.1))
js(f'tl.to("#sG .mod", {{ borderColor: "{TERRA}", duration: 0.3, stagger: 0.05 }}, {W("e8", "sistema", 0.0):.3f});')
# H · close
wipe("#sH", "#sG", S[7])
popin("#Hlg", S[7] + 0.35, 0.6); show("#Hwm", W("e9", "encatalogo", 0.2), 0.45, 20)
show("#Ht1", W("e9", "tu", -0.1), 0.5, 30); show("#Ht2", W("e9", "tu", -0.1, 1), 0.5, 30)
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
    <title>EnCatalogo.pe — un día con EnCatalogo</title>
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
{CLK}
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
