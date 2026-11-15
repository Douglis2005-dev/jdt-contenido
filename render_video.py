"""Generador de Reels de JDT TECHNOLOGICS (motion graphics por codigo).

Dibuja cada cuadro con Pillow y lo codifica a MP4 vertical 1080x1920 con FFmpeg
(el binario viene con el paquete imageio-ffmpeg). Opcionalmente mezcla una voz
en off y ajusta la duracion de las escenas a la del audio.

Uso:
    py render_video.py guion.json
    py render_video.py guion.json --cuadro 3.5 salida.png   (un solo cuadro, para revisar)

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
    {"tipo": "cierre",   "texto": "Hablemos de tu proyecto", "subtexto": "@technologicsjdt"}
  ]
}
ESTILO: cada video sale con un estilo distinto al anterior (fondo, color de
apoyo, entrada del texto, transicion entre escenas, ambiente y variante de
cada escena). Se elige solo segun el puesto del guion entre los de videos/.
Para forzarlo: "estilo": 7 en el guion (cualquier entero), y "variante": 0|1|2
en una escena.
Las palabras entre *asteriscos* salen en amarillo. "voz" es lo que dice la
locucion durante esa escena: si hay audio, cada escena dura en proporcion al
largo de su "voz" (o de su "duracion" si falta).
"""
from __future__ import annotations

import functools
import json
import math
import random
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CARPETA = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
FONDO, FONDO_ALT, SUPERFICIE = (10, 14, 39), (13, 18, 48), (19, 26, 58)
AMARILLO, BLANCO, GRIS, GRIS_OSC = (250, 204, 21), (255, 255, 255), (148, 163, 184), (100, 116, 139)
ROJO, BORDE = (248, 113, 113), (42, 52, 96)
TIPOS = {"titular", "caos", "flujo", "panel", "lista", "telefono", "chat", "comparar", "conexion",
         "reloj", "web", "documento", "pasos", "cierre"}

# ---------------------------------------------------------------- estilo
FONDOS = ["rejilla", "puntos", "diagonales", "anillos", "circuito"]
ACENTOS = [(59, 91, 219), (34, 211, 238), (139, 92, 246), (52, 211, 153)]
ENTRADAS = ["sube", "cortina", "pop", "maquina", "izquierda"]
TRANSICIONES = ["fundido", "barrido", "desliza-izq", "zoom", "desliza-arriba"]
ESQUINAS = ["ne-so", "barra", "no-se"]
AMBIENTES = ["particulas", "lineas", "pulsos"]
ESTILO = {"n": 0, "fondo": "rejilla", "acento": ACENTOS[0], "entrada": "sube", "transicion": "fundido",
          "esquinas": "ne-so", "ambiente": "ninguno", "semilla": 0}


