# 11 · Diagramas: cómo generarlos bonitos y funcionales

> Basado en el análisis del proyecto **diagram-design** de Cathryn Lavery (MIT, v2.6), presentado en [Web Reactiva](https://www.webreactiva.com/blog/diagram-design-skill). Repo: <https://github.com/cathrynlavery/diagram-design> · Galería: <https://cathrynlavery.github.io/diagram-design/>.
> Este archivo extrae su "inteligencia" y la adapta a nuestro generador de presentaciones.

## 1. Cómo funciona diagram-design (resumen)

Es una **skill para agentes** (Claude Code, Codex, Pi): instrucciones en Markdown + plantillas HTML + scripts Python de validación. No es una librería de layout automático: **el agente calcula las coordenadas** siguiendo reglas editoriales estrictas y produce **SVG inline dentro de un HTML único**.

```
skills/diagram-design/
├── SKILL.md                    ← filosofía, selección de tipo, reglas de conectores, presupuesto, checklist
├── references/
│   ├── style-guide.md          ← tokens semánticos (paper, ink, muted, accent, link) + tipografía + contraste
│   ├── primitives-core.md      ← markup exacto: nodo, flechas, labels con máscara, leyenda, SVG accesible
│   ├── layout-budget.md        ← grid 4px, tamaños permitidos, límites por tipo
│   ├── semantic-patterns.md    ← 9 patrones de comportamiento (cola/cuello de botella, frontera de confianza…)
│   ├── type-*.md (45)          ← gramática de layout de cada tipo de diagrama
│   ├── animation.md            ← modos none/reveal/step/loop, contrato "static-first"
│   ├── output-spec.md          ← presets de tamaño (slide-16x9…), detalle, audiencia
│   ├── onboarding.md/profiles  ← extraer marca de una URL → tokens; perfiles por cliente
│   └── import-*.md             ← redibujar desde draw.io, Mermaid, Excalidraw
├── assets/                     ← template.html, -dark, -full, -motion + ~100 ejemplos
└── scripts/                    ← self_check.py, export_svg/png.py, *_extract.py
```

**Flujo del agente:**
1. *Gate* de marca: si los tokens son los de fábrica, pregunta si personalizar (URL, carpeta, tokens pegados, perfil guardado).
2. **¿Vale la pena dibujar?** Si una tabla de 3 columnas o un párrafo lo explican igual → no dibuja.
3. Elige **patrón semántico** (si el comportamiento importa) → luego **tipo visual**.
4. **Anuncia el plan** (tipo, tamaño, qué recortará por presupuesto) antes de dibujar.
5. Copia la plantilla, dibuja: **flechas primero, cajas después**.
6. Corre el **taste gate** (checklist) + `self_check.py`.
7. Reporta qué dejó fuera (ledger de fidelidad).

## 2. Filosofía (lo más valioso)

- **"El movimiento de mayor calidad suele ser borrar."** Un diagrama está listo cuando no se puede quitar nada.
- Cada nodo = una idea distinta. Dos nodos que siempre van juntos son uno.
- Cada conexión debe aportar información; si el layout ya la muestra, se quita la línea.
- **Densidad objetivo 4/10.** Más de 9 nodos → probablemente son dos diagramas (overview + detalle).
- **Acento editorial, no semáforo**: color de acento en **1–2 elementos máx.**

## 3. Selección del tipo (45 tipos, agrupados)

| Quieres mostrar… | Tipo |
|---|---|
| Componentes + conexiones (snapshot) | **Architecture** (y *Architecture delta* para antes/después de topología) |
| Estado actual de TI legado | IT current-state |
| Decisiones con ramas | **Flowchart** |
| Mensajes en el tiempo entre actores | **Sequence** (≤5 lifelines) |
| Estados + transiciones | **State machine** / lifecycle |
| Entidades y relaciones | ER, DB schema, UML class |
| Eventos / plan en el tiempo | **Timeline**, Gantt, Story map |
| Proceso con traspasos entre áreas | **Swimlane** (≤5 carriles), Process, Service blueprint, User journey |
| Priorización 2 ejes | **Quadrant** (incl. 2×2 "consultora") |
| Jerarquía | Tree, Org chart, Nested, **Layer stack**, Pyramid/funnel |
| Ciclos que se refuerzan | **Loop / flywheel** |
| Plataforma de datos | Medallion, Data flow, DP integration, DP security matrix, High-level |
| Infraestructura | **Deployment**, Dependency graph |
| Cuantitativos | Bar, Waterfall, Line (slope, bump, ridgeline), Scatter, Heatmap, Treemap, Sankey, Radar, Polar |
| Estrategia / análisis | **Wardley map**, Fishbone (causa raíz), Venn, Kanban |
| Producto físico | Exploded axonometric, Axonometric plan |

**Patrones semánticos** (se eligen antes del tipo cuando el comportamiento es lo importante): cola/cuello de botella → data flow; marco de etapas con slots → process; input desestructurado → artefacto estructurado; trazas de evaluación de políticas → flowchart; *secure paved road* (fronteras de confianza) → architecture; catálogo de controles / capas de seguridad compensatorias → layer stack; descomposición trazable → tree; ciclo de vida con esperas/reintentos → state machine.

**No dibujar** para: listas, comparaciones de atributos (usar tabla), diagramas de una sola caja.

## 4. Sistema visual del diagrama

### Tokens semánticos (nunca hex en las reglas)
| Rol | Uso | Default light | Default dark |
|---|---|---|---|
| `paper` / `paper-2` | Fondo / contenedor | `#f5f5f5` / `#ececec` | `#2d3142` / `#393e53` |
| `ink` | Texto y trazo principal | `#2d3142` | `#f5f5f5` |
| `muted` / `soft` | Secundario, flechas por defecto, sublabels | `#4f5d75` / `#5a6580` | `#bfc0c0` / `#949eb2` |
| `rule` | Bordes finos | `ink @ .12` | `paper @ .12` |
| `accent` / `accent-tint` | Foco (1–2 máx.) | `#bf4520` / `@ .08` | `#f08a59` |
| `link` | HTTP/API, externos | `#2e5aa8` | `#739fdf` |

**Contrato de contraste:** texto ≥ 4.5:1, texto grande ≥ 3:1, trazos esenciales ≥ 3:1; colores `rgba` se componen sobre el fondo antes de medir. Inversión dark: mismas opacidades, RGB invertido; acento algo más brillante.

**Mapeo a nuestros tokens de deck** (`02-diseno-visual.md`): `paper→--bg`, `paper-2→--surface`, `ink→--text`, `muted→--muted`, `accent→--accent`, `link→--accent-2`. Así el diagrama hereda el tema del deck automáticamente.

### Tratamiento por tipo de nodo
| Nodo | Relleno | Borde |
|---|---|---|
| `focal` (1–2) | `accent-tint` | `accent` |
| `backend` / API / paso | blanco | `ink` |
| `store` (BD, estado) | `ink @ .05` | `muted` |
| `external` / cloud | `ink @ .03` | `ink @ .30` |
| `input` / usuario | `muted @ .10` | `soft` |
| `optional` / async | `ink @ .02` | `ink @ .20` punteado `4,3` |
| `security` / frontera | `accent @ .05` | `accent @ .50` punteado `4,4` |

### Tipografía del diagrama (3 roles)
- `title`: serif display (Instrument Serif) — título.
- `node-name`: sans 600 (Geist) — **nombres legibles por humanos**.
- `sublabel` / `eyebrow` / `arrow-label`: mono (Geist Mono) — **solo contenido técnico** (puertos, protocolos, URLs, tipos), etiquetas en MAYÚSCULAS con tracking.
- *Callouts* editoriales en serif itálica (máx. 2).
- Para slides usar la **rampa "presentation"** (nombres ~16 px en viewBox 1280×720) y menos nodos.

### Grid y medidas (múltiplos de 4)
- Ancho/alto de nodo: 80, 96, 112, 120, 128, 140, 144, 160, 180, 200, 240, 320.
- Separación entre nodos: 20, 24, 32, 40, 48. Padding interno: 8, 12, 16. Radio: 4, 6, 8 (**nunca redondeado tipo píldora**).
- Margen exterior 40 px; leyenda = franja inferior de 60 px.

## 5. Las 6 reglas obligatorias de conectores
1. **Solo ortogonales**: codos en ángulo recto redondeados `r=8` (mín. 6). Diagonales = falla. Entran/salen perpendiculares al borde, a ≥ 8 px de una esquina.
2. **Etiqueta separada**: máx. 14 caracteres, MAYÚSCULAS, sobre máscara opaca color `paper`, con **6–10 px de aire** respecto al trazo (al costado en tramos verticales). Nunca texto vertical.
3. **Sin solapes**: rutas paralelas separadas ≥ 12 px; en cruces usar "puente/salto".
4. **Puntos de anclaje repartidos**: N conectores en un borde de largo L → punto k en `L·k/(N+1)`, ≥ 12 px entre sí.
5. **No pasar por detrás de una caja** que no sea origen/destino (si es inevitable: punteado `4,3`, etiqueta en el extremo visible).
6. **Máscara antes que nodo**: la máscara de un label no puede quedar tapada por un nodo dibujado después.

Roles de flecha: `muted` por defecto · `accent` para el camino principal · `link` para HTTP/API · punteado `5,4` = opcional/async/retorno. Marcadores `arrow`, `arrow-accent`, `arrow-link` siempre definidos.

## 6. Presupuesto de complejidad
| Límite general | Valor |
|---|---|
| Nodos | 9 |
| Flechas | 12 |
| Elementos con acento | 2 |
| Callouts | 2 |
| Animación | 8 pasos, 12 ítems, 2 simultáneos |

Por tipo (ejemplos): sequence 5 lifelines · swimlane 5 carriles · ER 8 entidades · árbol 4 niveles · layer stack 6 capas · barras 8 · líneas 5 series · Gantt 12 tareas · Sankey 3 etapas/8 nodos · deployment 3 zonas/6 nodos · kanban 5 columnas/12 tarjetas. Si se excede → **dividir en overview + detalle** (en un deck: 2 slides, o 1 slide con zoom por fragmentos).

Modos de detalle: `simplified` (≤7) para ejecutivos · `balanced` (≤12) · `faithful` (≤24 con zonas). Audiencia `engineer | mixed | executive` cambia la redacción, no la cantidad.

## 7. Anti-patrones de "AI slop" en diagramas
Dark mode con glow cian/morado · mono como fuente "dev" para todo · todas las cajas iguales · leyenda flotando dentro del área · labels sin máscara · texto vertical · 3 tarjetas idénticas · **sombras** (usar bordes) · radios grandes · acento en todo · copiar el layout automático de Mermaid.

> ⚠️ **Conciliación con `02-diseno-visual.md`**: dentro del **área del diagrama** mandan estas reglas (sin sombras, radio ≤ 8, sin glow). Fuera del diagrama (chrome de la slide, tarjetas bento) se mantienen las reglas del deck.

## 8. Animación de diagramas (contrato "static-first")
- El SVG **está completo sin JS**; la animación solo explica orden, nunca agrega significado. Print/PDF/export/reduced-motion = frame completo.
- Modos: `none` (default) · `reveal` (una vez, termina completo) · **`step`** (pasos controlados) · `loop` (solo token decorativo, ciclo ≥ 3 s).
- Ítems marcados `data-motion-item data-step="1..8"`, máx. 2 entran por paso; opacidad + translate ≤ 8 px.
- Primitivas: dibujado de camino (`pathLength="1"` + dashoffset), revelado escalonado, contador de cola, tipeo de campos, evaluación de políticas, token de flujo, contención, log de auditoría.
- Prohibido: animar coordenadas, rutas, viewBox o texto; zoom, parallax, rebote, glow, partículas.

**Integración con el deck:** el modo `step` se mapea 1:1 a nuestros **fragmentos** (`05-animaciones.md` §2.2): cada `data-step` del diagrama avanza con →/clicker. Es la forma de "narrar" una arquitectura en vivo.

## 9. Accesibilidad del SVG
`<svg role="img" aria-labelledby="<slug>-title <slug>-desc">` → `<title>` como primer hijo (≤ 60 caracteres) y `<desc>` de una oración sobre el **contenido** (no la geometría). IDs con prefijo por diagrama (evita colisiones cuando hay varios diagramas en el mismo deck — **crítico para nosotros**).

## 10. Cómo lo usamos en el generador

### 10.1 Contrato en el outline (`01-storytelling.md` §7)
```json
"visual": {
  "kind": "diagram",
  "diagram": {
    "type": "architecture|flowchart|sequence|swimlane|timeline|quadrant|layers|loop|data-flow|deployment|…",
    "pattern": null,
    "detail": "simplified|balanced|faithful",
    "audience": "executive|mixed|engineer",
    "nodes": [ { "id":"api", "label":"API Gateway", "sub":"APIM · https", "kind":"backend|store|external|input|optional|security", "focal":false, "step":1 } ],
    "edges": [ { "from":"web", "to":"api", "label":"HTTPS", "role":"default|accent|link", "dashed":false, "step":2 } ],
    "groups": [ { "id":"azure", "label":"Azure · Landing zone", "contains":["api","fn","db"], "kind":"security" } ],
    "motion": "none|reveal|step"
  }
}
```

### 10.2 Pipeline de render
1. **Validar presupuesto** (nodos/flechas/acento por tipo) → si excede, dividir en 2 slides o pasar a `simplified`.
2. **Layout**: el agente asigna posiciones en grid de 4 px siguiendo la gramática del `type-*.md` correspondiente. Opción de automatizar con un motor de layout por capas (p. ej. ELK/dagre) **solo para posiciones**, y luego aplicar ruteo ortogonal y reglas editoriales propias (nunca el estilo del motor).
3. **Render SVG** con `viewBox="0 0 1280 720"` (preset `slide-16x9`) escalado dentro del área de contenido del slide; tokens vía `var(--…)` del deck.
4. **Orden de pintado**: fondo → zonas/grupos → flechas → máscaras de label → nodos → leyenda.
5. **Validar** las 6 reglas de conectores + contraste + IDs únicos (port simplificado de `self_check.py`/`verify-geometry.py` en nuestro QA Playwright).
6. Notas del orador: generar automáticamente un guion "recorrido del diagrama" paso a paso.

### 10.3 Tipos prioritarios para Miguel (cloud / integraciones / IA)
Architecture (+ delta antes/después) · Data flow · Sequence (integraciones APIM/Logic Apps/Service Bus) · Deployment (AKS, zonas) · Layer stack (seguridad, gobierno) · Swimlane (procesos de negocio) · Quadrant (priorización) · Timeline/Roadmap · Loop (flywheel de adopción IA) · Wardley (estrategia build/buy).

### 10.4 Opciones de reutilización directa
- **Instalar la skill** en Claude Code (`/plugin marketplace add cathrynlavery/diagram-design` + `/plugin install`) y pedir diagramas con preset `slide-16x9` para incrustar.
- **Vendorizar** (licencia MIT, mantener aviso de copyright) las plantillas, `style-guide.md` y scripts en `vendor/diagram-design/` y crear un perfil de marca propio (`profiles.md`).
- **Importar** diagramas existentes de draw.io / Mermaid / Excalidraw y redibujarlos con estas reglas (extrae contenido, descarta coordenadas y estilos).
