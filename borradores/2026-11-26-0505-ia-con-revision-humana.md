# Borrador 2026-11-26-0505-ia-con-revision-humana

**Modo de la ejecución:** nuevo (calidad.py --estado: sin contenido a mejorar). Ejecución de jueves 26-nov-2026, 05:05 hora de Colombia.
**Tema:** La IA ordena tus correos, tú decides qué se envía.
**Modo de tema:** propio de JDT (plan B). Motivo: ninguna noticia del recolector cumplía los criterios (los temas de GitHub, Hacker News y Lobsters eran de nicho o incidentes de terceros) y los 5 temas propios del recolector ya estaban usados. Se usó el servicio de automatización con IA y revisión humana de marca.md.
**url:** jdt:ia-con-revision-humana
**Fuente:** marca.md. Sin cifras, estudios ni datos de terceros.

## Por qué este tema
Es el servicio de marca.md que más se diferencia (IA con revisión humana), resuelve un dolor reconocible del cliente ideal (correos y solicitudes que se acumulan y se copian a mano) y no repite los títulos recientes.

## Métricas (metricas.md / metricas.json)
Se aplicó: el alcance viene sobre todo de no seguidores (82 %), así que el gancho se entiende en 2 s y no depende de seguidores; los Reels puntuaron menos que las imágenes, por eso el banner tiene peso y el caption usa 8 hashtags (no más de 8); la franja nocturna fue la que mejor respondió, pero la publicación la hace el dueño. Sin datos suficientes para medir retención de este video (aún no publicado).

## Estilo del día (estilos.py, registrado una vez con --elegir)
- Video principal: creator-autentico (POV, cámara en mano, notas en primera persona).
- Apoyo: pantalla-dividida-dinamica (una escena).
- Gancho: tres-senales. Ritmo: mixto. Banner: vidrio-liquido.
- Tres rasgos del principal en el Reel: rótulo «POV · abres el correo» en el gancho; cámara en mano (latido y paneo); notas en primera persona («yo, otra vez a medianoche» y «yo: leo, ajusto y envío»).
- Investigación (WebSearch, 2 búsquedas): metricool.com/es/tendencias-instagram y advids.co (video B2B). **Evidencia limitada:** los resultados devolvieron enlaces sin texto completo; no se afirma ningún porcentaje ni que sea «lo que más convierte».

## Concepto y formato
Concepto: «3 señales de que tu correo te maneja», con la pantalla dividida que muestra que la IA ordena y prepara, y el  ser humano decide; el remate es un botón «Enviar» que solo se activa con el visto bueno.
Formato: Reel vertical 1080x1920, 23,69 s, con voz. Storyboard de 11 beats (validación retencion.py: ok).
Producción: look amarillo en la escena 4 (único momento fuerte, un destello), look azul en la escena 5.
Hipótesis creativa: un espectador que no nos sigue se queda si en 2 s se reconoce en una lista numerada; la pantalla dividida y el botón que espera aprobación responden la objeción «no quiero que una máquina conteste por mí» antes de presentar a JDT. Se contrastará con la retención real cuando se publique.

## Guion (videos/2026-11-26-0505-ia-con-revision-humana.json)
Escenas: 1 gancho (0–2,73 s) · 2 las tres señales (2,73–10,37) · 3 pantalla dividida IA/tú (10,37–15,15) · 4 remate con «Enviar» en amarillo (15,15–17,51) · 5 JDT y el servicio, look azul (17,51–21,09) · 6 cierre con logo, CTA y @technologicsjdt (21,09–23,57).

## Locución
Voz: ElevenLabs, **Douglas pupi** (voice_id Qvk5mDvl4UUK5PrXXheQ), modelo eleven_v4, una generación (345 créditos). Se usó la voz de ElevenLabs y no la local.
Texto: «Tres señales de que tu correo te maneja. Uno: contestas de noche. Dos: se pierden solicitudes. Tres: copias datos a mano. La IA clasifica, saca los datos y deja el borrador. Tú decides. Y nada se envía sin tu visto bueno. En JDT automatizamos procesos con IA y revisión humana. ¡Hablemos de tu proyecto!» (303 caracteres).
**Ajuste de voz (aplicado sin regenerar):** la locución original duraba 24,7 s y el video superaba el máximo de 24 s; se aceleró el MP3 un 12 % con ffmpeg (atempo=1.12, conserva el tono). El original está fuera del repo. Los tiempos de palabras se reescalaron y sincronia.py se volvió a ejecutar.
Palabras con tiempos: videos/2026-11-26-0505-ia-con-revision-humana.palabras.json.
Audio: videos/2026-11-26-0505-ia-con-revision-humana.mp3 (voz) y videos/2026-11-26-0505-ia-con-revision-humana-mezcla.mp3 (con música).
Créditos de voz: 345 gastados en esta ejecución. Antes de generar había 35.135 de 40.000 caracteres usados (4.865 disponibles). No se volvió a consultar el saldo.

