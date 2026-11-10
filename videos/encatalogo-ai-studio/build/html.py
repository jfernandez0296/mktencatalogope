# EnCatalogo.pe — AI Studio vertical 9:16 (~60 s). Identidad: brand/encatalogo/frame.md · datos: brand/encatalogo/producto.md
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
HL = {"encatalogo", "celular", "catálogo", "ai", "studio", "blazer", "vestido", "jean", "excel", "whatsapp", "fotos", "tallas",
      "precios", "stock", "equipo", "claude", "gemini", "gratis", "prenda", "enlace", "setecientos", "digital"}
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

# ---- vector garments (recreación ilustrativa), viewBox 200x240
GARM = {
 "blazer": '''<path d="M62 20 L100 40 L138 20 L176 44 L190 200 L160 206 L156 120 L150 232 L50 232 L44 120 L40 206 L10 200 L24 44 Z" fill="{c}"/>
  <path d="M62 20 L100 120 L138 20" fill="none" stroke="{l}" stroke-width="5"/><path d="M100 120 L100 232" stroke="{l}" stroke-width="3"/>
  <circle cx="108" cy="150" r="5" fill="{l}"/><circle cx="108" cy="180" r="5" fill="{l}"/>
  <path d="M70 170 L90 170" stroke="{l}" stroke-width="4"/><path d="M114 100 L132 100" stroke="{l}" stroke-width="4"/>''',
 "vestido": '''<path d="M74 10 L88 30 L112 30 L126 10 L142 22 L132 84 L124 96 L178 232 L22 232 L76 96 L68 84 L58 22 Z" fill="{c}"/>
  <path d="M88 30 Q100 52 112 30" fill="none" stroke="{l}" stroke-width="4"/><path d="M72 96 L128 96" stroke="{l}" stroke-width="6"/>
  <path d="M100 100 L92 232 M100 100 L134 232 M100 100 L64 232" stroke="{l}" stroke-width="2" opacity=".6"/>''',
 "jean": '''<path d="M42 12 L158 12 L168 234 L118 234 L102 96 L98 96 L82 234 L32 234 Z" fill="{c}"/>
  <path d="M42 34 L158 34" stroke="{l}" stroke-width="4"/><path d="M100 34 L100 92" stroke="{l}" stroke-width="3"/>
  <path d="M50 46 Q66 70 82 46 M118 46 Q134 70 150 46" fill="none" stroke="{l}" stroke-width="3"/>
  <circle cx="100" cy="24" r="4" fill="{l}"/>''',
 "camisa": '''<path d="M70 14 L100 26 L130 14 L178 46 L162 92 L146 84 L146 232 L54 232 L54 84 L38 92 L22 46 Z" fill="{c}"/>
  <path d="M84 18 L100 44 L116 18" fill="none" stroke="{l}" stroke-width="4"/><path d="M100 44 L100 232" stroke="{l}" stroke-width="3"/>
  <circle cx="106" cy="80" r="4" fill="{l}"/><circle cx="106" cy="120" r="4" fill="{l}"/><circle cx="106" cy="160" r="4" fill="{l}"/>''',
}
COL = {"blazer": ("#1a1a1a", "#3d3d3d", "#2a2622", "#4a433c"), "vestido": ("#A65353", "#c27a6c", "#6e4440", "#8a5a52"),
       "jean": ("#3b5373", "#5c7699", "#36404c", "#4c5866"), "camisa": ("#F2E6CE", "#D9C8AA", "#9b8f7a", "#857a68")}
def garm(kind, w, after=True):
    c = COL[kind]; fill, line = (c[0], c[1]) if after else (c[2], c[3])
    return f'<svg viewBox="0 0 200 240" width="{w}" height="{w * 1.2:.0f}" aria-label="{kind}">{GARM[kind].format(c=fill, l=line)}</svg>'
