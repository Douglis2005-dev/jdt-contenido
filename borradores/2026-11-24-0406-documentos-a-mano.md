# Reel + banner: Facturas y documentos que alguien transcribe dato por dato

- **Fecha de ejecución:** 2026-11-24, 04:06 (hora de Colombia). Modo: **nuevo**.
- **Modo de tema:** propio de JDT (plan B). No hubo noticia que cumpliera los criterios de forma verificable; los temas de GitHub y Lobsters del recolector eran de videojuegos, emuladores o herramientas sin relación con un negocio. Fuente: `marca.md` (servicio: Automatización con IA).
- **Servicio de JDT que resuelve el problema:** Automatización con IA (extraer datos de documentos, con revisión humana).
- **Concepto (una frase):** el «error» en pantalla no está en el sistema sino en la mano que copia cada factura dato por dato; con IA el dato llega leído y el equipo solo revisa.
- **Formato:** microhistoria de 6 escenas con un gancho de error falso, una pantalla dividida (a mano frente a capturado), un giro en pantalla amarilla y un cierre con CTA.

## Estilo del día (paso 3B)
- Video principal: **microdocumental-cinematografico**. Apoyo (solo en la escena dividida): **pantalla-dividida-dinamica**.
- Gancho: **error-falso**. Ritmo: **mixto**. Banner: **collage-recorte**.
- Pulso: Metricool 2026 indica caída de Reels y auge de YouTube, así que el video debe ganarse la atención en los primeros segundos. Un estudio de motion en video corporativo B2B (interempresas) indica que el motion sustituye al video caro y que la confianza viene de ver el proceso real.
- Fuentes consultadas (2026-11-24): https://metricool.com/es/tendencias-instagram/ · https://www.interempresas.net/TIC/618149-Eficiencia-y-creatividad-en-los-videos-corporativos-con-IA.html
- Tres rasgos visibles del estilo principal: (1) planos con profundidad, grano y viñeta en la escena de contexto; (2) luz amarilla y cámara lenta en el giro; (3) cortes motivados por la voz (la pantalla dividida cambia de lado al decir «de este otro»).
- Motor: **HTML** (`html/2026-11-24-0406-documentos-a-mano.html`). Storyboard validado con `retencion.py` (11 beats, hook a 2,2 s, sin huecos).

## Guion
| Escena | Tiempo | Voz | Visual |
|---|---|---|---|
| 1 gancho | 0,0–2,55 s | ¡Uy! Un dato mal copiado. | Titular «¿Error? Un dato mal copiado», tarjeta amarilla «Campo no coincide», texto cortado y barra trabada |
| 2 contexto | 2,55–6,07 s | Alguien pasa cada factura a mano, dato por dato. | Documento grande y tres píldoras que viajan por una línea |
| 3 tensión | 6,07–10,39 s | De este lado, tecleas. De este otro, el dato ya llegó. | Pantalla dividida: MANUAL a la izquierda, CAPTURADO a la derecha |
| 4 giro y solución | 10,39–18,95 s | En JDT TECHNOLOGICS hacemos automatización con IA: lee tus documentos y extrae los datos. Tu equipo solo revisa. | Pantalla amarilla, robot que lee, «Campo verificado», «Con revisión de tu equipo» |
| 5 notificaciones | 18,95–20,79 s | Más control de tus datos. | Avisos en azul de marca |
| 6 cierre | 20,79–23,5 s | Hablemos de tu proyecto. | Logo, «Hablemos de tu proyecto», @technologicsjdt |

**Locución completa (293 caracteres):** «¡Uy! Un dato mal copiado. Alguien pasa cada factura a mano, dato por dato. De este lado, tecleas. De este otro, el dato ya llegó. En JDT TECHNOLOGICS hacemos automatización con IA: lee tus documentos y extrae los datos. Tu equipo solo revisa. Más control de tus datos. Hablemos de tu proyecto.»

