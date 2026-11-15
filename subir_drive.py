"""Copia un video o banner a Google Drive a traves de Google Drive para escritorio.

Busca la carpeta "jdt technologics" dentro de "Mi unidad" (o "My Drive") en
cualquier letra de unidad, o en la ruta indicada en la variable de entorno
JDT_DRIVE (por ejemplo G:\\Mi unidad\\jdt technologics). Los .mp4 van a Videos y
los .png/.jpg a Banners. Drive para escritorio los sube solo despues.

Uso:
    py subir_drive.py ARCHIVO [ARCHIVO ...]
    py subir_drive.py --donde          -> imprime la carpeta encontrada
Sale con codigo 1 y un mensaje claro si Drive para escritorio no esta listo.
"""
from __future__ import annotations

import os
import shutil
import string
import sys
from pathlib import Path

CARPETA_JDT = "jdt technologics"
DESTINOS = {".mp4": "Videos", ".png": "Banners", ".jpg": "Banners", ".jpeg": "Banners"}


def encontrar_base() -> Path | None:
    propia = os.environ.get("JDT_DRIVE")
    candidatos = [Path(propia)] if propia else []
    for letra in string.ascii_uppercase[2:]:  # D: en adelante, y C: al final
        for unidad in ("Mi unidad", "My Drive"):
            candidatos.append(Path(f"{letra}:/{unidad}/{CARPETA_JDT}"))
    for c in candidatos:
        try:
            if c.is_dir():
                return c
        except OSError:
            continue
    return None


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    base = encontrar_base()
    if base is None:
        print("ERROR: no encontre la carpeta de Google Drive para escritorio "
              f"('Mi unidad\\{CARPETA_JDT}'). Revisa que Drive para escritorio este "
              "instalado, abierto y con la sesion de technologicsjdt iniciada.")
        sys.exit(1)
    if sys.argv[1] == "--donde":
        print(base)
        return
    fallos = 0
    for arg in sys.argv[1:]:
        origen = Path(arg)
        sub = DESTINOS.get(origen.suffix.lower())
        if not origen.is_file() or sub is None:
            print(f"ERROR: {origen} no existe o no es .mp4/.png/.jpg")
            fallos += 1
            continue
        destino = base / sub / origen.name
        destino.parent.mkdir(exist_ok=True)
        shutil.copy2(origen, destino)
        if destino.stat().st_size != origen.stat().st_size:
            print(f"ERROR: la copia de {origen.name} quedo incompleta")
            fallos += 1
            continue
        print(f"Copiado a Drive: {destino}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
