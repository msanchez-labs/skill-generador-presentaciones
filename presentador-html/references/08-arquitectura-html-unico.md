# 08 · Arquitectura del HTML único (HTML + CSS + JS en un archivo)

## 1. Objetivos no funcionales
- **Un solo `.html`**, abre con doble clic, funciona **offline** (fuentes, íconos, imágenes y JS incrustados).
- **Cero dependencias obligatorias**; CDN solo como opción y siempre con versión fija.
- Arranque < 1 s; navegación a 60 fps.
- Peso objetivo: < 500 KB sin imágenes; < 10 MB total.
- Fidelidad idéntica en Chrome, Edge, Safari y Firefox recientes.
- Contenido separado de la presentación (JSON de config + HTML semántico) para que el generador solo "rellene".

## 2. Estructura del documento
```html
<!doctype html>
<html lang="es" data-theme="dark">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Título del deck</title>
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob: 'unsafe-inline'">
  <style>/* 1) @font-face base64  2) tokens  3) base/stage  4) layouts  5) componentes  6) animaciones  7) HUD/herramientas  8) print */</style>
</head>
<body>
  <svg hidden><!-- sprite de íconos <symbol> --></svg>

  <main id="stage" aria-live="off">
    <section class="slide" data-type="hero" data-transition="fade" data-timing="45" id="s1">
      <img class="full-bleed" src="data:image/avif;base64,..." alt="">
      <h1 data-morph="title">Afirmación principal</h1>
      <aside class="notes">Guion del orador…</aside>
    </section>
    <!-- … -->
  </main>

  <!-- Overlays (fuera del stage escalado o dentro, según necesidad) -->
  <canvas id="ink"></canvas><canvas id="laser"></canvas><div id="spot"></div>
  <div id="hud"><!-- progreso, contador, toolbar de herramientas --></div>
  <aside id="notes-panel" hidden></aside>
  <div id="overview" hidden></div>
  <div id="sr-status" class="sr-only" aria-live="polite"></div>

  <script type="application/json" id="deck-config">
  { "id":"deck-2026-11-xxxx", "aspect":"16:9", "theme":"dark", "transition":"fade",
    "totalTime":1200, "sound":false, "features":{ "laser":true, "ink":true, "edit":true, "notes":true, "presenter":true } }
  </script>
  <script>/* engine: IIFE con módulos */</script>
</body>
</html>
```

## 3. Capas de CSS (orden y responsabilidad)
1. **Fuentes** (`@font-face` base64).
2. **Tokens**: color (OKLCH), tipografía (escala), espaciado, radios, sombras, movimiento. Temas por `[data-theme]`.
3. **Base / stage**: reset mínimo, `#stage` 1920×1080, `.slide{position:absolute; inset:0; display:none}`, `.slide.active{display:grid}`.
4. **Layouts**: `.slide[data-type="split"]{grid-template-columns:5fr 7fr}`, etc.
5. **Componentes**: card, badge, stat, quote, timeline, chart, code, device-mockup.
6. **Animaciones**: keyframes, `.frag`, transiciones, View Transitions.
7. **HUD y herramientas**: toolbar, paneles, overview, cursores.
8. **Print**: `@media print`.
9. **Reduced motion**.

Recomendado usar `@layer tokens, base, layouts, components, motion, tools, print;` para controlar la cascada.

## 4. Motor JS (módulos dentro de una IIFE)
| Módulo | Responsabilidad |
|---|---|
| `Config` | Leer `#deck-config`, defaults, feature flags |
| `State` | `{slide, step, mode, tool, muted}` + event bus (`EventTarget`) |
| `Stage` | Escalado `fit()`, fullscreen, wake lock, ocultar cursor |
| `Nav` | goto/next/prev, hash routing, teclado, swipe, clic, clickers |
| `Fragments` | Steps por slide, `visible/dim` |
| `Transitions` | Fade/slide/zoom/morph (View Transitions + fallback) |
| `Overview` / `Menu` / `Palette` | Grid de miniaturas, índice, Ctrl+K |
| `Laser` / `Spotlight` / `Zoom` | Herramientas de foco |
| `Ink` | Dibujo vectorial por slide, undo/redo, export |
| `Editor` | contenteditable, toolbar, guardar HTML |
| `Notes` | Notas del orador + notas de sesión, export MD |
| `Presenter` | Ventana presentador + BroadcastChannel + timer/pacing |
| `Audio` | Web Audio, SFX, mute |
| `Storage` | `localStorage` con prefijo `deck:<id>:` y try/catch |
| `Exporter` | Guardar HTML, PNG, PDF (print), MD de notas |
| `A11y` | aria, anuncios, foco |
| `Help` | Overlay `?` con atajos |

Patrón: cada módulo `init(bus, state)` y se suscribe a eventos (`slidechange`, `stepchange`, `modechange`). Así el generador puede **activar/desactivar features** sin tocar el núcleo.

## 5. Persistencia
- Clave por deck: `deck:<id>:ink`, `:edits`, `:notes`, `:prefs`.
- Siempre envuelto en `try/catch` (modo privado, `file://` en algunos navegadores, cuotas).
- Botón "Restablecer" para limpiar estado local.
- "Guardar como HTML" incrusta ediciones, notas y anotaciones en el propio archivo (en el `<script type="application/json">`) → portabilidad total.

## 6. Rendimiento
- Slides no activas con `display:none` (o `content-visibility:auto` en modo scroll).
- Imágenes con `decoding="async"`; precargar la siguiente slide.
- `will-change` solo durante la animación.
- Canvas con `devicePixelRatio` (nítido en 4K) pero tope en 2×.
- Evitar layout thrashing (leer luego escribir).

## 7. Pipeline del generador
```
Brief / documento fuente
  → 1. Outline narrativo (JSON, ver 01-storytelling §7) + validaciones
  → 2. Selección de tema (tokens) y parejas tipográficas
  → 3. Asignación de layout por slide (beat → type) y de visuales (íconos, imágenes, charts)
  → 4. Render: plantilla HTML + CSS de layouts + componentes
  → 5. Inlining: fuentes subset base64, sprite de íconos, imágenes optimizadas (AVIF/WebP), engine JS
  → 6. QA automático (Playwright): capturas por slide, overflow de texto, contraste, peso, errores de consola
  → 7. Entrega: deck.html (+ opcional PDF exportado)
```

QA automático sugerido (Playwright):
- Detectar **desbordes**: `el.scrollHeight > el.clientHeight` en contenedores de texto.
- Contraste de texto vs fondo calculado.
- Ninguna request de red en modo offline.
- Screenshot por slide → contacto visual (grid PNG) para revisión rápida.

## 8. Seguridad
- Escapar contenido generado por IA antes de insertarlo como HTML (evitar `<script>` inyectado).
- CSP en `<meta>`; iframes de demos con `sandbox` y `allow` mínimo.
- No incrustar secretos/tokens (si hay encuestas en vivo, endpoints públicos con claves de solo lectura).

## 9. Compatibilidad / degradación
| Feature | Si no existe |
|---|---|
| View Transitions | Fade CSS |
| Fullscreen API (iOS Safari limitado) | Modo "pseudo-fullscreen" (ocultar UI) |
| BroadcastChannel | `localStorage` + evento `storage` |
| Pointer pressure | `simulatePressure` |
| AVIF | `<picture>` con WebP/JPEG |
| Wake Lock | Ignorar |
