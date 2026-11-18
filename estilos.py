"""Selector de ESTILOS DE MODA para el agente de contenido de JDT TECHNOLOGICS.

Cada ejecucion usa una combinacion distinta de: estilo visual del video (principal + de apoyo), gancho de los
primeros 2 segundos, ritmo de montaje y estilo del banner. Todos salen de lo que hoy se usa y funciona en redes
(ver tendencias.md) y se rotan para que NUNCA se repita lo de las ultimas ejecuciones.

Uso (desde la raiz del repositorio):
    python3 estilos.py --elegir                 elige y REGISTRA la combinacion de esta ejecucion (una sola vez por ejecucion)
    python3 estilos.py --lista                  catalogo completo
    python3 estilos.py --ultimos                lo usado en las ultimas ejecuciones
    python3 estilos.py --marcar video=ID banner=ID [apoyo=ID gancho=ID ritmo=ID]   corrige lo registrado si cambiaste una pieza
    python3 estilos.py --nota "hallazgo"        agrega una linea fechada a tendencias_vivas.md (maximo 40 lineas; las viejas se borran)
Las respuestas son JSON. Estado en estilos_estado.json (se guarda en el repositorio, igual que voz_estado.json).
"""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
ESTADO = CARPETA / "estilos_estado.json"
VIVAS = CARPETA / "tendencias_vivas.md"

