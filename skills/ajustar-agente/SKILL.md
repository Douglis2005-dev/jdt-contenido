---
name: ajustar-agente-contenido
description: Cambia la CONFIGURACIÓN del agente de contenido de JDT (jdt-contenido) cuando al dueño no le gusta un video, banner, caption, voz o tema. Solo ajustes de configuración, en la rama propia, sin tocar producción.
---

# Ajustar la configuración del agente de contenido de JDT

Esta skill la usan Claude y ChatGPT. Sirve para UNA cosa: cuando el dueño dice «no me gustó…», «muy genérico», «cámbialo», «más…», se cambia **cómo está configurado el agente** para que las próximas ejecuciones salgan mejor. No es para producir contenido y no es para arreglar un archivo suelto.

## Cómo la usa cada IA
- Cada IA recibe este texto por su cuenta (Claude como skill; ChatGPT pegado en las instrucciones de su proyecto). Ninguna necesita leer la rama de la otra.
- Este archivo vive en el repositorio en una sola copia, que la sube Claude desde `Claude-testing`. ChatGPT no lo commitea en `ChatGPT-testing`, para no generar conflictos al unir las ramas.

## Alcance
- SÍ: editar la configuración del agente (instrucciones, catálogo de estilos, motores de render, reglas de marca).
- NO: generar videos o banners «a mano» para entregarlos, editar los videos o banners ya hechos, publicar en redes, subir a Google Drive, ni correr el agente completo.
- Un arreglo que solo corrige UN video o banner ya hecho no sirve: el cambio debe quedar en la configuración para que el problema no vuelva.

## Reglas que no se rompen
1. Trabajas SOLO en tu rama: Claude en `Claude-testing`, ChatGPT en `ChatGPT-testing`. Nunca en `main` (es producción: el agente la lee en cada ejecución) y nunca en la rama de la otra IA.
2. Nada llega a `main` sin la aprobación del dueño. El merge lo hace Claude, una rama por vez, cuando el dueño diga «aprobado».
3. Paleta de marca fija: azul marino #0A0E27, amarillo #FACC15 / dorado #EAB308, blanco y gris azulado #94A3B8. Todo video lleva voz en off. Estilo sobrio y amigable (una idea por escena). Nunca inventar cifras, clientes, precios ni garantías. Textos en español de Colombia con tildes.
4. Las pruebas no gastan créditos de ElevenLabs ni escriben en producción. No uses `estilos.py --elegir` para probar (registra la elección en `estilos_estado.json`), no ejecutes `recolector.py --marcar` ni `--voz`, no hagas `git push` a `main`.

## Procedimiento
1. **Entiende la queja.** Identifica qué no gustó: visual del video, ritmo, voz o locución, música, banner, caption, tema elegido o tono. Si la queja es vaga, haz UNA sola pregunta concreta; si no, sigue.
2. **Ubica qué la controla** con esta tabla:

| Qué no gustó | Dónde se cambia |
|---|---|
| Estilo visual del video, gancho, ritmo | `estilos.py` (catálogo y rotación) y `tendencias.md` |
| Banner (diseño, estilos, textos) | `render_banner_html.py` y el paso 8 de `INSTRUCCIONES.md` |
| Idea, guion, locución, humor, estructura | pasos 3 y 4 de `INSTRUCCIONES.md` |
| Efectos, transiciones, sobriedad, escenas | `INSTRUCCIONES.md` (punto 4 y paso 6), `html/jdt.js`, `html/jdt.css` |
| Voz en off | paso 5 de `INSTRUCCIONES.md` y `recolector.py` (rotación de voces) |
| Música y mezcla | `musica.py` |
| Caption y hashtags | paso 8 de `INSTRUCCIONES.md` |
| Temas que elige | `recolector.py` y paso 3 de `INSTRUCCIONES.md` |
| Tono, servicios, identidad | `marca.md` |
| Sistema de notas (umbral, meta, cuántas versiones, qué aprende) | `calidad.py` (constantes `META`, `UMBRAL_BAJO`, `MAX_VERSION`) y el paso 1B de `INSTRUCCIONES.md`. `calificaciones.md` es del revisor: no se toca |

3. **Revisa antes de editar.** Mira el último resultado del agente en `videos/`, `banners/` y `borradores/` para ver el problema real. Haz `git fetch` y compara con la rama de la otra IA (`git diff origin/main..origin/OTRA-RAMA --stat`): si va a tocar el mismo archivo, avisa al dueño antes de editarlo.
4. **Cambio mínimo y a la causa.** Modifica lo menos posible y vuélvelo una REGLA de la configuración (no un parche para un solo caso). Si el dueño dijo «no me gusta X», deja escrito en la configuración que no se haga X, con el motivo.
5. **Prueba sin tocar producción.** Banners: `python3 render_banner_html.py --muestra /tmp/muestra`. Video: genera cuadros de prueba (`render_html.py --fotos`, `render_video.py --hoja`) con una voz local; no llames a ElevenLabs. Mira el resultado antes de entregarlo.
6. **Entrega al dueño**, corto: qué no gustó, qué archivos cambiaste y qué cambió en cada uno, cómo lo vio probado y qué riesgo hay. Sin inventar resultados. Luego espera su respuesta: «aprobado» (se hace el merge) o «ajusta X» (vuelves al paso 4).
7. **Commit en tu rama** con un mensaje que diga qué se ajustó y por qué. Un cambio por commit para que sea fácil deshacerlo.

## Si algo no está claro
- Duda entre dos archivos: elige el que corresponde a la tabla y dilo al dueño.
- La queja contradice una regla de marca (por ejemplo, pide un color fuera de la paleta): no lo hagas, explica por qué y propón la alternativa dentro de la marca.
- Un cambio podría afectar la otra rama: avisa y espera.
