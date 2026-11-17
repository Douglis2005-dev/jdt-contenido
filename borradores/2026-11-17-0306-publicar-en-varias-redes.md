# Borrador 2026-11-17-0306 · Publicar en varias redes (copiar y pegar)

**Tema:** publicar lo mismo en varias redes sociales es copiar y pegar una y otra vez.
**Fuente:** https://github.com/CzzzzzzJ/mdldm-maitian (README: el usuario escribe el texto y sube video y portada a cada plataforma; el proyecto arma un calendario de publicaciones, carga en varias plataformas y deja el botón final al usuario).
**Por qué se eligió:** el recolector trajo casi solo GitHub (Hacker News, dev.to y Lobsters bloqueados por la red); el tema toca un dolor de dueños de negocio y conecta con el servicio de automatización de marca.md. Se descartaron temas ya usados y los que dependían de cifras no verificables (las páginas de noticias de Colombia no se pudieron abrir desde la nube).

**Concepto:** la promo se duplica en pantalla como un video trabado porque así se vive publicar red por red; el bucle se rompe cuando se arma una sola vez y un calendario la organiza.
**Formato:** «el bucle» (gancho, tarea que cae, giro azul, contador «1 botón final», remate, cierre).
**Producción:** oscuro con pila de tarjetas en diagonal, notificaciones que caen, calendario que reparte a tres redes, contador amarillo, copias que se funden en un visto bueno, cierre de marca. Un barrido en cada uno de dos cortes; grano solo en la escena 2; destello no aplicado.

## Guion
Escenas (de videos/2026-11-17-0306-publicar-en-varias-redes.json):
1. Gancho (0–5,1 s): «¿Otra vez *lo mismo*?»
2. Tareas (5,1–11,1 s): escribir el texto, subir el video, subir la portada, siguiente red… «¡Desde cero!»
3. Giro (11,1–15,0 s): calendario que reparte a tres redes. «Lo armas *una vez*»
4. Contador (15,0–17,3 s): «1» y «botón final». «Y es *tuyo*»
5. Remate (17,3–21,6 s): «Adiós al *copiar y pegar*»
6. Cierre (21,6–24,2 s): logo, «Hablemos de tu proyecto», @technologicsjdt

## Locución
Voz: **ElevenLabs**, voz de turno «Juan» (voice_id rX5fO2VkGJYiYGyfqt8r), modelo eleven_v4, una generación. Duración 22,6 s.
Texto: Subes la promo… y otra vez. ¡Y otra vez! Escribes el texto, subes el video, la portada… y en la siguiente red, ¡desde cero! ¿Y si lo armas UNA sola vez y un calendario lo carga en varias redes? Tú solo revisas y le das al botón final. En JDT Technologics eliminamos esas tareas repetitivas de tu día a día. ¡Hablemos de tu proyecto!
Créditos de voz: 379 créditos gastados en esta ejecución; antes del render quedaban 24.832 de 40.000 caracteres (límite del plan Starter). La transcripción de tiempos (scribe) no consume caracteres.

## Caption
¿Publicas lo mismo en cada red, una por una? Ya no tiene que ser así. Armas la publicación una sola vez, un calendario la organiza y tú solo revisas antes del botón final. Eliminamos esas tareas repetitivas de tu día a día. Hablemos de tu proyecto: @technologicsjdt

#JDTTechnologics #SoftwareAMedida #DesarrolloDeSoftware #Automatizacion #TransformacionDigital #Bogota #Colombia #AppsMoviles #DesarrolloWeb #IA

## Banner
Texto: «¿Publicas lo mismo en cada red? Eso se *automatiza*». Puntos: un solo flujo para varias redes; tú revisas antes de publicar; menos copiar y pegar cada semana. CTA: Hablemos de tu proyecto.
Rutas: banners/2026-11-17-0306-publicar-en-varias-redes.json y banners/2026-11-17-0306-publicar-en-varias-redes.png

## Rutas
- Video: videos/2026-11-17-0306-publicar-en-varias-redes.mp4 (1080x1920, 25,4 s, con voz y música; 3,1 MB)
- Guion: videos/2026-11-17-0306-publicar-en-varias-redes.json · Voz: videos/2026-11-17-0306-publicar-en-varias-redes.mp3 · Mezcla: videos/2026-11-17-0306-publicar-en-varias-redes-mezcla.mp3 · Tiempos: videos/2026-11-17-0306-publicar-en-varias-redes.palabras.json
- HTML: html/2026-11-17-0306-publicar-en-varias-redes.html

## Revisiones
- Modelo capaz consultado 2 veces (1 concepto y guion, 1 validación creativa, que dio NO APROBADO con 9 correcciones; se aplicaron las 1 a 4 y la 8, más limpieza de código). La validación se hizo sobre cuadros, después del primer render.
- Pendiente de la revisión: escena 5 con copias poco visibles (se aceptó); la primera escena dura 5,1 s, más que los 3 s de la regla de ritmo, porque la voz tarda eso en la primera frase.
- Dato a corregir en el repo: render_video.py se cae si encuentra un *.palabras.json en videos/ (no se tocó por la regla de scripts).
