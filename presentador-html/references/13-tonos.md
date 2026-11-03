# 13 · Tonos de presentación

> El **tono** define *cómo* se cuenta (densidad de texto, rol de la imagen, ritmo, movimiento, voz). El **tipo** (`12-tipos-presentacion.md`) define *para qué*. Clave en el outline: `meta.tone`.
> Cada tono es un **perfil de parámetros** que el generador aplica a layouts, tipografía, animación y redacción.

## 1. Resumen

| `tone` | Esencia | Texto por slide | Rol de la imagen | Ritmo | Inspiración |
|---|---|---|---|---|---|
| `storytelling` | Una historia con tensión y resolución | 10–25 palabras | Emocional, metáfora | Ondas (es ↔ podría ser) | Duarte, *Resonate* |
| `directo` | La conclusión primero, sin rodeos | 15–35 palabras | Evidencia (dato/gráfico) | Rápido, denso en valor | Minto, BLUF |
| `explicativo` | Entender paso a paso | 25–50 palabras | Diagrama, ejemplo | Progresivo, por fragmentos | Diseño instruccional |
| `minimalista` | Una idea, máximo aire | 1–10 palabras | Opcional, casi nunca | Pausado | Takahashi, Presentation Zen |
| `grafico` | La imagen cuenta; el orador narra | 0–6 palabras | **Protagonista** a sangre | Fluido, muchas slides | Presentation Zen, Lessig |
| `datos` | El número es el argumento | 10–30 palabras | Gráfico con insight | Analítico | *Storytelling with Data* |
| `consultor` | Títulos-acción y lógica MECE | 30–60 palabras (denso controlado) | Gráfico, matriz, tabla | Estructurado | Estilo McKinsey/BCG, assertion-evidence |
| `inspiracional` | Emocionar y movilizar | 5–15 palabras | Cinemática, personas | Crescendo al STAR | Keynote |
| `ludico` | Jugar para aprender | 10–25 palabras | Ilustración, íconos de color | Dinámico, con desafíos | Gamificación |
| `tecnico` | Precisión para expertos | 20–60 palabras | Diagrama, código, terminal | Profundo | Docs / arquitectura |

## 2. Perfiles detallados

### 2.1 Storytelling (narrativo)
- **Voz:** cercana, 2ª persona, verbos de acción; personajes concretos (cliente, usuario); conflicto explícito.
- **Estructura:** Sparkline o viaje del héroe; apertura con historia o pregunta; cierre que vuelve al inicio.
- **Visual:** fotos de personas/contexto, `hero` y `split`; contraste visual entre slides "lo que es" (fríos, desaturados) y "lo que podría ser" (cálidos, luminosos).
- **Movimiento:** transiciones suaves, **morph** para continuidad; build en el momento de tensión.
- **Sonido:** opcional en el STAR moment.
- **Notas del orador:** guion completo con pausas marcadas.

### 2.2 Directo (ejecutivo / BLUF)
- **Voz:** afirmativa, impersonal o 1ª plural, frases cortas; cifra en el título.
- **Estructura:** respuesta en la slide 2, luego soporte; decisión explícita.
- **Visual:** big-number, chart con 1 serie resaltada, comparison; sin fotos decorativas.
- **Movimiento:** mínimo (fade); sin builds salvo en el gráfico clave.
- **Sonido:** ninguno.
- **Texto:** cada slide pasa el test "¿y entonces qué?".

### 2.3 Explicativo (didáctico)
- **Voz:** clara, paso a paso, definiciones, analogías ("es como…"), preguntas retóricas.
- **Estructura:** concepto → ejemplo → práctica → recap.
- **Visual:** diagramas con revelado **step**, procesos numerados, capturas anotadas, código resaltado por líneas.
- **Movimiento:** **fragmentos** abundantes (uno por idea), dim de lo anterior, zoom a zonas.
- **Sonido:** opcional (tick suave en checks/quiz).
- **Extra:** slide `recap` cada 10–15 min; cheat-sheet final.

### 2.4 Minimalista
- **Voz:** frases-titular, sustantivos fuertes; lo demás lo dice el orador.
- **Estructura:** muchas slides de una idea (Takahashi: solo texto enorme; fondo liso).
- **Visual:** `statement` dominante; tipografía display gigante; 1 color de acento; mucho blanco/negro.
- **Movimiento:** cortes secos o fade breve; tipografía cinética sutil.
- **Sonido:** ninguno.
- **Riesgo:** exige orador preparado → notas del orador obligatorias y completas.

### 2.5 Gráfico (visual, poco texto)
> "Que las imágenes expresen lo que se va a hablar."
- **Voz:** el texto en pantalla es un **rótulo** (0–6 palabras); la explicación va en la voz y en las notas.
- **Estructura:** 1 imagen = 1 idea; ritmo rápido (estilo Lessig: slide cambia con cada frase clave; Pecha Kucha: 20 slides × 20 s como disciplina).
- **Visual:** foto/ilustración **a sangre**, metáforas visuales (no literales), tratamiento de color unificado (duotono), íconos grandes, diagramas simplificados (`simplified`), big-numbers.
- **Selección de imagen (regla del generador):** por cada slide derivar `visual.query` desde la **idea** (no las palabras): concepto → metáfora → escena concreta. Ej.: "deuda técnica" → "iceberg", "cuello de botella" → "embudo de tránsito".
- **Movimiento:** Ken Burns lento, morph entre imágenes relacionadas, reveal del rótulo.
- **Sonido:** ambiente suave opcional.
- **Requisito:** **modo lectura** o notas visibles para quien reciba el deck sin orador.

