# Tendencias de contenido y estilos visuales (base, actualizada 2026-11-18)

El agente lee este archivo en cada ejecucion (paso 3B). `estilos.py` elige la combinacion del dia a partir de este
catalogo y `tendencias_vivas.md` guarda lo que el agente va aprendiendo de la web. La paleta de JDT no se negocia:
todo lo que sigue se adapta a azul marino, amarillo/dorado, blanco y gris azulado.

## Lo que hoy atrae mas a los clientes (resumen de fuentes de 2026)
1. **Video corto vertical, pensado sin sonido.** Domina el tiempo en redes y casi todo se ve en silencio: el texto en pantalla carga el mensaje desde el segundo 0, con subtitulos legibles y zonas seguras (nada importante en los bordes).
2. **El gancho decide.** Los primeros 2 a 3 segundos ganan o pierden el video. Preguntas incomodas, confesiones, resultado primero, mito vs realidad, POV y listas numeradas son los formatos que mas se repiten.
3. **Tipografia cinetica.** Es la tendencia de motion mas citada: la letra ya no acompana, es la imagen. Ritmo de palabras al compas de la voz.
4. **Liquid glass y 3D estilizado.** Vidrio con refraccion, formas liquidas, letras infladas o cromadas. Se prefiere el 3D estilizado y suave al fotorrealismo.
5. **Hecho a mano frente a la IA.** Collage, recortes, texturas, grano, imperfeccion: el contenido que se ve humano destaca entre tanto generado por IA.
6. **Producto en accion.** En videos de software de 2026 ganaron las pantallas reales usandose (cursor, clics, numeros que cambian) sobre las animaciones abstractas.
7. **Minimalismo audaz, neobrutalismo y editorial.** Color pleno, bordes gruesos con sombra dura, composiciones tipo revista con numeros enormes y anotaciones.
8. **Bucles y marca en movimiento.** Animaciones que se repiten solas, logo animado y un sonido corto de marca al cierre.
9. **Nostalgia (Y2K, 90s, 70s)** en dosis pequeñas: cromo, estrellas, rejilla retrofuturista.

## Como se traduce a JDT (sin salirse de la marca)
- «Color atrevido» = **amarillo pleno** como fondo o como bloque, con tinta azul marino; azul marino profundo con un solo acento amarillo.
- «Cromo/inflado» = degradados **dorado-blanco** con extrusion; vidrio azul con destello dorado.
- «Hecho a mano» = papel blanco o gris azulado, cinta amarilla, notas, puntos de trama.
- Nada de cian, rojo, violeta ni verde: los scripts rechazan los cuadros con colores fuera de la paleta.

## Videos: 12 estilos de moda (los elige `estilos.py`)
tipografia-cinetica · vidrio-liquido · interfaz-en-movimiento · collage-recorte · minimalismo-audaz · dorado-3d ·
neobrutalista · apertura-de-pelicula · bucle-hipnotico · editorial-zine · mascota-con-actitud · datos-que-se-arman.
Cada ejecucion recibe un estilo PRINCIPAL y uno de APOYO (una o dos escenas de contraste), un GANCHO y un RITMO.
`python3 estilos.py --lista` trae la receta de cada uno.

## Banners: 9 estilos de moda (motor `render_banner_html.py`)
vidrio-liquido · tipografia-gigante · bento · amarillo-total · collage-recorte · neobrutal · cromo-dorado · editorial · terminal-ui.
`python3 render_banner_html.py --lista` los describe. Cada banner usa uno distinto a los ultimos 4.

## Reglas para aplicarlas bien
- **Moda con criterio:** el estilo es el vestido de la idea, no la idea. Primero el concepto del tema; luego se viste con el estilo del dia.
- **Sobrio y amable:** una idea por escena. Si hay que elegir entre un efecto mas y aire, gana el aire.
- **Siempre vigente y siempre distinto:** nunca el mismo estilo principal en las ultimas 4 ejecuciones ni el mismo banner en las ultimas 4.
- **Prueba de vigencia** (antes de renderizar): ¿se entiende sin sonido?, ¿el primer cuadro ya muestra la idea?, ¿se ve como algo de 2026 y no como una diapositiva?, ¿el estilo del dia se nota de verdad (no es solo el fondo)?
- **Pulso de la semana:** cada ejecucion hace 2 busquedas web de tendencias y deja UNA nota en `tendencias_vivas.md`. Si una busqueda trae un estilo nuevo que encaja con la paleta, se prueba como apoyo y se anota.

## Fuentes consultadas (2026-11-18)
Resumenes y analisis publicados en 2026 por Adobe Express, Designity, G2, Penji, Renderforest, Garagefarm, Graphic Design Junction, Metricool, ShortGenius, Benchmark Email y ADVIDS (analisis de 100 videos de interfaz, sep 2026). Se usaron como señal de tendencia, no como datos exactos.
