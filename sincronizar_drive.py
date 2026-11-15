"""Trae del repo lo que produjo el agente en la nube y lo copia a Google Drive.

Corre en el PC (no en la nube). Hace `git pull`, busca los .mp4 de videos\\ y los
.png de banners\\ que aun no se copiaron, y los pasa a Drive para escritorio con
subir_drive.py (Mi unidad\\jdt technologics\\Videos y \\Banners). Lleva la cuenta
en .sincronizados.txt (no se sube al repo). Si el PC estuvo apagado varios dias,
copia todo lo pendiente de una vez.

Uso:
    py sincronizar_drive.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import subir_drive

CARPETA = Path(__file__).resolve().parent
REGISTRO = CARPETA / ".sincronizados.txt"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    r = subprocess.run(["git", "-C", str(CARPETA), "pull", "--ff-only", "-q"],
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print("AVISO: git pull fallo, se copia lo que ya hay en el PC:\n" + r.stderr.strip())

    base = subir_drive.encontrar_base()
    if base is None:
        print("ERROR: no encontre Mi unidad\\jdt technologics. Abre Drive para escritorio.")
        sys.exit(1)

    hechos = set(REGISTRO.read_text(encoding="utf-8").split("\n")) if REGISTRO.exists() else set()
    pendientes = [p for p in sorted((CARPETA / "videos").glob("*.mp4")) + sorted((CARPETA / "banners").glob("*.png"))
                  if not p.name.startswith(("prueba", "_")) and p.name not in hechos]
    if not pendientes:
        print("Nada nuevo para copiar.")
        return

    fallos = 0
    for origen in pendientes:
        destino = base / subir_drive.DESTINOS[origen.suffix.lower()] / origen.name
        try:
            destino.parent.mkdir(exist_ok=True)
            destino.write_bytes(origen.read_bytes())
        except OSError as e:
            print(f"ERROR copiando {origen.name}: {e}")
            fallos += 1
            continue
        hechos.add(origen.name)
        print(f"Copiado a Drive: {destino}")
    REGISTRO.write_text("\n".join(sorted(h for h in hechos if h)), encoding="utf-8")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
