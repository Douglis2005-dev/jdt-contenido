"""Generador de Reels de JDT TECHNOLOGICS (motion graphics por codigo).

Dibuja cada cuadro con Pillow y lo codifica a MP4 vertical 1080x1920 con FFmpeg
(el binario viene con el paquete imageio-ffmpeg). Opcionalmente mezcla una voz
en off y ajusta la duracion de las escenas a la del audio.

Uso:
    py render_video.py guion.json
    py render_video.py guion.json --cuadro 3.5 salida.png   (un solo cuadro, para revisar)
    py render_video.py guion.json --hoja /tmp/hoja.png      (hoja de revision: 2 cuadros por escena,
                                                             a la mitad y al final; ademas guarda cada
                                                             cuadro a tamano real: /tmp/hoja_escena1a.png ...)

guion.json:
{
  "salida": "videos/2026-11-14-tema.mp4",
  "audio": "videos/2026-11-14-tema.mp3",          (opcional)
  "escenas": [
    {"tipo": "titular",  "texto": "¿Tu negocio sigue *copiando y pegando*?", "voz": "...", "duracion": 3},
    {"tipo": "caos",     "texto": "...", "etiquetas": ["Excel", "Correo", "WhatsApp", "Facturas"]},
    {"tipo": "flujo",    "texto": "...", "etiquetas": ["Pedido", "Proceso automático", "Factura"]},
    {"tipo": "panel",    "texto": "...", "etiquetas": ["Ventas", "Pedidos", "Clientes"]},
    {"tipo": "lista",    "texto": "...", "etiquetas": ["...", "...", "..."]},
    {"tipo": "telefono", "texto": "...", "etiquetas": ["Reservas", "Pedidos", "Pagos"]},
    {"tipo": "chat",      "texto": "...", "etiquetas": ["¿Tienen cupo hoy?", "Sí, te agendo ya", "¡Listo, gracias!"]},
    {"tipo": "comparar",  "texto": "...", "etiquetas": ["Antes 1", "Antes 2", "Después 1", "Después 2"]},
    {"tipo": "conexion",  "texto": "...", "centro": "Tu sistema", "etiquetas": ["Ventas", "Bodega", "Contabilidad", "Clientes"]},
    {"tipo": "reloj",     "texto": "...", "etiquetas": ["Copiar datos", "Revisar correos", "Armar reportes"]},
    {"tipo": "web",       "texto": "...", "url": "tunegocio.com", "etiquetas": ["Catálogo", "Pedidos en línea", "Contacto"]},
    {"tipo": "documento", "texto": "...", "etiquetas": ["Cliente", "Fecha", "Total"]},
    {"tipo": "pasos",     "texto": "...", "etiquetas": ["Analizamos", "Desarrollamos", "Entregamos"]},
    {"tipo": "palabras",  "frases": ["Copiar.", "Pegar.", "*Repetir.*", "¿Hasta cuándo?"]},
    {"tipo": "libre",     "texto": "(opcional)", "elementos": [ ... ]},      (ver ESCENA LIBRE abajo)
    {"tipo": "cierre",   "texto": "Hablemos de tu proyecto", "subtexto": "@technologicsjdt"}
  ]
}
VOZ: todo video lleva locucion. Sin "audio" el script se detiene (para pruebas: --sin-audio).
Si la voz se hizo con voz_local.py, el guion trae "sincronia": "exacta" y cada escena dura
justo lo que dura su frase.

PALETA: solo se usan los colores de la marca, por nombre: amarillo, dorado, blanco, gris,
azul (azul marino claro), superficie, borde, fondo. Cualquier otro color da error.

VARIEDAD: el script se detiene si una escena libre repite casi los mismos elementos de otra del
mismo guion o de los 4 guiones anteriores de la carpeta (hay que disenarla distinta).

ESCENA LIBRE ("tipo": "libre"): el guionista arma su propia escena con "elementos" (1 a 14).
Posiciones en porcentaje del lienzo: x de 4 a 96, y de 12 a 90 (con "texto" de titular, de 36 en
adelante). Cada elemento:
  {"el": "icono",   "nombre": "engranaje", "x": 50, "y": 55, "tam": 30, "color": "amarillo"}
  {"el": "texto",   "texto": "Todo en *un solo lugar*", "x": 50, "y": 70, "tam": "l"}   (tam: xl, l, m, s)
  {"el": "forma",   "forma": "circulo|anillo|rect|pildora|triangulo", "x": 50, "y": 50, "ancho": 30, "alto": 30}
  {"el": "linea",   "x": 20, "y": 50, "a": [80, 50], "estilo": "solida|punteada|flecha", "pulso": true}
  {"el": "tarjeta", "texto": "Pedido recibido", "icono": "check", "x": 50, "y": 60}
  {"el": "burbuja", "texto": "¿Ya salió mi pedido?", "x": 40, "y": 45, "cola": "izq|der|ninguna"}
  {"el": "barra",   "x": 50, "y": 60, "ancho": 60, "valor": 80}
Opcionales en cualquier elemento: "color" (de la paleta), "entra" (aparece, sube, baja, izquierda,
derecha, pop, gira, dibuja), "mueve" (flota, late, gira, tiembla, balancea, orbita), "t" y "sale"
(momento de entrada y de salida, como fraccion de la escena: 0 a 1; sin "t" entran en orden),
"a": [x, y] (viaja hasta ese punto), "giro" (grados), "opacidad" (0 a 1).
Iconos: py iconos.py hoja.png los dibuja todos; la lista esta en iconos.NOMBRES.

PRODUCCION NUEVA (para que los videos no se parezcan entre si; ver videos/prueba-produccion.json):
  Escenas nuevas (no llevan "texto" obligatorio; el de terminal y notificaciones es titular opcional):
    {"tipo": "terminal", "texto": "(opcional)", "titulo": "ejemplo@sistema", "lineas": ["> abrir pedido", "pedido abierto", "> enviar factura", "factura enviada"]}
        ventana de comandos que escribe letra por letra (2 a 6 lineas de max 34 caracteres; las ordenes empiezan con "> ").
    {"tipo": "notificaciones", "etiquetas": ["Pedido nuevo", "Pago recibido"], "detalles": ["Mesa 4", "Transferencia"], "iconos": ["campana", "moneda"]}
        tarjetas de notificacion que caen una tras otra, con campana que cuenta (2 a 5; titulos de max 24 caracteres).
    {"tipo": "contador", "valor": "24/7", "unidad": "atencion", "etiqueta": "Sin que *nadie* se desvele"}
        dato gigante dentro de un anillo; si "valor" es un numero cuenta hasta el. Solo datos genericos, nunca cifras inventadas.
    {"tipo": "dividida", "etiquetas": ["Lo de antes", "Lo *nuevo*"], "iconos": ["papeles", "robot"], "rotulos": ["ANTES", "AHORA"]}
        pantalla partida: arriba lo oscuro, abajo entra una mitad amarilla con corte diagonal.
    {"tipo": "marquesina", "palabras": ["COPIAR", "PEGAR", "REPETIR"], "texto": "(opcional)"}
        filas de palabras gigantes que corren en sentidos opuestos (2 a 5 palabras de max 14 caracteres; la ultima sale en amarillo).
  En cualquier escena: "look": "oscuro" | "amarillo" | "azul" (fondo de pantalla completa; vale en libre, palabras,
    terminal, notificaciones, contador y marquesina; en amarillo la tinta es azul marino y las palabras clave van en pastilla),
    "fx": lista de glitch | vibra | destello | pulso | grano | escaneo | vineta (efectos de postproduccion, solo colores de la paleta),
    "transicion": fundido | barrido | desliza-izq | desliza-arriba | zoom | persiana | circulo | destello | glitch | giro,
    "camara": acerca | aleja | empuja | paneo | paneo-der | latido | giro-lento.
  Si una escena no pide transicion ni fx, el script elige unos suaves que cambian de video a video.
  Fondos oscuros de apoyo nuevos: ondas y hexagonos (los elige solo).

ESTILO: cada video sale con un estilo distinto al anterior (fondo, color de
apoyo, entrada del texto, transicion entre escenas, ambiente y variante de cada
escena). Una escena puede pedir "camara": "acerca" o "aleja" (acercamiento lento; usalo en
una o dos escenas como mucho, porque alarga el render). Se elige solo segun el puesto del guion entre los de videos/.
Para forzarlo: "estilo": 7 en el guion (cualquier entero), y "variante": 0|1|2
en una escena.
Las palabras entre *asteriscos* salen en amarillo. "voz" es lo que dice la
locucion durante esa escena: si hay audio, cada escena dura en proporcion al
largo de su "voz" (o de su "duracion" si falta).
"""
from __future__ import annotations

import functools
import json
from collections import Counter
import math
import random
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import iconos

CARPETA = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
FONDO, FONDO_ALT, SUPERFICIE = (10, 14, 39), (13, 18, 48), (19, 26, 58)
AMARILLO, BLANCO, GRIS, GRIS_OSC = (250, 204, 21), (255, 255, 255), (148, 163, 184), (100, 116, 139)
DORADO, AZUL, BORDE = (234, 179, 8), (84, 102, 180), (42, 52, 96)
# Paleta de la marca (marca.md). Son los UNICOS colores de videos y banners: azul marino y sus
# tonos, amarillo/dorado, blanco y gris azulado. Nada de rojo, verde ni otros.
PALETA = {"amarillo": AMARILLO, "dorado": DORADO, "blanco": BLANCO, "gris": GRIS, "azul": AZUL,
          "superficie": SUPERFICIE, "borde": BORDE, "fondo": FONDO}
TIPOS = {"terminal", "notificaciones", "contador", "dividida", "marquesina", "titular", "caos", "flujo", "panel", "lista", "telefono", "chat", "comparar", "conexion",
         "reloj", "web", "documento", "pasos", "palabras", "libre", "cierre"}

# ---------------------------------------------------------------- look de escena
# Cada escena puede tener su propio fondo ("look"): oscuro (el de siempre), amarillo (pantalla completa
# amarilla con tinta azul marino) o azul. LOOK dice con que colores se dibuja lo que NO tiene color propio.
LOOKS_DEF = {
    "oscuro":   {"tinta": BLANCO, "destaca": AMARILLO, "icono": AMARILLO, "marca": AMARILLO, "sobre_marca": FONDO,
                 "linea": GRIS, "punto_off": BORDE, "apoyo": None},
    "amarillo": {"tinta": FONDO, "destaca": BLANCO, "icono": FONDO, "marca": FONDO, "sobre_marca": AMARILLO,
                 "linea": FONDO, "punto_off": DORADO, "apoyo": FONDO},
    "azul":     {"tinta": BLANCO, "destaca": AMARILLO, "icono": AMARILLO, "marca": AMARILLO, "sobre_marca": FONDO,
                 "linea": BLANCO, "punto_off": (62, 78, 150), "apoyo": BLANCO},
}
LOOK = dict(LOOKS_DEF["oscuro"])
LOOK["nombre"] = "oscuro"


def aplicar_look(nombre) -> None:
    nombre = nombre if nombre in LOOKS_DEF else "oscuro"
    LOOK.clear()
    LOOK.update(LOOKS_DEF[nombre])
    LOOK["nombre"] = nombre


def apoyo():
    return LOOK["apoyo"] or ESTILO["acento"]


# ---------------------------------------------------------------- estilo
FONDOS = ["rejilla", "puntos", "diagonales", "anillos", "circuito", "ondas", "hexagonos"]
ACENTOS = [AZUL, GRIS, DORADO, BLANCO]
ENTRADAS = ["sube", "cortina", "pop", "maquina", "izquierda", "resaltador"]
CAMARAS = ["quieta", "acerca", "aleja", "empuja", "paneo", "paneo-der", "latido", "giro-lento"]
TRANSICIONES = ["fundido", "barrido", "desliza-izq", "zoom", "desliza-arriba", "persiana", "circulo", "destello", "glitch", "giro"]
FX_TODOS = {"glitch", "vibra", "destello", "pulso", "grano", "escaneo", "vineta"}
LOOKS = {"oscuro", "amarillo", "azul"}
LOOK_EN = {"libre", "palabras", "contador", "marquesina", "terminal", "notificaciones"}
TIPOS_NUEVOS = {"terminal", "notificaciones", "contador", "dividida", "marquesina"}
ESQUINAS = ["ne-so", "barra", "no-se"]
AMBIENTES = ["particulas", "lineas", "pulsos"]
ESTILO = {"n": 0, "fondo": "rejilla", "acento": ACENTOS[0], "entrada": "sube", "transicion": "fundido",
          "esquinas": "ne-so", "ambiente": "ninguno", "camara": "quieta", "semilla": 0}


def fijar_estilo(n: int, esquinas=None) -> dict:
    """Elige el estilo del video numero n: dos videos seguidos nunca comparten fondo,
    color de apoyo, entrada de texto, transicion ni ambiente."""
    esq = esquinas or ESQUINAS
    ESTILO.update(n=n, fondo=FONDOS[n % len(FONDOS)], acento=ACENTOS[n % 4], entrada=ENTRADAS[(n * 5 + 1) % 6],
                  transicion=TRANSICIONES[(n * 3 + 1) % len(TRANSICIONES)], esquinas=esq[n % len(esq)],
                  ambiente=AMBIENTES[n % 3], camara="quieta", semilla=n * 7919 + 13)
    return ESTILO


def puesto_del_guion(ruta: Path, carpeta: Path) -> int:
    """Cuantos guiones de la carpeta van antes de este (por nombre, que empieza por la fecha)."""
    nombres = sorted(p.stem for p in carpeta.glob("*.json") if not p.stem.startswith(("prueba", "_")))
    return sum(1 for x in nombres if x < ruta.stem)


def variante(esc: dict, cuantas: int) -> int:
    if "variante" in esc:
        return int(esc["variante"]) % cuantas
    return (ESTILO["n"] + esc.get("_i", 0)) % cuantas
FUENTES = Path("C:/Windows/Fonts")