# --------------------------------------------------------------------------- catalogo de VIDEO
# receta = como se hace con el motor HTML (html/jdt.js, html/jdt.css, canvas, SVG y CSS propios), siempre con la paleta JDT.
VIDEO = {
    "tipografia-cinetica": {
        "nombre": "Tipografia cinetica",
        "por_que": "El texto en movimiento es la tendencia de motion mas citada de 2026: casi todo se ve sin sonido y la letra carga el mensaje.",
        "receta": "Frases de 110 a 180 px que golpean la pantalla palabra por palabra al ritmo EXACTO de la voz (JDT.letras / JDT.revelar con los tiempos de palabras.json). "
                  "Palabra clave en amarillo; una palabra que se estira, se parte o cae; una marquesina de palabras gigantes en sentidos opuestos. Subtitulo legible desde el segundo 0.",
        "pillow": "escenas 'palabras' y 'marquesina'",
    },
    "vidrio-liquido": {
        "nombre": "Vidrio liquido",
        "por_que": "Liquid glass: transparencias, refraccion y formas liquidas dominan interfaces y motion de 2026.",
        "receta": "Paneles .vidrio con backdrop-filter sobre manchas doradas y azules que se mueven lento (JDT.metaballs, JDT.fondo), camara 3D suave (JDT.camara con rx/ry), "
                  "destello dorado que recorre el borde del panel. Un panel = una idea. Mucho aire.",
        "pillow": "look azul con 'camara' empuja y escenas 'panel'",
    },
    "interfaz-en-movimiento": {
        "nombre": "Interfaz en movimiento",
        "por_que": "En videos de software de 2026 ganaron las pantallas de producto en accion sobre los dibujos abstractos: se entiende que es real y util.",
        "receta": "Dibuja en HTML una ventana, un telefono o un tablero genericos (sin marcas) y haz que ALGO SE USE: cursor que se mueve y hace clic, casilla que se marca, tarjeta que se arrastra, "
                  "numero que sube, JDT.tipear para escribir. Zoom (JDT.camara s) a UN detalle por escena. El producto es el protagonista, no un icono.",
        "pillow": "escenas 'telefono', 'web', 'panel' o 'terminal'",
    },
    "collage-recorte": {
        "nombre": "Collage de recortes",
        "por_que": "Mixed media y piezas hechas a mano contrastan con el contenido generado por IA y se ven humanas.",
        "receta": "Tiras de papel claro, cinta, notas adhesivas y puntos de trama sobre fondo azul marino; las piezas se PEGAN con rebote corto (outBack) y rotacion irregular. "
                  "Cuantiza el tiempo (t = Math.floor(t * 10) / 10) para un ritmo de stop motion. Grano suave encima.",
        "pillow": "escenas 'libre' con tarjetas rotadas",
    },
    "minimalismo-audaz": {
        "nombre": "Minimalismo audaz",
        "por_que": "El minimalismo se volvio fuerte y ruidoso: color pleno, una forma, una palabra gigante.",
        "receta": "Pantalla completa AMARILLA (tinta azul marino) o AZUL, un solo elemento enorme y una frase corta, cortes secos, un unico movimiento limpio por escena y quietud total en el momento clave. "
                  "Cero particulas, cero HUD.",
        "pillow": "'look' amarillo/azul con 'titular' y 'contador'",
    },
    "dorado-3d": {
        "nombre": "Dorado en 3D",
        "por_que": "Las letras y objetos con volumen (inflados, cromados, de vidrio) son de lo mas visible de 2026; el retrofuturismo y lo Y2K siguen vivos.",
        "receta": "Titulo con extrusion (text-shadow/drop-shadow apilados) en degradado dorado-blanco que gira lento en 3D, rejilla en perspectiva con camino dorado (JDT.rejilla) y un sol de franjas. "
                  "Objetos redondeados y brillantes (SVG con degradados). Musica con bajo marcado.",
        "pillow": "fondo 'rejilla' con 'camara' giro-lento",
    },
    "neobrutalista": {
        "nombre": "Neobrutalismo",
        "por_que": "Bordes gruesos, sombras duras y pegatinas dan un aire directo y juvenil que destaca en el feed.",
        "receta": "Tarjetas blancas con borde grueso azul marino y sombra dura amarilla que SALTAN a su lugar (outBack), pegatinas circulares que giran, rejilla visible de fondo, "
                  "rotulos en mayusculas con tipografia mono. Ritmo seco, cortes cada 2 s.",
        "pillow": "escenas 'lista', 'comparar' con 'look' amarillo",
    },
    "apertura-de-pelicula": {
        "nombre": "Apertura de pelicula",
        "por_que": "Los openers cinematograficos y titulos de pelicula siguen entre los estilos de motion mas pedidos.",
        "receta": "Barras de cine (letterbox), grano y vineta, JDT.hud con codigo de tiempo, cuenta regresiva, titulo que aparece con barrido de luz y un tono de voz grave. "
                  "Trailer de 'tu proceso antes y despues'. Un solo destello fuerte, en el giro.",
        "pillow": "escenas con 'fx' vineta y grano, 'transicion' destello",
    },
    "bucle-hipnotico": {
        "nombre": "Bucle hipnotico",
        "por_que": "Las animaciones cortas en bucle se repiten solas en el feed y suben el tiempo de vista.",
        "receta": "Una forma geometrica viva (anillos, orbitas, ondas, nodos que se conectan) que evoluciona y cuyo ultimo cuadro CONECTA con el primero; la frase clave se escribe encima. "
                  "El cierre vuelve al arranque para que el video parezca no terminar.",
        "pillow": "fondo 'anillos' o 'ondas' con escena 'conexion'",
    },
    "editorial-zine": {
        "nombre": "Editorial / zine",
        "por_que": "Composiciones libres tipo revista, con numeros grandes y anotaciones, marcan una tendencia de diseno 2026.",
        "receta": "Fondo CLARO (blanco o gris azulado, para variar) con tinta azul marino, composicion asimetrica, numeros enormes, lineas finas y anotaciones que se dibujan a mano "
                  "(SVG con stroke-dashoffset): flechas, circulos y subrayados amarillos que marcan lo importante.",
        "pillow": "escena 'libre' con lineas y flechas",
    },
    "mascota-con-actitud": {
        "nombre": "Personaje con actitud",
        "por_que": "Los personajes expresivos y las mascotas simples humanizan el contenido de marca y se comparten mas.",
        "receta": "Un personaje hecho con los iconos de iconos.py (persona-sorpresa, persona-triste, robot...) o dibujado en SVG, con CONFLICTO y GIRO: se desespera, se multiplica, se cansa, celebra. "
                  "Burbujas de dialogo cortas. Humor colombiano amable.",
        "pillow": "escenas 'libre' con iconos y burbujas",
    },
    "datos-que-se-arman": {
        "nombre": "Datos que se arman",
        "por_que": "Las infografias animadas aclaran ideas complejas en segundos y se ven bien sin sonido.",
        "receta": "Barras, anillos, lineas o piezas que se dibujan y se ordenan hasta formar la respuesta; comparacion de tamanos; un embudo que se llena. "
                  "SOLO datos genericos (24/7, 3 pasos, 1 solo lugar); nunca cifras inventadas.",
        "pillow": "escenas 'contador', 'panel', 'pasos'",
    },
    "creator-autentico": {
        "nombre": "Creador autentico / POV",
        "por_que": "Los Reels con tono cercano, POV y momentos humanos se sienten nativos del feed y ayudan a explicar temas B2B sin voz corporativa distante.",
        "receta": "Abre con una pregunta o POV directo; usa encuadre gráfico cercano, notas adhesivas, subrayados a mano y pequeños movimientos de camara simulada. La locucion suena conversacional. No inventes clientes, empleados, testimonios ni experiencias en primera persona que JDT no haya vivido.",
        "pillow": "escenas 'libre' con burbujas, notas y movimientos suaves",
    },
    "microdocumental-cinematico": {
        "nombre": "Microdocumental cinematografico",
        "por_que": "El storytelling documental y cinematografico sigue siendo una forma relevante de explicar temas B2B con contexto y confianza.",
        "receta": "Cuenta una microhistoria en 4 o 5 planos: detalle, contexto, problema, giro y salida. Usa profundidad, luz lateral azul/dorada, camara lenta y cortes motivados. Un unico momento dramatico; evita trailer exagerado, humo visual y afirmaciones de casos reales.",
        "pillow": "escenas 'libre' con camara empuja/paneo, vineta sutil y un solo destello",
    },
    "pantalla-dividida-dinamica": {
        "nombre": "Pantalla dividida dinamica",
        "por_que": "El contraste en paralelo permite comparar procesos, decisiones o antes/despues de forma inmediata en formato vertical.",
        "receta": "Construye dos zonas asimetricas con divisor claro; cada lado tiene una accion y una etiqueta breve. Sincroniza el cambio de lado con la voz y resuelve la comparacion con un barrido o intercambio de posiciones. No uses comparaciones que impliquen cifras o resultados no demostrados.",
        "pillow": "escenas 'dividida' y 'comparar' con transicion barrido",
    },
    "motion-modular": {
        "nombre": "Motion modular",
        "por_que": "Los sistemas modulares de rotulos, subtitulos, etiquetas y microanimaciones permiten videos social-first variados sin perder consistencia de marca.",
        "receta": "Define un sistema visual para este video: subtitulo, etiqueta de seccion, tarjeta de dato y transicion breve. Recombina esos modulos con jerarquia y posiciones distintas; cada escena cambia de composicion. Animaciones cortas, precisas y sincronizadas con la voz, sin HUD permanente ni plantilla repetida.",
        "pillow": "escenas 'libre', 'titular', 'pasos' y 'notificaciones' con rotulos coherentes",
    },
}

