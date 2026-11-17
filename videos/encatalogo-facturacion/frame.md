---
version: 1.0
name: EnCatalogo.pe — Frame (video / frame layer)
description: >
  Identidad gráfica de EnCatalogo.pe adaptada a video (HyperFrames). Fuente de verdad:
  EnCatalogo-Design-System.pdf (v1.0 · Nov. 2026). Cálida, operativa, editorial, directa.
  Fondos crema cálidos, DM Serif Display para promesas, Inter para operación, eyebrows en
  terracota oscuro, CTA negro en píldora, terracota como único acento. Copiar este archivo como
  `frame.md` en la raíz de cada video de EnCatalogo.
unit: the frame — 1920×1080 primary; 9:16 (1080×1920) y 1:1 documentados
principle: operación primero · tecnología como capacidad conectada · cada frase verificable

colors:
  # — los ocho tokens oficiales (no se agregan otros) —
  cream: "#F2EDE4"          # fondo cálido principal — hero, cabecera, secciones alternas
  light: "#FAF9F5"          # fondo claro — alterna con crema
  white: "#FFFFFF"          # superficie elevada — tarjetas, formularios, mockups
  ink: "#0F0F10"            # tinta / contraste — texto, CTA principal, secciones oscuras
  terracotta: "#D99873"     # terracota principal — acentos, CTA en fondo oscuro, numerales
  terracotta-dark: "#A65353"  # terracota oscuro — eyebrows, foco de campos, texto de acento
  terracotta-soft: "#F2E6CE"  # terracota suave — badges, iconos, callouts
  border: "#E7DDD1"         # borde cálido — tarjetas y campos
  # — semánticos (sólo para su estado, nunca decorativos) —
  success: "#3F7A4F"        # éxito; nunca se sustituye por terracota
  error: "#B23B3B"          # aviso / error
  whatsapp: "#25D366"       # SÓLO para el botón/ícono de WhatsApp
  # — derivados de texto —
  body: "#57534E"           # texto explicativo sobre crema/blanco
  muted: "#8A8178"          # meta, pies, etiquetas secundarias
  logo-brown: "#5E2C2C"     # SÓLO dentro del isotipo

forbidden_colors: [cyan, fucsia, rosa, magenta, "gradientes eléctricos", "neón"]

typography:
  display:   { fontFamily: "DM Serif Display", weight: 400, note: "titulares y promesas; máx. 2 líneas" }
  display-i: { fontFamily: "DM Serif Display", style: italic, color: "{colors.terracotta-dark}", note: "citas / tagline" }
  sans:      { fontFamily: "Inter", weights: [400, 500, 600, 700], note: "interfaz, cuerpo, etiquetas" }
  # escala web (PDF) → escala de frame 1920×1080
  hero-title:     { fontFamily: "DM Serif Display", cqw: 5.6, lineHeight: 1.04, tracking: "-0.01em" }   # H1 40–48px web
  section-title:  { fontFamily: "DM Serif Display", cqw: 3.8, lineHeight: 1.08 }                        # H2 28–32px
  block-title:    { fontFamily: "Inter", cqw: 2.0, weight: 700, lineHeight: 1.2 }                       # H3 18–20px
  body:           { fontFamily: "Inter", cqw: 1.5, weight: 400, lineHeight: 1.45, color: "{colors.body}" } # cuerpo 15–16px
  eyebrow:        { fontFamily: "Inter", cqw: 0.95, weight: 700, tracking: "0.14em", upper: true, color: "{colors.terracotta-dark}" }
  ordinal:        { fontFamily: "DM Serif Display", cqw: 4.5, color: "{colors.terracotta}", note: "01, 02… decorativo; en grande usar terracotta-soft" }

spacing:
  pad-x: "5cqw"
  pad-y: "4.5cqw"
  gap: "1.6cqw"
  card-pad: "1.8cqw"

radius:
  card: "1.4cqw"       # rounded-2xl
  field: "0.8cqw"
  pill: "999px"

components:
  cta-primary:   { bg: "{colors.ink}", text: "{colors.white}", shape: pill, font: "Inter 600", minHeight: "44px equiv." }
  cta-secondary: { bg: "{colors.white}", text: "{colors.ink}", border: "1px {colors.border}", shape: pill }
  cta-on-dark:   { bg: "{colors.terracotta}", text: "{colors.ink}", shape: pill, note: "única CTA permitida dentro de sección oscura" }
  badge:         { bg: "{colors.terracotta-soft}", text: "{colors.terracotta-dark}", font: "eyebrow", shape: pill, example: "NUEVO · TRASLADOS AUTOMÁTICOS" }
  badge-on-dark: { bg: "rgba(217,152,115,.18)", text: "{colors.terracotta}", shape: pill }
  card:          { bg: "{colors.white}", border: "1px {colors.border}", radius: card, shadow: "0 1px 2px rgba(15,15,16,.04), 0 8px 24px rgba(15,15,16,.05)" }
  icon-chip:     { bg: "{colors.terracotta-soft}", fg: "{colors.terracotta-dark}", radius: "0.6cqw" }
  callout:       { bg: "{colors.terracotta-soft}", borderLeft: "0.25cqw {colors.terracotta-dark}", radius: card }
  quote-rule:    { borderLeft: "0.25cqw {colors.terracotta}", text: "display-i" }
  step-dot:      { bg: "{colors.ink}", text: "{colors.white}", shape: circle, font: "Inter 700" }
  dark-section:  { bg: "{colors.ink}", headline: "DM Serif Display blanco", accent: "terracota únicamente" }
  field-focus:   { border: "{colors.terracotta-dark}", ring: "{colors.terracotta-soft}" }
