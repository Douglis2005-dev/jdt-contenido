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
    {"tipo": "cierre",   "texto": "Hablemos de tu proyecto", "subtexto": "@technologicsjdt"}
  ]
}
Las palabras entre *asteriscos* salen en amarillo. "voz" es lo que dice la
locucion durante esa escena: si hay audio, cada escena dura en proporcion al
largo de su "voz" (o de su "duracion" si falta).
"""
from __future__ import annotations

import json
import math
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
TIPOS = {"titular", "caos", "flujo", "panel", "lista", "telefono", "cierre"}
FUENTES = Path("C:/Windows/Fonts")


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
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=(16, 22, 54))
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=(16, 22, 54))
    brillo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = ImageDraw.Draw(brillo)
    b.ellipse([W - 520, -380, W + 380, 520], fill=(250, 204, 21, 38))
    b.ellipse([-420, H - 620, 420, H + 220], fill=(59, 91, 219, 50))
    brillo = brillo.filter(ImageFilter.GaussianBlur(160))
    img.paste(brillo, (0, 0), brillo)
    d = ImageDraw.Draw(img)
    # franjas diagonales amarillas, como en el logo
    d.polygon([(W - 250, 0), (W, 0), (W, 150)], fill=AMARILLO)
    d.polygon([(W - 360, 0), (W - 290, 0), (W, 190), (W, 232)], fill=AMARILLO)
    d.polygon([(0, H - 150), (0, H), (250, H)], fill=AMARILLO)
    d.polygon([(0, H - 232), (0, H - 190), (290, H), (360, H)], fill=AMARILLO)
    return img


def dibujar_marca(d: ImageDraw.ImageDraw) -> None:
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


def dibujar_titular(d, texto: str, t: float, y: int, tam_max: int = 96, lineas_max: int = 4, centro: bool = False):
    f, tam, lineas = componer(texto, W - 160, tam_max, lineas_max)
    alto = int(tam * 1.18)
    i = 0
    for n, linea in enumerate(lineas):
        ancho_linea = linea[-1][2] + linea[-1][3]
        x0 = (W - ancho_linea) / 2 if centro else 80
        for p, ac, x, _ in linea:
            k = suave((t - 0.07 * i) / 0.35)
            i += 1
            if k <= 0:
                continue
            d.text((x0 + x, y + n * alto + (1 - k) * 36), p, font=f, fill=con_alfa(AMARILLO if ac else BLANCO, k))
    return y + len(lineas) * alto


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
    fin = dibujar_titular(d, esc["texto"], t, 640, tam_max=120, lineas_max=5)
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
    pos = [(90, 880, -9), (560, 820, 7), (300, 1090, -4), (60, 1300, 6), (590, 1290, -8)]
    for i, img in enumerate(cache):
        x, y, ang = pos[i]
        k = rebote((t - 0.15 * i) / 0.5)
        if t < 0.15 * i:
            continue
        tiembla = math.sin(t * 9 + i * 2.1) * 2.2
        rot = img.rotate(ang + tiembla, resample=Image.BICUBIC, expand=True)
        capa.alpha_composite(rot, (int(x + math.sin(t * 2 + i) * 10), int(y + (1 - k) * 260 + math.cos(t * 2.4 + i) * 8)))
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
        x = 120 + (1 - k) * 120
        tarjeta(d, [x, y, W - 120 + (1 - k) * 120, y + alto], relleno=(34, 44, 30) if activo else SUPERFICIE,
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
    bw = (W - 240 - 5 * 30) / 6
    for i, h in enumerate(alturas):
        q = suave((t - 0.3 - 0.07 * i) / 0.45)
        if q <= 0:
            continue
        x = 120 + i * (bw + 30)
        color = AMARILLO if i == len(alturas) - 1 else (59, 91, 219)
        d.rounded_rectangle([x, base - tope * h * q - 6, x + bw, base - 4], radius=14, fill=color)


def esc_lista(capa, d, esc, t, dur):
    dibujar_titular(d, esc["texto"], t, 300)
    nombres = etiquetas_de(esc, ["Se adapta a tu proceso", "Pagas solo lo que necesitas", "Evoluciona contigo"])[:4]
    paso = max(0.45, (dur - 1.0) / len(nombres))
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
        d.ellipse([x0 + 58, y + 33, x0 + 118, y + 93], fill=con_alfa(AMARILLO if i == 0 else (59, 91, 219), a))
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


ESCENAS = {"titular": esc_titular, "caos": esc_caos, "flujo": esc_flujo, "panel": esc_panel,
           "lista": esc_lista, "telefono": esc_telefono, "cierre": esc_cierre}


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
    for esc, dur in zip(guion["escenas"], durs):
        if t < inicio + dur or esc is guion["escenas"][-1]:
            break
        inicio += dur
    local = t - inicio
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ESCENAS[esc["tipo"]](capa, d, esc, local, dur)
    ultima = esc is guion["escenas"][-1]
    desv = 1.0 if ultima else suave((dur - local) / 0.22)
    if desv < 1:
        capa.putalpha(capa.getchannel("A").point(lambda v: int(v * desv)))
    img = fondo.copy()
    img.paste(capa, (0, 0), capa)
    dibujar_marca(ImageDraw.Draw(img))
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
                      "con_audio": bool(audio), "escenas_s": [round(x, 2) for x in durs]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