@functools.lru_cache(maxsize=256)
def fuente(tam: int, negrita: bool = True) -> ImageFont.FreeTypeFont:
    propias = sorted((CARPETA / "recursos" / "fuentes").glob("*Bold*.ttf" if negrita else "*Regular*.ttf"))
    for ruta in [*propias, FUENTES / ("segoeuib.ttf" if negrita else "segoeui.ttf"), FUENTES / "arial.ttf"]:
        if Path(ruta).exists():
            return ImageFont.truetype(str(ruta), tam)
    return ImageFont.load_default(tam)


def suave(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def rebote(x: float) -> float:
    x = max(0.0, min(1.0, x))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def sobre(color):
    """Color de texto que se lee encima de `color`: azul marino sobre claros, blanco sobre oscuros."""
    r, g, b = color[:3]
    return FONDO if 0.299 * r + 0.587 * g + 0.114 * b > 125 else BLANCO


def color_de(nombre, por_defecto):
    if nombre is None:
        return por_defecto
    if nombre not in PALETA:
        raise SystemExit(f"El color '{nombre}' no es de la paleta de JDT. Usa uno de: {', '.join(PALETA)}.")
    return PALETA[nombre]


def con_alfa(color, a: float):
    return (*color[:3], int(255 * max(0.0, min(1.0, a))))


# ---------------------------------------------------------------- fondo
def crear_fondo() -> Image.Image:
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(FONDO[i] + (FONDO_ALT[i] - FONDO[i]) * k) for i in range(3)))
    trama, tipo, rng = (16, 22, 54), ESTILO["fondo"], random.Random(ESTILO["semilla"])
    if tipo == "puntos":
        for x in range(45, W, 60):
            for y in range(45, H, 60):
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(20, 28, 66))
    elif tipo == "diagonales":
        for x in range(-H, W, 110):
            d.line([(x, 0), (x + H, H)], fill=trama, width=2)
    elif tipo == "anillos":
        cx, cy = int(W * 0.78), int(H * 0.2)
        for r in range(120, int(H * 1.1), 120):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=trama, width=2)
    elif tipo == "ondas":
        for k in range(14):
            y0 = 120 + k * 135
            pts = [(x, y0 + 38 * math.sin(x / 150 + k * 0.7)) for x in range(0, W + 30, 30)]
            d.line(pts, fill=trama, width=3)
    elif tipo == "hexagonos":
        r = 70
        for fila in range(-1, int(H / (r * 1.5)) + 2):
            for col in range(-1, int(W / (r * 1.74)) + 2):
                cx = col * r * 1.74 + (r * 0.87 if fila % 2 else 0)
                cy = fila * r * 1.5
                d.polygon([(cx + r * math.cos(math.radians(60 * j + 30)), cy + r * math.sin(math.radians(60 * j + 30)))
                           for j in range(6)], outline=trama)
    elif tipo == "circuito":
        for _ in range(26):
            x, y = rng.randrange(0, W, 90), rng.randrange(0, H, 90)
            for _ in range(rng.randint(2, 4)):
                if rng.random() < 0.5:
                    x2, y2 = x + rng.choice([-180, -90, 90, 180]), y
                else:
                    x2, y2 = x, y + rng.choice([-180, -90, 90, 180])
                d.line([(x, y), (x2, y2)], fill=(18, 25, 60), width=3)
                x, y = x2, y2
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(24, 33, 76))
    else:
        for x in range(0, W, 90):
            d.line([(x, 0), (x, H)], fill=trama)
        for y in range(0, H, 90):
            d.line([(0, y), (W, y)], fill=trama)
    esq = ESTILO["esquinas"]
    brillo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = ImageDraw.Draw(brillo)
    ax = -70 if esq == "no-se" else W - 70          # luz amarilla arriba, del lado de las franjas
    bx = W if esq == "no-se" else 0                 # luz de apoyo abajo, al lado contrario
    b.ellipse([ax - 450, -380, ax + 450, 520], fill=(250, 204, 21, 38))
    b.ellipse([bx - 420, H - 620, bx + 420, H + 220], fill=(*ESTILO["acento"], 52))
    brillo = brillo.filter(ImageFilter.GaussianBlur(160))
    img.paste(brillo, (0, 0), brillo)
    d = ImageDraw.Draw(img)
    # franjas diagonales amarillas, como en el logo
    if esq == "no-se":
        d.polygon([(250, 0), (0, 0), (0, 150)], fill=AMARILLO)
        d.polygon([(360, 0), (290, 0), (0, 190), (0, 232)], fill=AMARILLO)
        d.polygon([(W, H - 150), (W, H), (W - 250, H)], fill=AMARILLO)
        d.polygon([(W, H - 232), (W, H - 190), (W - 290, H), (W - 360, H)], fill=AMARILLO)
    elif esq == "barra":
        d.rectangle([0, 0, 16, H], fill=AMARILLO)
        d.polygon([(W - 250, 0), (W, 0), (W, 150)], fill=AMARILLO)
        d.polygon([(W - 360, 0), (W - 290, 0), (W, 190), (W, 232)], fill=AMARILLO)
    else:
        d.polygon([(W - 250, 0), (W, 0), (W, 150)], fill=AMARILLO)
        d.polygon([(W - 360, 0), (W - 290, 0), (W, 190), (W, 232)], fill=AMARILLO)
        d.polygon([(0, H - 150), (0, H), (250, H)], fill=AMARILLO)
        d.polygon([(0, H - 232), (0, H - 190), (290, H), (360, H)], fill=AMARILLO)
    return img


def dibujar_ambiente(img: Image.Image, t: float) -> None:
    """Movimiento sutil del fondo (particulas, lineas de luz o pulsos), distinto segun el estilo."""
    tipo = ESTILO["ambiente"]
    if tipo == "ninguno":
        return
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(ESTILO["semilla"] + 5)
    if tipo == "particulas":
        for i in range(34):
            x, y0, v, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(18, 70), rng.uniform(2, 6)
            y = (y0 - v * t) % H
            x += math.sin(t * 0.8 + i) * 14
            color = AMARILLO if i % 3 == 0 else ESTILO["acento"]
            d.ellipse([x - r, y - r, x + r, y + r], fill=(*color, int(46 + 30 * math.sin(t * 2 + i))))
    elif tipo == "lineas":
        for i in range(7):
            y0, v, largo = rng.uniform(0, H), rng.uniform(140, 320), rng.uniform(160, 380)
            x = (rng.uniform(0, W) + v * t) % (W + 500) - 250
            y = y0 - (x / W) * 240
            color = AMARILLO if i % 2 == 0 else ESTILO["acento"]
            d.line([(x, y), (x + largo, y - largo * 0.22)], fill=(*color, 44), width=3)
    elif tipo == "pulsos":
        cx, cy = (W - 60, H - 220) if ESTILO["esquinas"] != "no-se" else (60, H - 220)
        for i in range(3):
            q = ((t * 0.22) + i / 3) % 1
            r = 120 + q * 900
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*ESTILO["acento"], int(70 * (1 - q))), width=4)


def dibujar_marca(d: ImageDraw.ImageDraw) -> None:
    if ESTILO["esquinas"] == "no-se" or LOOK["nombre"] != "oscuro" and ESTILO["n"] % 2:   # la marca pasa a la derecha
        f = fuente(34)
        ancho = f.getlength("JDT TECHNOLOGICS")
        d.ellipse([W - 80 - ancho - 42, 150, W - 80 - ancho - 18, 174], fill=LOOK["marca"])
        d.text((W - 80, 162), "JDT TECHNOLOGICS", font=f, fill=LOOK["tinta"], anchor="rm")
        return
    d.ellipse([80, 150, 104, 174], fill=LOOK["marca"])
    d.text((122, 162), "JDT TECHNOLOGICS", font=fuente(34), fill=LOOK["tinta"], anchor="lm")


# ---------------------------------------------------------------- texto
def partir(texto: str):
    """Devuelve [(palabra, es_acento)] leyendo *asteriscos*."""
    salida, acento = [], False
    for trozo in re.split(r"(\*)", texto):
        if trozo == "*":
            acento = not acento
            continue
        for n, p in enumerate(trozo.split()):
            pegada = n == 0 and bool(salida) and not trozo[0].isspace() and not any(c.isalnum() for c in p)
            salida.append((p, acento, pegada))
    return salida


def componer(texto: str, ancho: int, tam_max: int, lineas_max: int):
    palabras = partir(texto)
    for tam in range(tam_max, 40, -4):
        f = fuente(tam)
        espacio = f.getlength(" ")
        lineas, actual, x = [], [], 0.0
        for p, ac, pegada in palabras:
            w = f.getlength(p)
            if pegada and actual:
                x -= espacio
            elif actual and x + w > ancho:
                lineas.append(actual)
                actual, x = [], 0.0
            actual.append((p, ac, x, w))
            x += w + espacio
        if actual:
            lineas.append(actual)
        if len(lineas) <= lineas_max and all(l[-1][2] + l[-1][3] <= ancho for l in lineas):
            return f, tam, lineas
    return f, tam, lineas


def dibujar_titular(d, texto: str, t: float, y: int, tam_max: int = 96, lineas_max: int = 4, centro: bool = False,
                    modo: str | None = None):
    modo = modo or ESTILO["entrada"]
    if LOOK["nombre"] == "amarillo":
        modo = "resaltador"      # palabras clave en pastilla azul marino: se leen sobre el amarillo
    f, tam, lineas = componer(texto, W - 160, tam_max, lineas_max)
    alto = int(tam * 1.18)
    asc, desc = f.getmetrics()
    letras = int(max(0.0, t) * 34)       # para "maquina"
    total_letras = sum(len(p) for linea in lineas for p, *_ in linea)
    i = vistas = 0
    for n, linea in enumerate(lineas):
        ancho_linea = linea[-1][2] + linea[-1][3]
        x0 = (W - ancho_linea) / 2 if centro else 80
        yl = y + n * alto
        if modo == "cortina":
            q = max(0.0, min(1.0, (t - 0.16 * n) / 0.6))
            if q <= 0:
                continue
            if q >= 0.5:
                for p, ac, x, _ in linea:
                    d.text((x0 + x, yl), p, font=f, fill=LOOK["destaca"] if ac else LOOK["tinta"])
            if q < 1:
                a, b = (0.0, suave(q * 2)) if q < 0.5 else (suave((q - 0.5) * 2), 1.0)
                d.rectangle([x0 - 8 + ancho_linea * a, yl + tam * 0.1, x0 + 8 + ancho_linea * b, yl + tam * 1.14], fill=LOOK["marca"])
            continue
        for p, ac, x, w in linea:
            color = LOOK["destaca"] if ac else LOOK["tinta"]
            if modo == "maquina":
                resto = letras - vistas
                vistas += len(p)
                if resto <= 0:
                    continue
                trozo = p[:resto]
                d.text((x0 + x, yl), trozo, font=f, fill=color)
                if resto < len(p) and letras < total_letras:
                    cx = x0 + x + f.getlength(trozo) + 6
                    d.rectangle([cx, yl + tam * 0.14, cx + tam * 0.09, yl + tam * 1.06], fill=LOOK["marca"])
                continue
            q = (t - 0.07 * i) / 0.35
            i += 1
            if q <= 0:
                continue
            k = suave(q)
            if modo == "resaltador":      # las palabras clave van sobre una franja amarilla
                if ac:
                    sigue = any(p2 is not p and x2 > x and ac2 for p2, ac2, x2, _ in linea)
                    extra = f.getlength(" ") if sigue else 0
                    d.rounded_rectangle([x0 + x - 12, yl + tam * 0.1, x0 + x - 12 + (w + 24 + extra) * k, yl + tam * 1.16],
                                        radius=10, fill=LOOK["marca"])
                d.text((x0 + x, yl), p, font=f, fill=con_alfa(LOOK["sobre_marca"] if ac else LOOK["tinta"], k if not ac else min(1.0, k * 1.5)))
            elif modo == "pop" and q < 1:
                fp = fuente(max(8, int(tam * (0.45 + 0.55 * rebote(q)))))
                d.text((x0 + x + w / 2, yl + (asc + desc) / 2), p, font=fp, fill=con_alfa(color, k * 1.5), anchor="mm")
            elif modo == "pop":
                d.text((x0 + x + w / 2, yl + (asc + desc) / 2), p, font=f, fill=color, anchor="mm")
            elif modo == "izquierda":
                d.text((x0 + x - (1 - k) * 90, yl), p, font=f, fill=con_alfa(color, k))
            else:
                d.text((x0 + x, yl + (1 - k) * 36), p, font=f, fill=con_alfa(color, k))
    return y + len(lineas) * alto


def ajustar(texto: str, ancho: float, tam: int, minimo: int, negrita: bool = True):
    f = fuente(tam, negrita)
    while f.getlength(texto) > ancho and f.size > minimo:
        f = fuente(f.size - 2, negrita)
    return f


def texto_en_caja(d, texto: str, cx: float, cy: float, ancho: float, tam: int, minimo: int, fill):
    """Centra el texto en (cx, cy); si no cabe en una linea lo parte en dos."""
    f = ajustar(texto, ancho, tam, minimo)
    palabras = texto.split()
    if f.getlength(texto) <= ancho or len(palabras) < 2:
        d.text((cx, cy), texto, font=f, fill=fill, anchor="mm")
        return
    mejor = min(range(1, len(palabras)), key=lambda j: abs(len(" ".join(palabras[:j])) - len(" ".join(palabras[j:]))))
    l1, l2 = " ".join(palabras[:mejor]), " ".join(palabras[mejor:])
    f = ajustar(max(l1, l2, key=len), ancho, tam, minimo)
    d.text((cx, cy - f.size * 0.6), l1, font=f, fill=fill, anchor="mm")
    d.text((cx, cy + f.size * 0.6), l2, font=f, fill=fill, anchor="mm")


def equis(d, cx, cy, r, k, color=BLANCO):
    if k <= 0:
        return
    k, g = min(1.0, k), max(4, int(r * 0.24))
    q = min(1.0, k * 2)
    d.line([(cx - r * 0.42, cy - r * 0.42), (cx - r * 0.42 + r * 0.84 * q, cy - r * 0.42 + r * 0.84 * q)], fill=color, width=g)
    if k > 0.5:
        q = (k - 0.5) * 2
        d.line([(cx + r * 0.42, cy - r * 0.42), (cx + r * 0.42 - r * 0.84 * q, cy - r * 0.42 + r * 0.84 * q)], fill=color, width=g)


