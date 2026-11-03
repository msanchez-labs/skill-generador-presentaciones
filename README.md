# Generador de presentaciones · `presentador-html`

Skill para agentes de IA (Claude) que crea **presentaciones profesionales en un único archivo HTML** —sin dependencias, offline— desde cualquier fuente: texto pegado, un título que la IA investiga, PDF, Word, PowerPoint, Excel, links o una imagen del estilo deseado. Hace como máximo 3 preguntas.

## Qué trae cada presentación

| | Atajo |
|---|---|
| Avanzar / retroceder (teclado, clicker, swipe) | `→` `←` `Espacio` `PgUp/PgDn` |
| Pantalla completa | `F` |
| Puntero láser con estela · Foco · Lupa | `L` · `H` · `Z` |
| Lápiz (5 colores) · Resaltador · Flecha · Rectángulo · Borrador | `D` `1–5` · `Shift+D` · barra · `X` |
| Deshacer / rehacer trazo · Limpiar slide | `Ctrl+Z` / `Ctrl+Y` · `C` |
| Resaltar texto seleccionado | botón *Resaltar* / `Shift+M` |
| Comentarios anclados a un punto | `Shift+C` |
| Notas de sesión → minuta Markdown | `T` |
| Editar textos en vivo | `E` |
| Vista del presentador (notas, siguiente, cronómetro, ritmo) | `S` |
| Vista general · Buscar slide/comando | `O` · `G` / `Ctrl+K` |
| Pizarra en blanco · Pantalla negra | `W` · `B` |
| Guardar como HTML (incluye trazos, notas, comentarios y ediciones) | `Ctrl+S` |
| Sonido sintetizado (opcional) · Autoavance · Ayuda | `U` · `A` · `?` |

Imprimir/PDF: `Ctrl+P` (una slide por página, fragmentos visibles).

## Estructura

```
presentador-html/            ← la skill (carpeta autocontenida, rutas relativas)
├── SKILL.md                 ← instrucciones para el agente
├── requirements.txt
├── references/              ← base de conocimiento (storytelling, diseño, tonos, tipos, diagramas, schema)
├── examples/                ← decks de ejemplo (few-shot)
├── assets/                  ← motor (engine.js/css/template), temas, fuentes WOFF2, íconos Lucide
└── scripts/                 ← build_deck.py · qa_deck.py · extract_source.py · doctor.py
tests/test_engine.py         ← pruebas funcionales del motor (Chromium, Firefox, WebKit)
.github/workflows/ci.yml     ← CI en Windows, macOS y Linux
```

## Instalación (Windows, macOS, Linux)

Requisitos: **Python 3.10+**.

```bash
python -m pip install -r presentador-html/requirements.txt
python -m playwright install chromium
python presentador-html/scripts/doctor.py
```
(En Windows usa `py` si `python` no está en el PATH.)

Como skill de Claude: copia la carpeta `presentador-html/` donde tu cliente carga skills (por ejemplo `~/.claude/skills/presentador-html/`). Funciona desde cualquier ubicación: todas las rutas son relativas a la carpeta de la skill.

## Uso manual

```bash
python presentador-html/scripts/build_deck.py mi-charla/deck.json   # → mi-charla/deck.html
python presentador-html/scripts/qa_deck.py   mi-charla/deck.html    # → mi-charla/qa/contact-sheet.png + report.json
```
Formato del `deck.json`: [`presentador-html/references/deck-schema.md`](presentador-html/references/deck-schema.md).

## Dependencias

| | Para qué | ¿Obligatoria? |
|---|---|---|
| Python 3.10+ | ejecutar scripts | Sí |
| Playwright + Chromium | QA visual real, PDF | Sí (calidad) |
| Pillow | optimizar imágenes | Sí |
| pypdf · python-docx · python-pptx · openpyxl | leer fuentes | Solo si usas ese formato |

La presentación generada **no tiene dependencias**: HTML/CSS/JS vanilla, sin CDN ni frameworks.
Navegadores: Chrome/Edge 111+, Firefox 133+, Safari 18+ (degradación elegante en versiones anteriores).

## Compartir

- Algunos correos bloquean adjuntos `.html` → envíalo en `.zip` o por link.
- Teams/SharePoint/OneDrive suelen descargar el HTML en vez de mostrarlo: se abre descargado.
- Respaldo sin interactividad: `Ctrl+P` → Guardar como PDF.

Avisos de terceros: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