### 2.6 Datos (analítico)
- **Voz:** precisa, con fuente y periodo; insight en el título ("El churn se duplicó en Q3").
- **Visual:** gráficos limpios, anotaciones directas, 1 serie resaltada, small multiples, tablas con cifras tabulares.
- **Movimiento:** construcción del gráfico (barras crecen, línea se dibuja), count-up.
- **Interacción:** tooltips, filtro/escenario en vivo, comparación con periodo anterior.

### 2.7 Consultor (action titles)
- **Voz:** cada título es una conclusión completa (≤ 2 líneas); argumentos MECE; "so what" al pie.
- **Visual:** matrices 2×2, waterfalls, Harvey balls, tablas comparativas, tracker de secciones arriba.
- **Densidad:** mayor que el resto pero ordenada en grid; fuente de datos en cada slide.
- **Uso:** documentos que se **leen** además de presentarse (pre-reads).

### 2.8 Inspiracional (keynote)
- **Voz:** emocional, frases memorables, repetición retórica, "imaginen…".
- **Visual:** fotografía cinematográfica, video de fondo, tipografía gigante, oscuro con acentos luminosos.
- **Movimiento:** transiciones cinematográficas, crescendo hacia el STAR; música de intro.
- **Sonido:** sí, con intención (intro, STAR, cierre).

### 2.9 Lúdico (gamificado)
- **Voz:** cercana, retadora, humor ligero, 2ª persona ("¿te atreves?").
- **Visual:** ilustraciones, colores vivos (hasta 2 acentos), tipografía redondeada, badges, barras de nivel.
- **Movimiento:** rebote leve, celebración (confeti), volteo de tarjetas.
- **Sonido:** recompensas, timer, celebración (silenciable).
- **Interacción:** quiz, marcador, ruleta, escenarios.

### 2.10 Técnico
- **Voz:** precisa, términos correctos, sin marketing; supuestos y restricciones explícitos.
- **Visual:** diagramas de arquitectura/sequence/deployment (`11-diagramas.md`), código, terminal, tablas de decisión (ADR).
- **Movimiento:** step en diagramas, resaltado de líneas de código.
- **Interacción:** código en vivo, demos embebidas, links a repos.

## 3. Parámetros que el generador ajusta por tono

| Parámetro | storytelling | directo | explicativo | minimalista | grafico | datos | consultor | inspiracional | ludico | tecnico |
|---|---|---|---|---|---|---|---|---|---|---|
| `maxWords` | 25 | 35 | 50 | 10 | 6 | 30 | 60 | 15 | 25 | 60 |
| `maxBullets` | 3 | 3 | 5 | 0 | 0 | 3 | 5 | 0 | 3 | 5 |
| `imageWeight` (0–3) | 2 | 0 | 1 | 0 | 3 | 0 | 0 | 3 | 2 | 1 |
| `diagramWeight` | 1 | 1 | 3 | 0 | 1 | 1 | 2 | 0 | 1 | 3 |
| `chartWeight` | 1 | 3 | 1 | 0 | 1 | 3 | 3 | 0 | 1 | 1 |
| `fragments` | medio | bajo | alto | bajo | bajo | medio | bajo | medio | alto | alto |
| `transition` | morph/fade | fade | fade | none/fade | morph | fade | none | cinematic | zoom | none |
| `sound` | opcional | no | opcional | no | opcional | no | no | sí | sí | no |
| `accentColors` | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1–2 | 2 | 1 |
| `typePairing` (`03`) | Editorial | Tech | Tech | Minimal / display | Editorial | Tech/IBM | Corporativo | Editorial display | Futurista redondeada | Editorial-técnico |
| `notesDepth` | guion | puntos | guion | **guion completo** | **guion completo** | puntos | puntos | guion | puntos | puntos |
| `slidesPerMin` | 0.7 | 0.5 | 0.5 | 2 | 2–3 | 0.5 | 0.4 | 1 | 0.8 | 0.5 |

## 4. Matriz tipo × tono recomendado

| Tipo ↓ / Tono → | Primario | Secundarios compatibles |
|---|---|---|
| Ejecutiva | `directo` | `datos`, `consultor`, `storytelling` (apertura) |
| Estatus | `directo` | `datos` |
| Comercial | `storytelling` | `grafico`, `datos` (prueba), `inspiracional` (keynote de producto) |
| Capacitación | `explicativo` | `ludico`, `tecnico`, `grafico` |
| Capacitación comercial | `explicativo` | `ludico`, `storytelling` |
| Gamificada | `ludico` | `explicativo` |
| Propuesta técnica | `tecnico` | `explicativo`, `directo` |
| Keynote / visión | `inspiracional` | `storytelling`, `grafico`, `minimalista` |

**Mezcla de tonos:** permitido un tono primario + 1 secundario por sección (ej. comercial: apertura `storytelling`, prueba en `datos`, cierre `directo`). Se declara por slide con `tone` opcional que hereda de `meta.tone`.

## 5. Ejemplo: el mismo mensaje en 5 tonos

Mensaje: *migrar las integraciones a Azure API Management redujo los incidentes.* (Cifra y personaje **ilustrativos**, no son datos reales.)

| Tono | Título en pantalla | Visual |
|---|---|---|
| storytelling | "Cada lunes, María apagaba incendios. Hoy revisa métricas." | Foto antes/después, morph |
| directo | "Los incidentes bajaron 62% tras centralizar en APIM" | Big-number + barra comparativa |
| explicativo | "Cómo APIM reduce incidentes: 3 mecanismos" | Diagrama step: políticas → retry → observabilidad |
| minimalista | "−62%" | Nada más |
| grafico | "Del caos al control" | Imagen a sangre: cables enredados → panel ordenado |
