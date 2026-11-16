"""Iconos planos de JDT TECHNOLOGICS dibujados por codigo (sin archivos ni marcas de terceros).

Los usan las escenas "libre" de render_video.py. Cada icono se dibuja en una caja
de 100x100 unidades, con suavizado, en UN solo color de la paleta de la marca.

Uso:
    import iconos
    img = iconos.icono("engranaje", 240, (250, 204, 21))   # imagen RGBA de 240x240
    iconos.NOMBRES                                          # lista de iconos disponibles
    py iconos.py hoja.png                                   # hoja con todos, para verlos
"""
from __future__ import annotations

import functools
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CARPETA = Path(__file__).resolve().parent
NADA = (0, 0, 0, 0)
SUPER = 3   # se dibuja al triple y se reduce, para que los bordes salgan suaves


class _P:
    """Pincel en unidades 0-100. borra=True recorta (deja transparente) en vez de pintar."""

    def __init__(self, lado: int, color):
        self.u = lado / 100
        self.c = (*color[:3], 255)
        self.im = Image.new("RGBA", (lado, lado), NADA)
        self.d = ImageDraw.Draw(self.im)

    def _f(self, borra):
        return NADA if borra else self.c

    def _b(self, *v):
        return [x * self.u for x in v]

    def circ(self, x, y, r, borra=False):
        self.d.ellipse(self._b(x - r, y - r, x + r, y + r), fill=self._f(borra))

    def elip(self, x0, y0, x1, y1, borra=False):
        self.d.ellipse(self._b(x0, y0, x1, y1), fill=self._f(borra))

    def rr(self, x0, y0, x1, y1, r=0, borra=False):
        self.d.rounded_rectangle(self._b(x0, y0, x1, y1), radius=r * self.u, fill=self._f(borra))

    def rro(self, x0, y0, x1, y1, r, w):
        self.d.rounded_rectangle(self._b(x0, y0, x1, y1), radius=r * self.u, outline=self.c, width=max(1, int(w * self.u)))

    def poly(self, pts, borra=False):
        self.d.polygon([(x * self.u, y * self.u) for x, y in pts], fill=self._f(borra))

    def ln(self, pts, w, borra=False):
        f = self._f(borra)
        p = [(x * self.u, y * self.u) for x, y in pts]
        self.d.line(p, fill=f, width=max(1, int(w * self.u)), joint="curve")
        r = w * self.u / 2
        for x, y in p:   # puntas redondeadas
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=f)

    def arc(self, x0, y0, x1, y1, a0, a1, w, borra=False):
        self.d.arc(self._b(x0, y0, x1, y1), a0, a1, fill=self._f(borra), width=max(1, int(w * self.u)))

    def pie(self, x0, y0, x1, y1, a0, a1, borra=False):
        self.d.pieslice(self._b(x0, y0, x1, y1), a0, a1, fill=self._f(borra))

    def txt(self, x, y, s, tam, borra=False):
        self.d.text((x * self.u, y * self.u), s, font=_fuente(int(tam * self.u)), fill=self._f(borra), anchor="mm")

    def punta(self, x, y, ang, tam):
        """Triangulo que apunta en la direccion ang (radianes), con la punta en (x, y)."""
        ux, uy = math.cos(ang), math.sin(ang)
        bx, by = x - ux * tam, y - uy * tam
        self.poly([(x, y), (bx - uy * tam * 0.6, by + ux * tam * 0.6), (bx + uy * tam * 0.6, by - ux * tam * 0.6)])


@functools.lru_cache(maxsize=32)
def _fuente(tam: int):
    for ruta in sorted((CARPETA / "recursos" / "fuentes").glob("*Bold*.ttf")):
        return ImageFont.truetype(str(ruta), tam)
    return ImageFont.load_default(tam)