CLUTTER = '''<svg class="abs" style="left:0;top:0" width="100%" height="100%" aria-hidden="true">
  <rect x="6%" y="4%" width="34%" height="88%" fill="none" stroke="#2e2419" stroke-width="10"/>
  <line x1="0" y1="18%" x2="100%" y2="14%" stroke="#3a2d20" stroke-width="8"/>
  <ellipse cx="82%" cy="30%" rx="12%" ry="18%" fill="#6f5a43" opacity=".55"/>
  <rect x="68%" y="70%" width="26%" height="22%" rx="6" fill="#3b2f23"/><rect x="72%" y="62%" width="18%" height="10%" rx="4" fill="#57452f"/>
  <rect x="2%" y="76%" width="22%" height="20%" rx="6" fill="#4a3a2a"/><circle cx="18%" cy="12%" r="7%" fill="#e8c27a" opacity=".22"/>
</svg>'''
def before(kind, W_, H_, gw, gx, gy, rot=-8, lab=None, sid=""):
    l = f'<div class="abs lab" style="left:20px;bottom:20px">{lab}</div>' if lab else ""
    return (f'<div class="abs bf" {sid} style="left:0;top:0;width:{W_}px;height:{H_}px">{CLUTTER}'
            f'<div class="abs" style="left:{gx}px;top:{gy}px;transform:rotate({rot}deg)">{garm(kind, gw, False)}</div>'
            f'<div class="abs dim"></div>{l}</div>')
def after(kind, W_, H_, gw, gx, gy, lab=None, sid=""):
    l = f'<div class="abs lab lt" style="right:20px;bottom:20px">{lab}</div>' if lab else ""
    return (f'<div class="abs af" {sid} style="left:0;top:0;width:{W_}px;height:{H_}px">'
            f'<div class="abs floor" style="left:{gx + gw * 0.1:.0f}px;top:{gy + gw * 1.2 - 14:.0f}px;width:{gw * 0.8:.0f}px"></div>'
            f'<div class="abs" style="left:{gx}px;top:{gy}px">{garm(kind, gw)}</div>{l}</div>')
ILLU = lambda sid, top, dark=False: f'<div class="abs illu{" dk" if dark else ""}" id="{sid}il" style="left:70px;top:{top}px">Recreación ilustrativa</div>'

# A · hook
A = f'''      <div class="sc" id="sA" style="background:{CREAM}">
        {BRAND("A")}
        {head("A", "AI STUDIO", "¿Tus fotos de producto se ven así?", top=290, size=100)}
        <div class="abs shot" id="Ash" style="left:70px;top:640px;width:560px;height:760px">
          {before("blazer", 560, 760, 380, 90, 150, -9)}
          <div class="abs flash" id="Afl"></div>
        </div>
        {"".join(chip(f"Ac{i}", ic, t, 660, 760 + i * 170) for i, (ic, t) in enumerate([("smartphone", "Celular"), ("shirt", "Probador"), ("camera", "Poca luz")]))}
        {ILLU("A", 1420)}
      </div>'''

# B · before/after reveal
B = f'''      <div class="sc" id="sB" style="background:{INK}">
        {head("B", "AI STUDIO · ENCATALOGO", "De la foto del celular a la foto de catálogo", True, size=84)}
        <div class="abs frame" id="Bfr" style="left:70px;top:600px;width:940px;height:800px">
          {before("blazer", 940, 800, 440, 250, 120, -9, "Foto del celular")}
          {after("blazer", 940, 800, 440, 250, 110, "Foto de catálogo", 'id="Baf"')}
          <div class="abs handle" id="Bhd" style="height:800px"><div class="knob" style="top:363px">{icon("wand-sparkles", 36, INK)}</div></div>
        </div>
        {ILLU("B", 1420, True)}
      </div>'''

# C · three garments
items = [("blazer", "Blazer Siena"), ("vestido", "Vestido Emilia"), ("jean", "Jean Araña")]
C = f'''      <div class="sc" id="sC" style="background:{LIGHT}">
        {head("C", "CADA PRENDA", "Lista para tu catálogo")}
        {"".join(f"""<div class="abs tile" id="Ct{i}" style="left:{70 + i * 325}px;top:560px">
          {before(k, 290, 560, 220, 35, 150, -7 + i * 5)}
          {after(k, 290, 560, 220, 35, 140, None, f'id="Ca{i}"')}
          <div class="abs ok" id="Co{i}">{icon("check", 30, WHITE, 3)}</div>
        </div><div class="abs tname" id="Cn{i}" style="left:{70 + i * 325}px;top:1150px">{n}</div>""" for i, (k, n) in enumerate(items))}
        {ILLU("C", 1240)}
      </div>'''