## Producción de la voz
- **Voz:** ElevenLabs, voz «Douglas pupi» (`Qvk5mDvl4UUK5PrXXheQ`), modelo eleven_v4, turno de voz de esta ejecución.
- **Generaciones:** tres intentos. El primero (328 caracteres, 24,6 s) hacía que el video durara 25 s, por encima del tope de 24 s del validador. El segundo (310 caracteres) seguía en 24,5 s con el colchón de cierre. El tercero (293 caracteres, 22,96 s) es el que se usó. Caracteres de cuota gastados en esta ejecución: 328 + 310 + 293 = 931 (la cuenta marcaba 31.154 de 40.000 antes de empezar; quedan aprox. 7.900 este mes).
- **Transcripción con tiempos:** ElevenLabs Scribe (sin costo de créditos); `videos/2026-11-24-0406-documentos-a-mano.palabras.json`.
- **Sincronía:** confianza alta, por palabras; cortes en 2,55 / 6,07 / 10,39 / 18,95 / 20,79 s.

## Caption (copiar y pegar)
¿Cuántas facturas copia alguien en tu empresa a mano, dato por dato? Cada dato tecleado puede equivocarse, y el tiempo se va en algo que una máquina lee en segundos. En JDT TECHNOLOGICS hacemos automatización con IA: leemos tus documentos, extraemos los datos y tu equipo solo revisa. Hablemos de tu proyecto. @technologicsjdt

#JDTTechnologics #Automatizacion #AutomatizacionConIA #SoftwareAMedida #TransformacionDigital #Bogota #Colombia #Pymes #Facturacion #InteligenciaArtificial

## Banner
- Archivo: `banners/2026-11-24-0406-documentos-a-mano.png` (JSON en `banners/2026-11-24-0406-documentos-a-mano.json`, estilo collage-recorte, icono documento).
- Titular: «¿Copias facturas *a mano* todos los días?» · Subtítulo: «Cada dato que alguien teclea es una oportunidad de error y tiempo perdido.» · CTA: «Hablemos de tu proyecto.» · Logo y @technologicsjdt visibles.

## Rutas
- Video: `videos/2026-11-24-0406-documentos-a-mano.mp4` (23,6 s, 8,4 MB, con audio).
- Banner: `banners/2026-11-24-0406-documentos-a-mano.png`.
- Guion: `videos/2026-11-24-0406-documentos-a-mano.json`. Voz: `videos/2026-11-24-0406-documentos-a-mano.mp3`. Mezcla: `videos/2026-11-24-0406-documentos-a-mano-mezcla.mp3`.

## Revisión y nota
- Validación creativa (modelo capaz, Opus; Fable no tenía créditos): **CORREGIR, nota interna 7/10**. Notas: sobriedad 4, claridad 4, impacto 3, originalidad 3, marca 4, vigencia 3, aprendizaje 3.
- Correcciones aplicadas: gancho visible desde t=0 con un solo golpe de glitch, barra de «Guardando…» con relleno, salida del amarillo sin corte seco, flecha y robot en amarillo sobre azul, la alerta se resuelve en «Campo verificado» y se nombra «Automatización con IA» en la escena 4.
- **No se volvió a revisar después de corregir.** La nota 7 queda por debajo del mínimo de 8. Se recomienda una segunda revisión antes de publicar.
- Glitch: se quitó un filtro `hue-rotate` que sacaba colores fuera de la paleta (el script lo detectó).
- Consultas al modelo capaz en esta ejecución: 2 (Opus): una para concepto y guion (Fable falló por falta de créditos) y una para la validación 3b. No hubo revisión final separada tras las correcciones.

## Hipótesis creativa
Si el gancho se lee desde el primer cuadro y el giro resuelve el error visual con una sola acción, la retención del primer tramo debería mejorar frente a los videos con texto en reposo. Se contrastará con métricas reales cuando estén disponibles; hoy no hay datos de finalización.

**Para calificar:** agrega en calificaciones.md la fila | 2026-11-24-0406-documentos-a-mano | nota | comentario |
