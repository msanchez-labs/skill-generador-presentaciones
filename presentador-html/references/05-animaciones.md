# 05 · Animaciones y transiciones

> Regla de oro: **toda animación debe tener un propósito**: dirigir la atención, mostrar una relación (de dónde viene / a dónde va) o dar continuidad. Si es solo decoración, se quita.

## 1. Parámetros de movimiento (tokens)

| Token | Valor | Uso |
|---|---|---|
| `--dur-micro` | 150–200 ms | Hover, toggles, feedback UI |
| `--dur-fragment` | 350–500 ms | Aparición de elementos (builds) |
| `--dur-slide` | 500–800 ms | Transición entre slides |
| `--dur-hero` | 900–1400 ms | Portada, momento STAR |
| `--stagger` | 50–90 ms | Retardo entre elementos de una lista |
| `--ease-out` | `cubic-bezier(.16,1,.3,1)` (expo-out) | Entradas (default) |
| `--ease-in-out` | `cubic-bezier(.65,0,.35,1)` | Movimientos de posición / morph |
| `--ease-spring` | `linear(...)` o WAAPI con overshoot leve | Elementos lúdicos |

- Animar **solo `transform` y `opacity`** (y `filter`/`clip-path` con moderación) → 60 fps.
- Desplazamientos cortos: 16–40 px, no 200 px.
- **Máx. 1 tipo de transición entre slides por deck** (+1 especial para secciones).

## 2. Catálogo

### 2.1 Transiciones entre slides
| Nombre | Descripción | Cuándo |
|---|---|---|
| `fade` | Crossfade | Default seguro |
| `slide` | Desplazamiento horizontal según dirección | Decks narrativos lineales |
| `zoom` | Escala 0.96→1 + fade | Entradas a sección |
| **`morph`** | Elementos compartidos se transforman entre slides (estilo "Morph" de PowerPoint / Magic Move de Keynote) | **Diferenciador clave**: mismo elemento cambia de tamaño/posición |
| `none` | Corte seco | Demos, código |

**Morph con View Transitions API** (same-document; soporte: Chrome/Edge 111+, Safari 18+, Firefox 133+ según devtoolbox 2026). Fallback: cambiar sin animación.
```js
function go(n, dir){
  const update = () => showSlide(n);
  if (!document.startViewTransition || matchMedia('(prefers-reduced-motion: reduce)').matches) return update();
  document.startViewTransition({ update, types: [dir > 0 ? 'forward' : 'backward'] });
}
```
```css
/* el mismo nombre en dos slides distintas = morph automático */
.slide.active [data-morph="logo"]{ view-transition-name: logo; }
::view-transition-group(*){ animation-duration: .7s; animation-timing-function: cubic-bezier(.65,0,.35,1); }
html:active-view-transition-type(forward)  ::view-transition-new(root){ animation: in-right .6s var(--ease-out); }
html:active-view-transition-type(backward) ::view-transition-new(root){ animation: in-left  .6s var(--ease-out); }
```
> Nota: `view-transition-name` debe ser único en el documento en cada instante → aplicarlo solo a la slide activa.

### 2.2 Fragmentos / builds (revelado paso a paso)
Elementos con `data-step="1..n"`; la tecla "siguiente" avanza fragmentos antes de cambiar de slide.
```html
<li class="frag" data-step="1">Primero</li>
<li class="frag" data-step="2" data-anim="fade-up">Después</li>
```
```css
.frag{ opacity:0; transform:translateY(24px); transition: opacity var(--dur-fragment) var(--ease-out), transform var(--dur-fragment) var(--ease-out); }
.frag.visible{ opacity:1; transform:none; }
.frag.dim{ opacity:.35; }          /* foco: atenuar lo ya visto (como el Spotlight de Gamma) */
.frag[data-anim="highlight"].visible{ background-size:100% 40%; }
```
Variantes: `fade-up`, `fade`, `scale-in`, `blur-in`, `highlight`, `strike`, `dim-previous`.

### 2.3 Entrada de contenido al llegar a la slide (sin clic)
Stagger automático con `--i`:
```css
.slide.active .stagger > *{ animation: fadeUp var(--dur-fragment) var(--ease-out) both; animation-delay: calc(var(--i) * var(--stagger)); }
@keyframes fadeUp{ from{ opacity:0; transform:translateY(24px) } }
```

### 2.4 Tipografía cinética
- Split por palabras: `title.innerHTML = words.map((w,i)=>`<span style="--i:${i}">${w}</span>`).join(' ')`.
- Revelado con máscara: `clip-path: inset(0 100% 0 0)` → `inset(0 0 0 0)`.
- Peso variable: `@keyframes bold{ to{ font-variation-settings:"wght" 800 } }`.

### 2.5 Datos
- **Count-up** de cifras (big-number):
```js
function countUp(el, to, ms=1200){ const t0=performance.now(), fmt=new Intl.NumberFormat('es-CL');
  (function f(t){ const p=Math.min(1,(t-t0)/ms), e=1-Math.pow(1-p,4); el.textContent=fmt.format(Math.round(to*e)); if(p<1) requestAnimationFrame(f); })(t0); }
```
- Barras que crecen: `transform: scaleY(0)` → `1` con `transform-origin: bottom` + stagger.
- Línea que se dibuja: `stroke-dasharray: L; stroke-dashoffset: L` → `0` (L = `path.getTotalLength()`).

### 2.6 Diagramas
- Conectores que se dibujan en orden lógico (flujo de datos).
- "Cámara" que hace zoom/pan a una zona del diagrama por fragmento (`transform` del grupo SVG o del contenedor).
- Pulsos en nodos activos (`@keyframes pulse` en `box-shadow`/`r`).

### 2.7 Ambientales (sutiles)
- Ken Burns en fotos de portada (escala 1.08→1 en 10–14 s).
- Aurora de fondo con `background-position` animado muy lento (20–40 s).
- Parallax ligero de capas al moverse el puntero (≤ 10 px). Desactivar al presentar si distrae.

### 2.8 Efectos de "momento" (con atajo, uso puntual)
Confeti (canvas), "drumroll" + reveal, desenfoque del fondo para enfocar un elemento, "mic drop". Útiles en STAR / celebraciones; nunca automáticos.

## 3. Motores
| Opción | Cuándo |
|---|---|
| **CSS transitions/keyframes** | 90% de los casos |
| **Web Animations API** (`el.animate()`) | Secuencias controladas por JS, pausables, con `finished` promise |
| **View Transitions API** | Morph entre slides |
| GSAP (CDN, opcional) | Timelines complejos; no necesario por defecto (mantener cero dependencias) |

## 4. Accesibilidad y control
```css
@media (prefers-reduced-motion: reduce){
  *, *::before, *::after{ animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }
}
```
- Toggle de animaciones en el HUD (algunas salas/proyectores sufren con movimiento).
- Sin parpadeos > 3 por segundo.
- El modo impresión/PDF muestra el **estado final** de todos los fragmentos.