# D · upload → digital catalog
prods = [("blazer", "Blazer Siena", "S/ 200"), ("vestido", "Vestido Emilia", "S/ 189"), ("jean", "Jean Araña", "S/ 129"), ("camisa", "Camisa Lino", "S/ 99")]
XLS = '<span class="xls">XLS</span>'
D = f'''      <div class="sc" id="sD" style="background:{CREAM}">
        {head("D", "SUBE TU CATÁLOGO", "Desde Excel o fotos del celular", size=86)}
        <div class="abs chip" id="Dx" style="left:70px;top:560px;background:{WHITE}">{XLS}<span>Excel</span></div>
        <div class="abs chip" id="Dc" style="left:330px;top:560px;background:{WHITE}">{icon("camera", 40, TERRAD)}<span>Fotos del celular</span></div>
        <div class="abs card brw" id="Dbr" style="left:70px;top:710px;width:940px;height:700px">
          <div class="abs bar0"><i></i><i></i><i></i><span>Tu catálogo digital</span><b id="Dlink">{icon("store", 28, WHITE)} Tienda online · enlace propio</b></div>
          {"".join(f"""<div class="abs pc" id="Dp{i}" style="left:{30 + (i % 2) * 450}px;top:{110 + (i // 2) * 290}px">
            <div class="pim">{garm(k, 170)}</div><div class="pinfo"><b>{n}</b><span>{pr}</span><i>S · M · L</i></div></div>""" for i, (k, n, pr) in enumerate(prods))}
        </div>
      </div>'''

# E · WhatsApp seller sends the photos
E = f'''      <div class="sc" id="sE" style="background:{INK}">
        {head("E", "VENDEDOR IA · WHATSAPP", "Envía tus fotos, con tallas y precios", True, size=86)}
        <div class="abs chat" id="Echat" style="left:70px;top:590px;width:940px;height:830px">
          <div class="abs chd"><span class="wa">{logo("whatsapp", 40, WHITE)}</span><div><b>Tu tienda</b><i>en línea</i></div></div>
          <div class="abs bub in" id="Em0" style="top:150px">Hola, ¿tienes el vestido en talla M?</div>
          <div class="abs bub out pho" id="Em1" style="top:260px">
            <div class="pimg">{after("vestido", 230, 260, 170, 30, 30)}</div>
            <div class="pt"><b>Vestido Emilia</b><span id="Epr">S/ 189.00</span><i id="Etl">Tallas S · M · L</i></div>
          </div>
          <div class="abs bub out" id="Em2" style="top:600px">Sí, quedan 5 en talla M</div>
          <div class="abs paid" id="Ehd" style="top:716px">{icon("bell-ring", 32, TERRAD)} Sabe cuándo pasar a tu equipo</div>
        </div>
      </div>'''

# F · proof + tech
F = f'''      <div class="sc" id="sF" style="background:{LIGHT}">
        {head("F", "VENDEDOR IA EN NÚMEROS", "Ya atiende a tus clientes")}
        <div class="abs card" id="Fcard" style="left:70px;top:560px;width:940px;height:400px">
          <div class="abs eyebrow" style="left:50px;top:50px">CHATS ATENDIDOS POR LA IA</div>
          <div class="abs bignum" style="left:50px;top:110px">+<span id="Fn">2.700</span></div>
        </div>
        {"".join(f'<div class="abs mini" id="Fs{i}" style="left:{70 + i * 485}px;top:990px"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate([("+117 mil", "mensajes de WhatsApp"), ("+20 mil", "clientes gestionados")]))}
        <div class="abs eyebrow" id="Fte" style="left:70px;top:1210px;color:{MUTED}">TECNOLOGÍA DE</div>
        <div class="abs tech" id="Fc" style="left:70px;top:1270px"><span class="cl">{logo("claude", 40, TERRA)}</span>Claude · Anthropic</div>
        <div class="abs tech" id="Fg" style="left:560px;top:1270px"><span class="cl">{icon("sparkles", 40, TERRAD)}</span>Google Gemini</div>
      </div>'''

