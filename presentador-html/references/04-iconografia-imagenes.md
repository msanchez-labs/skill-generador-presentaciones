# 04 · Iconografía, imágenes y recursos gráficos

## 1. Iconografía

### Sets recomendados (licencias permisivas)
| Set | Licencia | Estilo | Nota |
|---|---|---|---|
| **Lucide** | ISC | Línea 24px, stroke 2 | Default recomendado; uso por CDN con `data-lucide` + `lucide.createIcons()` o SVG inline |
| **Phosphor** | MIT | 6 pesos (thin→fill, duotone) | Ideal para variar peso según tema |
| **Tabler Icons** | MIT | Línea, +5.000 íconos | Muy amplio |
| **Heroicons** | MIT | Outline/solid | Pocos pero muy pulidos |
| **Material Symbols** | Apache 2.0 | Variable (fill, weight, grade) | Bueno para estilo Google |
| **Simple Icons** | CC0 (marcas sujetas a sus guías) | Logos de marcas tech | Para logos de tecnologías (Azure, GitHub…) |

### Reglas
- **Un solo set por deck** (no mezclar estilos ni grosores).
- Mismo `stroke-width` y tamaño por rol: 32 px en listas, 48–64 px en tarjetas bento, 96–128 px como ilustración.
- Color con `currentColor` para heredar del tema.
- Ícono **acompaña** al texto, no lo reemplaza (salvo que sea universal).
- Contenedor opcional: círculo/cuadrado redondeado con fondo `--accent` al 12% de opacidad.

### Incrustación offline (HTML único)
Generar **sprite SVG** solo con los íconos usados:
```html
<svg style="display:none" aria-hidden="true">
  <symbol id="i-rocket" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">…paths…</symbol>
</svg>
<svg class="icon" aria-hidden="true"><use href="#i-rocket"/></svg>
```
```css
.icon{ width:1em; height:1em; } /* escala con font-size */
```
Ventaja: cada ícono pesa ~300–600 bytes; sin dependencias.

## 2. Imágenes

### Principios
- **Una imagen fuerte > cinco mediocres.** Preferir full-bleed (a sangre) o mitad de slide.
- La imagen debe **significar** algo (metáfora del mensaje), no decorar.
- **Legibilidad sobre foto**: overlay gradiente (`linear-gradient(to top, rgb(0 0 0/.75), transparent 60%)`), o texto en zona "vacía" de la foto (`object-position`).
- **Unificar** fotos de distintas fuentes: duotono, desaturar, o mismo tratamiento de color.
- Rostros mirando hacia el contenido, no fuera del slide.
- Evitar stock cliché (apretón de manos, gente señalando pantallas).

### Tratamientos CSS útiles
```css
.full-bleed{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.duotone{ filter: grayscale(1) contrast(1.1); mix-blend-mode:multiply; } /* sobre fondo --accent */
.kenburns{ animation: kb 12s ease-out both; } @keyframes kb{ from{ transform:scale(1.08) } to{ transform:scale(1) } }
.mask-fade{ mask-image: linear-gradient(to right, #000 60%, transparent); }
.blob{ clip-path: url(#blob) /* o */ ; border-radius: 42% 58% 63% 37% / 41% 44% 56% 59%; }
```

### Formatos y peso (archivo único)
| Formato | Uso |
|---|---|
| **SVG inline** | Ilustraciones, diagramas, gráficos, fondos generativos (peso mínimo, escalable) |
| **AVIF / WebP** en base64 | Fotos; 1920 px de ancho máx., calidad 60–75 → 80–250 KB c/u |
| **JPEG** | Fallback si el visor no soporta AVIF |
| **Video MP4 (H.264) / WebM** | Demos cortas; si > 2 MB, referenciar por URL, no incrustar |

- `decoding="async"` y `loading="lazy"` excepto en la primera slide.
- Presupuesto total recomendado del HTML: **< 10 MB** (ideal < 5 MB).

### Fuentes de imágenes
- **Unsplash / Pexels**: licencias gratuitas de uso comercial (sin atribución obligatoria, pero recomendada en notas). Verificar siempre la licencia vigente del sitio.
- **Generación con IA**: cuidando coherencia de estilo (mismo prompt base de estilo para todo el deck) y sin personas reales identificables.
- **Ilustraciones**: unDraw (personalizable al color de acento), Open Peeps, Humaaans — revisar licencias.
- **Capturas propias** de producto/dashboards en marcos de dispositivo (mockup CSS).
- **No usar** fotos de figuras públicas ni logos de terceros fuera de su uso nominativo.

### Accesibilidad
- `alt` descriptivo en imágenes informativas; `alt=""` en decorativas.
- No poner texto importante "dentro" de la imagen (no es seleccionable, no se traduce, no escala).

## 3. Fondos y recursos generativos (peso ~0)

```css
/* Aurora / mesh gradient */
.bg-aurora{ background:
  radial-gradient(60% 80% at 10% 10%, oklch(70% .18 260 / .55), transparent 60%),
  radial-gradient(50% 70% at 90% 20%, oklch(75% .16 180 / .45), transparent 60%),
  radial-gradient(70% 90% at 50% 100%, oklch(65% .2 320 / .40), transparent 60%), var(--bg); }

/* Grano */
.grain::after{ content:""; position:absolute; inset:0; pointer-events:none; opacity:.06;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }

/* Grid de puntos */
.bg-dots{ background-image: radial-gradient(var(--muted) 1px, transparent 1px); background-size: 32px 32px; }
```

## 4. Diagramas
- Dibujar en **SVG inline** (nodos `rect` redondeados, conectores `path` con `marker-end`).
- Opcional: Mermaid por CDN para borradores; para entrega final, **pre-renderizar a SVG** e incrustar (evita dependencia y cambia de estilo con tokens CSS).
- Animar conectores con `stroke-dasharray/stroke-dashoffset` (ver `05-animaciones.md`).
- Íconos de nube: usar los íconos oficiales del proveedor (Azure Architecture Icons) respetando sus términos.
