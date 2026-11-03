# 12 · Tipos de presentación (por propósito)

> Cada tipo define **estructura, slides obligatorias, KPIs de éxito y herramientas interactivas** recomendadas. Se combina con un **tono** (`13-tonos.md`).
> Clave en el outline: `meta.kind`.

| `kind` | Objetivo | Audiencia | Duración típica | Tono por defecto |
|---|---|---|---|---|
| `ejecutiva` | Que decidan | C-level, comité, directorio | 10–20 min + discusión | Directo |
| `estatus` | Que sepan dónde estamos y qué se necesita | Steering, sponsor, cliente | 5–15 min | Directo / Datos |
| `comercial` | Que avancen al siguiente paso de compra | Prospecto, cliente | 15–30 min | Storytelling |
| `capacitacion` | Que sepan hacer algo | Equipo, usuarios, clientes, partners | 30–120 min | Explicativo |
| `capacitacion-comercial` | Que vendan / adopten mejor (sales enablement, onboarding de clientes) | Fuerza de venta, partners, clientes | 30–90 min | Explicativo + Lúdico |
| `gamificada` | Que participen y retengan | Cualquier grupo en vivo | 20–90 min | Lúdico |

---

## 1. Ejecutiva

**Principio: la respuesta primero (BLUF / Pirámide).** Duarte recomienda iniciar con hallazgos, conclusiones, recomendación y llamada a la acción; imaginar que solo hay 5 minutos; avisar que tras el resumen viene la discusión (reduce interrupciones) y dejar el resto como apéndice (**regla del 10%**: por cada 50 slides de apéndice, 5 de resumen).

**Estructura (SCQA):**
1. `title` con la recomendación como subtítulo.
2. **Resumen ejecutivo** (1 slide): situación · complicación · recomendación · impacto · decisión pedida.
3. 2–4 slides de soporte (un argumento cada una, título-afirmación + 1 evidencia).
4. Opciones evaluadas (`comparison`, la recomendada destacada) con costo / riesgo / plazo.
5. **Decisión requerida** (`cta`): qué, quién, cuándo, cuánto.
6. `appendix` (oculto en el flujo; accesible por menú/paleta `Ctrl+K`).

**Reglas:** máx. 10 slides principales · un número por slide · sin jerga técnica (traducir a riesgo, costo, tiempo, cliente) · siempre "costo de no actuar".
**Herramientas clave:** salto rápido al apéndice (`Ctrl+K` / número+Enter), zoom, lápiz para marcar sobre gráficos en la discusión, **notas de sesión para registrar acuerdos** → exportar minuta.
**KPI:** decisión tomada en la reunión.

## 2. Estatus de avance (steering / proyecto)

**Estructura de la slide de estatus (one-pager)**, según buenas prácticas de consultoría:
1. Identificación: proyecto, periodo, **fecha de corte**.
2. **Salud general** (RAG o badge En plan / En riesgo / Fuera de plan) — el elemento más visible.
3. 5–7 métricas: cronograma (% avance vs plan), presupuesto (gasto vs plan, forecast), alcance, recursos, calidad.
4. Logros desde el último reporte (2–4, **resultados, no actividades**).
5. Próximas prioridades (2–4, con fecha).
6. Riesgos (futuros) y problemas (ya ocurridos): responsable, impacto, estado.
7. **Decisiones requeridas** — o explícitamente "solo informativo".

**Criterios RAG** (definirlos y compartirlos con stakeholders):
| Estado | Ejemplo cronograma | Ejemplo presupuesto | Acción |
|---|---|---|---|
| 🟢 Verde | En plan | Variación < 5% | Mantener |
| 🟠 Ámbar | 1–2 semanas de atraso | 5–10% | Vigilar y mitigar |
| 🔴 Rojo | > 2 semanas | > 10% | Escalar |

Reglas: RAG **por dimensión** (no esconder problemas tras un verde general) · **flecha de tendencia** (↑ → ↓) · calcular desde datos · no abusar del ámbar · nunca "sandía" (verde por fuera, rojo por dentro) · Harvey balls para madurez/avance por fase (0/25/50/75/100%).
RAG nunca solo por color: siempre texto + ícono (accesibilidad).

**Deck de estatus completo:** one-pager → roadmap/timeline con hito actual → detalle por frente (1 slide c/u) → riesgos (matriz probabilidad × impacto) → decisiones → apéndice.
**Diagramas útiles** (`11-diagramas.md`): Timeline, Gantt, Kanban, Architecture delta (qué cambió).
**Herramientas:** datos actualizables (bloque JSON en el HTML para regenerar semanalmente), comparación vs reporte anterior, notas de sesión para acuerdos.
**KPI:** stakeholders alineados y bloqueos resueltos.

## 3. Comercial (venta / pitch)

**Estructura base de 8 slides** (Storydoc, a partir de >100.000 sesiones analizadas):
1. Portada con movimiento + tiempo de lectura.
2. Propuesta de valor (qué resuelves, para quién, por qué tú — ~30–35 palabras).
3. Empresa — **lo que le importa al prospecto**, no un "quiénes somos" largo.
4. **Problema** de alto impacto + costo de no actuar (urgencia).
5. **Solución**: cómo funciona, demo, cada función → resultado.
6. **Beneficios** cuantificados y con plazo.
7. **Prueba social**: casos de un cliente similar, testimonios, logos, premios.
8. **Siguiente paso**: un compromiso pequeño (< 10 min), inmediato (agendar desde la misma slide/QR). Nunca terminar en "Gracias".