# --------------------------------------------------------------------------- ganchos (primeros 2 segundos)
GANCHOS = {
    "pregunta-incomoda": "Abre con una pregunta que duele o da risa, dicha de frente («¿Cuántas veces copiaste lo mismo hoy?»).",
    "confesion": "Abre con una confesion en primera persona («Despedí a mi mejor empleado: el copiar y pegar»).",
    "error-falso": "Abre con algo que parece un error en pantalla (aviso, ventana trabada, texto cortado) que luego se resuelve.",
    "resultado-primero": "Muestra el final bonito en el primer segundo (el tablero ordenado, el boton unico) y luego cuenta como se llego.",
    "mito-vs-realidad": "Abre con un MITO tachado y la realidad que lo reemplaza.",
    "pov": "Abre con «POV: eres el dueño que…» y una situacion reconocible, en primera persona.",
    "tres-senales": "Abre con «3 señales de que…» y las muestra una por una, cada una con su golpe visual.",
    "antes-despues": "Abre con el caos y corta de golpe al orden (pantalla dividida o barrido).",
    "cuenta-regresiva": "Abre con una cuenta regresiva o un reloj que corre y el problema que se acaba el tiempo.",
    "nadie-te-cuenta": "Abre con «lo que nadie te cuenta de…» y una verdad simple que sorprende.",
    "reto-10-segundos": "Abre con un reto corto («en 10 segundos te muestro…») y cumple con una demostracion rapida.",
    "afirmacion-absurda": "Abre con una afirmacion exagerada que el resto del video justifica con humor («Tu hoja de cálculo tiene vida propia»).",
}

