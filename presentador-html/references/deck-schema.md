# Esquema de `deck.json`

Contrato entre el agente (que escribe el contenido) y `scripts/build_deck.py` (que genera el HTML).
**Rutas de imágenes y SVG: relativas a la carpeta del `deck.json`** (o URL https, que se descarga y cachea en `.cache/`).
Texto: admite markdown mínimo → `**negrita**`, `*itálica*`, `==resaltado==`, `[texto](https://…)`, `\n` = salto.

## meta

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `title` | str | 1ª slide | Título del documento y de la minuta |
| `lang` | str | `es` | Idioma (formato de números, fechas) |
| `kind` | str | — | `ejecutiva \| estatus \| comercial \| capacitacion \| capacitacion-comercial \| gamificada` (ref. 12) |
| `tone` | str | — | `storytelling \| directo \| explicativo \| minimalista \| grafico \| datos \| consultor \| inspiracional \| ludico \| tecnico` (ref. 13). Activa avisos de palabras por slide |
| `bigIdea` | str | — | Idea central (1 oración). Documental |
| `theme` | str \| obj | `editorial-claro` | `editorial-claro`, `tech-oscuro`, `corporativo`, `ludico`, `noche`, ruta a un `.json` propio, u objeto con la misma forma que `assets/themes/*.json` |
| `themeOverrides` | obj | — | Sobrescribe partes del tema: `{"colors":{"accent":"#…"},"fonts":{"display":"sora"}}` |
| `author`, `date` | str | — | Aparecen en la portada (`title`) |
| `fragments` | bool | `false` | Revelado paso a paso por defecto en todas las slides |
| `dimPrevious` | bool | `false` | Atenúa fragmentos anteriores (efecto foco) |
| `aurora` | bool | `false` | Fondo degradado sutil en slides sin imagen (title, statement, big-number, cta, closing) |
| `fileName` | str | slug | Base del nombre al guardar/exportar |
| `output` | str | `deck.html` | Archivo de salida (relativo al deck.json) |
| `quizPoints` | int | 10 | Puntos por respuesta correcta |
| `autoplaySec` | int | 8 | Segundos por paso con la tecla A |
| `inkColors` | [str] | rojo, amarillo, verde, azul, blanco | Colores del lápiz (teclas 1–5) |
| `css` | str | — | CSS adicional (escape hatch) |

Fuentes disponibles para `themeOverrides.fonts`: `inter`, `space-grotesk`, `instrument-serif`, `plus-jakarta-sans`, `sora`, `jetbrains-mono`.
Colores de tema: `bg, surface, surface2, text, muted, line, accent, accent2, onAccent, good, warn, bad`.

## Campos comunes a toda slide

| Campo | Descripción |
|---|---|
| `type` | Ver tipos abajo (obligatorio) |
| `id` | Identificador estable (default `s1`, `s2`…). Úsalo si vas a reordenar: anotaciones y notas se guardan por id |
| `eyebrow` | Etiqueta pequeña sobre el título (MAYÚSCULAS automáticas) |
| `title` | **Afirmación** (no etiqueta). En `title` es el H1 |
| `subtitle` / `lead` | Bajada |
| `text` | Párrafo o lista de párrafos |
| `bullets` | Lista de viñetas (máx. 3–5) |
| `facts` | Lista con ícono: `[{icon, title, text}]` |
| `figure` | Imagen pequeña sobre el título: `"ruta"` o `{src, alt, size:200, shape:"circle", fit:"contain"}` (logo, ilustración, fase lunar…) |
| `chips` | Etiquetas: `["Día 7"]` o `[{icon, text}]` |
| `image` | `"ruta"` o `{src, alt, credit, position, fit:"contain"}` |
| `background` | `{image:{…}, overlay:"bottom\|left\|none", kenburns:true, grain:false, aurora:false}` |
| `notes` | Notas del orador (str o lista). Solo se ven en la vista del presentador (S) |
| `timing` | Segundos planificados (ritmo en la vista del presentador) |
| `fragments` | `true` para revelar viñetas/ítems paso a paso |
| `sfx` | Sonido al entrar: `tick, pop, ding, whoosh, rise, success, error` (solo si el usuario activa sonido con U) |
| `source` | Fuente/cita al pie |
| `tone` | Sobrescribe el tono de meta para esta slide |
| `class`, `align:"center"` | Ajustes finos |

