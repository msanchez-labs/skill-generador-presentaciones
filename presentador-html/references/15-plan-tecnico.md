# 15 · Plan técnico de construcción

> Estado: **implementado** en el repo `msanchez-labs/skill-generador-presentaciones` (skill `presentador-html`).
>
> Principio: **la presentación entregada tiene cero dependencias**. Las dependencias existen solo en la **máquina que genera**, son pocas, mainstream y multiplataforma (Windows, macOS, Linux).

## 1. Dos mundos separados

| | **Deck entregado** (`deck.html`) | **Generador** (la skill) |
|---|---|---|
| Quién lo usa | Cualquiera que lo reciba | Quien crea presentaciones (agente + scripts) |
| Dependencias | **Ninguna**. Solo un navegador moderno | Python 3.10+ y 4–8 paquetes pip (§3) |
| Tecnología | HTML + CSS + JavaScript vanilla (sin frameworks, sin CDN, sin build) | Scripts Python + Playwright |
| Red | No requiere internet (todo incrustado) | Solo para investigar / instalar |
| SO | Cualquiera con Chrome, Edge, Firefox o Safari | Windows, macOS, Linux |

## 2. El motor del deck (runtime) — 100% propio

Todo escrito en JS/CSS vanilla, sin librerías de terceros:

| Componente | Implementación propia | Reemplaza a |
|---|---|---|
| Navegación, fragmentos, hash, overview | ~400 líneas JS | reveal.js |
| Escalado 16:9 + pantalla completa | Fullscreen API + `transform: scale` | — |
| Láser, spotlight, lupa | Canvas 2D + CSS mask | — |
| Trazos, resaltador, formas, undo | Pointer Events + Canvas, suavizado con curvas cuadráticas | perfect-freehand (no se usa) |
| Subrayado de texto | Selection API + `<mark>` | — |
| Comentarios anclados | DOM + coordenadas normalizadas 1920×1080 | — |
| Notas, minuta MD | DOM + Blob download | — |
| Vista presentador | `window.open` + **`postMessage` vía `window.opener`** (funciona en `file://`); BroadcastChannel como complemento | Servidor de reveal.js |
| Transiciones / morph | CSS + View Transitions API con fallback | GSAP |
| Gráficos | SVG generado por el script en build | Chart.js |
| Diagramas | SVG generado (reglas `kb/11`) | Mermaid |
| Íconos | Sprite SVG con solo los usados (copiados de Lucide, ISC, con aviso de licencia) | CDN de Lucide |
| Fuentes | WOFF2 **ya subseteadas** en `assets/fonts/` como base64 | Google Fonts |
| Sonido | Web Audio API sintetizado | archivos de audio |
| Persistencia | `localStorage` (try/catch) + "Guardar como HTML" | backend |

Peso estimado: motor 70–100 KB · fuentes 2 familias ~150 KB · íconos < 10 KB → **< 300 KB sin imágenes**.

Implementación v1: `assets/engine/engine.js` y `engine.css` (un archivo cada uno, organizados por secciones) + `template.html`; `build_deck.py` los **incrusta** en el HTML (sin bundler, sin npm).

### Compatibilidad con abrir por doble clic (`file://`)
Restricciones que el motor respeta para funcionar abriendo el archivo directo en Windows/Mac/Linux:
- Sin `import` de módulos ni `fetch` de archivos locales → todo inline.
- Vista presentador vía `window.opener.postMessage` (BroadcastChannel puede fallar en `file://` según navegador).
- `localStorage` puede estar aislado por archivo (Firefox) o bloqueado → envolver en try/catch; "Guardar como HTML" es la persistencia garantizada.
- Portapapeles requiere contexto seguro → fallback a descarga de archivo.
- Navegadores objetivo: Chrome/Edge 111+, Firefox 133+, Safari 18+ (con degradación elegante en versiones anteriores, `kb/08 §9`).

## 3. Dependencias del generador

### 3.1 Obligatorias (sin ellas no se garantiza la calidad)

| Dependencia | Para qué | Por qué es obligatoria |
|---|---|---|
| **Python 3.10+** | Ejecutar los scripts (build, extracción, QA) | Un solo runtime, disponible en los 3 SO |
| **Playwright (Python) + Chromium** | QA: renderiza cada slide, detecta texto desbordado, contraste, errores de consola, requests externas; genera la hoja de contacto (capturas) que el agente revisa visualmente; exporta PDF | **Es la única forma de verificar lo que realmente se ve.** Sin render real, los desbordes y solapes pasan inadvertidos |
| **Pillow** | Redimensionar/comprimir imágenes (WebP, máx. 1920 px) antes de incrustarlas | Sin esto un deck con fotos pesa 30–80 MB y se vuelve inmanejable para compartir |

