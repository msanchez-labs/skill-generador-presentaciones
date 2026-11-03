# 03 · Tipografía y fuentes

## 1. Escala tipográfica (en px sobre lienzo 1920×1080)

Escala modular ratio **1.333 (cuarta perfecta)** base 28 px:

| Token | Tamaño | Uso | line-height | peso |
|---|---|---|---|---|
| `--fs-caption` | 20–22 | Fuentes, pies, etiquetas | 1.3 | 500 |
| `--fs-body` | 28–32 | Texto de cuerpo (mínimo legible en sala) | 1.4 | 400 |
| `--fs-lead` | 40 | Bajadas, subtítulos | 1.3 | 400–500 |
| `--fs-h2` | 56 | Títulos de slide | 1.1 | 650–700 |
| `--fs-h1` | 80–96 | Títulos de portada/sección | 1.05 | 700–800 |
| `--fs-display` | 140–200 | Statement, hero | 0.95 | 800 |
| `--fs-mega` | 240–320 | Big number | 0.9 | 800–900 |

Reglas:
- **Nunca < 20 px** en el lienzo (regla práctica: si no se lee desde la última fila, no va).
- Largo de línea **≤ 60 caracteres** en slides.
- `letter-spacing` negativo (−0.02em a −0.04em) en tamaños display; positivo (+0.08em) en etiquetas en MAYÚSCULAS.
- `text-wrap: balance` en títulos; `text-wrap: pretty` en párrafos (evita viudas).
- Números en tablas/métricas: `font-variant-numeric: tabular-nums;`.
- Comillas tipográficas « » o “ ”, no ".

## 2. Parejas tipográficas recomendadas (todas libres, OFL)

| Estilo | Títulos | Cuerpo | Carácter |
|---|---|---|---|
| Tech / SaaS moderno | **Inter Tight** / Inter | Inter | Neutro, muy legible |
| Startup geométrica | **Space Grotesk** | Inter | Técnico con personalidad |
| Editorial premium | **Fraunces** o **Instrument Serif** | Inter / Manrope | Elegante, contraste serif+sans |
| Corporativo cálido | **Plus Jakarta Sans** | Plus Jakarta Sans | Amigable, profesional |
| Minimal suizo | **Manrope** | Manrope | Limpio, compacto |
| Futurista | **Sora** / **Outfit** | DM Sans | Redondeado, moderno |
| Sistema IBM | **IBM Plex Sans** | IBM Plex Sans + Plex Mono | Corporativo-técnico |
| Editorial-técnico (alineado con diagramas, ver `11-diagramas.md`) | **Instrument Serif** | **Geist** + Geist Mono | Serif display + sans + mono solo para lo técnico |
| Código | — | **Geist Mono** / JetBrains Mono / Fira Code | Monoespaciada — **solo** en bloques de código, comandos, URLs; nunca como fuente general "dev" |

Regla: **máx. 2 familias** (+1 mono si hay código). Preferir **fuentes variables** (un archivo, todos los pesos, permite animar `font-weight`).

## 3. Estrategia de carga en un HTML único

| Estrategia | Pros | Contras | Cuándo |
|---|---|---|---|
| **A. Google Fonts `<link>`** | Cero peso en el archivo | Requiere internet; privacidad | Decks online / borradores |
| **B. WOFF2 en base64 dentro de `@font-face`** | 100% offline, fidelidad total | +30–120 KB por fuente | **Default para entrega final** |
| **C. Pila de sistema** | Cero peso, instantáneo | Menos identidad | Fallback siempre |

Recomendado: **B con subsetting** (solo caracteres latinos + español: `U+0000-00FF, U+0131, U+0152-0153, U+2013-2014, U+2018-201E, U+2026, U+20AC`) usando `pyftsubset` (fonttools) → WOFF2 → base64.

```bash
pyftsubset Inter.var.ttf --unicodes="U+0000-00FF,U+2013-2014,U+2018-201E,U+2026,U+20AC" \
  --flavor=woff2 --layout-features='*' --output-file=inter-sub.woff2
base64 -i inter-sub.woff2 | tr -d '\n' > inter.b64
```
```css
@font-face{
  font-family:"Inter"; font-weight:100 900; font-style:normal; font-display:swap;
  src:url(data:font/woff2;base64,AAAA...) format("woff2");
}
:root{ --font-sans:"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
       --font-display:"Fraunces", Georgia, serif;
       --font-mono:"JetBrains Mono", ui-monospace, Menlo, Consolas, monospace; }
```

## 4. Tipografía cinética (tipo como protagonista)

- Revelar palabra por palabra o línea por línea (split en `<span>` con `--i` para stagger).
- Animar `font-weight` de variables (300→800) para énfasis.
- Resaltado tipo marcador: `background: linear-gradient(transparent 60%, var(--accent) 60%)` animando `background-size`.
- Palabra clave en color de acento o serif itálica dentro de un título sans.
- Ver snippets en `05-animaciones.md`.

## 5. Checklist tipográfico
- [ ] ≤ 2 familias, todas con licencia libre verificada.
- [ ] Todas las fuentes incrustadas (modo offline) o con fallback definido.
- [ ] Ningún texto < 20 px en lienzo.
- [ ] Títulos balanceados, sin viudas.
- [ ] Cifras tabulares en tablas y métricas.
- [ ] Acentos y ñ renderizan (subset correcto).