**Narrativa:** Problema → Solución → Beneficio, o Antes → Después → Puente (`01-storytelling.md`). El cliente es el héroe.
**Personalización:** logo/nombre/colores del prospecto, datos de su industria, caso del mismo segmento (variables en el JSON del deck).
**Interactividad:** demo embebida o capturas animadas, **calculadora de ROI** con sliders ("¿qué pasa si…?"), comparativa filtrable, QR para agendar.
**KPI:** siguiente reunión agendada / propuesta solicitada.

## 4. Capacitación

**Diseño instruccional:** 3–5 objetivos de aprendizaje medibles ("al terminar podrás…"). Estructura por módulo:
```
Objetivo → Concepto (1 idea) → Ejemplo real → Práctica / check → Recap
```
Secuencia general: bienvenida + reglas → agenda (mapa de progreso) → módulos → caso integrador → evaluación → recap + recursos → encuesta de satisfacción.

**Principios de aprendizaje aplicables:** chunking (bloques de 10–15 min), señalización (resaltar lo clave), contigüidad (texto junto a su imagen), recuperación activa (preguntar antes de explicar), repetición espaciada (recap al inicio de cada módulo), ejemplos trabajados paso a paso.
**Slides propias:** `objective`, `concept`, `example`, `try-it` (ejercicio con timer), `quiz`, `recap`, `cheat-sheet` (hoja de referencia descargable).
**Herramientas:** timer de ejercicio en pantalla, pizarra en blanco (`W`), código ejecutable en vivo, **modo lectura** para estudiar después, notas del alumno exportables.
**KPI:** % de acierto en la evaluación, tiempo hasta la competencia.

### 4.1 Capacitación con fines comerciales (sales enablement / onboarding de clientes / partners)
Mezcla capacitación + comercial: enseñar el producto **a través del valor que entrega al cliente**.
- Módulos: el cliente ideal y sus dolores → propuesta de valor → producto (demo) → manejo de objeciones → casos de éxito → pricing/packaging → proceso de venta → role-play.
- Recursos: **battle cards** (competidor: fortalezas, debilidades, cómo ganar), scripts de discovery, árbol de objeciones (diagrama flowchart), calculadora de ROI reutilizable.
- Gamificar: role-play con puntaje, quiz de objeciones, ranking por equipo, badge de certificación.
- KPI de negocio: tasa de conversión, tiempo de ramp-up, adopción del producto por el cliente.

## 5. Gamificada

Gamificación = **mecánicas de juego al servicio de un objetivo**, no decoración. Mapear 3–5 objetivos a 3–5 mecánicas.

| Mecánica | Implementación en HTML único | Para qué |
|---|---|---|
| **Quiz** de opción múltiple | Slide `quiz` con opciones clicables / teclas A–D, feedback inmediato explicando por qué | Recuperación activa |
| **Puntos y marcador** | Contador en HUD; marcador por equipos editable por el presentador (+/–) | Motivación |
| **Niveles / progreso** | Barra de "nivel" por módulo; mapa de misión (camino con hitos desbloqueados) | Sensación de avance |
| **Badges** | Medalla SVG animada al completar módulo | Reconocimiento |
| **Desafío con tiempo** | Cuenta regresiva + sonido final | Tensión / foco |
| **Revelado / misterio** | Tarjetas que se voltean, "adivina el número" antes de mostrar el big-number | Curiosidad |
| **Ruleta / sorteo** | Rueda SVG que elige participante o pregunta | Participación |
| **Narrativa** | Misión con personaje y escenario (viaje del héroe) | Cohesión |
| **Escenarios ramificados** | "¿Qué harías?" → slide destino según respuesta (máx. 2 niveles) | Toma de decisiones |
| **Celebración** | Confeti + sonido (`07-sonido.md`) | Cierre de hito |
| **Participación del público** (con backend opcional) | Votación desde celular vía QR, leaderboard en vivo (tipo Kahoot) | Escala a grupos grandes |

**Temática del juego (implementado):** el contenido y la temática son independientes. `meta.game` = `carrera` · `espacial` · `tesoro` · `montana` (o personalizada) cambia vocabulario (km, años luz, monedas, metros), avatar de la barra de progreso, sonidos, decoración y niveles finales. Ej.: *fases lunares* gamificadas como *carrera de autos*.

**Reglas:** feedback específico (nunca punitivo) · no depender solo de puntos · progreso visible y honesto · ramificación limitada · accesible (teclado, contraste, texto + color) · medir aciertos y finalización.
**Errores:** brillo sin propósito, texto denso, demasiadas ramas, mecánicas desconectadas del objetivo.
**Estética:** más color (2 acentos permitidos), ilustraciones/íconos rellenos, tipografía redondeada (Sora, Outfit), animaciones con rebote leve, sonidos de recompensa.

## 6. Plantillas de outline por tipo (resumen)

```json
{ "ejecutiva":   ["title","executive-summary","support×3","options","decision","appendix"],
  "estatus":     ["status-onepager","timeline","workstream×N","risks-matrix","decisions","appendix"],
  "comercial":   ["hero","value-prop","why-us","problem","solution-demo","benefits","proof","next-step"],
  "capacitacion":["welcome","objectives","agenda","(concept,example,try-it,quiz)×N","case","assessment","recap","resources"],
  "capacitacion-comercial":["welcome","objectives","icp-pains","value-prop","demo","objections-quiz","cases","battle-cards","role-play","certification"],
  "gamificada":  ["mission","rules-scoring","(challenge,quiz,reveal)×N","leaderboard","badge-celebration","recap"] }
```
