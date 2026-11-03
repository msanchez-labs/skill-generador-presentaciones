# 09 · Benchmark: Gamma vs. nuestro generador

> Investigado nov-2026 (ver `fuentes.md`). Gamma es la referencia de "presentaciones con IA"; el objetivo es superarlo en **presentación en vivo, control de diseño, portabilidad y utilidad**.

## 1. Qué hace bien Gamma (lo que debemos igualar)
- Generación con IA desde prompt / outline / archivo; edición con IA (reescribir, cambiar tono, expandir, reestructurar).
- "Cards" que se adaptan al contenido y responden en móvil.
- Temas, fuentes y colores personalizados; plantillas de workspace.
- **Spotlight** (`S`): resalta el bloque actual, atenúa lo visto y difumina lo siguiente.
- **Edición rápida en vivo** (`E` o clic derecho) durante la presentación.
- Presenter view con notas privadas; **Follow mode** (la audiencia sigue con link).
- Barra de progreso; animaciones activables en Page setup.
- Embeds (YouTube, Loom, Vimeo), Smart Charts, Smart Diagrams, imágenes IA.
- Analytics de vistas y tiempo por card; publicación como sitio web con dominio.
- Export a PDF, PowerPoint, Google Slides; API y servidor MCP.

## 2. Debilidades documentadas de Gamma (nuestra oportunidad)
| Debilidad | Evidencia | Nuestra respuesta |
|---|---|---|
| Sin **puntero láser / lápiz / resaltador** en modo presentación | Idea abierta en ideas.gamma.app; usuarios reportan que el láser existió y desapareció; el equipo propone Spotlight como sustituto | Láser con estela, spotlight, lupa, **dibujo vectorial con presión**, pizarra en blanco |
| Control de diseño limitado (sin precisión de píxel) | Reviews 2026 | Lienzo fijo 1920×1080 + grid + tokens; edición fina |
| Exportación con pérdida (gráficos movidos, fuentes sustituidas, fallos > ~150 slides) | Reviews 2026 | El HTML **es** el entregable: fidelidad 100%; PDF desde el mismo motor |
| Depende de conexión; app móvil limitada | Reviews 2026 | **Offline total**, un archivo, sin cuenta |
| Spotlight poco compatible con clickers | ideas.gamma.app | Mapear PageUp/PageDown/B/. de clickers estándar |
| Fuentes personalizadas solo en plan pago; API solo Pro | Reviews 2026 | Libre y abierto, fuentes OFL incrustadas |
| Pocas transiciones "cinematográficas" | Help center solo ofrece on/off de animaciones | **Morph** entre slides (View Transitions), builds, count-up, diagramas que se dibujan |

## 3. Diferenciadores propuestos ("mejor que Gamma")
1. **Kit de presentador completo**: láser, spotlight, zoom, lápiz/resaltador/flechas, pizarra, blackout, timer con pacing.
2. **Notas de sesión** integradas (tomar notas, acuerdos, preguntas) exportables a Markdown — el deck se vuelve **minuta**.
3. **Edición en vivo** + "Guardar como HTML" que persiste cambios, notas y anotaciones en el mismo archivo.
4. **Storytelling primero**: outline con Big Idea, estructura narrativa elegida por propósito, validación de lógica horizontal y STAR moment.
5. **Morph y animación narrativa** de datos y diagramas.
6. **Sonido opcional** sintetizado (0 KB) y narración TTS desde notas.
7. **Portabilidad**: un `.html` offline, versionable en Git, enviable por correo, publicable en cualquier hosting estático.
8. **Doble modo**: presentación ↔ lectura (scroll) para quien recibe el deck sin presentador.
9. **QA automático** de calidad visual (overflow, contraste, peso) antes de entregar.
10. **Extensible**: módulos plug-in (encuestas, follow mode, control remoto desde celular).

## 4. Lo que Gamma tiene y queda como roadmap
- Analytics de visualización (requiere backend / beacon opcional).
- Colaboración multiusuario en tiempo real y comentarios.
- Export a PPTX editable (posible con `pptxgenjs` como módulo aparte).
- Hosting con dominio y SEO (cualquier hosting estático lo resuelve).