def fijar_estilo(n: int, esquinas=None) -> dict:
    """Elige el estilo del video numero n: dos videos seguidos nunca comparten fondo,
    color de apoyo, entrada de texto, transicion ni ambiente."""
    esq = esquinas or ESQUINAS
    ESTILO.update(n=n, fondo=FONDOS[n % 5], acento=ACENTOS[n % 4], entrada=ENTRADAS[(n * 2 + 1) % 5],
                  transicion=TRANSICIONES[(n * 3 + 1) % 5], esquinas=esq[n % len(esq)],
                  ambiente=AMBIENTES[n % 3], semilla=n * 7919 + 13)
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
    if ESTILO["esquinas"] == "no-se":   # las franjas van a la izquierda: la marca pasa a la derecha
        f = fuente(34)
        ancho = f.getlength("JDT TECHNOLOGICS")
        d.ellipse([W - 80 - ancho - 42, 150, W - 80 - ancho - 18, 174], fill=AMARILLO)
        d.text((W - 80, 162), "JDT TECHNOLOGICS", font=f, fill=BLANCO, anchor="rm")
        return
    d.ellipse([80, 150, 104, 174], fill=AMARILLO)
    d.text((122, 162), "JDT TECHNOLOGICS", font=fuente(34), fill=BLANCO, anchor="lm")


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
                    d.text((x0 + x, yl), p, font=f, fill=AMARILLO if ac else BLANCO)
            if q < 1:
                a, b = (0.0, suave(q * 2)) if q < 0.5 else (suave((q - 0.5) * 2), 1.0)
                d.rectangle([x0 - 8 + ancho_linea * a, yl + tam * 0.1, x0 + 8 + ancho_linea * b, yl + tam * 1.14], fill=AMARILLO)
            continue
        for p, ac, x, w in linea:
            color = AMARILLO if ac else BLANCO
            if modo == "maquina":
                resto = letras - vistas
                vistas += len(p)
                if resto <= 0:
                    continue
                trozo = p[:resto]
                d.text((x0 + x, yl), trozo, font=f, fill=color)
                if resto < len(p) and letras < total_letras:
                    cx = x0 + x + f.getlength(trozo) + 6
                    d.rectangle([cx, yl + tam * 0.14, cx + tam * 0.09, yl + tam * 1.06], fill=AMARILLO)
                continue
            q = (t - 0.07 * i) / 0.35
            i += 1
            if q <= 0:
                continue
            k = suave(q)
            if modo == "pop" and q < 1:
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
    for i, c in enumerate([(248, 113, 113), (250, 204, 21), (74, 222, 128)]):
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
        d2.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROJO)
        d2.text((cx, cy - 2), "!", font=fuente(int(56 * k) or 1), fill=BLANCO, anchor="mm")


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
        tarjeta(d, [x, y, W - 120 + (1 - k) * 160 * lado, y + alto], relleno=(34, 44, 30) if activo else SUPERFICIE,
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
        d.text((x + 45, yy + 63), m, font=f, fill=con_alfa(FONDO if ultimo else BLANCO, a), anchor="lm")


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
        tarjeta(d, [x, y, x + W - 160, y + alto], radio=32, borde=AMARILLO if despues else ROJO, ancho=5 if despues else 3, a=k * apagado)
        d.text((x + 40, y + 55), titulo.upper(), font=fuente(40), fill=con_alfa(AMARILLO if despues else ROJO, k * apagado), anchor="lm")
        for i, it in enumerate(lista):
            yy = y + 110 + i * 100
            q = (t - t0 - 0.3 - 0.25 * i) / 0.3
            d.ellipse([x + 40, yy + 6, x + 104, yy + 70], fill=con_alfa(AMARILLO if despues else ROJO, k * apagado))
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
        d.pieslice([cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16], -90, -90 + 360 * gasto, fill=con_alfa(ROJO, 0.55))
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
        tarjeta(d, [x, y, x + ancho, y + 96], radio=48, borde=ROJO)
        d.ellipse([x + 26, y + 30, x + 62, y + 66], fill=ROJO)
        d.text((x + 84, y + 46), tarea, font=ajustar(tarea, ancho - 110, 36, 22), fill=BLANCO, anchor="lm")


def esc_web(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    secciones = etiquetas_de(esc, ["Catálogo", "Pedidos en línea", "Contacto"])[:3]
    k = suave(t / 0.5)
    y0 = 840 + (1 - k) * 120
    tarjeta(d, [80, y0, W - 80, y0 + 800], radio=30, a=k)
    d.rounded_rectangle([80, y0, W - 80, y0 + 84], radius=30, fill=con_alfa((28, 37, 80), k))
    d.rectangle([80, y0 + 50, W - 80, y0 + 84], fill=con_alfa((28, 37, 80), k))
    for i, c in enumerate([(248, 113, 113), (250, 204, 21), (74, 222, 128)]):
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
    d.rounded_rectangle([x0, y0, x1, y0 + alto], radius=20, fill=con_alfa((226, 232, 244), k))
    d.polygon([(x1 - 80, y0 - 2), (x1 + 2, y0 + 80), (x1 + 2, y0 - 2)], fill=con_alfa(FONDO, k))
    d.polygon([(x1 - 80, y0), (x1 - 80, y0 + 80), (x1, y0 + 80)], fill=con_alfa((180, 190, 212), k))
    largo = max(1.2, dur * 0.45)
    barrido = (t - 0.6) / largo
    ys = y0 + alto * max(0.0, min(1.0, barrido))
    for i in range(7):
        ly = y0 + 70 + i * 50
        leida = ly < ys and barrido > 0
        ancho = [0.5, 0.8, 0.7, 0.85, 0.6, 0.78, 0.45][i] * (x1 - x0 - 150)
        d.rounded_rectangle([x0 + 40, ly, x0 + 40 + ancho, ly + 22], radius=10,
                            fill=con_alfa((202, 138, 4) if leida and i in (0, 3, 5) else (148, 163, 184), k))
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


ESCENAS = {"titular": esc_titular, "caos": esc_caos, "flujo": esc_flujo, "panel": esc_panel,
           "lista": esc_lista, "telefono": esc_telefono, "chat": esc_chat, "comparar": esc_comparar,
           "conexion": esc_conexion, "reloj": esc_reloj, "web": esc_web, "documento": esc_documento,
           "pasos": esc_pasos, "cierre": esc_cierre}


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
        if e.get("tipo") not in TIPOS:
            raise SystemExit(f"Escena {i}: tipo '{e.get('tipo')}' no existe. Tipos: {sorted(TIPOS)}")
        if not str(e.get("texto", "")).strip():
            raise SystemExit(f"Escena {i}: falta 'texto'.")
        if len(partir(e["texto"])) > 12:
            raise SystemExit(f"Escena {i}: el texto en pantalla tiene mas de 12 palabras; acortalo.")
    if escenas[-1]["tipo"] != "cierre":
        raise SystemExit("La ultima escena debe ser de tipo 'cierre'.")


def repartir(guion: dict, audio: Path | None) -> list[float]:
    escenas = guion["escenas"]
    durs = [float(e.get("duracion") or 3) for e in escenas]
    if audio:
        total = duracion_audio(audio) + 1.0
        pesos = [len(e["voz"]) for e in escenas] if all(e.get("voz") for e in escenas) else durs
        durs = [total * p / sum(pesos) for p in pesos]
        falta = 2.4 - durs[-1]
        if falta > 0:  # el cierre necesita tiempo para leerse
            durs[-1] += falta
    return [max(2.6, x) for x in durs]


def cuadro(guion, durs, fondo, t: float) -> Image.Image:
    inicio = 0.0
    for idx, (esc, dur) in enumerate(zip(guion["escenas"], durs)):
        if t < inicio + dur or esc is guion["escenas"][-1]:
            break
        inicio += dur
    local = t - inicio
    esc["_i"] = idx
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ESCENAS[esc["tipo"]](capa, d, esc, local, dur)
    ultima = esc is guion["escenas"][-1]
    trans = ESTILO["transicion"]
    sale = 1.0 if ultima else suave((dur - local) / 0.25)      # 1 = escena completa, 0 = ya salio
    entra = 1.0 if idx == 0 else suave(local / 0.25)
    dx = dy = 0
    if sale < 1 and trans != "barrido":
        capa.putalpha(capa.getchannel("A").point(lambda v: int(v * sale)))
        if trans == "desliza-izq":
            dx = -int((1 - sale) * W * 0.45)
        elif trans == "desliza-arriba":
            dy = -int((1 - sale) * 320)
        elif trans == "zoom":
            z = 1 + 0.28 * (1 - sale)
            capa = capa.resize((int(W * z), int(H * z)), Image.BILINEAR)
            dx, dy = (W - capa.width) // 2, (H - capa.height) // 2
    elif entra < 1 and trans == "desliza-izq":
        dx = int((1 - entra) * W * 0.3)
    elif entra < 1 and trans == "desliza-arriba":
        dy = int((1 - entra) * 220)
    img = fondo.copy()
    dibujar_ambiente(img, t)
    img.paste(capa, (dx, dy), capa)
    dibujar_marca(ImageDraw.Draw(img))
    if trans == "barrido":      # una cortina amarilla cruza la pantalla entre escenas
        dd = ImageDraw.Draw(img)
        if sale < 1:
            dd.rectangle([0, 0, W * (1 - sale), H], fill=AMARILLO)
        elif entra < 1:
            dd.rectangle([W * entra, 0, W, H], fill=AMARILLO)
    # barra de progreso
    total = sum(durs)
    ImageDraw.Draw(img).rectangle([0, H - 10, W * min(1, t / total), H], fill=AMARILLO)
    return img


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ruta_guion = Path(sys.argv[1]).resolve()
    guion = json.loads(ruta_guion.read_text(encoding="utf-8"))
    validar(guion)
    base = ruta_guion.parent

    def resolver(p):
        p = Path(p)
        return p if p.is_absolute() else (CARPETA / p if (CARPETA / p).parent.exists() else base / p)

    audio = resolver(guion["audio"]) if guion.get("audio") else None
    if audio and not audio.exists():
        raise SystemExit(f"No existe el audio: {audio}")
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

    salida = resolver(guion.get("salida") or f"videos/{ruta_guion.stem}.mp4")
    salida.parent.mkdir(parents=True, exist_ok=True)
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", str(audio), "-af", "adelay=300|300,apad", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-t", f"{total:.3f}", str(salida)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS)
    for i in range(n):
        proc.stdin.write(cuadro(guion, durs, fondo, i / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("FFmpeg fallo al codificar el video.")
    print(json.dumps({"video": str(salida), "duracion_s": round(total, 2), "cuadros": n,
                      "con_audio": bool(audio),
                      "estilo": {k: ESTILO[k] for k in ("n", "fondo", "entrada", "transicion", "esquinas", "ambiente")},
                      "escenas_s": [round(x, 2) for x in durs]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