Instalación (idéntica en Windows/macOS/Linux):
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```
> En Windows usar `py -m pip …` si `python` no está en el PATH. En macOS/Linux puede ser `python3`.

### 3.2 Obligatorias solo si aparece esa fuente

| Paquete | Se usa cuando el usuario comparte… |
|---|---|
| `pypdf` | PDF |
| `python-docx` | Word |
| `python-pptx` | PowerPoint (contenido + colores/fuentes del tema) |
| `openpyxl` | Excel |

Todos son paquetes pip estándar, puro Python o con wheels para los 3 SO. Se instalan juntos en `requirements.txt` para simplicidad (≈ 10 MB).

### 3.3 Solo para quien mantiene la skill (no para quien la usa)

| Herramienta | Para qué |
|---|---|
| `fonttools` + `brotli` | Subsetear nuevas fuentes a WOFF2 (se hace una vez y se guardan en `assets/fonts/`) |
| Playwright con **Firefox y WebKit** | Probar el motor en los 3 motores de navegador |
| **GitHub Actions** (matriz `windows-latest`, `macos-latest`, `ubuntu-latest`) | Garantizar que build + QA + tests del motor pasan en los 3 SO en cada cambio |

### 3.4 Lo que NO se usa (decisión explícita)
Node/npm, React/Vue, bundlers, CDN, reveal.js, GSAP, Chart.js, Mermaid, perfect-freehand, LibreOffice, ImageMagick, servidores. Cualquiera de ellos puede sumarse como módulo opcional, nunca como requisito.

## 4. Reglas de código multiplataforma
- Rutas con `pathlib`, nunca concatenando con `/` o `\`.
- **Leer y escribir siempre con `encoding="utf-8"`** (en Windows el default es cp1252 y rompe tildes y ñ).
- Sin scripts `.sh` ni `.ps1`: todo en Python.
- Nombres de archivo sin caracteres reservados de Windows (`<>:"/\|?*`) y cortos.
- Saltos de línea normalizados (`.gitattributes` con `* text=auto`).
- Lanzar Chromium vía Playwright (no depender del navegador instalado del usuario).
- `scripts/doctor.py`: verifica versión de Python, paquetes y Chromium; dice exactamente qué falta y el comando para instalarlo en ese SO.

## 5. Estructura del repositorio

```
proyecto-generador-ppt/
├── kb/                           ← base de conocimientos (esta)
├── engine/
│   ├── src/                      ← core.js, nav.js, laser.js, ink.js, comments.js, notes.js, presenter.js, editor.js, audio.js, *.css
│   └── template.html             ← esqueleto con {{STYLE}} {{SLIDES}} {{CONFIG}} {{SCRIPT}}
├── skill/presentador-html/
│   ├── SKILL.md
│   ├── references/               ← copia/condensado de kb/
│   ├── assets/ (themes/, fonts/, icons.json, layouts.html, engine.html compilado)
│   ├── profiles/
│   ├── scripts/ (doctor.py, extract_source.py, build_deck.py, qa_deck.py, charts.py, icons.py)
│   └── requirements.txt          ← versiones fijadas
├── examples/                     ← decks demo (uno por tipo de kb/12)
├── tests/                        ← Playwright: atajos, láser, trazos, notas, comentarios, edición, print
└── .github/workflows/ci.yml      ← matriz 3 SO × 3 navegadores
```

## 6. Garantía de calidad (obligatoria en cada generación)

| Chequeo | Herramienta | Criterio |
|---|---|---|
| Texto desbordado / cortado | Playwright: `scrollHeight > clientHeight` en cada contenedor | 0 casos |
| Contraste | Cálculo WCAG sobre colores computados | ≥ 4.5:1 texto, ≥ 3:1 grande |
| Offline | Interceptar red durante la carga | 0 requests externas |
| Errores | Consola del navegador | 0 errores |
| Peso | Tamaño del archivo | < 10 MB (aviso > 5 MB) |
| Fuentes cargadas | `document.fonts.check()` | Todas las del tema |
| Visual | Hoja de contacto PNG revisada por el agente | Sin solapes, jerarquía clara |
| Rúbrica | `kb/10` | ≥ 85/100 |
| Funcionalidad del motor | Tests en `tests/` (solo en desarrollo/CI) | 100% verde en 3 SO |

## 7. Compartir

**El deck:** un solo `.html`. Ojo con canales que bloquean o no ejecutan HTML:
- Algunos correos/antivirus corporativos bloquean adjuntos `.html` → enviar en `.zip` o por link.
- SharePoint/OneDrive/Teams suelen **descargar** el `.html` en vez de mostrarlo (no ejecutan JS en la vista previa) → se abre descargado o se publica en un hosting estático / página compartible.
- Siempre se puede entregar además el **PDF** exportado (sin interactividad) como respaldo.

**La skill:** carpeta `skill/presentador-html/` + `requirements.txt` + `doctor.py`. Quien la reciba ejecuta los 2 comandos de instalación de §3.1 y `python scripts/doctor.py`.

## 8. Orden de construcción
1. `engine/` con todos los módulos + `tests/` + deck demo (validar en los 3 navegadores).
2. `build_deck.py` (outline JSON → HTML) + temas + layouts.
3. `qa_deck.py` (Playwright) + `doctor.py`.
4. `extract_source.py` (PDF, DOCX, PPTX, XLSX, URL).
5. `charts.py` / diagramas SVG.
6. SKILL.md + references + CI multiplataforma → empaquetar.
