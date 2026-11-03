# 01 · Storytelling para presentaciones

> Objetivo: que cada deck sea una **historia con una idea central**, no una colección de diapositivas. El generador debe construir primero la narrativa (outline) y solo después el diseño.

## 1. Principios base

| Principio | Qué significa | Regla para el generador |
|---|---|---|
| **Big Idea** (Duarte) | Una oración con tu punto de vista + qué está en juego para la audiencia | Exigir/derivar `bigIdea` antes de crear slides. Si no cabe en 1 oración (≤25 palabras), la historia no está clara |
| **La audiencia es el héroe** | El presentador es el mentor que entrega la "herramienta" | Redactar beneficios en 2ª persona ("tú/ustedes logran…"), no en "nosotros hicimos…" |
| **Una idea por slide** | Cada slide responde a una sola pregunta | Máx. 1 mensaje; si hay 2, dividir |
| **Título = afirmación** (Assertion-Evidence, M. Alley) | El título es una frase completa con la conclusión; el cuerpo es la evidencia visual | Títulos tipo "Los costos cayeron 32% tras migrar a Azure", no "Costos" |
| **Lógica horizontal** (ghost deck) | Leer solo los títulos en orden debe contar la historia completa | Validación automática: concatenar títulos y verificar coherencia |
| **Contraste y tensión** | La historia avanza alternando problema ↔ solución | Alternar slides de "lo que es" y "lo que podría ser" |
| **Momento STAR** (Something They'll Always Remember) | Un momento memorable: dato impactante, demo, imagen, anécdota | Marcar 1 slide `star: true` por deck, con tratamiento visual especial |
| **Menos texto, más prueba** | Datos, casos, demos, imágenes > bullets | Bullets máx. 3–5, ≤8 palabras c/u |

## 2. Estructuras narrativas (plantillas de outline)

### 2.1 Sparkline — Nancy Duarte (*Resonate*)
Alterna entre **lo que es** (statu quo) y **lo que podría ser** (futuro mejor), cierra con **llamada a la acción** y **nueva felicidad**.
```
Inicio: Lo que es → Lo que podría ser
Medio:  (es ↔ podría ser) × N   ← contraste genera tensión
Cierre: Llamada a la acción → Nueva felicidad (visión del futuro)
```
Ideal para: keynotes, propuestas de cambio, visión estratégica.

### 2.2 SCQA / Pirámide de Minto
**S**ituación → **C**omplicación → **Q** (Pregunta) → **A**nswer (respuesta primero) → argumentos de soporte agrupados (MECE).
Ideal para: comités ejecutivos, steering, decisiones. **Respuesta en la slide 2.**

### 2.3 Problema → Solución → Beneficio → Prueba → CTA
Ideal para: ventas, pitch de producto, propuestas comerciales.

### 2.4 Antes → Después → Puente (BAB)
Muestra el dolor actual, el estado deseado, y tu solución como puente. Ideal para: casos de éxito, demos.

### 2.5 Viaje del héroe (simplificado)
Mundo ordinario → llamado/conflicto → mentor/herramienta → prueba → transformación → regreso con el aprendizaje. Ideal para: charlas inspiracionales, cultura, lecciones aprendidas.

### 2.6 Narrativa de datos (Cole Nussbaumer Knaflic, *Storytelling with Data*)
1. Entender el contexto (quién, qué, cómo) 2. Elegir el visual adecuado 3. Eliminar ruido 4. Dirigir la atención (color/tamaño) 5. Pensar como diseñador 6. Contar la historia.
Ideal para: reportes, QBR, dashboards narrados.

### 2.7 Técnica / Arquitectura (formato útil para Miguel)
Contexto → Problema/Restricciones → Opciones evaluadas → Decisión (ADR) → Arquitectura objetivo → Plan/Roadmap → Riesgos → Próximos pasos.

## 3. Selección automática de estructura

| Propósito / audiencia | Estructura recomendada | Nº slides típico |
|---|---|---|
| Decisión ejecutiva (C-level) | SCQA / Pirámide | 6–10 |
| Visión / keynote | Sparkline | 12–20 |
| Venta / pitch | Problema-Solución-Beneficio | 8–12 |
| Caso de éxito | BAB | 6–10 |
| Reporte con datos | Narrativa de datos | 8–15 |
| Capacitación / workshop | Agenda → módulos (concepto → ejemplo → práctica → recap) | 15–40 |
| Propuesta técnica | Técnica/Arquitectura | 10–18 |

Regla de tiempo: **~1–2 min por slide** de contenido; slides "statement" cuentan como 20–30 s.

## 4. Arquitectura de un deck (beats → tipos de slide)

| Beat narrativo | Tipo de slide sugerido (ver `02-diseno-visual.md` §5) |
|---|---|
| Gancho / apertura | `hero` con imagen full-bleed, pregunta provocadora o dato impactante (`big-number`) |
| Agenda (solo si > 10 slides) | `agenda` con 3–5 hitos, se reutiliza como separador de sección |
| Contexto / lo que es | `split` (imagen + texto), `quote` de cliente |
| Complicación / dolor | `big-number`, `chart` con insight resaltado |
| Lo que podría ser | `hero` aspiracional, `before-after` |
| Solución | `diagram`, `process`, `bento` de capacidades |
| Prueba / evidencia | `chart`, `case`, `logos`, `demo` embebida |
| Comparación de opciones | `comparison` / tabla con recomendada destacada |
| Plan | `timeline`, `roadmap` |
| STAR moment | `statement` tipografía gigante o `video`/`demo` |
| CTA | `cta` con 1 acción concreta + responsable + fecha |
| Cierre | `closing` que vuelve al gancho inicial (cierre en círculo) |

## 5. Patrones de apertura y cierre

**Aperturas fuertes:** dato sorprendente · pregunta a la audiencia · historia breve (personaje + conflicto) · imagen potente sin texto · "imaginen que…" · demo directa.
**Evitar:** "Hola, mi nombre es…" + agenda de 8 puntos como slide 2.

**Cierres fuertes:** volver a la imagen/pregunta inicial (callback) · CTA único y concreto · visión de la "nueva felicidad" · cita breve.
**Evitar:** slide "¿Preguntas?" como último mensaje; mejor dejar el CTA proyectado durante el Q&A.

## 6. Redacción en slides

- Títulos: afirmación completa, ≤ 12 palabras, verbo activo, cifra si existe.
- Cuerpo: ≤ 30 palabras por slide de contenido (excepto slides de referencia/anexo).
- Números: redondear y contextualizar ("3 de cada 4", "2× más rápido") + fuente pequeña al pie.
- Jerga: adaptar a la audiencia (ejecutiva vs técnica). Definir siglas la primera vez.
- Lo que no se dice en voz alta, va en **notas del orador**, no en la slide.

## 7. Contrato de outline para el generador (JSON)

```json
{
  "meta": { "title": "", "audience": "ejecutiva|técnica|general", "purpose": "decidir|informar|vender|enseñar|inspirar",
            "durationMin": 20, "language": "es", "structure": "sparkline|scqa|psb|bab|hero|data|tecnica|workshop",
            "kind": "ejecutiva|estatus|comercial|capacitacion|capacitacion-comercial|gamificada  (ver 12-tipos-presentacion.md)",
            "tone": "storytelling|directo|explicativo|minimalista|grafico|datos|consultor|inspiracional|ludico|tecnico  (ver 13-tonos.md)" },
  "bigIdea": "Una oración con punto de vista + qué está en juego",
  "slides": [
    {
      "id": "s1",
      "beat": "hook|context|tension|vision|solution|proof|comparison|plan|star|cta|closing|section|agenda",
      "type": "hero|statement|big-number|split|bento|chart|comparison|timeline|process|quote|diagram|demo|cta|closing",
      "title": "Afirmación completa",
      "body": ["máx 3–5 bullets cortos"],
      "visual": { "kind": "image|icon|chart|diagram|video|none", "query": "descripción para buscar/generar", "data": null },
      "notes": "Lo que el orador dice (guion)",
      "durationSec": 60,
      "star": false,
      "animation": { "enter": "fade-up", "fragments": true },
      "sound": null
    }
  ]
}
```

### Validaciones automáticas del outline
1. `bigIdea` presente y ≤ 25 palabras.
2. Lógica horizontal: los títulos concatenados forman un argumento continuo.
3. Exactamente 1 `star: true` (o 0 en decks < 6 slides).
4. Existe un `cta` antes del `closing`.
5. Suma `durationSec` ≈ `durationMin × 60` (± 15%).
6. No hay 3 slides seguidas del mismo `type` (monotonía visual).
7. Ninguna slide supera el límite de palabras.
