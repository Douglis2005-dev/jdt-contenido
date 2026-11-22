"""Validador del storyboard de retención para los Reels de JDT TECHNOLOGICS.

El guion conserva sus escenas de voz actuales. Este módulo valida el campo adicional
"direccion", que describe micro-momentos visuales independientes de las escenas habladas.

Uso:
    python3 retencion.py videos/AAAA-MM-DD-HHMM-tema.json

Esquema mínimo:
    "direccion": {
      "hook": "Promesa visual del primer segundo",
      "payoff": "Qué respuesta recibe el espectador al final",
      "familias": ["motion-graphics", "mixed-media"],
      "beats": [
        {"inicio": 0, "fin": 2, "funcion": "hook",
         "familia": "motion-graphics", "visual": "Titular que irrumpe"},
        ...
        {"inicio": 21, "fin": 23, "funcion": "cierre",
         "familia": "motion-graphics", "visual": "Payoff y CTA"}
      ]
    }

No renderiza ni agrega efectos automáticamente: comprueba que el plan que ejecutará
render_html.py tenga ritmo, cobertura temporal y coherencia narrativa.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FAMILIAS = {"motion-graphics", "vfx-tracking", "mixed-media", "ia"}
FUNCIONES = {"hook", "contexto", "tension", "demostracion", "giro",
             "recompensa", "respiro", "cierre", "payoff"}
MIN_DURACION = 15.0
MAX_DURACION = 24.0
MAX_BEAT = 3.2
MAX_HUECO = 0.35
TOLERANCIA_FINAL = 0.5


def _duracion(guion: dict) -> float | None:
    tiempos = guion.get("tiempos") or {}
    candidatos = (tiempos.get("duracion"), guion.get("duracion"))
    for valor in candidatos:
        try:
            n = float(valor)
            if n > 0:
                return n
        except (TypeError, ValueError):
            pass
    escenas = guion.get("escenas") or []
    duraciones = []
    for escena in escenas:
        try:
            duraciones.append(float(escena["duracion"]))
        except (KeyError, TypeError, ValueError):
            return None
    return sum(duraciones) if duraciones else None


def validar(guion: dict) -> dict:
    errores: list[str] = []
    avisos: list[str] = []
    direccion = guion.get("direccion")
    if not isinstance(direccion, dict):
        return {"ok": False, "errores": ['Falta el objeto "direccion" en el guion.'],
                "avisos": [], "beats": 0, "duracion": _duracion(guion)}

    duracion = _duracion(guion)
    if duracion is None:
        errores.append("No se pudo determinar la duración: agrega tiempos.duracion o duracion.")
    elif not MIN_DURACION <= duracion <= MAX_DURACION:
        errores.append(f"La duración ({duracion:.2f} s) debe estar entre {MIN_DURACION:g} y {MAX_DURACION:g} s.")

    for campo in ("hook", "payoff"):
        if not isinstance(direccion.get(campo), str) or not direccion[campo].strip():
            errores.append(f'Falta una descripción concreta en direccion.{campo}.')

    declaradas = direccion.get("familias")
    if not isinstance(declaradas, list) or not declaradas:
        declaradas = []
        errores.append('direccion.familias debe ser una lista con 2 o 3 familias.')
    if len(declaradas) < 2 or len(declaradas) > 3:
        errores.append("Selecciona 2 o 3 familias de efectos; no es necesario forzar las cuatro.")
    desconocidas = sorted(set(declaradas) - FAMILIAS)
    if desconocidas:
        errores.append("Familias desconocidas: " + ", ".join(desconocidas) + ".")
    if len(set(declaradas)) != len(declaradas):
        errores.append("direccion.familias contiene valores duplicados.")

    beats = direccion.get("beats")
    if not isinstance(beats, list):
        beats = []
        errores.append('direccion.beats debe ser una lista.')
    if not 6 <= len(beats) <= 12:
        errores.append(f"El storyboard debe tener entre 6 y 12 beats; tiene {len(beats)}.")

    normalizados = []
    familias_usadas = set()
    for indice, beat in enumerate(beats, 1):
        if not isinstance(beat, dict):
            errores.append(f"Beat {indice}: debe ser un objeto.")
            continue
        try:
            inicio, fin = float(beat["inicio"]), float(beat["fin"])
        except (KeyError, TypeError, ValueError):
            errores.append(f"Beat {indice}: inicio y fin deben ser números.")
            continue
        if inicio < 0 or fin <= inicio:
            errores.append(f"Beat {indice}: intervalo inválido ({inicio}, {fin}).")
        if fin - inicio > MAX_BEAT:
            errores.append(f"Beat {indice} dura {fin - inicio:.2f} s; máximo {MAX_BEAT:g} s.")
        if normalizados and inicio < normalizados[-1]["inicio"]:
            errores.append(f"Beat {indice}: los beats deben estar ordenados cronológicamente.")
        funcion = beat.get("funcion")
        familia = beat.get("familia")
        visual = beat.get("visual")
        if funcion not in FUNCIONES:
            errores.append(f"Beat {indice}: funcion debe ser uno de {', '.join(sorted(FUNCIONES))}.")
        if familia not in FAMILIAS:
            errores.append(f"Beat {indice}: familia desconocida '{familia}'.")
        else:
            familias_usadas.add(familia)
        if not isinstance(visual, str) or len(visual.strip()) < 8:
            errores.append(f"Beat {indice}: describe la acción visual concreta (mínimo 8 caracteres).")
        normalizados.append({"indice": indice, "inicio": inicio, "fin": fin,
                             "funcion": funcion, "familia": familia, "visual": visual or ""})

    if normalizados:
        primero = normalizados[0]
        if abs(primero["inicio"]) > 0.1:
            errores.append("El primer beat debe empezar en 0 s: el hook no puede tener intro.")
        if not 1.0 <= primero["fin"] <= 2.5:
            errores.append("El hook debe establecerse visualmente entre 1 y 2,5 s.")
        if primero["funcion"] != "hook":
            errores.append("El primer beat debe tener funcion='hook'.")
        if normalizados[-1]["funcion"] not in {"cierre", "payoff"}:
            errores.append("El último beat debe resolver la promesa o cerrar con el CTA.")
        if not any(b["funcion"] in {"giro", "recompensa", "demostracion", "payoff"} for b in normalizados[1:]):
            errores.append("Falta una demostración, giro o recompensa después del hook.")

        for actual, siguiente in zip(normalizados, normalizados[1:]):
            hueco = siguiente["inicio"] - actual["fin"]
            if hueco > MAX_HUECO:
                errores.append(f"Hay {hueco:.2f} s sin beat entre {actual['indice']} y {siguiente['indice']}.")
            if hueco < -0.05:
                errores.append(f"Los beats {actual['indice']} y {siguiente['indice']} se solapan más de 0,05 s.")
        ultimo = normalizados[-1]
        if duracion is not None and abs(ultimo["fin"] - duracion) > TOLERANCIA_FINAL:
            errores.append(f"El storyboard termina en {ultimo['fin']:.2f} s, pero el video dura {duracion:.2f} s.")
        if duracion is not None and normalizados[0]["inicio"] >= duracion:
            errores.append("El primer beat queda fuera de la duración del Reel.")

        vistas = [re.sub(r"\s+", " ", b["visual"].strip().lower()) for b in normalizados]
        if len(vistas) != len(set(vistas)):
            avisos.append("Hay descripciones visuales repetidas: comprueba que los beats cambien de verdad.")

    no_usadas = sorted(set(declaradas) - familias_usadas)
    no_declaradas = sorted(familias_usadas - set(declaradas))
    if no_usadas:
        errores.append("Familias declaradas pero no aplicadas en ningún beat: " + ", ".join(no_usadas) + ".")
    if no_declaradas:
        errores.append("Hay beats que usan familias no declaradas: " + ", ".join(no_declaradas) + ".")

    return {
        "ok": not errores,
        "duracion": round(duracion, 2) if duracion is not None else None,
        "beats": len(beats),
        "familias_declaradas": declaradas,
        "familias_usadas": sorted(familias_usadas),
        "errores": errores,
        "avisos": avisos,
    }


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1].startswith("-"):
        raise SystemExit(__doc__)
    ruta = Path(sys.argv[1])
    try:
        guion = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"No se pudo leer el guion {ruta}: {exc}")
    resultado = validar(guion)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if not resultado["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
