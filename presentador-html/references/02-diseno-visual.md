# 02 · Diseño visual y layouts

> Objetivo: slides con jerarquía clara, aire, consistencia de sistema y un "look" moderno que se perciba superior a las plantillas genéricas.

## 1. Lienzo (stage)

- **Resolución lógica fija 1920×1080 (16:9)**; se escala con `transform: scale()` al viewport con letterbox. Todo el diseño se piensa en px de 1080p → garantiza fidelidad idéntica en cualquier pantalla y al exportar a PDF.
- Zona segura: márgenes de **96–120 px** laterales y **72–96 px** verticales (≈5–6%). Nada importante fuera de ella (proyectores recortan).
- Alternativa 4:3 (1440×1080) o vertical 1080×1920 como configuración del deck (`meta.aspect`).

## 2. Grid y espaciado

- **Grid de 12 columnas**, gutter 32 px, dentro de la zona segura.
- **Escala de espaciado** (base 8): `8, 16, 24, 32, 48, 64, 96, 128`. Prohibido usar valores fuera de la escala.
- **Espacio en blanco ≥ 35–40%** del área. El aire comunica calidad.
- Alineación: un único eje de alineación por slide (izquierda por defecto; centrado solo para `statement`, `hero`, `quote`).

## 3. Jerarquía (principios Gestalt aplicados)

1. **Un punto focal por slide**: lo que se ve primero debe ser el mensaje. Controlar con tamaño > color > posición > peso.
2. **Proximidad**: agrupar lo relacionado; separar grupos con ≥ 2× el espacio interno.
3. **Repetición**: mismos estilos para mismos roles (títulos, etiquetas, cifras) en todo el deck.
4. **Contraste**: si dos cosas son distintas, que se vean MUY distintas (tamaño ×2 o más).
5. **Lectura en Z / F**: título arriba-izquierda, evidencia al centro, fuente/nota abajo.

## 4. Color

- **Regla 60-30-10**: 60% fondo/neutro, 30% secundario (superficies), 10% acento (solo para lo que importa).
- Definir paleta como **tokens** y preferir **OKLCH** (`oklch(L C H)`) para generar variaciones perceptualmente uniformes (hover, tintes, modo oscuro).
- Contraste mínimo **WCAG AA**: texto normal 4.5:1, texto grande (≥ 24 px regular / ≥ 18.66 px bold) 3:1. En proyector, apuntar a **≥ 7:1** (los proyectores lavan el color).
- Un **solo color de acento** para resaltar datos/insights; el resto en grises.
- Temas mínimos: `light`, `dark`, `brand`. Cambio en vivo con `data-theme` en `<html>`.

```css
:root{
  --bg: oklch(98% 0.005 260);  --surface: oklch(94% 0.01 260);
  --text: oklch(22% 0.02 260); --muted: oklch(50% 0.02 260);
  --accent: oklch(62% 0.19 255); --accent-2: oklch(72% 0.17 160);
  --danger: oklch(60% 0.2 25);  --radius: 20px; --shadow: 0 10px 30px oklch(20% 0.02 260 / .12);
}
[data-theme="dark"]{
  --bg: oklch(16% 0.02 260); --surface: oklch(22% 0.02 260);
  --text: oklch(96% 0.01 260); --muted: oklch(72% 0.02 260);
}
```

## 5. Catálogo de layouts (tipos de slide)

| `type` | Uso | Composición |
|---|---|---|
| `hero` | Portada, apertura, visión | Imagen full-bleed + overlay gradiente + título XXL abajo-izquierda |
| `section` | Separador de capítulo | Número grande (01, 02…) + título; color de acento como fondo |
| `statement` | Mensaje clave / STAR | Una frase en 96–160 px, centrada, nada más |
| `big-number` | Dato impactante | Cifra 200–320 px + etiqueta + contexto + fuente |
| `split` | Texto + visual | 5/7 o 6/6 columnas; imagen a sangre de un lado |
| `bento` | Capacidades / features | Grid asimétrico de 3–6 tarjetas de distinto tamaño, iconos |
| `chart` | Evidencia con datos | Título-insight + gráfico + 1 serie resaltada + anotación |
| `comparison` | Opciones / antes-después | 2–3 columnas; opción recomendada destacada (borde/acento/badge) |
| `timeline` / `roadmap` | Plan, historia | Eje horizontal con hitos; hito actual resaltado |
| `process` | Pasos / flujo | 3–5 pasos con iconos y conectores; se revelan por fragmentos |
| `diagram` | Arquitectura | SVG con nodos/flechas; zoom a zonas por fragmentos |
| `quote` | Testimonio, cita | Cita grande con comillas tipográficas + autor + foto circular |
| `team` / `logos` | Credibilidad | Grid uniforme, escala de grises con hover a color |
| `demo` / `embed` | Producto en vivo | iframe/video ocupando 80% + leyenda |
| `code` | Técnico | Bloque monoespaciado con resaltado de líneas por fragmentos |
| `agenda` | Índice | 3–5 ítems; el actual se resalta al reutilizar como separador |
| `cta` | Llamada a la acción | 1 acción, responsable, fecha; QR opcional |
| `closing` | Cierre | Callback a la portada + contacto |

## 6. Estética moderna (2025–2026) — usar con criterio

- **Bento grids** (tarjetas de distintos tamaños, esquinas 20–28 px).
- **Tipografía gigante / editorial**: títulos enormes con mucho aire, mezcla sans + serif display.
- **Gradientes mesh** y "auroras" suaves de fondo (CSS `radial-gradient` múltiples) + **grano** (SVG `feTurbulence` al 4–8% de opacidad) para quitar el aspecto plano digital.
- **Glassmorphism sutil**: `backdrop-filter: blur(16px)` sobre fondos con imagen; usar solo en 1–2 elementos.
- **Duotono** en fotos para unificar imágenes de distintas fuentes con la paleta.
- **Microinteracciones**: hover en tarjetas, contadores animados, líneas que se dibujan.
- **3D ligero**: `perspective` + `rotateX/Y` leves en mockups de pantallas.
- **Variación de ritmo**: alternar slides densas con slides `statement` de respiro.

## 7. Visualización de datos en slides

- El **título es el insight**, no el nombre del gráfico.
- **Resaltar 1 serie** en color de acento; resto en gris.
- **Etiquetas directas** sobre las series (eliminar leyendas cuando se pueda).
- Quitar chartjunk: bordes, grillas pesadas, 3D, sombras, decimales innecesarios.
- Barras para comparar, líneas para tendencia, un número grande cuando el dato es único. Evitar tortas con > 3 segmentos.
- Animar la construcción (barras que crecen, línea que se dibuja) para narrar.
- Gráficos en **SVG inline** generado (sin librerías) o con librería ligera opcional; siempre con `role="img"` + `aria-label` con el insight.

## 8. Anti-patrones (el generador debe evitarlos)

- Muros de bullets / texto en párrafos.
- Más de 2 familias tipográficas (3 si una es monoespaciada para código).
- Más de 1 color de acento compitiendo.
- Clip-art, stock genérico de "gente dándose la mano", íconos de estilos mezclados.
- Logos en cada slide, pies de página recargados.
- Elementos alineados "a ojo" fuera del grid.
- Sombras duras, bordes gruesos, biseles, WordArt.
- Animaciones en todo (ver `05-animaciones.md`).