def tarjeta(d, caja, radio=28, relleno=SUPERFICIE, borde=BORDE, ancho=3, a=1.0):
    d.rounded_rectangle(caja, radius=radio, fill=con_alfa(relleno, a), outline=con_alfa(borde, a), width=ancho)


def palomita(d, cx, cy, r, k, color=FONDO):
    if k <= 0:
        return
    k = min(1.0, k)
    p1, p2, p3 = (cx - r * 0.5, cy), (cx - r * 0.12, cy + r * 0.38), (cx + r * 0.55, cy - r * 0.4)
    g = max(4, int(r * 0.24))
    if k < 0.5:
        q = k / 0.5
        d.line([p1, (p1[0] + (p2[0] - p1[0]) * q, p1[1] + (p2[1] - p1[1]) * q)], fill=color, width=g)
    else:
        q = (k - 0.5) / 0.5
        d.line([p1, p2], fill=color, width=g)
        d.line([p2, (p2[0] + (p3[0] - p2[0]) * q, p2[1] + (p3[1] - p2[1]) * q)], fill=color, width=g)


def etiquetas_de(esc, por_defecto):
    e = [str(x) for x in esc.get("etiquetas") or []]
    return e or por_defecto


# ---------------------------------------------------------------- escenas
def esc_titular(capa, d, esc, t, dur):
    v = variante(esc, 3)
    if v == 1:      # centrado, con anillos que laten detras
        f, tam, lineas = componer(esc["texto"], W - 160, 116, 5)
        alto = len(lineas) * int(tam * 1.18)
        cy = 900
        for i in range(3):
            q = ((t * 0.45) + i / 3) % 1
            r = 260 + q * 420
            d.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], outline=con_alfa(AMARILLO if i == 0 else ESTILO["acento"], 0.5 * (1 - q)), width=6)
        fin = dibujar_titular(d, esc["texto"], t, cy - alto // 2, tam_max=116, lineas_max=5, centro=True)
        k = suave((t - 0.5) / 0.5)
        d.rounded_rectangle([W / 2 - 150 * k, fin + 50, W / 2 + 150 * k, fin + 64], radius=7, fill=AMARILLO)
        if esc.get("subtexto"):
            d.text((W / 2, fin + 130), esc["subtexto"], font=fuente(48, False), fill=con_alfa(GRIS, suave((t - 0.8) / 0.4)), anchor="mm")
        return
    y = 640
    if v == 2:      # signo gigante de fondo y texto mas abajo
        signo = "?" if "?" in esc["texto"] else "!"
        k = suave(t / 0.7)
        d.text((W - 60 + (1 - k) * 200, 700 + math.sin(t * 1.4) * 18), signo, font=fuente(1100), fill=con_alfa(ESTILO["acento"], 0.22 * k), anchor="rm")
        y = 820
    fin = dibujar_titular(d, esc["texto"], t, y, tam_max=120, lineas_max=5)
    k = suave((t - 0.5) / 0.5)
    d.rounded_rectangle([80, fin + 50, 80 + 300 * k, fin + 64], radius=7, fill=AMARILLO)
    if esc.get("subtexto"):
        a = suave((t - 0.8) / 0.4)
        d.text((80, fin + 120), esc["subtexto"], font=fuente(48, False), fill=con_alfa(GRIS, a))


def _ventana(titulo: str) -> Image.Image:
    img = Image.new("RGBA", (430, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 429, 299], radius=24, fill=SUPERFICIE, outline=BORDE, width=3)
    d.rounded_rectangle([0, 0, 429, 66], radius=24, fill=(28, 37, 80))
    d.rectangle([0, 40, 429, 66], fill=(28, 37, 80))
    for i, c in enumerate([GRIS_OSC, AMARILLO, BLANCO]):
        d.ellipse([22 + i * 30, 24, 40 + i * 30, 42], fill=c)
    d.text((130, 33), titulo[:16], font=fuente(30), fill=BLANCO, anchor="lm")
    for fila in range(4):
        y = 96 + fila * 48
        for col, ancho in enumerate([110, 150, 90]):
            x = 24 + sum([110, 150, 90][:col]) + col * 14
            d.rounded_rectangle([x, y, x + ancho, y + 30], radius=8, fill=(36, 46, 96))
    return img


def esc_caos(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nombres = etiquetas_de(esc, ["Excel", "Correo", "WhatsApp", "Facturas"])[:5]
    cache = esc.setdefault("_v", [_ventana(n) for n in nombres])
    v = variante(esc, 2)
    pos = [(90, 880, -9), (560, 820, 7), (300, 1090, -4), (60, 1300, 6), (590, 1290, -8)] if v == 0 else \
          [(520, 850, 10), (70, 960, -6), (560, 1180, -11), (150, 1330, 5), (330, 1080, 3)]
    for i, img in enumerate(cache):
        x, y, ang = pos[i]
        k = rebote((t - 0.15 * i) / 0.5)
        if t < 0.15 * i:
            continue
        tiembla = math.sin(t * 9 + i * 2.1) * 2.2
        rot = img.rotate(ang + tiembla, resample=Image.BICUBIC, expand=True)
        dx, dy = (0, (1 - k) * 260) if v == 0 else ((1 - k) * (700 if i % 2 == 0 else -700), 0)
        px, py = int(x + dx + math.sin(t * 2 + i) * 10), int(y + dy + math.cos(t * 2.4 + i) * 8)
        hoja = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hoja.paste(rot, (px, py))
        capa.alpha_composite(hoja)
    d2 = ImageDraw.Draw(capa)
    for i, (cx, cy) in enumerate([(500, 900), (980, 1130), (470, 1500), (760, 1570)][: len(cache)]):
        k = rebote((t - 0.9 - 0.2 * i) / 0.35)
        if t < 0.9 + 0.2 * i:
            continue
        r = 44 * k * (1 + 0.06 * math.sin(t * 8 + i))
        d2.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMARILLO)
        d2.text((cx, cy - 2), "!", font=fuente(int(56 * k) or 1), fill=FONDO, anchor="mm")


def esc_flujo(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nombres = etiquetas_de(esc, ["Entrada", "Proceso automático", "Salida"])[:4]
    n = len(nombres)
    alto, hueco = 170, (760 - 170 * n) // max(1, n - 1) if n > 1 else 0
    y0 = 860
    paso = max(0.6, (dur - 1.2) / n)
    for i, nombre in enumerate(nombres):
        y = y0 + i * (alto + hueco)
        k = suave((t - 0.12 * i) / 0.45)
        if k <= 0:
            continue
        activo = t > 0.5 + paso * i
        lado = -1 if variante(esc, 2) == 1 and i % 2 else 1
        x = 120 + (1 - k) * 160 * lado
        tarjeta(d, [x, y, W - 120 + (1 - k) * 160 * lado, y + alto], relleno=(30, 40, 88) if activo else SUPERFICIE,
                borde=AMARILLO if activo else BORDE, ancho=5 if activo else 3, a=k)
        d.ellipse([x + 36, y + 45, x + 116, y + 125], fill=con_alfa(AMARILLO if activo else (36, 46, 96), k))
        if activo:
            palomita(d, x + 76, y + 85, 40, (t - 0.5 - paso * i) / 0.3)
        else:
            d.text((x + 76, y + 83), str(i + 1), font=fuente(44), fill=con_alfa(GRIS, k), anchor="mm")
        f = fuente(54)
        while f.getlength(nombre) > W - 440 and f.size > 30:
            f = fuente(f.size - 4)
        d.text((x + 150, y + 85), nombre, font=f, fill=con_alfa(BLANCO, k), anchor="lm")
        if i < n - 1:
            ya, yb = y + alto + 10, y + alto + hueco - 10
            d.line([(W / 2, ya), (W / 2, yb)], fill=con_alfa(BORDE, k), width=6)
            q = (t - 0.5 - paso * i) / paso
            if 0 < q:
                q = min(1.0, q)
                d.line([(W / 2, ya), (W / 2, ya + (yb - ya) * q)], fill=AMARILLO, width=6)
                if q < 1:
                    cy = ya + (yb - ya) * q
                    d.ellipse([W / 2 - 16, cy - 16, W / 2 + 16, cy + 16], fill=AMARILLO)


def esc_panel(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nombres = etiquetas_de(esc, ["Ventas", "Pedidos", "Clientes"])[:3]
    k = suave(t / 0.5)
    y0 = 850 + (1 - k) * 80
    tarjeta(d, [70, y0, W - 70, y0 + 780], radio=36, a=k)
    ancho = (W - 140 - 40 * 2 - 24 * (len(nombres) - 1)) / len(nombres)
    for i, nombre in enumerate(nombres):
        x = 110 + i * (ancho + 24)
        a = suave((t - 0.25 - 0.1 * i) / 0.4)
        tarjeta(d, [x, y0 + 40, x + ancho, y0 + 220], radio=22, relleno=(28, 37, 80), a=a)
        f = fuente(34)
        while f.getlength(nombre) > ancho - 40 and f.size > 20:
            f = fuente(f.size - 2)
        d.text((x + 22, y0 + 84), nombre, font=f, fill=con_alfa(GRIS, a), anchor="lm")
        d.rounded_rectangle([x + 22, y0 + 136, x + ancho - 22, y0 + 160], radius=12, fill=con_alfa((36, 46, 96), a))
        lleno = suave((t - 0.3 - 0.08 * i) / 0.5) * [0.82, 0.64, 0.9][i]
        if lleno > 0.03:
            d.rounded_rectangle([x + 22, y0 + 136, x + 22 + (ancho - 44) * lleno, y0 + 160], radius=12, fill=AMARILLO)
    alturas = [0.35, 0.5, 0.42, 0.66, 0.78, 0.95]
    base, tope = y0 + 720, 380
    d.line([(120, base), (W - 120, base)], fill=con_alfa(BORDE, k), width=4)
    if variante(esc, 2) == 1:   # linea que se dibuja, en vez de barras
        pts = [(140 + i * (W - 280) / 5, base - 20 - tope * h) for i, h in enumerate(alturas)]
        q = suave((t - 0.3) / max(1.0, dur * 0.45)) * 5
        for i in range(5):
            if q <= i:
                break
            f_ = min(1.0, q - i)
            a_, b_ = pts[i], pts[i + 1]
            d.line([a_, (a_[0] + (b_[0] - a_[0]) * f_, a_[1] + (b_[1] - a_[1]) * f_)], fill=ESTILO["acento"], width=10)
        for i, (px, py) in enumerate(pts):
            if q >= i and t > 0.3:
                r = 16 if i < 5 else 24
                d.ellipse([px - r, py - r, px + r, py + r], fill=AMARILLO if i == 5 else BLANCO)
        return
    bw = (W - 240 - 5 * 30) / 6
    for i, h in enumerate(alturas):
        q = suave((t - 0.3 - 0.07 * i) / 0.45)
        if q <= 0:
            continue
        x = 120 + i * (bw + 30)
        color = AMARILLO if i == len(alturas) - 1 else ESTILO["acento"]
        d.rounded_rectangle([x, base - tope * h * q - 6, x + bw, base - 4], radius=14, fill=color)


def esc_lista(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nombres = etiquetas_de(esc, ["Se adapta a tu proceso", "Pagas solo lo que necesitas", "Evoluciona contigo"])[:4]
    paso = max(0.45, (dur - 1.0) / len(nombres))
    if variante(esc, 2) == 1:
        for i, nombre in enumerate(nombres):
            y = 900 + i * 190
            k = suave((t - 0.25 - paso * 0.6 * i) / 0.45)
            if k <= 0:
                continue
            d.text((80 - (1 - k) * 60, y + 60), f"{i + 1:02d}", font=fuente(92), fill=con_alfa(AMARILLO, k), anchor="lm")
            d.text((240, y + 60), nombre, font=ajustar(nombre, W - 320, 50, 26), fill=con_alfa(BLANCO, k), anchor="lm")
            d.rounded_rectangle([240, y + 118, 240 + (W - 320) * k, y + 124], radius=3, fill=con_alfa(ESTILO["acento"], k))
        return
    for i, nombre in enumerate(nombres):
        y = 880 + i * 190
        k = suave((t - 0.15 * i) / 0.45)
        if k <= 0:
            continue
        x = 80 + (1 - k) * 100
        tarjeta(d, [x, y, W - 80, y + 150], a=k)
        hecho = (t - 0.5 - paso * i) / 0.3
        d.rounded_rectangle([x + 34, y + 39, x + 106, y + 111], radius=18,
                            fill=con_alfa(AMARILLO if hecho > 0 else (36, 46, 96), k))
        palomita(d, x + 70, y + 75, 36, hecho)
        f = fuente(46)
        while f.getlength(nombre) > W - 330 and f.size > 26:
            f = fuente(f.size - 2)
        d.text((x + 140, y + 75), nombre, font=f, fill=con_alfa(BLANCO, k), anchor="lm")


def esc_telefono(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nombres = etiquetas_de(esc, ["Reservas", "Pedidos", "Pagos"])[:4]
    k = suave(t / 0.55)
    x0, y0 = 290, 830 + (1 - k) * 200
    d.rounded_rectangle([x0, y0, x0 + 500, y0 + 860], radius=70, fill=con_alfa((5, 8, 24), k), outline=con_alfa(GRIS_OSC, k), width=6)
    d.rounded_rectangle([x0 + 180, y0 + 26, x0 + 320, y0 + 52], radius=13, fill=con_alfa((30, 38, 80), k))
    d.rounded_rectangle([x0 + 36, y0 + 90, x0 + 464, y0 + 180], radius=22, fill=con_alfa(AMARILLO, k))
    d.text((x0 + 250, y0 + 135), "Tu app", font=fuente(44), fill=con_alfa(FONDO, k), anchor="mm")
    for i, nombre in enumerate(nombres):
        a = suave((t - 0.5 - 0.22 * i) / 0.4)
        if a <= 0:
            continue
        y = y0 + 210 + i * 150 + (1 - a) * 60
        tarjeta(d, [x0 + 36, y, x0 + 464, y + 126], radio=22, a=a)
        d.ellipse([x0 + 58, y + 33, x0 + 118, y + 93], fill=con_alfa(AMARILLO if i == 0 else ESTILO["acento"], a))
        f = fuente(38)
        while f.getlength(nombre) > 300 and f.size > 22:
            f = fuente(f.size - 2)
        d.text((x0 + 140, y + 63), nombre, font=f, fill=con_alfa(BLANCO, a), anchor="lm")


def _logo() -> Image.Image | None:
    ruta = CARPETA / "recursos" / "logo.jpeg"
    if not ruta.exists():
        return None
    img = Image.open(ruta).convert("RGBA").resize((460, 460), Image.LANCZOS)
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, 459, 459], radius=70, fill=255)
    img.putalpha(mascara)
    return img


def esc_cierre(capa, d, esc, t, dur):
    logo = esc.setdefault("_logo", _logo())
    k = rebote(t / 0.6)
    if logo is not None and k > 0.05:
        lado = max(2, int(460 * k))
        capa.alpha_composite(logo.resize((lado, lado), Image.LANCZOS), ((W - lado) // 2, 430 + (460 - lado) // 2))
    d = ImageDraw.Draw(capa)
    if variante(esc, 2) == 1 and t > 0.5:      # puntos que orbitan el logo
        a_ = suave((t - 0.5) / 0.5)
        d.ellipse([W / 2 - 300, 360, W / 2 + 300, 960], outline=con_alfa(BORDE, a_), width=3)
        for i in range(3):
            ang = t * 1.3 + i * 2.094
            px, py = W / 2 + 300 * math.cos(ang), 660 + 300 * math.sin(ang)
            r = 16 if i else 22
            d.ellipse([px - r, py - r, px + r, py + r], fill=con_alfa(AMARILLO if i == 0 else ESTILO["acento"], a_))
    fin = dibujar_titular(d, esc["texto"], t - 0.35, 990, tam_max=104, lineas_max=3, centro=True)
    sub = esc.get("subtexto") or "@technologicsjdt"
    a = rebote((t - 0.9) / 0.45)
    if t > 0.9:
        f = fuente(54)
        ancho = f.getlength(sub) + 110
        alto = 116 * a
        cy = fin + 130
        d.rounded_rectangle([(W - ancho) / 2, cy - alto / 2, (W + ancho) / 2, cy + alto / 2], radius=58, fill=AMARILLO)
        if a > 0.7:
            d.text((W / 2, cy - 2), sub, font=f, fill=FONDO, anchor="mm")
    b = suave((t - 1.3) / 0.5)
    d.text((W / 2, fin + 260), esc.get("pie") or "Te respondemos en menos de 24 horas",
           font=fuente(40, False), fill=con_alfa(GRIS, b), anchor="mm")


def esc_chat(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    msgs = etiquetas_de(esc, ["¿Tienen cupo hoy?", "Sí, te agendo ya", "¡Listo, gracias!"])[:4]
    paso = max(0.55, (dur - 1.2) / len(msgs))
    for i, m in enumerate(msgs):
        t0 = 0.4 + paso * i
        y = 850 + i * 195
        izq = i % 2 == 0
        f = ajustar(m, 700, 46, 28)
        ancho = f.getlength(m) + 90
        x = 80 if izq else W - 80 - ancho
        if t0 - 0.45 < t < t0:      # "escribiendo..."
            bx = 80 if izq else W - 80 - 170
            tarjeta(d, [bx, y + 20, bx + 170, y + 110], radio=45)
            for j in range(3):
                r = 10 + 4 * math.sin(t * 12 + j * 1.2)
                d.ellipse([bx + 50 + j * 35 - r, y + 65 - r, bx + 50 + j * 35 + r, y + 65 + r], fill=GRIS)
        if t < t0:
            continue
        k = rebote((t - t0) / 0.35)
        a = suave((t - t0) / 0.2)
        ultimo = i == len(msgs) - 1
        relleno = AMARILLO if ultimo else (SUPERFICIE if izq else ESTILO["acento"])
        yy = y + (1 - k) * 50
        d.rounded_rectangle([x, yy, x + ancho, yy + 130], radius=44, fill=con_alfa(relleno, a),
                            outline=con_alfa(BORDE if izq and not ultimo else relleno, a), width=3)
        d.text((x + 45, yy + 63), m, font=f, fill=con_alfa(sobre(relleno), a), anchor="lm")


def esc_comparar(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    items = etiquetas_de(esc, ["Copiar y pegar", "Errores a diario", "Todo conectado", "Datos al instante"])[:6]
    mitad = (len(items) + 1) // 2
    grupos = [items[:mitad], items[mitad:]]
    titulos = esc.get("titulos") or ["Antes", "Después"]
    t2 = max(1.1, dur * 0.42)
    alto = 110 + 100 * mitad
    for g, (lista, titulo) in enumerate(zip(grupos, titulos)):
        t0 = 0.15 if g == 0 else t2
        k = suave((t - t0) / 0.45)
        if k <= 0:
            continue
        y = 850 + g * (alto + 50)
        x = 80 + (1 - k) * (-140 if g == 0 else 140)
        despues = g == 1
        apagado = 0.55 if (not despues and t > t2) else 1.0
        tarjeta(d, [x, y, x + W - 160, y + alto], radio=32, borde=AMARILLO if despues else GRIS_OSC, ancho=5 if despues else 3, a=k * apagado)
        d.text((x + 40, y + 55), titulo.upper(), font=fuente(40), fill=con_alfa(AMARILLO if despues else GRIS, k * apagado), anchor="lm")
        for i, it in enumerate(lista):
            yy = y + 110 + i * 100
            q = (t - t0 - 0.3 - 0.25 * i) / 0.3
            d.ellipse([x + 40, yy + 6, x + 104, yy + 70], fill=con_alfa(AMARILLO if despues else GRIS_OSC, k * apagado))
            (palomita if despues else equis)(d, x + 72, yy + 38, 32, q, FONDO if despues else BLANCO)
            d.text((x + 130, yy + 38), it, font=ajustar(it, W - 340, 44, 26), fill=con_alfa(BLANCO, k * apagado), anchor="lm")


def esc_conexion(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nodos = etiquetas_de(esc, ["Ventas", "Bodega", "Contabilidad", "Clientes"])[:5]
    cx, cy, n = W / 2, 1240, len(nodos)
    pos = []
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n + (math.pi / n if n % 2 == 0 else 0)
        pos.append((cx + 330 * math.cos(ang), cy + 360 * math.sin(ang)))
    for i, (px, py) in enumerate(pos):
        q = suave((t - 0.5 - 0.3 * i) / 0.5)
        if q <= 0:
            continue
        d.line([(cx, cy), (cx + (px - cx) * q, cy + (py - cy) * q)], fill=ESTILO["acento"], width=6)
        if q >= 1:
            f_ = (t * 0.7 + i * 0.37) % 1
            if i % 2:
                f_ = 1 - f_
            mx, my = cx + (px - cx) * f_, cy + (py - cy) * f_
            d.ellipse([mx - 13, my - 13, mx + 13, my + 13], fill=AMARILLO)
    for i, ((px, py), nombre) in enumerate(zip(pos, nodos)):
        k = rebote((t - 0.2 - 0.12 * i) / 0.4)
        if t < 0.2 + 0.12 * i:
            continue
        f = ajustar(nombre, 330, 38, 22)
        ancho, alto = (f.getlength(nombre) + 64) * k, 92 * k
        px = max(50 + ancho / 2, min(W - 50 - ancho / 2, px))
        tarjeta(d, [px - ancho / 2, py - alto / 2, px + ancho / 2, py + alto / 2], radio=int(alto / 2))
        if k > 0.8:
            d.text((px, py - 2), nombre, font=f, fill=BLANCO, anchor="mm")
    k = rebote(t / 0.5)
    r = 128 * k * (1 + 0.03 * math.sin(t * 4))
    if r > 4:
        d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], outline=con_alfa(AMARILLO, 0.35), width=4)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMARILLO)
    if k > 0.8:
        texto_en_caja(d, esc.get("centro") or "Tu sistema", cx, cy, 200, 40, 22, FONDO)


def esc_reloj(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    tareas = etiquetas_de(esc, ["Copiar datos", "Revisar correos", "Armar reportes"])[:4]
    cx, cy, k = W / 2, 1130, rebote(t / 0.5)
    r = 250 * k
    if r > 30:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUPERFICIE, outline=BORDE, width=6)
        gasto = min(1.0, max(0.0, (t - 0.4) / max(1.0, dur - 1.0)))
        d.pieslice([cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16], -90, -90 + 360 * gasto, fill=con_alfa(GRIS_OSC, 0.75))
        for i in range(12):
            a = i * math.pi / 6
            d.line([(cx + r * 0.84 * math.sin(a), cy - r * 0.84 * math.cos(a)), (cx + r * 0.93 * math.sin(a), cy - r * 0.93 * math.cos(a))], fill=GRIS, width=6)
        am, ah = -math.pi / 2 + 2 * math.pi * gasto, -math.pi / 2 + t * 9
        d.line([(cx, cy), (cx + r * 0.78 * math.cos(am), cy + r * 0.78 * math.sin(am))], fill=BLANCO, width=12)
        d.line([(cx, cy), (cx + r * 0.5 * math.cos(ah), cy + r * 0.5 * math.sin(ah))], fill=AMARILLO, width=10)
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=AMARILLO)
    for i, tarea in enumerate(tareas):
        a = rebote((t - 0.7 - 0.3 * i) / 0.4)
        if t < 0.7 + 0.3 * i:
            continue
        col, fila = i % 2, i // 2
        solo = len(tareas) % 2 == 1 and i == len(tareas) - 1
        ancho = 450
        x = (W - ancho) / 2 if solo else 70 + col * (ancho + 40)
        y = 1460 + fila * 120 + (1 - a) * 60 + math.sin(t * 3 + i) * 5
        tarjeta(d, [x, y, x + ancho, y + 96], radio=48, borde=GRIS_OSC)
        d.ellipse([x + 26, y + 30, x + 62, y + 66], fill=GRIS)
        d.text((x + 84, y + 46), tarea, font=ajustar(tarea, ancho - 110, 36, 22), fill=BLANCO, anchor="lm")


def esc_web(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    secciones = etiquetas_de(esc, ["Catálogo", "Pedidos en línea", "Contacto"])[:3]
    k = suave(t / 0.5)
    y0 = 840 + (1 - k) * 120
    tarjeta(d, [80, y0, W - 80, y0 + 800], radio=30, a=k)
    d.rounded_rectangle([80, y0, W - 80, y0 + 84], radius=30, fill=con_alfa((28, 37, 80), k))
    d.rectangle([80, y0 + 50, W - 80, y0 + 84], fill=con_alfa((28, 37, 80), k))
    for i, c in enumerate([GRIS_OSC, AMARILLO, BLANCO]):
        d.ellipse([112 + i * 36, y0 + 30, 136 + i * 36, y0 + 54], fill=con_alfa(c, k))
    d.rounded_rectangle([250, y0 + 20, W - 120, y0 + 64], radius=22, fill=con_alfa(FONDO, k))
    url = str(esc.get("url") or "tunegocio.com")
    d.text((276, y0 + 42), url[: max(0, int((t - 0.3) * 22))], font=fuente(30, False), fill=con_alfa(GRIS, k), anchor="lm")
    a = suave((t - 0.8) / 0.4)
    if a > 0.05:
        d.rounded_rectangle([120, y0 + 124, 120 + 560 * a, y0 + 176], radius=12, fill=con_alfa(BLANCO, a))
        d.rounded_rectangle([120, y0 + 200, 120 + 400 * a, y0 + 230], radius=10, fill=con_alfa((60, 72, 130), a))
        pulso = 1 + 0.05 * math.sin(t * 6)
        d.rounded_rectangle([120, y0 + 262, 120 + 290 * pulso * a, y0 + 262 + 76 * a], radius=int(38 * a), fill=con_alfa(AMARILLO, a))
    for i, sec in enumerate(secciones):
        q = suave((t - 1.1 - 0.3 * i) / 0.4)
        if q <= 0:
            continue
        y = y0 + 380 + i * 132 + (1 - q) * 50
        tarjeta(d, [120, y, W - 120, y + 108], radio=22, relleno=(28, 37, 80), a=q)
        d.rounded_rectangle([144, y + 24, 204, y + 84], radius=14, fill=con_alfa(ESTILO["acento"] if i else AMARILLO, q))
        d.text((232, y + 52), sec, font=ajustar(sec, W - 400, 42, 24), fill=con_alfa(BLANCO, q), anchor="lm")


def esc_documento(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    campos = etiquetas_de(esc, ["Cliente", "Fecha", "Total"])[:3]
    k = suave(t / 0.5)
    x0, x1, y0 = 250, W - 250, 830 + (1 - k) * 100
    alto = 440
    d.rounded_rectangle([x0, y0, x1, y0 + alto], radius=20, fill=con_alfa((236, 239, 245), k))
    d.polygon([(x1 - 80, y0 - 2), (x1 + 2, y0 + 80), (x1 + 2, y0 - 2)], fill=con_alfa(FONDO, k))
    d.polygon([(x1 - 80, y0), (x1 - 80, y0 + 80), (x1, y0 + 80)], fill=con_alfa(GRIS, k))
    largo = max(1.2, dur * 0.45)
    barrido = (t - 0.6) / largo
    ys = y0 + alto * max(0.0, min(1.0, barrido))
    for i in range(7):
        ly = y0 + 70 + i * 50
        leida = ly < ys and barrido > 0
        ancho = [0.5, 0.8, 0.7, 0.85, 0.6, 0.78, 0.45][i] * (x1 - x0 - 150)
        d.rounded_rectangle([x0 + 40, ly, x0 + 40 + ancho, ly + 22], radius=10,
                            fill=con_alfa(DORADO if leida and i in (0, 3, 5) else GRIS, k))
    if 0 < barrido < 1:
        d.rectangle([x0 - 30, ys - 40, x1 + 30, ys], fill=con_alfa(AMARILLO, 0.22))
        d.rounded_rectangle([x0 - 30, ys - 5, x1 + 30, ys + 5], radius=5, fill=AMARILLO)
    for i, campo in enumerate(campos):
        t0 = 0.6 + largo * [0.2, 0.55, 0.85][i]
        a = suave((t - t0) / 0.35)
        if a <= 0:
            continue
        y = 1320 + i * 126
        x = 80 + (1 - a) * 80
        tarjeta(d, [x, y, W - 80, y + 106], radio=24, a=a)
        d.rounded_rectangle([x + 26, y + 21, x + 90, y + 85], radius=16, fill=con_alfa(AMARILLO, a))
        palomita(d, x + 58, y + 53, 32, (t - t0 - 0.15) / 0.3)
        d.text((x + 120, y + 51), campo, font=ajustar(campo, W - 320, 44, 26), fill=con_alfa(BLANCO, a), anchor="lm")


def esc_pasos(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    pasos = etiquetas_de(esc, ["Analizamos", "Desarrollamos", "Entregamos"])[:4]
    n = len(pasos)
    xs = [170 + i * (W - 340) / max(1, n - 1) for i in range(n)]
    cy, paso = 1010, max(0.6, (dur - 1.0) / n)
    actual = max(0, min(n - 1, int((t - 0.5) / paso)))
    d.line([(xs[0], cy), (xs[-1], cy)], fill=con_alfa(BORDE, suave(t / 0.4)), width=10)
    avance = max(0.0, min(n - 1.0, (t - 0.5) / paso))
    if avance > 0:
        d.line([(xs[0], cy), (xs[0] + (xs[-1] - xs[0]) * avance / max(1, n - 1), cy)], fill=AMARILLO, width=10)
    for i, x in enumerate(xs):
        k = rebote((t - 0.1 * i) / 0.4)
        if t < 0.1 * i:
            continue
        hecho = i < actual or (i == n - 1 and t > 0.5 + paso * i + min(0.9, paso * 0.6))
        activo = i == actual
        r = (88 + (8 * math.sin(t * 6) if activo and not hecho else 0)) * k
        if r < 6:
            continue
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=AMARILLO if (hecho or activo) else SUPERFICIE,
                  outline=AMARILLO if (hecho or activo) else BORDE, width=5)
        if hecho:
            palomita(d, x, cy, 46, 1.0)
        elif k > 0.7:
            d.text((x, cy - 3), str(i + 1), font=fuente(64), fill=FONDO if activo else GRIS, anchor="mm")
    nombre = pasos[actual]
    local = (t - 0.5) - paso * actual if t > 0.5 else t
    a = suave(local / 0.3)
    y = 1240 + (1 - a) * 40
    tarjeta(d, [100, y, W - 100, y + 300], radio=36, borde=AMARILLO, ancho=4, a=a)
    d.text((W / 2, y + 80), f"PASO {actual + 1} DE {n}", font=fuente(38), fill=con_alfa(AMARILLO, a), anchor="mm")
    texto_en_caja(d, nombre, W / 2, y + 190, W - 300, 74, 36, con_alfa(BLANCO, a))


# ---------------------------------------------------------------- palabras y escena libre
TAM_TEXTO = {"xl": 132, "l": 96, "m": 64, "s": 44}
ELEMENTOS = {"icono", "texto", "forma", "linea", "tarjeta", "burbuja", "barra"}
FORMAS = {"circulo", "anillo", "rect", "pildora", "triangulo"}
ENTRA = {"aparece", "sube", "baja", "izquierda", "derecha", "pop", "gira", "dibuja"}
MUEVE = {"flota", "late", "gira", "tiembla", "balancea", "orbita"}


def sprite_texto(texto: str, ancho: float, tam_max: int, lineas_max: int = 3, color=None, acento=None, pildora=False) -> Image.Image:
    """Bloque de texto centrado como imagen suelta (para moverlo, escalarlo o girarlo)."""
    f, tam, lineas = componer(texto, int(ancho), tam_max, lineas_max)
    alto = int(tam * 1.18)
    w = int(max(l[-1][2] + l[-1][3] for l in lineas)) + 8
    img = Image.new("RGBA", (w, alto * len(lineas) + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = color or LOOK["tinta"]
    acento = acento or (LOOK["destaca"] if color == LOOK["tinta"] else (BLANCO if color == AMARILLO else AMARILLO))
    for n, linea in enumerate(lineas):
        x0 = (w - (linea[-1][2] + linea[-1][3])) / 2
        for p, ac, x, wp in linea:
            if ac and (pildora or LOOK["nombre"] == "amarillo"):
                d.rounded_rectangle([x0 + x - 6, n * alto + tam * 0.08, x0 + x + wp + 6, n * alto + tam * 1.12], radius=12, fill=FONDO)
                d.text((x0 + x, n * alto), p, font=f, fill=AMARILLO)
            else:
                d.text((x0 + x, n * alto), p, font=f, fill=acento if ac else color)
    return img


def pegar(capa, sprite, cx, cy, escala=1.0, giro=0.0, alfa=1.0) -> None:
    """Pega una imagen centrada en (cx, cy) con escala, giro y transparencia; recorta lo que se salga."""
    if alfa <= 0.01 or escala <= 0.03:
        return
    if abs(escala - 1) > 0.01:
        sprite = sprite.resize((max(1, int(sprite.width * escala)), max(1, int(sprite.height * escala))), Image.BILINEAR)
    if abs(giro) > 0.3:
        sprite = sprite.rotate(giro, resample=Image.BICUBIC, expand=True)
    if alfa < 0.99:
        sprite = sprite.copy()
        sprite.putalpha(sprite.getchannel("A").point(lambda v: int(v * alfa)))
    x, y = int(cx - sprite.width / 2), int(cy - sprite.height / 2)
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + sprite.width), min(H, y + sprite.height)
    if x1 > x0 and y1 > y0:
        capa.alpha_composite(sprite.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def esc_palabras(capa, d, esc, t, dur):
    """Tipografia cinetica: frases cortas que golpean la pantalla una por una."""
    frases = [str(x) for x in esc.get("frases") or []] or [str(esc.get("texto", ""))]
    pesos = [max(7, len(f)) for f in frases]
    pesos[-1] = pesos[-1] * 1.5        # la ultima se queda un poco mas
    total, ini, idx, lt = sum(pesos), 0.0, len(frases) - 1, 0.0
    for j, peso in enumerate(pesos):
        tramo = dur * peso / total
        if t < ini + tramo or j == len(pesos) - 1:
            idx, lt = j, t - ini
            break
        ini += tramo
    cache = esc.setdefault("_f", {})
    if idx not in cache:
        cache[idx] = sprite_texto(frases[idx], W - 160, 190, 3)
    modo = (ESTILO["n"] + esc.get("_i", 0) + idx) % 3
    q = lt / 0.2
    k = suave(q)
    escala, dy = 1.0, 0.0
    if modo == 0:
        escala = 1 + 0.6 * (1 - k)                 # llega grande y se asienta
    elif modo == 1:
        escala = rebote(q) if q < 1 else 1.0       # salta desde el centro
    else:
        dy = (1 - k) * 170                         # sube desde abajo
    cy = 930
    ancho = cache[idx].width * k
    d.rounded_rectangle([W / 2 - ancho / 2, cy + cache[idx].height / 2 + 34, W / 2 + ancho / 2, cy + cache[idx].height / 2 + 48],
                        radius=7, fill=LOOK["marca"] if idx == len(frases) - 1 else apoyo())
    pegar(capa, cache[idx], W / 2, cy + dy, escala, 0, min(1.0, q * 2.5))
    n = len(frases)
    for j in range(n):
        r = 10 if j == idx else 6
        px = W / 2 - (n - 1) * 24 + j * 48
        d.ellipse([px - r, 1580 - r, px + r, 1580 + r], fill=LOOK["marca"] if j <= idx else LOOK["punto_off"])


def _sprite(el: dict) -> Image.Image:
    if "_s" in el:
        return el["_s"]
    tipo = el["el"]
    if tipo == "icono":
        s = iconos.icono(el["nombre"], int(float(el.get("tam", 22)) / 100 * W), color_de(el.get("color"), LOOK["icono"]))
    elif tipo == "texto":
        s = sprite_texto(str(el["texto"]), float(el.get("ancho", 84)) / 100 * W, TAM_TEXTO[el.get("tam", "m")], 3,
                         color_de(el.get("color"), LOOK["tinta"]))
    elif tipo == "forma":
        w = max(8, int(float(el.get("ancho", 20)) / 100 * W))
        h = max(8, int(float(el.get("alto", el.get("ancho", 20))) / 100 * W))
        forma, c, g = el.get("forma", "circulo"), (*color_de(el.get("color"), LOOK["icono"]), 255), int(el.get("grosor", 8)) * 2
        img = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
        dd = ImageDraw.Draw(img)
        kw = {"fill": c} if el.get("relleno", forma != "anillo") else {"outline": c, "width": g}
        caja = [0, 0, w * 2 - 1, h * 2 - 1]
        if forma in ("circulo", "anillo"):
            dd.ellipse(caja, **kw)
        elif forma == "triangulo":
            dd.polygon([(w, 0), (w * 2 - 1, h * 2 - 1), (0, h * 2 - 1)], **kw)
        else:
            dd.rounded_rectangle(caja, radius=min(w, h) if forma == "pildora" else int(min(w, h) * 0.24), **kw)
        s = img.resize((w, h), Image.LANCZOS)
    elif tipo == "tarjeta":
        texto, col = str(el.get("texto", "")), color_de(el.get("color"), SUPERFICIE)
        tinta, ic, alto, pad = sobre(col), el.get("icono"), 124, 38
        ancho_max = float(el.get("ancho", 84)) / 100 * W
        f = ajustar(texto, ancho_max - pad * 2 - (88 if ic else 0), 46, 26)
        w = int(min(ancho_max, f.getlength(texto) + pad * 2 + (88 if ic else 0)))
        s = Image.new("RGBA", (w, alto), (0, 0, 0, 0))
        dd = ImageDraw.Draw(s)
        dd.rounded_rectangle([0, 0, w - 1, alto - 1], radius=32, fill=(*col, 255),
                             outline=(*(BORDE if tinta == BLANCO else col), 255), width=3)
        x = pad
        if ic:
            s.alpha_composite(iconos.icono(ic, 72, AMARILLO if tinta == BLANCO else FONDO), (pad - 8, (alto - 72) // 2))
            x = pad + 80
        ImageDraw.Draw(s).text((x, alto / 2 - 2), texto, font=f, fill=tinta, anchor="lm")
    elif tipo == "burbuja":
        col = color_de(el.get("color"), BLANCO)
        tinta = sobre(col)
        txt = sprite_texto(str(el["texto"]), float(el.get("ancho", 62)) / 100 * W - 84, 46, 3, tinta,
                           acento=AMARILLO if tinta == BLANCO else tinta)
        w, h, cola = txt.width + 84, txt.height + 52, el.get("cola", "izq")
        s = Image.new("RGBA", (w, h + 44), (0, 0, 0, 0))
        dd = ImageDraw.Draw(s)
        if cola != "ninguna":
            bx, sentido = (72, -1) if cola == "izq" else (w - 72, 1)
            dd.polygon([(bx - 28, h - 8), (bx + 28, h - 8), (bx + sentido * 40, h + 40)], fill=(*col, 255))
        dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=44, fill=(*col, 255),
                             outline=(*(BORDE if tinta == BLANCO else col), 255), width=3)
        s.alpha_composite(txt, (42, 24))
    else:
        raise SystemExit(f"Elemento '{tipo}' no tiene imagen propia.")
    el["_s"] = s
    return s


def _linea(d, el, k, alfa, t, i):
    x0, y0, x1, y1 = el["x"] / 100 * W, el["y"] / 100 * H, el["a"][0] / 100 * W, el["a"][1] / 100 * H
    c, g = con_alfa(color_de(el.get("color"), LOOK["linea"]), alfa), int(el.get("grosor", 8))
    estilo = el.get("estilo", "solida")
    xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    if estilo == "punteada":
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 36))
        for j in range(n + 1):
            if j / n > k:
                break
            px, py = x0 + (x1 - x0) * j / n, y0 + (y1 - y0) * j / n
            d.ellipse([px - g * 0.7, py - g * 0.7, px + g * 0.7, py + g * 0.7], fill=c)
    else:
        d.line([(x0, y0), (xe, ye)], fill=c, width=g)
        d.ellipse([x0 - g / 2, y0 - g / 2, x0 + g / 2, y0 + g / 2], fill=c)
        if estilo != "flecha":
            d.ellipse([xe - g / 2, ye - g / 2, xe + g / 2, ye + g / 2], fill=c)
    if estilo == "flecha" and k > 0.12:
        ang, lado = math.atan2(y1 - y0, x1 - x0), g * 3.4
        ux, uy = math.cos(ang), math.sin(ang)
        d.polygon([(xe + ux * lado * 0.7, ye + uy * lado * 0.7), (xe - ux * lado * 0.4 - uy * lado * 0.7, ye - uy * lado * 0.4 + ux * lado * 0.7),
                   (xe - ux * lado * 0.4 + uy * lado * 0.7, ye - uy * lado * 0.4 - ux * lado * 0.7)], fill=c)
    if el.get("pulso") and k >= 1:      # un punto viaja por la linea, como un dato que pasa
        q = (t * 0.8 + i * 0.3) % 1
        px, py, r = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q, g * 1.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=con_alfa(LOOK["marca"] if LOOK["nombre"] != "oscuro" else AMARILLO, alfa))


def _elemento(capa, d, el, i, n, t, dur):
    paso = min(0.5, dur * 0.55 / max(1, n))
    t0 = float(el["t"]) * dur if "t" in el else 0.15 + i * paso
    if t < t0:
        return
    alfa = float(el.get("opacidad", 1))
    if "sale" in el:
        fin = float(el["sale"]) * dur
        if t > fin + 0.3:
            return
        if t > fin:
            alfa *= 1 - (t - fin) / 0.3
    lt = t - t0
    q = lt / 0.45
    k = suave(q)
    tipo = el["el"]
    x, y = el["x"] / 100 * W, el["y"] / 100 * H
    if tipo == "linea":
        _linea(d, el, suave(lt / 0.6), alfa, t, i)
        return
    if tipo == "barra":
        w, h = float(el.get("ancho", 60)) / 100 * W, max(10, int(float(el.get("alto", 3.4)) / 100 * W))
        v = max(0.0, min(100.0, float(el.get("valor", 80)))) / 100
        d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=h // 2, fill=con_alfa((36, 46, 96), alfa * k))
        lleno = w * v * suave((lt - 0.2) / 0.9)
        if lleno > h:
            d.rounded_rectangle([x - w / 2, y - h / 2, x - w / 2 + lleno, y + h / 2], radius=h // 2,
                                fill=con_alfa(color_de(el.get("color"), LOOK["icono"]), alfa))
        return
    entra = el.get("entra") or ("pop" if tipo == "icono" else "sube")
    escala, giro = 1.0, float(el.get("giro", 0))
    if entra == "sube":
        y += (1 - k) * 90
        alfa *= k
    elif entra == "baja":
        y -= (1 - k) * 90
        alfa *= k
    elif entra == "izquierda":
        x -= (1 - k) * 170
        alfa *= k
    elif entra == "derecha":
        x += (1 - k) * 170
        alfa *= k
    elif entra == "pop":
        escala = rebote(q) if q < 1 else 1.0
        alfa *= min(1.0, q * 3)
    elif entra == "gira":
        escala, giro = max(0.05, k), giro + (1 - k) * 140
        alfa *= k
    else:
        alfa *= k
    if "a" in el:       # viaja de (x, y) al punto "a" a mitad de la escena
        v = suave((lt - 0.5) / max(0.4, dur * 0.3))
        x += (el["a"][0] - el["x"]) / 100 * W * v
        y += (el["a"][1] - el["y"]) / 100 * H * v
    mueve, fase = el.get("mueve"), i * 1.3
    if mueve == "flota":
        y += math.sin(t * 2.2 + fase) * 14
    elif mueve == "late":
        escala *= 1 + 0.06 * math.sin(t * 5 + fase)
    elif mueve == "gira":
        giro -= t * 70
    elif mueve == "tiembla":
        giro += math.sin(t * 22 + fase) * 3
        x += math.sin(t * 31 + fase) * 4
    elif mueve == "balancea":
        giro += math.sin(t * 2.4 + fase) * 9
    elif mueve == "orbita":
        x += math.cos(t * 1.8 + fase) * 26
        y += math.sin(t * 1.8 + fase) * 26
    pegar(capa, _sprite(el), x, y, escala, giro, alfa)


def esc_libre(capa, d, esc, t, dur):
    """Escena que arma el guionista con iconos, textos, formas, lineas, tarjetas y burbujas."""
    if str(esc.get("texto", "")).strip():
        dibujar_titular(d, esc["texto"], t, 300)
    els = esc.get("elementos") or []
    for i, el in enumerate(els):
        _elemento(capa, d, el, i, len(els), t, dur)


def _validar_libre(i: int, e: dict) -> None:
    els = e.get("elementos") or []
    if not 1 <= len(els) <= 14:
        raise SystemExit(f"Escena {i} (libre): 'elementos' debe tener de 1 a 14 elementos.")
    titulo = bool(str(e.get("texto", "")).strip())
    for j, el in enumerate(els, 1):
        donde = f"Escena {i}, elemento {j}"
        tipo = el.get("el")
        if tipo not in ELEMENTOS:
            raise SystemExit(f"{donde}: 'el' debe ser uno de {sorted(ELEMENTOS)}.")
        puntos = [(el.get("x"), el.get("y"))] + ([tuple(el["a"])] if isinstance(el.get("a"), (list, tuple)) and len(el["a"]) == 2 else [])
        if "a" in el and len(puntos) < 2:
            raise SystemExit(f"{donde}: 'a' debe ser [x, y].")
        if tipo == "linea" and len(puntos) < 2:
            raise SystemExit(f"{donde}: la linea necesita 'a': [x, y] (donde termina).")
        for px, py in puntos:
            if not isinstance(px, (int, float)) or not isinstance(py, (int, float)):
                raise SystemExit(f"{donde}: faltan 'x' e 'y' (porcentaje del lienzo, de 0 a 100).")
            if not 4 <= px <= 96 or not 12 <= py <= 90:
                raise SystemExit(f"{donde}: fuera de la zona segura (x de 4 a 96, y de 12 a 90).")
            if titulo and py < 36:
                raise SystemExit(f"{donde}: con 'texto' de titular los elementos van de y=36 hacia abajo (o quita el 'texto').")
        color_de(el.get("color"), BLANCO)
        if tipo == "icono" and el.get("nombre") not in iconos.ICONOS:
            raise SystemExit(f"{donde}: el icono '{el.get('nombre')}' no existe. Disponibles: {', '.join(iconos.NOMBRES)}.")
        if tipo == "tarjeta" and el.get("icono") and el["icono"] not in iconos.ICONOS:
            raise SystemExit(f"{donde}: el icono '{el['icono']}' no existe. Disponibles: {', '.join(iconos.NOMBRES)}.")
        if tipo in ("texto", "burbuja", "tarjeta"):
            largo, tope = len(str(el.get("texto", "")).strip()), {"texto": 60, "burbuja": 70, "tarjeta": 28}[tipo]
            if not 1 <= largo <= tope:
                raise SystemExit(f"{donde}: el 'texto' de {tipo} debe tener de 1 a {tope} caracteres.")
        if tipo == "texto" and el.get("tam", "m") not in TAM_TEXTO:
            raise SystemExit(f"{donde}: 'tam' del texto debe ser uno de {list(TAM_TEXTO)}.")
        if tipo == "icono" and not 6 <= float(el.get("tam", 22)) <= 70:
            raise SystemExit(f"{donde}: 'tam' del icono va de 6 a 70 (porcentaje del ancho).")
        if tipo == "forma" and el.get("forma", "circulo") not in FORMAS:
            raise SystemExit(f"{donde}: 'forma' debe ser una de {sorted(FORMAS)}.")
        if el.get("entra") and el["entra"] not in ENTRA:
            raise SystemExit(f"{donde}: 'entra' debe ser uno de {sorted(ENTRA)}.")
        if el.get("mueve") and el["mueve"] not in MUEVE:
            raise SystemExit(f"{donde}: 'mueve' debe ser uno de {sorted(MUEVE)}.")
        for clave in ("t", "sale"):
            if clave in el and not 0 <= float(el[clave]) <= 1:
                raise SystemExit(f"{donde}: '{clave}' es una fraccion de la escena, entre 0 y 1.")
        if tipo in ("linea", "barra"):
            continue
        sp = _sprite(el)
        for px, py in puntos:
            cx, cy = px / 100 * W, py / 100 * H
            if cx - sp.width / 2 < 24 or cx + sp.width / 2 > W - 24:
                raise SystemExit(f"{donde} ({tipo}): se sale por los lados; acercalo al centro (x=50) o hazlo mas pequeno.")
            if cy - sp.height / 2 < 210 or cy + sp.height / 2 > H - 70:
                raise SystemExit(f"{donde} ({tipo}): se sale por arriba o por abajo; muevelo (y) o hazlo mas pequeno.")


# ---------------------------------------------------------------- escenas de produccion nueva
def _ic(nombre, tam, color):
    return iconos.icono(nombre if nombre in iconos.ICONOS else "chispa", tam, color)


def esc_terminal(capa, d, esc, t, dur):
    """Ventana de terminal que escribe comandos y respuestas letra por letra."""
    lineas = [str(x) for x in esc.get("lineas") or ["> crear pedido", "pedido creado"]]
    con_titular = bool(str(esc.get("texto", "")).strip())
    alto = max(760, 200 + len(lineas) * 140)
    y_top = max(640 if con_titular else 360, int(1000 - alto / 2))
    if con_titular:
        dibujar_titular(d, esc["texto"], t, 300)
    x0, x1, y1 = 60, W - 60, y_top + alto
    d.rounded_rectangle([x0 + 10, y_top + 14, x1 + 10, y1 + 14], radius=34, fill=(4, 6, 20, 150))
    d.rounded_rectangle([x0, y_top, x1, y1], radius=34, fill=(6, 9, 28, 255), outline=(*BORDE, 255), width=4)
    d.rounded_rectangle([x0, y_top, x1, y_top + 84], radius=34, fill=(19, 26, 58, 255))
    d.rectangle([x0, y_top + 50, x1, y_top + 84], fill=(19, 26, 58, 255))
    for j, c in enumerate((AMARILLO, GRIS, BLANCO)):
        d.ellipse([x0 + 40 + j * 46, y_top + 30, x0 + 64 + j * 46, y_top + 54], fill=c)
    d.text((W / 2, y_top + 42), str(esc.get("titulo", "jdt@servidor")), font=fuente(30, False), fill=GRIS, anchor="mm")
    total = sum(len(l) for l in lineas)
    escritos = int(max(0.0, t - 0.35) * total / max(1.0, dur * 0.72))
    f, vistos, y = fuente(50), 0, y_top + 150
    ult_salida = max([i for i, l in enumerate(lineas) if not l.startswith(">")] or [-1])
    cursor = None
    for i, l in enumerate(lineas):
        resto = escritos - vistos
        vistos += len(l)
        if resto <= 0:
            break
        trozo = l[:resto]
        orden = l.startswith(">")
        x = x0 + 44
        if orden:
            d.text((x, y), ">", font=f, fill=AMARILLO)
            x += f.getlength("> ")
            trozo = trozo[1:].lstrip()
            col = BLANCO
        else:
            col = AMARILLO if i == ult_salida else GRIS
        d.text((x, y), trozo, font=f, fill=col)
        cursor = (x + f.getlength(trozo) + 8, y)
        y += 140
    if cursor and (int(t * 2.6) % 2 == 0 or escritos < total):
        d.rectangle([cursor[0], cursor[1] + 4, cursor[0] + 28, cursor[1] + 66], fill=AMARILLO)


def esc_notificaciones(capa, d, esc, t, dur):
    """Notificaciones de celular que caen una tras otra, con una campana que cuenta."""
    items = [str(x) for x in esc.get("etiquetas") or ["Pedido nuevo", "Pago recibido", "Factura enviada"]][:5]
    detalles = [str(x) for x in esc.get("detalles") or []]
    ics = esc.get("iconos") or ["campana", "moneda", "correo", "check", "calendario"]
    alto, sep = 190, 34
    con_titular = bool(str(esc.get("texto", "")).strip())
    y_top = max(720 if con_titular else 440, int(1000 - len(items) * (alto + sep) / 2))
    if con_titular:
        dibujar_titular(d, esc["texto"], t, 300)
    paso = min(0.7, dur * 0.62 / max(1, len(items)))
    visibles = 0
    for i, titulo in enumerate(items):
        t0 = 0.3 + i * paso
        if t < t0:
            continue
        visibles += 1
        q = (t - t0) / 0.5
        k = rebote(q) if q < 1 else 1.0
        y = y_top + i * (alto + sep) - (1 - min(1.0, q)) * 340
        w = W - 140
        x0 = 70
        d.rounded_rectangle([x0, y, x0 + w, y + alto], radius=40, fill=(*SUPERFICIE, int(255 * min(1.0, q * 3))),
                            outline=(*BORDE, 255), width=3)
        d.rounded_rectangle([x0 + 30, y + 37, x0 + 146, y + 153], radius=30, fill=AMARILLO)
        pegar(capa, _ic(ics[i % len(ics)], 84, FONDO), x0 + 88, y + 95)
        d.text((x0 + 180, y + 72), titulo, font=ajustar(titulo, w - 400, 44, 28), fill=BLANCO, anchor="lm")
        det = detalles[i] if i < len(detalles) else ("Hace un momento" if i == 0 else "Ahora")
        d.text((x0 + 180, y + 128), det, font=fuente(32, False), fill=GRIS, anchor="lm")
        d.text((x0 + w - 34, y + 46), "ahora", font=fuente(28, False), fill=GRIS_OSC, anchor="rm")
    cx, cy = W - 150, y_top - 90
    giro = math.sin(t * 16) * 12 if visibles and (t % 0.9) < 0.35 else 0
    pegar(capa, _ic("campana", 120, LOOK["icono"] if LOOK["nombre"] != "oscuro" else BLANCO), cx, cy, 1.0, giro)
    if visibles:
        r = 30
        d.ellipse([cx + 10 - r, cy - 52 - r, cx + 10 + r, cy - 52 + r], fill=AMARILLO if LOOK["nombre"] == "oscuro" else FONDO)
        d.text((cx + 10, cy - 52), str(visibles), font=fuente(36), fill=FONDO if LOOK["nombre"] == "oscuro" else AMARILLO, anchor="mm")


def esc_contador(capa, d, esc, t, dur):
    """Un numero (o dato corto) gigante que se llena, con un anillo de progreso."""
    valor = str(esc.get("valor", "3")).strip()
    rotulo = str(esc.get("etiqueta") or esc.get("texto") or "").strip()
    solo_num = valor.isdigit() and len(valor) <= 4
    q = suave(max(0.0, t - 0.25) / max(0.8, dur * 0.5))
    cx, cy, R = W / 2, 860, 400
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(*LOOK["punto_off"], 255), width=16)
    if q > 0:
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * q, fill=LOOK["marca"], width=16)
    shown = str(int(int(valor) * q)) if solo_num else valor
    f = ajustar(valor, 620, 330, 110)
    esc_k = 1.0 if solo_num else (rebote((t - 0.25) / 0.5) if t - 0.25 < 0.5 else 1.0)
    if t >= 0.25 or solo_num:
        if esc_k > 0.05:
            sp = Image.new("RGBA", (int(f.getlength(valor)) + 60, 460), (0, 0, 0, 0))
            ImageDraw.Draw(sp).text((sp.width / 2, 230), shown, font=f, fill=LOOK["destaca"] if LOOK["nombre"] == "oscuro" else LOOK["tinta"], anchor="mm")
            pegar(capa, sp, cx, cy, max(0.05, esc_k), 0, min(1.0, (t - 0.1) * 4))
    unidad = str(esc.get("unidad", "")).strip()
    if unidad:
        d.text((cx, cy + 190), unidad, font=fuente(54), fill=LOOK["tinta"], anchor="mm")
    if rotulo:
        sp = sprite_texto(rotulo, W - 200, 74, 3)
        pegar(capa, sp, cx, 1380, 1.0, 0, min(1.0, max(0.0, (t - 0.5) * 3)))


def esc_dividida(capa, d, esc, t, dur):
    """Pantalla partida: arriba lo de antes (oscuro), abajo lo nuevo (amarillo) que entra con un corte diagonal."""
    etq = [str(x) for x in esc.get("etiquetas") or ["Antes", "Despues"]]
    rot = [str(x) for x in esc.get("rotulos") or ["ANTES", "AHORA"]]
    ics = esc.get("iconos") or ["papeles", "robot"]
    q = suave((t - dur * 0.34) / 0.45)
    ys = H - (H - 1010) * q
    mov = math.sin(t * 2.2) * 6
    # mitad de arriba (antes)
    d.rectangle([0, 0, W, 1100], fill=(*FONDO, 255))
    cy = 560
    pegar(capa, _ic(ics[0], 330, GRIS), W / 2, cy - 20 + mov, 1.0, 0, min(1.0, t * 3))
    d.rounded_rectangle([W / 2 - 110, 250, W / 2 + 110, 316], radius=33, fill=(*BORDE, 255))
    d.text((W / 2, 283), rot[0], font=fuente(34), fill=GRIS, anchor="mm")
    sp = sprite_texto(etq[0], W - 200, 78, 2, GRIS, BLANCO)
    pegar(capa, sp, W / 2, 800, 1.0, 0, min(1.0, t * 3))
    # mitad de abajo (despues)
    if q > 0:
        d.polygon([(0, ys + 90), (W, ys - 90), (W, H), (0, H)], fill=(*AMARILLO, 255))
        d.polygon([(0, ys + 90), (W, ys - 90), (W, ys - 70), (0, ys + 110)], fill=(*DORADO, 255))
        ky = suave((q - 0.3) / 0.7)
        pegar(capa, _ic(ics[1] if len(ics) > 1 else "robot", 330, FONDO), W / 2, 1390 + (1 - ky) * 60 - mov, 1.0, 0, ky)
        d.rounded_rectangle([W / 2 - 110, ys + 130, W / 2 + 110, ys + 196], radius=33, fill=(*FONDO, 255))
        d.text((W / 2, ys + 163), rot[1], font=fuente(34), fill=AMARILLO, anchor="mm")
        sp = sprite_texto(etq[1], W - 200, 78, 2, FONDO, BLANCO, pildora=True)
        pegar(capa, sp, W / 2, 1740 - (1 - ky) * 30, 1.0, 0, ky)


def esc_marquesina(capa, d, esc, t, dur):
    """Filas de palabras gigantes que corren en sentidos opuestos, como un letrero en movimiento."""
    pal = [str(x).upper() for x in esc.get("palabras") or ["COPIAR", "PEGAR", "REPETIR"]][:5]
    n = len(pal)
    cache = esc.setdefault("_m", {})
    fila_h = 300 if n <= 4 else 250
    y0 = 960 - (n * fila_h) / 2 + fila_h / 2
    for i, palabra in enumerate(pal):
        ult = i == n - 1
        if i not in cache:
            f = fuente(210 if n <= 4 else 170)
            unidad = palabra + "   *   "
            uw = int(f.getlength(unidad))
            veces = int(W * 2.4 / uw) + 3
            tira = Image.new("RGBA", (uw * veces, int(fila_h)), (0, 0, 0, 0))
            col = (LOOK["marca"] if LOOK["nombre"] != "oscuro" else AMARILLO) if ult else (LOOK["tinta"] if i % 2 == 0 else apoyo())
            dd = ImageDraw.Draw(tira)
            for v in range(veces):
                dd.text((v * uw, fila_h / 2), palabra, font=f, fill=col, anchor="lm")
                dd.text((v * uw + f.getlength(palabra + "  "), fila_h / 2), "*", font=f, fill=(*col[:3], 120), anchor="lm")
            cache[i] = (tira, uw)
        tira, uw = cache[i]
        sentido = 1 if i % 2 == 0 else -1
        vel = 150 + 70 * i
        off = (t * vel) % uw
        cx = (tira.width / 2 - uw + off) if sentido > 0 else (tira.width / 2 - 2 * uw - off + uw)
        k = suave((t - 0.12 * i) / 0.4)
        pegar(capa, tira, cx, y0 + i * fila_h + (1 - k) * 80 * sentido, 1.0, 0, k)
    texto = str(esc.get("texto", "")).strip()
    if texto:
        sp = sprite_texto(texto, W - 200, 70, 2)
        pegar(capa, sp, W / 2, 1640, 1.0, 0, min(1.0, max(0.0, (t - 0.6) * 3)))


# ---------------------------------------------------------------- efectos y transiciones
_VINETA = {}


def _vineta():
    if "m" not in _VINETA:
        import numpy as np
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VINETA["m"] = (1 - 0.5 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype("float32")
    return _VINETA["m"]


def aplicar_fx(img: Image.Image, fx: list, local: float, t: float, trans_k: float) -> Image.Image:
    """Efectos de postproduccion sobre el cuadro final. Solo usan colores de la paleta (sin separacion de canales)."""
    import numpy as np
    n = int(t * FPS)
    rng = random.Random(n * 7919 + 17)
    a = np.asarray(img).copy()
    glitch = 0.0
    if "glitch" in fx:
        glitch = max(1 - local / 0.4, 0.0) + (0.55 if rng.random() < 0.07 else 0.0)
    glitch = max(glitch, trans_k)
    if glitch > 0.02:
        for _ in range(4 + int(12 * min(1.0, glitch))):
            y = rng.randrange(0, H - 30)
            h = rng.randrange(14, 70 + int(120 * glitch))
            dx = int(rng.choice((-1, 1)) * rng.uniform(30, 40 + 150 * min(1.0, glitch)))
            a[y:y + h] = np.roll(a[y:y + h], dx, axis=1)
    if "vibra" in fx:
        amp = 5 + 12 * max(0.0, 1 - local / 0.5)
        a = np.roll(a, (rng.randint(-int(amp), int(amp)), rng.randint(-int(amp), int(amp))), axis=(0, 1))
    if "grano" in fx:
        ruido = np.random.default_rng(n).normal(0, 9, (H // 4, W // 4)).astype("float32")
        ruido = np.repeat(np.repeat(ruido, 4, 0), 4, 1)[..., None]
        a = np.clip(a.astype("float32") + ruido, 0, 255).astype("uint8")
    if "escaneo" in fx:
        a[::4] = (a[::4].astype("float32") * 0.84).astype("uint8")
    if "vineta" in fx:
        a = (a.astype("float32") * _vineta()).astype("uint8")
    if "destello" in fx and local < 0.3:
        al = (1 - local / 0.3) ** 1.5 * 0.85
        a = (a.astype("float32") * (1 - al) + 255 * al).astype("uint8")
    return Image.fromarray(a)


ESCENAS = {"terminal": esc_terminal, "notificaciones": esc_notificaciones, "contador": esc_contador,
           "dividida": esc_dividida, "marquesina": esc_marquesina, "titular": esc_titular, "caos": esc_caos, "flujo": esc_flujo, "panel": esc_panel,
           "lista": esc_lista, "telefono": esc_telefono, "chat": esc_chat, "comparar": esc_comparar,
           "conexion": esc_conexion, "reloj": esc_reloj, "web": esc_web, "documento": esc_documento,
           "pasos": esc_pasos, "palabras": esc_palabras, "libre": esc_libre, "cierre": esc_cierre}


# ---------------------------------------------------------------- render
def duracion_audio(ruta: Path) -> float:
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(ruta)], capture_output=True, text=True, errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        raise SystemExit(f"No pude leer la duracion del audio: {ruta}")
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def validar(guion: dict) -> None:
    escenas = guion.get("escenas") or []
    if not 2 <= len(escenas) <= 8:
        raise SystemExit("El guion debe tener entre 2 y 8 escenas.")
    for i, e in enumerate(escenas, 1):
        tipo = e.get("tipo")
        if tipo not in TIPOS:
            raise SystemExit(f"Escena {i}: tipo '{tipo}' no existe. Tipos: {sorted(TIPOS)}")
        texto = str(e.get("texto", "")).strip()
        if not texto and tipo not in ("libre", "palabras", *TIPOS_NUEVOS):
            raise SystemExit(f"Escena {i}: falta 'texto'.")
        if texto and len(partir(texto)) > 12:
            raise SystemExit(f"Escena {i}: el texto en pantalla tiene mas de 12 palabras; acortalo.")
        if e.get("camara") and e["camara"] not in CAMARAS:
            raise SystemExit(f"Escena {i}: 'camara' debe ser una de {CAMARAS}.")
        if e.get("look") and (e["look"] not in LOOKS or (e["look"] != "oscuro" and tipo not in LOOK_EN)):
            raise SystemExit(f"Escena {i}: 'look' debe ser uno de {sorted(LOOKS)} y solo vale en escenas {sorted(LOOK_EN)}.")
        if e.get("transicion") and e["transicion"] not in TRANSICIONES:
            raise SystemExit(f"Escena {i}: 'transicion' debe ser una de {TRANSICIONES}.")
        if e.get("fx") is not None and (not isinstance(e["fx"], list) or any(x not in FX_TODOS for x in e["fx"])):
            raise SystemExit(f"Escena {i}: 'fx' es una lista con elementos de {sorted(FX_TODOS)}.")
        if tipo == "terminal":
            ls = e.get("lineas") or []
            if not 2 <= len(ls) <= 6 or any(len(str(x)) > 34 for x in ls):
                raise SystemExit(f"Escena {i} (terminal): 'lineas' son de 2 a 6 lineas de maximo 34 caracteres (las ordenes empiezan con '> ').")
        if tipo == "notificaciones":
            et = e.get("etiquetas") or []
            if not 2 <= len(et) <= 5 or any(len(str(x)) > 24 for x in et):
                raise SystemExit(f"Escena {i} (notificaciones): 'etiquetas' son de 2 a 5 titulos de maximo 24 caracteres.")
            for ic in e.get("iconos") or []:
                if ic not in iconos.ICONOS:
                    raise SystemExit(f"Escena {i}: el icono '{ic}' no existe.")
        if tipo == "contador":
            v = str(e.get("valor", "")).strip()
            if not v or len(v) > 8:
                raise SystemExit(f"Escena {i} (contador): 'valor' es un dato corto (maximo 8 caracteres), por ejemplo \"3\", \"24/7\" o \"1 solo\".")
        if tipo == "dividida":
            et = e.get("etiquetas") or []
            if len(et) != 2 or any(len(str(x)) > 40 for x in et):
                raise SystemExit(f"Escena {i} (dividida): 'etiquetas' son exactamente 2 textos (arriba = antes, abajo = ahora) de maximo 40 caracteres.")
            for ic in e.get("iconos") or []:
                if ic not in iconos.ICONOS:
                    raise SystemExit(f"Escena {i}: el icono '{ic}' no existe.")
        if tipo == "marquesina":
            pl = e.get("palabras") or []
            if not 2 <= len(pl) <= 5 or any(len(str(x)) > 14 for x in pl):
                raise SystemExit(f"Escena {i} (marquesina): 'palabras' son de 2 a 5 palabras de maximo 14 caracteres.")
        if tipo in TIPOS_NUEVOS:
            aplicar_look(e.get("look"))
        if tipo == "palabras":
            frases = e.get("frases") or []
            if not 2 <= len(frases) <= 6:
                raise SystemExit(f"Escena {i} (palabras): 'frases' debe tener de 2 a 6 frases cortas.")
            for fr in frases:
                if len(str(fr).split()) > 5 or len(str(fr)) > 30:
                    raise SystemExit(f"Escena {i} (palabras): la frase '{fr}' es larga; maximo 5 palabras y 30 caracteres.")
        if tipo == "libre":
            aplicar_look(e.get("look"))
            _validar_libre(i, e)
            aplicar_look("oscuro")
    if escenas[-1]["tipo"] != "cierre":
        raise SystemExit("La ultima escena debe ser de tipo 'cierre'.")


def _firma(esc: dict) -> list[str]:
    """Que elementos tiene una escena libre, sin posiciones ni textos: delata las composiciones copiadas."""
    firma = []
    for el in esc.get("elementos") or []:
        tipo = el.get("el")
        if tipo == "icono":
            firma.append("icono:" + str(el.get("nombre", "")).split("-")[0])
        elif tipo == "forma":
            firma.append("forma:" + str(el.get("forma", "circulo")))
        else:
            firma.append(str(tipo))
    return firma


def _parecido(a: list[str], b: list[str]) -> float:
    ca, cb = Counter(a), Counter(b)
    union = sum((ca | cb).values())
    return sum((ca & cb).values()) / union if union else 0.0


def revisar_repeticion(guion: dict, ruta: Path) -> None:
    """Pedido del dueno: los videos no pueden parecerse entre si. Compara el guion con los 4 anteriores
    de la misma carpeta y consigo mismo, y se detiene si una escena libre repite la composicion de otra."""
    if ruta.stem.startswith(("prueba", "_")) or isinstance(guion.get("estilo"), int):
        return
    escenas = guion["escenas"]
    libres = [(i, _firma(e)) for i, e in enumerate(escenas, 1) if e.get("tipo") == "libre"]
    for n, (i, fa) in enumerate(libres):
        for k, fb in libres[n + 1:]:
            if len(fa) >= 3 and _parecido(fa, fb) >= 0.7:
                raise SystemExit(f"Las escenas {i} y {k} (libres) usan casi los mismos elementos. Dale a cada una su propia "
                                 "composicion: otros iconos, otra disposicion.")
    novedosas = sum(1 for e in escenas if e.get("tipo") in TIPOS_NUEVOS or e.get("look", "oscuro") != "oscuro" or e.get("fx")
                    or e.get("transicion") or e.get("camara"))
    if novedosas < 4:
        raise SystemExit("Este video se ve igual a los anteriores: usa la produccion nueva en al menos 4 escenas (escenas terminal, "
                         "notificaciones, contador, dividida o marquesina; 'look' amarillo o azul; 'fx'; 'transicion'; 'camara'). "
                         "Mira el encabezado de render_video.py y videos/prueba-produccion.json.")
    looks = {e.get("look", "oscuro") for e in escenas}
    if looks == {"oscuro"}:
        raise SystemExit("Ninguna escena cambia de fondo: pon 'look': 'amarillo' o 'azul' en al menos una (libre, palabras, "
                         "contador, marquesina, terminal o notificaciones).")
    tipos = [e.get("tipo") for e in escenas]
    previos = sorted(p for p in ruta.parent.glob("*.json") if p.stem < ruta.stem and not p.stem.startswith(("prueba", "_")))[-4:]
    for p in previos:
        try:
            viejas = json.loads(p.read_text(encoding="utf-8")).get("escenas") or []
        except (OSError, ValueError):
            continue
        if len(libres) < 2 and [e.get("tipo") for e in viejas] == tipos:
            raise SystemExit(f"La secuencia de escenas {tipos} es la misma de {p.name}. Arma este video distinto: "
                             "otros tipos de escena u otro orden.")
        for i, fa in libres:
            if len(fa) < 3:
                continue
            for j, v in enumerate(viejas, 1):
                if v.get("tipo") == "libre" and _parecido(fa, _firma(v)) >= 0.55:
                    raise SystemExit(f"Escena {i} (libre): repite casi la misma composicion de la escena {j} de {p.name} "
                                     f"(elementos: {', '.join(sorted(set(fa)))}). Disenala de nuevo para ESTE tema: otra "
                                     "metafora visual, otros iconos y otra disposicion.")


def repartir(guion: dict, audio: Path | None) -> list[float]:
    escenas = guion["escenas"]
    durs = [float(e.get("duracion") or 3) for e in escenas]
    if audio and guion.get("sincronia") == "exacta" and all(e.get("duracion") for e in escenas):
        return durs        # voz_local.py ya midio cuanto dura la frase de cada escena
    if audio:
        total = duracion_audio(audio) + 1.0
        pesos = [len(e["voz"]) for e in escenas] if all(e.get("voz") for e in escenas) else durs
        durs = [total * p / sum(pesos) for p in pesos]
        falta = 2.4 - durs[-1]
        if falta > 0:  # el cierre necesita tiempo para leerse
            durs[-1] += falta
    return [max(2.6, x) for x in durs]


_FONDOS_LOOK = {}


def fondo_look(nombre: str) -> Image.Image:
    """Fondo de pantalla completa para las escenas con look amarillo o azul (con la marca, sin las franjas)."""
    if nombre in _FONDOS_LOOK:
        return _FONDOS_LOOK[nombre]
    img = Image.new("RGB", (W, H), AMARILLO if nombre == "amarillo" else AZUL)
    d = ImageDraw.Draw(img, "RGBA")
    if nombre == "amarillo":
        for x in range(-H, W, 120):
            d.line([(x, 0), (x + H, H)], fill=(*DORADO, 120), width=4)
        d.ellipse([W - 520, -300, W + 380, 600], fill=(*DORADO, 70))
        d.ellipse([-380, H - 700, 420, H + 100], fill=(*DORADO, 60))
    else:
        for y in range(H):
            k = y / H
            d.line([(0, y), (W, y)], fill=(int(AZUL[0] + (FONDO[0] - AZUL[0]) * k * 0.9), int(AZUL[1] + (FONDO[1] - AZUL[1]) * k * 0.9),
                                           int(AZUL[2] + (FONDO[2] - AZUL[2]) * k * 0.9)))
        for r in range(160, 1700, 170):
            d.ellipse([W * 0.2 - r, H * 0.28 - r, W * 0.2 + r, H * 0.28 + r], outline=(255, 255, 255, 26), width=3)
    _FONDOS_LOOK[nombre] = img
    return img


def _auto_escena(esc: dict, idx: int, ultima: bool) -> tuple:
    """Transicion y efectos de la escena: los que pide el guion o, si no pide, unos suaves que cambian de video a video."""
    n = ESTILO["n"]
    trans = esc.get("transicion") or TRANSICIONES[(n * 3 + idx * 2 + 1) % len(TRANSICIONES)]
    if "fx" in esc:
        fx = [x for x in esc["fx"] if x in FX_TODOS]
    else:
        fx = [[], ["grano"], ["vineta"], ["pulso"], ["escaneo"], ["vineta", "grano"]][(n + idx * 3) % 6]
    return trans, fx


def cuadro(guion, durs, fondo, t: float) -> Image.Image:
    inicio = 0.0
    for idx, (esc, dur) in enumerate(zip(guion["escenas"], durs)):
        if t < inicio + dur or esc is guion["escenas"][-1]:
            break
        inicio += dur
    local = t - inicio
    esc["_i"] = idx
    look = esc.get("look", "oscuro") if esc["tipo"] in LOOK_EN else "oscuro"
    aplicar_look(look)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ESCENAS[esc["tipo"]](capa, d, esc, local, dur)
    ultima = esc is guion["escenas"][-1]
    trans, fx = _auto_escena(esc, idx, ultima)
    sale = 1.0 if ultima else suave((dur - local) / 0.3)       # 1 = escena completa, 0 = ya salio
    entra = 1.0 if idx == 0 else suave(local / 0.3)
    dx = dy = 0
    giro_cam = 0.0
    camara, z = esc.get("camara") or ESTILO["camara"], 1.0
    avance = min(1.0, local / dur)
    if camara == "acerca":          # la camara se acerca muy despacio durante la escena
        z = 1 + 0.05 * avance
    elif camara == "aleja":
        z = 1.05 - 0.05 * avance
    elif camara == "empuja":        # empujon fuerte hacia el centro
        z = 1 + 0.2 * suave(avance)
    elif camara == "paneo":
        dx = int(70 - 140 * avance)
    elif camara == "paneo-der":
        dx = int(-70 + 140 * avance)
    elif camara == "latido":
        z = 1 + 0.035 * (abs(math.sin(math.pi * local / 0.5)) ** 6)
    elif camara == "giro-lento":
        giro_cam = -2.5 + 5 * avance
        z = 1.06
    if "pulso" in fx:
        z *= 1 + 0.028 * (abs(math.sin(math.pi * local / 0.52)) ** 8)
    trans_k = 0.0
    if sale < 1 and trans in ("fundido", "desliza-izq", "desliza-arriba", "zoom", "giro", "destello", "glitch"):
        capa.putalpha(capa.getchannel("A").point(lambda v: int(v * (sale if trans != "glitch" else 1.0 if sale > 0.5 else sale * 2))))
        if trans == "desliza-izq":
            dx = -int((1 - sale) * W * 0.45)
        elif trans == "desliza-arriba":
            dy = -int((1 - sale) * 320)
        elif trans == "zoom":
            z *= 1 + 0.28 * (1 - sale)
        elif trans == "giro":
            giro_cam += (1 - sale) * 14
            z *= 1 + 0.2 * (1 - sale)
    elif entra < 1 and trans == "desliza-izq":
        dx = int((1 - entra) * W * 0.3)
    elif entra < 1 and trans == "desliza-arriba":
        dy = int((1 - entra) * 220)
    elif entra < 1 and trans == "giro":
        giro_cam += -(1 - entra) * 10
    if trans == "glitch":
        trans_k = max(1 - sale, 1 - entra) * 1.4
    if abs(z - 1) > 0.001:          # zoom con precision de subpixel, para que no tiemble
        capa = capa.transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H * 0.5 * (1 - 1 / z)),
                              resample=Image.BILINEAR)
    if abs(giro_cam) > 0.05:
        capa = capa.rotate(giro_cam, resample=Image.BILINEAR, center=(W / 2, H / 2))
    img = (fondo if look == "oscuro" else fondo_look(look)).copy()
    if look == "oscuro":
        dibujar_ambiente(img, t)
    img.paste(capa, (dx, dy), capa)
    dibujar_marca(ImageDraw.Draw(img))
    cobertura = AMARILLO if look != "amarillo" else FONDO
    if trans in ("barrido", "persiana", "circulo", "destello") and (sale < 1 or entra < 1):
        dd = ImageDraw.Draw(img)
        if trans == "barrido":      # una cortina cruza la pantalla entre escenas
            if sale < 1:
                dd.rectangle([0, 0, W * (1 - sale), H], fill=cobertura)
            else:
                dd.rectangle([W * entra, 0, W, H], fill=cobertura)
        elif trans == "persiana":   # franjas horizontales que cierran y abren
            k = (1 - sale) if sale < 1 else (1 - entra)
            n_b = 9
            alto = H / n_b
            for b in range(n_b):
                kb = max(0.0, min(1.0, k * 1.6 - (b / n_b) * 0.6))
                if kb > 0:
                    dd.rectangle([0, b * alto, W, b * alto + alto * kb + 1], fill=cobertura)
        elif trans == "circulo":    # un circulo amarillo cierra la escena y se abre en la siguiente
            R = math.hypot(W, H) / 2 + 20
            mask = Image.new("L", (W, H), 0)
            md = ImageDraw.Draw(mask)
            if sale < 1:
                r = R * (1 - sale)
                md.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
            else:
                r = R * (1 - entra)
                md.rectangle([0, 0, W, H], fill=255)
                md.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=0)
            img.paste(Image.new("RGB", (W, H), cobertura), (0, 0), mask)
        elif trans == "destello":   # flash blanco
            k = (1 - sale) if sale < 1 else (1 - entra)
            img = Image.blend(img, Image.new("RGB", (W, H), BLANCO), min(0.95, k * 1.2))
    # barra de progreso
    total = sum(durs)
    ImageDraw.Draw(img).rectangle([0, H - 10, W * min(1, t / total), H], fill=LOOK["marca"] if look != "oscuro" else AMARILLO)
    if fx or trans_k:
        img = aplicar_fx(img, fx, local, t, trans_k)
    return img


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ruta_guion = Path(sys.argv[1]).resolve()
    guion = json.loads(ruta_guion.read_text(encoding="utf-8"))
    validar(guion)
    revisar_repeticion(guion, ruta_guion)
    base = ruta_guion.parent

    def resolver(p):
        p = Path(p)
        return p if p.is_absolute() else (CARPETA / p if (CARPETA / p).parent.exists() else base / p)

    sin_audio = "--sin-audio" in sys.argv
    audio = resolver(guion["audio"]) if guion.get("audio") and not sin_audio else None
    if audio and not audio.exists():
        raise SystemExit(f"No existe el audio: {audio}")
    if not audio and not sin_audio and "--cuadro" not in sys.argv and "--hoja" not in sys.argv:
        raise SystemExit("Este guion no tiene voz en off (falta \"audio\"). TODO video lleva locucion. Genera la voz con:\n"
                         f"    python3 voz_local.py \"{sys.argv[1]}\"\n"
                         "y vuelve a ejecutar este comando. (Solo para pruebas internas existe --sin-audio.)")
    durs = repartir(guion, audio)
    total = sum(durs)
    n = guion["estilo"] if isinstance(guion.get("estilo"), int) else puesto_del_guion(ruta_guion, ruta_guion.parent)
    fijar_estilo(n)
    fondo = crear_fondo()

    if "--cuadro" in sys.argv:
        i = sys.argv.index("--cuadro")
        cuadro(guion, durs, fondo, float(sys.argv[i + 1])).save(sys.argv[i + 2])
        print(f"Cuadro guardado: {sys.argv[i + 2]}")
        return
    if "--hoja" in sys.argv:
        destino = Path(sys.argv[sys.argv.index("--hoja") + 1])
        mini_w, mini_h = 360, 640
        hoja = Image.new("RGB", (mini_w * len(durs), mini_h * 2), FONDO)
        inicio, sueltos = 0.0, []
        for n, dur in enumerate(durs):
            for fila, (letra, frac) in enumerate((("a", 0.5), ("b", 0.93))):
                img = cuadro(guion, durs, fondo, inicio + dur * frac)
                suelto = destino.with_name(f"{destino.stem}_escena{n + 1}{letra}.png")
                img.save(suelto)
                sueltos.append(str(suelto))
                hoja.paste(img.resize((mini_w, mini_h), Image.LANCZOS), (mini_w * n, mini_h * fila))
            inicio += dur
        hoja.save(destino)
        print(json.dumps({"hoja": str(destino), "cuadros": sueltos, "escenas_s": [round(x, 2) for x in durs]}, ensure_ascii=False))
        return

    salida = resolver(guion.get("salida") or f"videos/{ruta_guion.stem}.mp4")
    salida.parent.mkdir(parents=True, exist_ok=True)
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio:
        retardo = 0 if guion.get("sincronia") == "exacta" else 300
        cmd += ["-i", str(audio), "-af", f"adelay={retardo}|{retardo},apad", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-t", f"{total:.3f}", str(salida)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS)
    for i in range(n):
        proc.stdin.write(cuadro(guion, durs, fondo, i / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("FFmpeg fallo al codificar el video.")
    if audio:       # comprobar que la voz quedo de verdad dentro del MP4 y que no es silencio
        r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(salida), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                           capture_output=True, text=True, errors="replace")
        m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
        if "Audio:" not in r.stderr or not m or float(m[1]) < -50:
            raise SystemExit("El video quedo SIN voz audible (pista de audio ausente o en silencio). Revisa el archivo de "
                             "audio o vuelve a generar la voz con voz_local.py.")
    print(json.dumps({"video": str(salida), "duracion_s": round(total, 2), "cuadros": n,
                      "con_audio": bool(audio),
                      "estilo": {k: ESTILO[k] for k in ("n", "fondo", "entrada", "transicion", "esquinas", "ambiente", "camara")},
                      "escenas_s": [round(x, 2) for x in durs]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