---

# EnCatalogo.pe — Frame

Fuente: `brand/encatalogo/EnCatalogo-Design-System.pdf`. Este archivo traduce esa guía web a
reglas de frame para videos HyperFrames. Si algo choca con el PDF, gana el PDF.

## Promesa y orden narrativo (regla obligatoria)

Promesa base: **"Tu mercadería en orden. Tu negocio bajo control."**

EnCatalogo es el *sistema operativo de una tienda*, no un bot de WhatsApp. Todo video sigue este orden:

1. **Inventario** — stock por sede y traslados
2. **App móvil** — monitoreo y analítica de ventas
3. **Facturación y caja** — conectadas al inventario
4. **Atención automática** — por WhatsApp
5. **Asistencia con Claude** — y generación de imágenes

Nunca abrir (hook/hero) con WhatsApp o IA: invierte la jerarquía comercial. La IA y WhatsApp son
capacidades conectadas, no la promesa principal.

## Personalidad → decisiones de frame

- **Cálida y confiable** — fondos crema (`#F2EDE4`) o claros (`#FAF9F5`), nunca blanco puro de fondo ni look futurista.
- **Operativa** — cada escena muestra un mockup real (stock, traslado, reporte, boleta), nunca ilustración decorativa sin datos.
- **Editorial** — poco ruido, jerarquía tipográfica marcada, 40–55 % de aire por frame.
- **Directa** — beneficios comprobables; nada de "revoluciona tu negocio" ni "IA sin límites".

## Superficies

- Escenas de producto: alternar **crema** y **claro** para separar bloques.
- Tarjetas y mockups: **blanco** con borde cálido `#E7DDD1`, radio amplio, sombra ligera.
- **Sección oscura** (`#0F0F10`) reservada para momentos de contraste: IA/Claude, comparación o cierre. Acentos sólo en terracota; CTA terracota con texto negro.
- El hero/apertura va siempre sobre **crema**, nunca oscuro.

## Tipografía

- **DM Serif Display** para promesas y titulares de escena (máx. 2 líneas). Itálica en terracota oscuro para la cita/tagline.
- **Inter** para todo lo funcional: cuerpo, UI de mockups, etiquetas, subtítulos.
- **Eyebrow**: Inter 700, MAYÚSCULAS, tracking amplio, siempre `#A65353`. Ej.: `CAPACIDAD CONECTADA`.
- Ordinales grandes (01, 02…) en DM Serif terracota suave como marca de sección.
- Piso de legibilidad: ninguna línea que deba leerse por debajo de 1.4cqw (16:9) / 3.2cqw (9:16).

## Componentes

CTA negro en píldora ("Probar gratis") + secundaria blanca ("Agendar demo"); badge terracota suave
arriba del titular; tarjetas blancas con borde cálido; íconos terracota oscuro sobre chip terracota
suave; callout crema-terracota con filete izquierdo terracota oscuro; pasos numerados con círculo
negro. Éxito = verde semántico con texto o ícono (nunca sólo color).

## Prohibido

- Cyan, fucsia, rosa, magenta, neón, degradados eléctricos.
- Verde fuera de estados de éxito; verde WhatsApp `#25D366` sólo en su ícono/botón.
- Abrir con bot/IA; promesas genéricas de IA; cifras inventadas (usar placeholder `— cifra —` si el guion no la da).
- Transmitir información sólo por color.

## Aspect ratio

| Escena          | 16:9                               | 9:16                                   |
| --------------- | ---------------------------------- | -------------------------------------- |
| Hero            | texto izq. + mockup der.           | badge + titular arriba, mockup abajo   |
| Capacidad       | título + mockup en tarjeta blanca  | título arriba, tarjeta a ancho completo|
| Sección oscura  | centrado, badge + titular + CTA    | centrado, titular 3 líneas máx.        |
| Cierre          | promesa + CTA negro + logo         | igual, CTA a ancho completo            |

## Assets

- Fuentes: `brand/encatalogo/fonts/` (DM Serif Display 400 normal/itálica, Inter 400–700; OFL).
- Tokens CSS listos: `brand/encatalogo/tokens.css` (copiar a `assets/` del video).
- **Logo (isotipo)**: bolsa de compras con franjas onduladas tinta → café → terracota oscuro → terracota → crema.
  - `brand/encatalogo/logo/encatalogo-logo.svg` — vector con fondo transparente (usar éste en videos).
  - `brand/encatalogo/logo/encatalogo-logo-original.jpg` — archivo original recibido (fondo blanco).
  - El café `#5E2C2C` existe **sólo dentro del logo**; no usarlo como color de UI.
  - Lockup: isotipo + wordmark "EnCatalogo.pe" en Inter 700 tinta, separación ≈ 0.25× alto del isotipo.
  - Sobre fondo oscuro: la bolsa tinta pierde contraste → colocarla sobre un chip crema redondeado, nunca recolorearla.
  - No deformar, rotar, sombrear ni cambiar el orden de las franjas.

## Checklist antes de renderizar

- [ ] La apertura prioriza inventario y operación, no el bot.
- [ ] Sin cyan, fucsia, rosa ni magenta.
- [ ] La CTA final coincide con la acción ("Probar gratis" / "Agendar demo").
- [ ] Los mockups muestran datos o flujos reales del producto.
- [ ] Revisado en el formato final (16:9 y/o 9:16).
- [ ] Copy y capacidades corresponden al producto disponible.
