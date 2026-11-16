# 2026-11-16-0606 · Pedir cambios desde el chat del equipo

**Tema:** GitHub lleva su asistente al chat de Slack y Teams (disponibilidad general), y el trabajo empieza en la conversación sin copiar y pegar.

**Fuente:** https://letsdatascience.com/news/github-makes-github-in-slack-and-teams-generally-available-e4c571a4 (7 nov 2026). Hechos sacados de esta nota. Corroboración: https://www.datastudios.org/post/github-copilot-slack-teams-generally-available-all-paid-plans-teams-canvas. La fuente primaria (changelog de GitHub) NO se pudo abrir.

**Hechos que dice la fuente:**
1. GitHub anunció el 6 nov 2026 que @GitHub en Slack y Teams está disponible de forma general.
2. Desde la conversación se pueden investigar errores, crear issues, implementar cambios y abrir pull requests.
3. El repositorio se identifica a partir del mensaje.
4. Los issues y PR creados llevan una nota con su origen en la conversación.

**No confirmado (no se usó):** quién puede disparar cambios. La fuente dice que no lo especifica. Tampoco precios, planes ni límites.

**Por qué este tema:** conecta con la automatización de procesos (servicio principal) y con software a medida como servicio secundario. Es un problema real de equipos de TI: el pedido nace en el chat y termina copiado a otra herramienta. Ángulo distinto del tema anterior (no es «humano aprueba»).

**Guion** (`videos/2026-11-16-0606-pedir-cambios-desde-el-chat.json`, 20 s, sin audio, 5 escenas de 4 s):
1. titular (gancho): «¿Otra vez *copiando* del chat al código?»
2. reloj: «Cada paso *te roba* minutos» · etiquetas: Leer el error / Abrir el proyecto / Crear la tarea
3. chat: «El pedido nace en *el chat*» · mensajes: Revisa el login, ¿sí? / Tarea creada / Cambio listo para revisar
4. pasos: «De la charla a *la revisión*» · etapas: Charla en el chat / Se busca el proyecto / Cambio para revisar
5. cierre: «Hablemos de *tu proyecto*» · @technologicsjdt

**Locución (texto preparado, NO generada):**
[curious] ¿Otra vez copiando lo que el equipo dice en el chat? [sighs] Así se va el tiempo: leer el error, abrir el proyecto, crear la tarea. [excited] ¡Imagínate que todo empiece en el chat, sin salir de la conversación! [short pause] La charla se vuelve tarea, y luego un cambio listo para revisar. [warmly] En JDT Technologics automatizamos tu operación. ¡Hablemos de tu proyecto!
Locución sin etiquetas: 332 caracteres.

**Voz:** SIN VOZ. La red de la nube bloquea elevenlabsusercontent.com (comprobación con curl: 403 del proxy, salida=56). No se llamó a creative_generate_speech ni a `recolector.py --voz`. Turno de voz pendiente: Juan (rX5fO2VkGJYiYGyfqt8r), no consumido.

**Créditos de voz:** gastados 0. Disponibles: no consultados (no se llamó a account_get_usage, porque la red bloqueó antes).

**Caption** (585 caracteres, 8 hashtags):
¿Otra vez copiando lo que el equipo dice en el chat?

GitHub ya tiene disponible en Slack y Teams su asistente para investigar errores, crear tareas (issues) y proponer cambios de código (pull requests) sin salir de la conversación.

En JDT Technologics automatizamos procesos para que el trabajo empiece donde ya se habla, sin copiar y pegar entre herramientas.

Hablemos de tu proyecto. Cuéntanos tu caso y te respondemos en menos de 24 horas. @technologicsjdt

#JDTTechnologics #Automatizacion #SoftwareAMedida #DesarrolloDeSoftware #TransformacionDigital #DevOps #Bogota #Colombia

**Texto del banner** (`banners/2026-11-16-0606-pedir-cambios-desde-el-chat.json`):
- Título: Del chat del equipo al *cambio para revisar*
- Subtítulo: Investigar, crear la tarea y proponer el cambio sin salir de la conversación.
- Puntos: Sin copiar y pegar · Tarea y cambio en un mismo hilo · Tu equipo revisa el cambio
- CTA: Hablemos de tu proyecto

**Rutas:**
- Video: `videos/2026-11-16-0606-pedir-cambios-desde-el-chat.mp4`
- Banner: `banners/2026-11-16-0606-pedir-cambios-desde-el-chat.png`
- Guion y banner JSON: `videos/2026-11-16-0606-pedir-cambios-desde-el-chat.json`, `banners/2026-11-16-0606-pedir-cambios-desde-el-chat.json`

**Autorrevisión:** cuadros de la mitad de cada escena revisados (y el final de las escenas de chat y pasos). Nada cortado ni encimado, tildes correctas, el cierre muestra logo y @technologicsjdt.

**Revisión final (modelo capaz, 1 consulta):** APROBADO con 3 correcciones, todas aplicadas:
1. Escena 2, voz: «Uy, eso se va el tiempo…» → «Así se va el tiempo…» (para no repetir la reacción en la locución).
2. Escena 3, tercera burbuja: «Ya quedó, revísalo» → «Cambio listo para revisar». El video se regeneró sin audio y el cuadro se revisó. La etiqueta mide 25 caracteres, por encima del máximo de 22 de INSTRUCCIONES.md; se aceptó por indicación del revisor y se anota aquí.
3. Caption, párrafo 2: se precisó «crear tareas (issues) y proponer cambios de código (pull requests)». Para no pasar de 600 caracteres se quitó «para llevarlo al código» de la primera línea.

**Consultas al modelo capaz:** 2 (elección del tema, revisión final). Máximo permitido: 3.

**Notas:** no se publicó nada en redes. No se usó la memoria del usuario. La voz no se consumió.