# G · close
G = f'''      <div class="sc" id="sG" style="background:{CREAM}">
        <div class="abs" id="Glg" style="left:390px;top:280px">{MARK(300)}</div>
        <div class="abs wm" id="Gwm" style="left:0;top:630px;width:1080px">EnCatalogo.pe</div>
        <div class="abs tag1" id="Gt1" style="left:0;top:750px;width:1080px;font-size:78px">Fotos IA, catálogo digital</div>
        <div class="abs tag2" id="Gt2" style="left:0;top:850px;width:1080px;font-size:78px">y vendedor virtual.</div>
        <div class="abs ctas" id="Gsb0" style="left:0;top:965px;width:1080px">Para marcas de retail peruanas</div>
        <div class="abs cta" id="Gcta" style="left:240px;top:1090px;width:600px">Probar 7 días gratis</div>
        <div class="abs ctas" id="Gsub" style="left:0;top:1220px;width:1080px">Sin tarjeta · encatalogo.pe</div>
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
def heading(sid, t): show(f"#{sid}k", t + 0.2, 0.4, 20); show(f"#{sid}t", t + 0.35, 0.5, 40)

# A
show("#Abr", 0.1, 0.4, 20); show("#Ak", 0.25, 0.4, 20); show("#At", 0.4, 0.55, 40)
js(f'tl.fromTo("#Ash", {{ autoAlpha: 0, rotation: -4, y: 80 }}, {{ autoAlpha: 1, rotation: 2, y: 0, duration: 0.6, ease: "power3.out" }}, {W("e1", "así", -0.3):.3f});')
js(f'tl.fromTo("#Afl", {{ autoAlpha: 0.9 }}, {{ autoAlpha: 0, duration: 0.5 }}, {W("e1", "así", 0.1):.3f});'); ev("click", W("e1", "así", 0.1))
for i, w_ in enumerate(["celular", "probador", "poca"]): slide(f"#Ac{i}", W("e1", w_, -0.1), 80)
show("#Ail", W("e1", "celular"), 0.4, 10)
# B
wipe("#sB", "#sA", S[1]); heading("B", S[1])
show("#Bfr", W("e2", "studio", -0.2), 0.5, 60); show("#Bil", W("e2", "studio", 0.2), 0.4, 10)
tw0, tw1 = W("e2", "pasas", -0.1), W("e2", "catálogo", 0.3)
js(f'tl.fromTo("#Baf", {{ clipPath: "inset(0% 0% 0% 100%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: {tw1 - tw0:.2f}, ease: "power2.inOut" }}, {tw0:.3f});')
js(f'tl.fromTo("#Bhd", {{ x: 940 }}, {{ x: 0, duration: {tw1 - tw0:.2f}, ease: "power2.inOut" }}, {tw0:.3f});'); ev("chime", tw1)
js(f'tl.to("#Bhd", {{ autoAlpha: 0, duration: 0.3 }}, {tw1 + 0.2:.3f});')
# C
wipe("#sC", "#sB", S[2]); heading("C", S[2])
js('gsap.set(["#Ca0", "#Ca1", "#Ca2", ".ok"], { autoAlpha: 0 });')
for i, w_ in enumerate(["blazer", "vestido", "jean"]):
    t0 = W("e3", w_, -0.35)
    show(f"#Ct{i}", t0, 0.4, 50); show(f"#Cn{i}", t0 + 0.1, 0.35, 20)
    js(f'tl.set("#Ca{i}", {{ autoAlpha: 1 }}, {t0 + 0.45:.3f});')
    js(f'tl.fromTo("#Ca{i}", {{ clipPath: "inset(100% 0% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.55, ease: "power2.inOut" }}, {t0 + 0.45:.3f});'); ev("pop", t0 + 0.6)
show("#Cil", W("e3", "blazer"), 0.4, 10)
js(f'tl.fromTo(".ok", {{ autoAlpha: 0, scale: 0.4 }}, {{ autoAlpha: 1, scale: 1, duration: 0.35, stagger: 0.12, ease: "back.out(2)" }}, {W("e3", "lista", -0.1):.3f});'); ev("chime2", W("e3", "lista", -0.1))
# D
wipe("#sD", "#sC", S[3]); heading("D", S[3])
popin("#Dx", W("e4", "excel", -0.1), 0.4); popin("#Dc", W("e4", "fotos", -0.1), 0.4)
show("#Dbr", W("e4", "celular", 0.1), 0.5, 60)
js(f'tl.fromTo("#sD .pc", {{ autoAlpha: 0, y: 40 }}, {{ autoAlpha: 1, y: 0, duration: 0.4, stagger: 0.14, ease: "power3.out" }}, {W("e4", "vende", -0.2):.3f});'); ev("pop", W("e4", "vende", -0.2))
popin("#Dlink", W("e4", "enlace", -0.2), 0.4); ev("chime2", W("e4", "enlace", 0.1))
# E
wipe("#sE", "#sD", S[4]); heading("E", S[4])
js('gsap.set(["#Ehd"], { autoAlpha: 0 });')
show("#Echat", W("e5", "whatsapp", -0.4), 0.5, 60)
popin("#Em0", W("e5", "whatsapp", 0.1), 0.35)
popin("#Em1", W("e5", "fotos", -0.2), 0.45)
js(f'tl.fromTo("#Etl", {{ color: "{INK}" }}, {{ color: "{TERRAD}", duration: 0.25 }}, {W("e5", "tallas"):.3f});')
js(f'tl.fromTo("#Epr", {{ color: "{INK}" }}, {{ color: "{TERRAD}", duration: 0.25 }}, {W("e5", "precios"):.3f});')
popin("#Em2", W("e6", "stock", -0.2), 0.35)
popin("#Ehd", W("e6", "pasar", -0.2), 0.4); ev("chime2", W("e6", "equipo"))
# F
wipe("#sF", "#sE", S[5]); heading("F", S[5])
show("#Fcard", W("e7", "son", -0.2), 0.5, 60)
js(f'(() => {{ const o = {{ v: 0 }}; tl.to(o, {{ v: 2700, duration: 1.3, ease: "power2.out", onUpdate: () => {{ const n = Math.round(o.v); document.querySelector("#Fn").textContent = n >= 1000 ? Math.floor(n / 1000) + "." + String(n % 1000).padStart(3, "0") : String(n); }} }}, {W("e7", "dos", -0.1):.3f}); }})();')
for i in range(2): show(f"#Fs{i}", W("e7", "chats", 0.1 + i * 0.15), 0.4, 30)
show("#Fte", W("e7", "tecnología", -0.2), 0.35, 15)
popin("#Fc", W("e7", "claude", -0.1), 0.4); popin("#Fg", W("e7", "google", -0.1), 0.4)
# G
wipe("#sG", "#sF", S[6])
popin("#Glg", S[6] + 0.35, 0.6); show("#Gwm", W("e8", "encatalogo", 0.2), 0.45, 20)
show("#Gt1", W("e8", "fotos", -0.1), 0.5, 30); show("#Gt2", W("e8", "vendedor", -0.1), 0.5, 30)
show("#Gsb0", W("e8", "marcas", -0.1), 0.4, 15)
popin("#Gcta", W("e8", "prueba", -0.15), 0.5); ev("chime", W("e8", "prueba", -0.15))
show("#Gsub", W("e8", "sin", -0.1), 0.4, 15)
js(f'tl.to("#Gcta", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {W("e8", "sin", 0.6):.3f});')
json.dump(EV, open(os.path.join(ROOT, "build", "events.json"), "w"))

CSS = open(os.path.join(ROOT, "build", "style.css")).read()
html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>EnCatalogo.pe — AI Studio</title>
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