def _rect_girado(cx, cy, w, h, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


def _estrella(cx, cy, R, r, puntas, giro=-math.pi / 2):
    pts = []
    for i in range(puntas * 2):
        a = giro + i * math.pi / puntas
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return pts


# ------------------------------------------------------------------ iconos
def engranaje(p):
    for i in range(8):
        a = i * math.pi / 4
        p.poly(_rect_girado(50 + 35 * math.cos(a), 50 + 35 * math.sin(a), 18, 17, a))
    p.circ(50, 50, 31)
    p.circ(50, 50, 13, borra=True)


def nube(p):
    p.circ(34, 58, 18); p.circ(54, 44, 24); p.circ(72, 60, 16); p.rr(22, 58, 84, 76, 9)


def carrito(p):
    p.ln([(8, 20), (22, 20), (33, 64), (80, 64)], 7)
    p.poly([(27, 30), (90, 30), (82, 55), (33, 55)])
    p.circ(40, 80, 8); p.circ(72, 80, 8)


def telefono(p):
    p.rr(27, 6, 73, 94, 10); p.rr(32, 16, 68, 80, 3, borra=True); p.circ(50, 87, 3.5, borra=True)


def chat(p):
    p.rr(8, 14, 92, 70, 16); p.poly([(24, 66), (24, 92), (50, 68)])
    for x in (31, 50, 69):
        p.circ(x, 42, 6, borra=True)


def documento(p):
    p.poly([(20, 6), (60, 6), (80, 26), (80, 94), (20, 94)])
    p.ln([(60, 8), (60, 26), (78, 26)], 3.5, borra=True)
    p.rr(31, 42, 69, 49, 3, borra=True); p.rr(31, 57, 69, 64, 3, borra=True); p.rr(31, 72, 56, 79, 3, borra=True)


def papeles(p):
    p.rr(34, 6, 88, 76, 7); p.rr(12, 18, 72, 96, 9, borra=True); p.rr(16, 22, 68, 94, 7)
    p.rr(26, 40, 58, 46, 3, borra=True); p.rr(26, 54, 58, 60, 3, borra=True); p.rr(26, 68, 46, 74, 3, borra=True)


def carpeta(p):
    p.rr(6, 14, 46, 40, 7); p.rr(6, 26, 94, 86, 9)


def grafica(p):
    p.rr(14, 56, 31, 88, 3); p.rr(41, 38, 58, 88, 3); p.rr(68, 14, 85, 88, 3); p.rr(8, 91, 92, 96, 2)


def crecimiento(p):
    p.ln([(10, 80), (36, 54), (52, 68), (82, 32)], 8)
    p.punta(92, 20, math.atan2(-36, 30), 22)


def usuario(p):
    p.circ(50, 32, 19); p.pie(16, 56, 84, 124, 180, 360)


def equipo(p):
    p.circ(22, 42, 12); p.pie(2, 60, 42, 100, 180, 360)
    p.circ(78, 42, 12); p.pie(58, 60, 98, 100, 180, 360)
    p.circ(50, 34, 19, borra=True); p.pie(22, 52, 78, 108, 180, 360, borra=True)
    p.circ(50, 34, 15); p.pie(26, 56, 74, 104, 180, 360)


def _persona(p):
    p.circ(50, 34, 27); p.pie(14, 66, 86, 126, 180, 360)
    p.circ(40, 29, 3.6, borra=True); p.circ(60, 29, 3.6, borra=True)


def persona_feliz(p):
    _persona(p); p.arc(36, 24, 64, 50, 25, 155, 3.6, borra=True)


def persona_triste(p):
    _persona(p); p.arc(38, 40, 62, 60, 205, 335, 3.6, borra=True)


def persona_sorpresa(p):
    _persona(p); p.circ(50, 45, 5.5, borra=True)


def persona_pensando(p):
    _persona(p); p.ln([(42, 45), (58, 43)], 3.6, borra=True); p.circ(86, 18, 5); p.circ(94, 6, 3)


def reloj(p):
    p.circ(50, 50, 42); p.circ(50, 50, 33, borra=True); p.ln([(50, 28), (50, 50), (65, 59)], 6.5)


def calendario(p):
    p.rr(10, 16, 90, 92, 10); p.rr(26, 5, 35, 26, 4); p.rr(65, 5, 74, 26, 4)
    p.rr(10, 36, 90, 39.5, 0, borra=True)
    for f in range(2):
        for c in range(3):
            p.rr(23 + 20 * c, 50 + 19 * f, 37 + 20 * c, 62 + 19 * f, 2.5, borra=True)


def candado(p):
    p.arc(27, 8, 73, 60, 180, 360, 9); p.rr(27, 32, 36, 48); p.rr(64, 32, 73, 48)
    p.rr(18, 44, 82, 92, 9); p.circ(50, 63, 6.5, borra=True); p.rr(47, 63, 53, 78, 2, borra=True)


def escudo(p):
    p.poly([(50, 5), (87, 19), (87, 50), (76, 74), (50, 95), (24, 74), (13, 50), (13, 19)])
    p.ln([(33, 49), (45, 61), (67, 36)], 8, borra=True)


def rayo(p):
    p.poly([(58, 4), (20, 55), (45, 55), (39, 96), (80, 42), (55, 42)])


def check(p):
    p.circ(50, 50, 43); p.ln([(30, 52), (44, 66), (70, 36)], 9, borra=True)


def equis(p):
    p.circ(50, 50, 43); p.ln([(34, 34), (66, 66)], 9, borra=True); p.ln([(66, 34), (34, 66)], 9, borra=True)


def alerta(p):
    p.poly([(50, 7), (95, 88), (5, 88)]); p.rr(45.5, 34, 54.5, 62, 4, borra=True); p.circ(50, 74, 5.5, borra=True)


def pregunta(p):
    p.circ(50, 50, 43); p.txt(50, 51, "?", 60, borra=True)


def flecha(p):
    p.poly([(8, 39), (54, 39), (54, 20), (93, 50), (54, 80), (54, 61), (8, 61)])


def ciclo(p):
    p.arc(14, 14, 86, 86, 30, 165, 9); p.arc(14, 14, 86, 86, 210, 345, 9)
    for a in (165, 345):
        r = math.radians(a)
        p.punta(50 + 36 * math.cos(r) - 13 * math.sin(r), 50 + 36 * math.sin(r) + 13 * math.cos(r), r + math.pi / 2, 22)


def tienda(p):
    p.poly([(14, 12), (86, 12), (95, 36), (5, 36)])
    for i in range(4):
        p.circ(16.5 + 22.3 * i, 36, 11.2)
    p.rr(13, 44, 87, 93, 3); p.rr(56, 60, 75, 93, 2, borra=True); p.rr(23, 58, 46, 77, 2, borra=True)


def bolsa(p):
    p.arc(31, 6, 69, 52, 180, 360, 7); p.rr(14, 30, 86, 94, 9)
    p.circ(35, 44, 4, borra=True); p.circ(65, 44, 4, borra=True)


def caja(p):
    p.poly([(50, 6), (91, 27), (50, 48), (9, 27)])
    p.poly([(9, 35), (46, 54), (46, 96), (9, 76)]); p.poly([(91, 35), (54, 54), (54, 96), (91, 76)])


def camion(p):
    p.rr(4, 24, 60, 70, 5); p.poly([(64, 37), (82, 37), (96, 54), (96, 70), (64, 70)])
    for x in (24, 78):
        p.circ(x, 74, 12, borra=True); p.circ(x, 74, 8.5)


def pin(p):
    p.circ(50, 37, 29); p.poly([(25, 52), (75, 52), (50, 96)]); p.circ(50, 37, 11, borra=True)


def casa(p):
    p.poly([(50, 6), (96, 48), (83, 48), (83, 92), (17, 92), (17, 48), (4, 48)]); p.rr(41, 60, 59, 92, 2, borra=True)


def correo(p):
    p.rr(6, 20, 94, 80, 9); p.ln([(13, 29), (50, 57), (87, 29)], 6, borra=True)


def campana(p):
    p.circ(50, 11, 6); p.pie(21, 14, 79, 76, 180, 360); p.rr(21, 44, 79, 68)
    p.poly([(10, 80), (21, 62), (79, 62), (90, 80)]); p.circ(50, 88, 8)


def megafono(p):
    p.poly([(10, 38), (38, 38), (78, 12), (78, 88), (38, 62), (10, 62)]); p.rr(24, 62, 38, 90, 4)
    p.arc(70, 30, 98, 70, 300, 60, 6)


def robot(p):
    p.circ(50, 9, 6); p.rr(47, 10, 53, 28, 2); p.rr(17, 28, 83, 86, 13)
    p.rr(6, 46, 14, 68, 3); p.rr(86, 46, 94, 68, 3)
    p.circ(36, 51, 8.5, borra=True); p.circ(64, 51, 8.5, borra=True); p.rr(35, 68, 65, 74.5, 3, borra=True)


def chispa(p):
    p.poly(_estrella(42, 56, 40, 10, 4)); p.poly(_estrella(80, 20, 17, 4.5, 4))


def bombilla(p):
    p.circ(50, 38, 31); p.rr(37, 60, 63, 80, 3); p.rr(42, 84, 58, 91, 3)
    p.rr(37, 70, 63, 73.5, 0, borra=True); p.ln([(42, 40), (50, 50), (58, 40)], 3.5, borra=True)


def datos(p):
    p.rr(15, 20, 85, 80); p.elip(15, 8, 85, 32); p.elip(15, 68, 85, 92)
    p.arc(15, 30, 85, 54, 0, 180, 4.5, borra=True); p.arc(15, 50, 85, 74, 0, 180, 4.5, borra=True)


def red(p):
    p.ln([(22, 76), (50, 24), (78, 76), (22, 76)], 5.5)
    for x, y in ((50, 24), (22, 76), (78, 76)):
        p.circ(x, y, 14)


def enlace(p):
    p.rro(6, 33, 57, 67, 17, 9); p.rro(43, 33, 94, 67, 17, 9)


def codigo(p):
    p.ln([(33, 26), (11, 50), (33, 74)], 8.5); p.ln([(67, 26), (89, 50), (67, 74)], 8.5); p.ln([(57, 18), (43, 82)], 8.5)


def pantalla(p):
    p.rr(6, 12, 94, 72, 9); p.rr(13, 19, 87, 65, 3, borra=True); p.rr(44, 72, 56, 85); p.rr(27, 84, 73, 92, 4)


def tabla(p):
    p.rr(8, 14, 92, 86, 9)
    for y in (34, 51, 68):
        p.rr(8, y, 92, y + 3.2, 0, borra=True)
    for x in (35, 63):
        p.rr(x, 34, x + 3.2, 86, 0, borra=True)


def lupa(p):
    p.circ(42, 42, 31); p.circ(42, 42, 20, borra=True); p.ln([(66, 66), (88, 88)], 12)


def ojo(p):
    p.poly([(4, 50), (26, 28), (50, 20), (74, 28), (96, 50), (74, 72), (50, 80), (26, 72)])
    p.circ(50, 50, 19, borra=True); p.circ(50, 50, 10)


def objetivo(p):
    p.circ(50, 50, 44); p.circ(50, 50, 34, borra=True); p.circ(50, 50, 24); p.circ(50, 50, 14, borra=True); p.circ(50, 50, 6)


def moneda(p):
    p.circ(50, 50, 44); p.circ(50, 50, 35, borra=True); p.circ(50, 50, 30); p.txt(50, 51, "$", 44, borra=True)


def tarjeta(p):
    p.rr(5, 20, 95, 80, 11); p.rr(5, 35, 95, 47, 0, borra=True); p.rr(15, 59, 45, 67, 3, borra=True)


def corazon(p):
    p.circ(31, 36, 22); p.circ(69, 36, 22); p.poly([(11.5, 47), (88.5, 47), (50, 93)])


def estrella(p):
    p.poly(_estrella(50, 54, 47, 19, 5))


def cohete(p):
    p.elip(31, 2, 69, 62); p.rr(31, 32, 69, 68, 3)
    p.poly([(31, 46), (12, 74), (31, 68)]); p.poly([(69, 46), (88, 74), (69, 68)])
    p.circ(50, 34, 9, borra=True); p.poly([(40, 72), (60, 72), (50, 98)])


def wifi(p):
    p.arc(6, 22, 94, 110, 225, 315, 9); p.arc(22, 40, 78, 96, 225, 315, 9); p.arc(37, 57, 63, 83, 225, 315, 9); p.circ(50, 84, 7)


ICONOS = {
    "engranaje": engranaje, "nube": nube, "carrito": carrito, "telefono": telefono, "chat": chat,
    "documento": documento, "papeles": papeles, "carpeta": carpeta, "grafica": grafica, "crecimiento": crecimiento,
    "usuario": usuario, "equipo": equipo, "persona-feliz": persona_feliz, "persona-triste": persona_triste,
    "persona-sorpresa": persona_sorpresa, "persona-pensando": persona_pensando, "reloj": reloj,
    "calendario": calendario, "candado": candado, "escudo": escudo, "rayo": rayo, "check": check, "equis": equis,
    "alerta": alerta, "pregunta": pregunta, "flecha": flecha, "ciclo": ciclo, "tienda": tienda, "bolsa": bolsa,
    "caja": caja, "camion": camion, "pin": pin, "casa": casa, "correo": correo, "campana": campana,
    "megafono": megafono, "robot": robot, "chispa": chispa, "bombilla": bombilla, "datos": datos, "red": red,
    "enlace": enlace, "codigo": codigo, "pantalla": pantalla, "tabla": tabla, "lupa": lupa, "ojo": ojo,
    "objetivo": objetivo, "moneda": moneda, "tarjeta": tarjeta, "corazon": corazon, "estrella": estrella,
    "cohete": cohete, "wifi": wifi,
}
NOMBRES = sorted(ICONOS)


@functools.lru_cache(maxsize=256)
def icono(nombre: str, tam: int, color: tuple) -> Image.Image:
    if nombre not in ICONOS:
        raise KeyError(f"No existe el icono '{nombre}'. Disponibles: {', '.join(NOMBRES)}")
    tam = max(8, int(tam))
    p = _P(tam * SUPER, color)
    ICONOS[nombre](p)
    return p.im.resize((tam, tam), Image.LANCZOS)


def main() -> None:
    salida = sys.argv[1] if len(sys.argv) > 1 else "iconos.png"
    cols, celda = 9, 150
    filas = math.ceil(len(NOMBRES) / cols)
    hoja = Image.new("RGB", (cols * celda, filas * (celda + 34)), (10, 14, 39))
    d = ImageDraw.Draw(hoja)
    for i, n in enumerate(NOMBRES):
        x, y = (i % cols) * celda, (i // cols) * (celda + 34)
        im = icono(n, 110, (250, 204, 21) if i % 2 == 0 else (255, 255, 255))
        hoja.paste(im, (x + 20, y + 14), im)
        d.text((x + celda / 2, y + celda + 8), n, font=_fuente(15), fill=(148, 163, 184), anchor="mm")
    hoja.save(salida)
    print(f"Hoja de iconos: {salida} ({len(NOMBRES)} iconos)")


if __name__ == "__main__":
    main()
