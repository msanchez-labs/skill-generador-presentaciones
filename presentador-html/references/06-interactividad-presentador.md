# 06 · Interactividad y herramientas del presentador

> Lo que convierte el deck en una **herramienta viva**: navegar, enfocar, rayar, editar y tomar notas **sin salir de la presentación**.

## 1. Mapa de atajos (estándar propuesto)

| Tecla | Acción | Referente |
|---|---|---|
| `→` `Espacio` `PageDown` `N` | Siguiente (fragmento o slide) | reveal.js / clickers |
| `←` `PageUp` `P` | Anterior | reveal.js |
| `Home` / `End` | Primera / última | — |
| `número` + `Enter` | Ir a slide N | PowerPoint |
| `F` | Pantalla completa | reveal.js |
| `O` / `Esc` | Overview (grid de miniaturas) | reveal.js |
| `M` | Menú / índice de secciones | reveal.js menu |
| `S` | **Vista del presentador** (ventana aparte) | reveal.js |
| `L` | **Puntero láser** | PowerPoint (Ctrl+L) |
| `H` | **Spotlight** (foco circular, resto oscurecido) | Gamma (S) |
| `Z` / `Alt+clic` | Zoom / lupa sobre zona | reveal.js zoom |
| `D` | **Modo dibujo** (lápiz) | reveal.js chalkboard (C) |
| `1–5` | Color del lápiz (en modo dibujo) | — |
| `Shift+D` / `X` | Resaltador / borrador | — |
| `Ctrl+Z` / `Ctrl+Shift+Z` | Deshacer / rehacer trazo | — |
| `C` | Limpiar dibujos de la slide | — |
| `W` | Pizarra en blanco | PowerPoint |
| `B` o `.` | Pantalla negra (pausa) | PowerPoint / clickers |
| `E` | **Edición en vivo** del texto | Gamma (E) |
| `T` | **Panel de notas** personales de la slide | — |
| `K` / `Ctrl+K` | Paleta de comandos (buscar slide/acción) | — |
| `U` | Silenciar / activar sonidos | — |
| `A` | Autoplay on/off | reveal.js |
| `?` | Ayuda con todos los atajos | — |

Todos los atajos se desactivan mientras el foco está en un `input`, `textarea` o `[contenteditable]`.

## 2. Navegación
- **Teclado, clic (zona derecha/izquierda), swipe táctil, clickers** (envían PageUp/PageDown/B/F5/Esc).
- **Deep-link** por hash `#/12` (y `#/12/3` para fragmento); `history.replaceState` al navegar; botón atrás del navegador funciona.
- **Barra de progreso** fina + contador `12 / 30` (autoocultable tras 2 s sin movimiento).
- **Overview**: grid de miniaturas (las mismas slides escaladas con `transform: scale(.2)`), navegable con flechas + Enter.
- **Índice/menú lateral** generado de `section` + títulos.
- **Saltar fragmentos**: `Alt+→`.
- Cursor y HUD se ocultan tras 2 s de inactividad.

## 3. Pantalla completa y escalado
```js
const toggleFS = () => document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
function fit(){ const s = Math.min(innerWidth/1920, innerHeight/1080);
  stage.style.transform = `translate(-50%,-50%) scale(${s})`; }
addEventListener('resize', fit); document.addEventListener('fullscreenchange', fit);
```
```css
#stage{ position:fixed; left:50%; top:50%; width:1920px; height:1080px; transform-origin:center; }
body{ background:#000; overflow:hidden; } /* letterbox */
```
- Pedir pantalla completa solo tras gesto del usuario (requisito del navegador).
- Wake Lock opcional (`navigator.wakeLock.request('screen')`) para que no se apague la pantalla.

## 4. Puntero láser, spotlight y zoom

**Láser**: punto rojo con halo + estela que se desvanece (canvas overlay, `pointer-events:none`).
```js
const trail=[]; addEventListener('pointermove', e => { if(!laserOn) return; trail.push({x:e.clientX,y:e.clientY,t:performance.now()}); });
function drawLaser(t){ ctx.clearRect(0,0,cv.width,cv.height);
  while(trail.length && t-trail[0].t>350) trail.shift();
  ctx.lineCap='round'; ctx.lineJoin='round';
  for(let i=1;i<trail.length;i++){ const a=(1-(t-trail[i].t)/350);
    ctx.strokeStyle=`rgba(255,40,40,${a*.8})`; ctx.lineWidth=10*a;
    ctx.beginPath(); ctx.moveTo(trail[i-1].x,trail[i-1].y); ctx.lineTo(trail[i].x,trail[i].y); ctx.stroke(); }
  const p=trail.at(-1); if(p){ ctx.shadowBlur=24; ctx.shadowColor='red'; ctx.fillStyle='#ff2a2a';
    ctx.beginPath(); ctx.arc(p.x,p.y,8,0,7); ctx.fill(); ctx.shadowBlur=0; }
  requestAnimationFrame(drawLaser); }
```
Ocultar el cursor del sistema (`cursor:none`) mientras el láser está activo.

**Spotlight**: capa a pantalla completa con máscara radial que sigue al puntero.
```css
#spot{ position:fixed; inset:0; pointer-events:none; background:rgb(0 0 0/.7);
  mask: radial-gradient(circle 160px at var(--x) var(--y), transparent 98%, #000 100%); }
```
**Zoom/lupa**: escalar el `#stage` ×2 con `transform-origin` en el punto clicado; Esc vuelve.

**Spotlight de bloque** (estilo Gamma): al avanzar fragmentos, `.dim` en los anteriores y foco en el actual.

## 5. Dibujo / anotación sobre lo proyectado