RITMOS = {
    "rapido": "Cortes cada 2 a 3 s, escenas contundentes, la primera de maximo 3 s. Para ganchos fuertes.",
    "mixto": "Alterna escenas activas (2 a 3 s) con una escena quieta de 4 a 5 s para que respire en el giro.",
    "contemplativo": "Planos mas largos (4 a 6 s) con un solo movimiento limpio y una pausa antes del remate.",
}

# banner: la fuente unica de verdad es render_banner_html.ESTILOS
RECIENTES = {"video": 4, "apoyo": 2, "gancho": 5, "banner": 4, "ritmo": 1}


def _banners() -> dict:
    sys.path.insert(0, str(CARPETA))
    import render_banner_html as rb
    return rb.ESTILOS


def _cargar() -> dict:
    if ESTADO.exists():
        try:
            return json.loads(ESTADO.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"historial": []}


def _guardar(e: dict) -> None:
    e["historial"] = e["historial"][-40:]
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")


def _evitar(hist: list, campo: str, n: int) -> set:
    return {h.get(campo) for h in hist[-n:] if h.get(campo)}


def _elegir_de(opciones, evitar: set, rng: random.Random, excluir=()):
    libres = [o for o in opciones if o not in evitar and o not in excluir]
    if not libres:   # si todo esta "reciente", toma el menos reciente que no sea el ultimo
        libres = [o for o in opciones if o not in excluir]
    return rng.choice(libres)


def _notas(n: int = 6) -> list[str]:
    if not VIVAS.exists():
        return []
    lineas = [l.strip() for l in VIVAS.read_text(encoding="utf-8").splitlines() if l.strip().startswith("- ")]
    return lineas[-n:]


def descripcion(estado: dict) -> dict:
    banners = _banners()
    v, a = VIDEO[estado["video"]], VIDEO[estado["apoyo"]]
    return {
        "fecha": estado["fecha"],
        "video": {"id": estado["video"], **v},
        "apoyo": {"id": estado["apoyo"], "nombre": a["nombre"], "receta": a["receta"],
                  "uso": "Una o dos escenas con este segundo estilo para dar contraste; el principal manda en el resto."},
        "gancho": {"id": estado["gancho"], "como": GANCHOS[estado["gancho"]]},
        "ritmo": {"id": estado["ritmo"], "como": RITMOS[estado["ritmo"]]},
        "banner": {"id": estado["banner"], "como": banners[estado["banner"]],
                   "usar": f"En el JSON del banner pon \"estilo\": \"{estado['banner']}\" y renderiza con render_banner_html.py"},
        "notas_recientes_de_tendencias": _notas(),
        "recordatorio": ("Esto es un PUNTO DE PARTIDA de moda, no una plantilla: el tema decide la idea. Si el estilo no encaja de verdad con el tema, cambia UNA pieza "
                         "con `python3 estilos.py --marcar video=ID ...` y explica por que en el borrador. Siempre paleta JDT y sobriedad: una idea por escena."),
    }


