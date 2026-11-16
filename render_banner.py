"""Generador de banners de JDT TECHNOLOGICS (post de Instagram 1080x1350, PNG).

Usa los mismos colores, fuentes, fondo y logo que render_video.py.

Uso:
    py render_banner.py banner.json

banner.json:
{
  "salida": "banners/2026-11-16-tema.png",
  "titulo": "¿Tu negocio sigue *copiando y pegando*?",     (max. 10 palabras; *asteriscos* = amarillo)
  "subtitulo": "Una frase corta que explica el problema",    (opcional, max. 14 palabras)
  "puntos": ["Beneficio 1", "Beneficio 2", "Beneficio 3"],   (2 a 3, max. 32 caracteres cada uno)
  "cta": "Hablemos de tu proyecto",                          (opcional)
  "icono": "robot"                                           (opcional: icono grande de fondo; lista en iconos.NOMBRES)
}
Colores: solo la paleta de la marca (los pone el script).
Si algo no cabe, el script termina con un error que dice que acortar.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import render_video as rv

W, H = 1080, 1350
MARGEN_INF = 1150  # por debajo de esto van el pie y las franjas diagonales


def validar(b: dict) -> None:
    if not str(b.get("titulo", "")).strip():
        raise SystemExit("Falta 'titulo'.")
    if len(rv.partir(b["titulo"])) > 10:
        raise SystemExit("El titulo tiene mas de 10 palabras; acortalo.")
    if b.get("subtitulo") and len(b["subtitulo"].split()) > 14:
        raise SystemExit("El subtitulo tiene mas de 14 palabras; acortalo.")
    puntos = b.get("puntos") or []
    if not 2 <= len(puntos) <= 3:
        raise SystemExit("'puntos' debe tener 2 o 3 frases.")
    for p in puntos:
        if len(p) > 32:
            raise SystemExit(f"El punto '{p}' pasa de 32 caracteres; acortalo.")


def texto_ajustado(d, xy, texto, ancho_max, tam, minimo, negrita=True, **kw):
    f = rv.fuente(tam, negrita)
    while f.getlength(texto) > ancho_max and f.size > minimo:
        f = rv.fuente(f.size - 2, negrita)
    if f.getlength(texto) > ancho_max:
        raise SystemExit(f"El texto '{texto}' no cabe; acortalo.")
    d.text(xy, texto, font=f, **kw)


def renderizar(b: dict) -> Image.Image:
    rv.W, rv.H = W, H  # el fondo y el titular del video leen estas medidas
    img = rv.crear_fondo().convert("RGBA")
    if b.get("icono"):      # motivo grande y tenue detras del titular, distinto en cada banner
        import iconos
        if b["icono"] not in iconos.ICONOS:
            raise SystemExit(f"El icono '{b['icono']}' no existe. Disponibles: {', '.join(iconos.NOMBRES)}.")
        motivo = iconos.icono(b["icono"], 400, rv.AZUL).copy()
        motivo.putalpha(motivo.getchannel("A").point(lambda v: int(v * 0.3)))
        img.alpha_composite(motivo, (W - 400 - 70, 215))
    d = ImageDraw.Draw(img)
    rv.dibujar_marca(d)

    # titular
    fin = rv.dibujar_titular(d, b["titulo"], 99, 250, tam_max=84, lineas_max=4)
    d.rounded_rectangle([80, fin + 30, 380, fin + 44], radius=7, fill=rv.AMARILLO)
    y = fin + 80
    if b.get("subtitulo"):
        f, tam, lineas = rv.componer(b["subtitulo"].replace("*", ""), W - 160, 42, 2)
        for n, linea in enumerate(lineas):
            d.text((80, y + n * int(tam * 1.3)), " ".join(p for p, *_ in linea), font=f, fill=rv.GRIS)
        y += len(lineas) * int(tam * 1.3) + 40

    # puntos con palomita
    puntos = b["puntos"]
    alto, hueco = 104, 18
    if y + len(puntos) * (alto + hueco) > MARGEN_INF:
        raise SystemExit("No caben titulo, subtitulo y puntos; acorta el titulo o quita el subtitulo.")
    for i, p in enumerate(puntos):
        yy = y + i * (alto + hueco)
        rv.tarjeta(d, [80, yy, W - 80, yy + alto], radio=26)
        d.rounded_rectangle([110, yy + 22, 174, yy + 86], radius=16, fill=rv.AMARILLO)
        rv.palomita(d, 142, yy + 54, 32, 1.0)
        texto_ajustado(d, (204, yy + 52), p, W - 80 - 204 - 30, 42, 28, fill=rv.BLANCO, anchor="lm")

    # pie: logo + llamado a la accion + usuario
    logo = rv._logo()
    if logo is not None:
        lado = 130
        img.alpha_composite(logo.resize((lado, lado), Image.LANCZOS), (W - 80 - lado, MARGEN_INF + 20))
    d = ImageDraw.Draw(img)
    cta = b.get("cta") or "Hablemos de tu proyecto"
    texto_ajustado(d, (W - 80 - 130 - 30, MARGEN_INF + 58), cta, 560, 40, 28, fill=rv.BLANCO, anchor="rm")
    f = rv.fuente(34)
    usuario = "@technologicsjdt"
    ancho = f.getlength(usuario) + 60
    x2 = W - 80 - 130 - 30
    d.rounded_rectangle([x2 - ancho, MARGEN_INF + 92, x2, MARGEN_INF + 146], radius=27, fill=rv.AMARILLO)
    d.text((x2 - ancho / 2, MARGEN_INF + 118), usuario, font=f, fill=rv.FONDO, anchor="mm")
    return img.convert("RGB")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ruta = Path(sys.argv[1]).resolve()
    b = json.loads(ruta.read_text(encoding="utf-8"))
    validar(b)
    # cada banner cambia de fondo y color de apoyo, igual que los videos
    n = b["estilo"] if isinstance(b.get("estilo"), int) else rv.puesto_del_guion(ruta, ruta.parent)
    rv.fijar_estilo(n, esquinas=["ne-so", "barra"])
    rv.ESTILO["entrada"] = "sube"
    salida = Path(b.get("salida") or f"banners/{ruta.stem}.png")
    if not salida.is_absolute():
        salida = rv.CARPETA / salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    renderizar(b).save(salida, optimize=True)
    print(f"Banner guardado: {salida}")


if __name__ == "__main__":
    main()