Requisitos:
- Canvas overlay **por slide** (los trazos pertenecen a la slide; al volver, reaparecen).
- **Pointer Events** (mouse, touch, lápiz) con `e.pressure` y `getCoalescedEvents()` para trazos finos.
- `touch-action: none` en el canvas durante el modo dibujo.
- Herramientas: lápiz, **resaltador** (`globalAlpha .35`, `globalCompositeOperation:'multiply'`, trazo grueso), flecha, rectángulo/elipse, texto rápido, **borrador**, limpiar, deshacer/rehacer, 5 colores + 3 grosores.
- **Trazos suaves**: librería **perfect-freehand** (MIT, de Steve Ruiz — tldraw): `getStroke(points, {size, thinning, smoothing, streamline, simulatePressure})` devuelve el contorno del trazo para pintarlo como polígono relleno. Incrustable (pocos KB). Alternativa sin dependencia: suavizado con curvas cuadráticas entre puntos medios.
- Guardar trazos como **vectores** (arrays de puntos normalizados a 1920×1080), no como bitmap → redibujo nítido a cualquier escala y persistencia ligera en `localStorage`.
- Exportar: PNG de la slide con anotaciones, o JSON de anotaciones; incluir en la exportación a PDF.
- **Pizarra en blanco** (W): una slide temporal vacía para explicar algo a mano alzada; se puede guardar como slide nueva.

Modelo de datos:
```js
ink = { "s7": [ { tool:"pen", color:"#ff3b30", size:6, pts:[[x,y,p],...] }, ... ] }
```
Suavizado simple sin librería:
```js
function drawSmooth(ctx, pts){ ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
  for(let i=1;i<pts.length-1;i++){ const mx=(pts[i][0]+pts[i+1][0])/2, my=(pts[i][1]+pts[i+1][1])/2;
    ctx.quadraticCurveTo(pts[i][0],pts[i][1],mx,my); } ctx.stroke(); }
```

## 6. Edición en vivo durante la presentación
- `E` activa `contenteditable` en títulos y textos de la slide actual (outline punteado visible solo para el presentador).
- Barra mínima flotante: negrita, color de acento, tamaño ±, deshacer.
- Arrastrar/reordenar elementos opcional (modo "layout").
- Cambios se guardan en `localStorage` (`deck:<id>:edits`) y se puede **"Guardar como HTML"**: serializar `document.documentElement.outerHTML` (limpiando estado de UI) y descargarlo con `Blob` + `<a download>` → el archivo único se auto-actualiza.
- Edición también desde la vista del presentador (sin que la audiencia vea la UI de edición).
- Duplicar slide / insertar slide en blanco / ocultar slide (`data-hidden`) en vivo.

## 7. Notas
Dos tipos distintos:

| | Notas del orador | Notas de sesión (tomar notas) |
|---|---|---|
| Quién | Escritas antes (guion) | Escritas durante (ideas, preguntas, acuerdos) |
| Dónde | `<aside class="notes">` por slide | Panel lateral `T`, `textarea` por slide |
| Visible | Solo vista presentador | Panel ocultable; opcional audiencia |
| Export | En PDF (página aparte) | **Markdown** con slide + timestamp; copiar al portapapeles |

Extras de notas de sesión: marcar **acuerdos/acciones** (`[ ]`), etiquetar preguntas del público, sticky notes ancladas sobre la slide, resumen final "todas las notas" al terminar.

## 8. Vista del presentador (`S`)
- `window.open()` de la misma URL con `?presenter`; sincronización por **BroadcastChannel** (sin servidor, mismo navegador).
```js
const bc = new BroadcastChannel('deck-' + DECK_ID);
bc.onmessage = ({data}) => { if(data.type==='goto') goto(data.slide, data.step, {silent:true}); };
function emit(){ bc.postMessage({type:'goto', slide:state.slide, step:state.step}); }
```
- Contenido: slide actual + **siguiente** (miniatura), notas del orador con tamaño ajustable, **cronómetro**, reloj, **pacing** por slide (verde/rojo/azul como reveal.js: `data-timing`, `totalTime`), contador de slides, controles de herramientas (láser, dibujo, blackout).
- Para control desde otro dispositivo (celular como control remoto): requiere relay (WebSocket/WebRTC); dejarlo como módulo opcional.

## 9. Interacción con la audiencia (opcional / con backend)
- **QR** a la versión pública del deck en la slide de apertura y CTA (generar QR en SVG local).
- Encuestas en vivo, reacciones, preguntas: requieren backend (p. ej. Azure Web PubSub / Supabase). Módulo plug-in.
- "Follow mode" (la audiencia sigue la slide del presentador en su dispositivo) — mismo relay.
- Slides **interactivas**: tabs, acordeones, calculadoras, sliders "¿qué pasa si…?", tablas filtrables, mapas, demos en iframe.
- Código ejecutable en vivo (`<textarea>` + `eval` sandbox en iframe) para workshops técnicos.

## 10. Otros modos
- **Autoplay/kiosk** con duración por slide y loop.
- **Modo lectura/scroll** (documento continuo) para quien recibe el deck sin presentador — una clase en `<html>` cambia el layout de slides apiladas a página.
- **Impresión/PDF**: `@page { size: 1920px 1080px; margin:0 }`, cada slide `break-after: page`, fragmentos visibles, anotaciones incluidas, notas opcionales.
- **Ensayo**: graba tiempos reales por slide y sugiere `data-timing`.
- Accesibilidad: `role="region"` + `aria-roledescription="slide"` + `aria-label="3 de 20: título"`, región `aria-live="polite"` que anuncia el cambio; navegación 100% con teclado; foco visible.