def elegir(preferencias=None) -> dict:
    e = _cargar()
    h = e["historial"]
    rng = random.Random(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    preferencias = preferencias or {}
    opciones = {"video": VIDEO, "apoyo": VIDEO, "gancho": GANCHOS, "ritmo": RITMOS, "banner": _banners()}

    def tomar(campo: str, evitar: set, excluir=()):
        elegido = preferencias.get(campo)
        if elegido:
            if elegido not in opciones[campo]:
                raise SystemExit(f"'{campo}={elegido}' no existe. Opciones: {', '.join(opciones[campo])}")
            if elegido in evitar or elegido in excluir:
                raise SystemExit(f"'{campo}={elegido}' se uso recientemente o coincide con otro estilo. Consulta --ultimos y elige otra opcion.")
            return elegido
        return _elegir_de(opciones[campo], evitar, rng, excluir=excluir)

    video = tomar("video", _evitar(h, "video", RECIENTES["video"]) | _evitar(h, "apoyo", 1))
    apoyo = tomar("apoyo", _evitar(h, "apoyo", RECIENTES["apoyo"]), excluir=(video,))
    nuevo = {
        "fecha": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "video": video, "apoyo": apoyo,
        "gancho": tomar("gancho", _evitar(h, "gancho", RECIENTES["gancho"])),
        "ritmo": tomar("ritmo", _evitar(h, "ritmo", RECIENTES["ritmo"])),
        "banner": tomar("banner", _evitar(h, "banner", RECIENTES["banner"])),
    }
    h.append(nuevo)
    _guardar(e)
    return descripcion(nuevo)


def marcar(pares: list[str]) -> dict:
    e = _cargar()
    if not e["historial"]:
        raise SystemExit("Aun no hay seleccion registrada: ejecuta primero --elegir.")
    ultimo = e["historial"][-1]
    validos = {"video": VIDEO, "apoyo": VIDEO, "gancho": GANCHOS, "ritmo": RITMOS, "banner": _banners()}
    for p in pares:
        k, _, v = p.partition("=")
        if k not in validos or v not in validos[k]:
            raise SystemExit(f"'{p}' no es valido. Opciones de {k}: {', '.join(validos.get(k, {}))}")
        ultimo[k] = v
    if ultimo["video"] == ultimo["apoyo"]:
        raise SystemExit("El estilo de apoyo debe ser distinto al principal.")
    _guardar(e)
    return descripcion(ultimo)


def nota(texto: str) -> dict:
    texto = " ".join(texto.split())[:400]
    cab = []
    cuerpo = []
    if VIVAS.exists():
        for l in VIVAS.read_text(encoding="utf-8").splitlines():
            (cuerpo if l.strip().startswith("- ") else cab).append(l)
    cuerpo.append(f"- {datetime.now().strftime('%Y-%m-%d')}: {texto}")
    cuerpo = cuerpo[-40:]
    VIVAS.write_text("\n".join(cab).rstrip() + "\n\n" + "\n".join(cuerpo) + "\n", encoding="utf-8")
    return {"ok": True, "lineas": len(cuerpo)}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        raise SystemExit(__doc__)
    if a[0] == "--elegir":
        preferencias = {}
        for par in a[1:]:
            k, sep, v = par.partition("=")
            if not sep or not k or not v or k in preferencias:
                raise SystemExit(f"Parametro invalido: {par}. Usa campo=ID.")
            if k not in {"video", "apoyo", "gancho", "ritmo", "banner"}:
                raise SystemExit(f"Campo desconocido: {k}.")
            preferencias[k] = v
        out = elegir(preferencias)
    elif a[0] == "--marcar":
        out = marcar(a[1:])
    elif a[0] == "--nota":
        out = nota(" ".join(a[1:]))
    elif a[0] == "--ultimos":
        out = _cargar()["historial"][-6:]
    elif a[0] == "--lista":
        out = {"video": {k: v["nombre"] + ": " + v["por_que"] for k, v in VIDEO.items()}, "ganchos": GANCHOS, "ritmos": RITMOS, "banners": _banners()}
    else:
        raise SystemExit(__doc__)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