## Caption (videos/2026-11-26-0505-ia-con-revision-humana.caption.txt)
¿Tu correo te maneja a ti? Si contestas de noche, se te pierden solicitudes o copias datos a mano, el problema no es tu disciplina: es tu proceso.

En JDT Technologics automatizamos esa parte con inteligencia artificial y revisión humana: la IA clasifica los mensajes, saca los datos y deja el borrador. Tú revisas y decides qué se envía.

Hablemos de tu proyecto. Escríbenos por DM o a technologicsjdt@gmail.com y te respondemos en menos de 24 horas.

@technologicsjdt

#JDTTechnologics #Automatizacion #SoftwareAMedida #InteligenciaArtificial #TransformacionDigital #Bogota #AppsMoviles #DesarrolloWeb

## Banner (banners/2026-11-26-0505-ia-con-revision-humana.png)
Estilo: vidrio-liquido. Título: «¿Tu correo te maneja *a ti*?». Subtítulo: «La IA ordena y prepara. Tú revisas y decides qué se envía.» Puntos: Clasifica y saca los datos · Borrador listo para revisar · Nada se envía sin tu visto bueno. CTA: «Hablemos de tu proyecto.» Logo y @technologicsjdt visibles. La etiqueta «IA CON CRITERIO» no se ve en el PNG final (el renderizador no la dibujó); se deja como pendiente.

## Rutas del video y del banner
- Video: videos/2026-11-26-0505-ia-con-revision-humana.mp4 (23,69 s, 1080x1920, con audio, 2,6 MB)
- Banner: banners/2026-11-26-0505-ia-con-revision-humana.png (1080x1350)
- Motor HTML: html/2026-11-26-0505-ia-con-revision-humana.html

## Revisión del modelo capaz (4 consultas, el máximo)
1. Concepto y guion (opus; fable sin créditos).
2. Validación 3b, ronda 1: **CORREGIR**, nota 6,5. Se aplicaron: azul de la paleta, persona triste, burbuja a la derecha, «✓ Aprobado por ti», JSON que describía iconos no dibujados. Se corrigió «unos 19 s» a «unos 24 s».
3. Validación 3b, ronda 2: **CORREGIR**, nota 8,0. Se aplicaron: chips de la escena 3 (movimiento), JSON alineado con el HTML, comentarios de tiempos.
4. Revisión final: **CORREGIR**, nota 7,0. Defectos: corte diagonal que tapaba el chip «Deja el borrador»; figura triste cortada por el pie; cuña de transición lavanda; @technologicsjdt pequeño; caption sin dónde escribir. **Se corrigieron** todos: chips más arriba, figura subida con cara triste, transición de barrido quitada, @ más grande, caption con DM y correo.

No hubo consulta adicional. La autorrevisión con la rúbrica da nota interna **7,5**.

## Nota interna y aviso
**Nota interna final: 7,5 / 10** (calidad.py --interna). **Está por debajo de la nota mínima de 8.** Lo que falta: la solapa en V del sobre del gancho (el icono sigue siendo un rectángulo), la expresión de la figura (mejor a tamaño real), y la originalidad (la fórmula «tres señales» es conocida). Se entrega para que el dueño decida si lo publica o si se rehace como v2.

Lección nueva guardada: ningún trazo decorativo puede cruzar un chip o un texto; los personajes deben caber enteros sobre el pie con la expresión legible; las transiciones deben usar colores de la paleta (no el azul lavanda de la librería).

## Pendientes de la ejecución
- La prueba de cuadro 0 del gancho: el titular se ve completo desde el cuadro 0,5 s; se cumple la lección.
- Duración: el video dura 23,69 s (dentro de 15–24 s).
- No se publicó nada en Instagram ni en otra red. La publicación la hace el dueño.

Para calificar: agrega en calificaciones.md la fila | 2026-11-26-0505-ia-con-revision-humana | nota | comentario |
