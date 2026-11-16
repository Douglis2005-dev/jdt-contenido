# jdt-contenido (privado)

Agente de contenido de JDT TECHNOLOGICS. Corre en la nube (rutinas de Claude Code) y deja un Reel (MP4 + caption) y un banner (PNG) por ejecución.

- Instrucciones del agente: `INSTRUCCIONES.md`
- Resultados: `videos/`, `banners/`, `borradores/`
- Motor: `render_video.py` (escenas prefabricadas, escena `libre` y `palabras`), `iconos.py` (54 iconos propios), `voz_local.py` (voz en off de respaldo, modelo en `recursos/voz`). Solo se usa la paleta de la marca y el script rechaza escenas libres repetidas.
- Google Drive: el agente sube el MP4 y el PNG a Mi unidad\jdt technologics (Videos y Banners) con el conector. Respaldo manual en el PC: `py sincronizar_drive.py`.
- Fuente: Montserrat (SIL Open Font License, ver `recursos/fuentes/OFL.txt`).
