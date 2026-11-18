# jdt-contenido (privado)

Agente de contenido de JDT TECHNOLOGICS. Corre en la nube (rutinas de Claude Code) y deja un Reel (MP4 + caption) y un banner (PNG) por ejecución.

- Instrucciones del agente: `INSTRUCCIONES.md`
- Resultados: `videos/`, `banners/`, `borradores/`
- Motor: `render_video.py` (escenas prefabricadas, escena `libre` y `palabras`), `iconos.py` (54 iconos propios), `voz_local.py` (voz en off de respaldo, modelo en `recursos/voz`). Solo se usa la paleta de la marca y el script rechaza escenas libres repetidas.
- Google Drive: el agente sube el MP4 y el PNG a Mi unidad\jdt technologics (Videos y Banners) con el conector. Respaldo manual en el PC: `py sincronizar_drive.py`.
- Fuente: Montserrat (SIL Open Font License, ver `recursos/fuentes/OFL.txt`).
- Tendencias (2026-11-18): `tendencias.md` (catálogo de estilos vigentes), `estilos.py` (elige y rota la combinación del día: estilo de video principal y de apoyo, gancho, ritmo y estilo de banner), `tendencias_vivas.md` (hallazgos web de cada ejecución) y `render_banner_html.py` (banners con 9 estilos de moda en la paleta JDT; `render_banner.py` queda de respaldo).
- Notas del revisor y auto-mejora (2026-11-18): el revisor califica cada contenido de 1 a 10 en `calificaciones.md` (tabla `| ID | Nota | Comentario |`). `calidad.py` lee esas notas: lo que saque menos de 7 se rehace como `-v2`/`-v3`, las lecciones quedan en `lecciones.md`, `estilos.py` favorece los estilos mejor calificados y el agente se autocalifica (`calidad_estado.json`) antes de entregar. `python3 calidad.py --pendientes` lista lo que falta calificar.