`icon`: cualquier nombre de [Lucide](https://lucide.dev/icons) (incluidos en `assets/icons.json`, ~2.300).

## Tipos

| `type` | Campos propios | Uso |
|---|---|---|
| `title` | `meta:[…]` (o usa meta.author/date), `image`/`background` | Portada |
| `section` | `number` | Separador de capítulo (fondo de acento) |
| `agenda` | `items:[str]`, `current` (índice) | Índice; reutilizable como separador |
| `statement` | `align:"center"`, `image` opcional como fondo | Una frase gigante |
| `big-number` | `stats:[{value, decimals, prefix, unit, label, note}]` (1–4) | Cifras con contador animado |
| `split` | `image`, `side:"left\|right"`, `bleed`, `wide`, + campos comunes | Imagen + contenido (el más versátil) |
| `image-full` | `image` (a sangre), `panel:"bottom\|left"` | Foto protagonista con texto encima |
| `gallery` | `images:[{src, alt, title, text, credit, position}]` (2–4) | Varias imágenes con pie |
| `cards` | `items:[{icon \| image, title, text, featured}]`, `cols` | Bento / capacidades |
| `process` | `steps:[{icon, title, text}]`, `current` | Pasos numerados (ideal con `fragments`) |
| `timeline` | `items:[{date, title, text, current}]` | Hitos / roadmap |
| `comparison` | `columns:[{title, subtitle, bullets, image, recommended, badge}]` | Opciones / antes-después |
| `chart` | `chart:{kind:"bar\|hbar\|line", labels, values, highlight, unit, decimals, max, alt}`, `insight` | Datos: título = insight; 1 serie resaltada |
| `quote` | `text`, `author`, `image` (fondo) | Cita / testimonio |
| `cycle` | `items:[{label, image \| icon}]`, `center:{title,text}`, `current`, `radius`, `nodeSize` + campos comunes a la izquierda | Ciclos (fases, flywheel) |
| `status` | `period`, `health:{status:"g\|a\|r", label}`, `metrics:[{name, value, rag, trend:"up\|down\|flat"}]`, `done`, `next`, `risks`, `decision` | One-pager de estatus (RAG) |
| `quiz` | `options:[{text, correct}]`, `explanation` | Pregunta; clic o teclas 1–4; suma puntos |
| `diagram` | `svg` (ruta a .svg o `<svg…>` inline) o `image` | Diagramas (reglas en ref. 11) |
| `cta` | `actions:[{icon, text}]` | Llamada a la acción |
| `closing` | `contact`, `bullets`, `background` | Cierre |
| `html` | `html` | Escape hatch: HTML propio dentro de `.inner` |

## Ejemplo mínimo

```json
{
  "meta": {"title": "Migración a APIM", "lang": "es", "kind": "ejecutiva", "tone": "directo", "theme": "corporativo"},
  "slides": [
    {"type": "title", "title": "Centralizar integraciones en APIM reduce riesgo y costo", "subtitle": "Comité de Arquitectura · Nov 2026"},
    {"type": "big-number", "title": "Hoy operamos 140 integraciones sin gobierno común", "stats": [{"value": 140, "label": "integraciones"}, {"value": 37, "unit": "%", "label": "sin monitoreo"}]},
    {"type": "cta", "title": "Decisión: aprobar la fase 1 (Q1 2027)", "actions": [{"icon": "check", "text": "Aprobar presupuesto fase 1"}]}
  ]
}
```
Más ejemplos completos (few-shot) en `examples/*/deck.json`.
