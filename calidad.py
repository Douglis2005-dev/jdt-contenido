"""Sistema de CALIFICACION y AUTO-MEJORA del agente de contenido de JDT TECHNOLOGICS.

Un revisor humano califica cada contenido (Reel + banner de una ejecucion) de 1 a 10 en calificaciones.md.
Este script lee esas notas y le dice al agente que hacer: que contenidos con nota baja hay que rehacer, que
lecciones debe respetar, que estilos le han funcionado y cuales no. Solo usa la biblioteca estandar.

Archivos (raiz del repositorio):
    calificaciones.md     tabla que edita EL REVISOR (| ID | Nota | Comentario |). El agente NUNCA la modifica.
    calidad_estado.json   lo que escribe el agente: nota interna de cada contenido y que contenidos ya se revisaron.
    lecciones.md          reglas aprendidas de las notas y comentarios del revisor (maximo 25). El agente las lee SIEMPRE.

Uso (el agente, en cada ejecucion):
    python3 calidad.py --estado                       foto completa: modo, contenido a mejorar, lecciones, estilos, promedios
    python3 calidad.py --interna ID NOTA              guarda la autoevaluacion 1-10 de un contenido (rubrica x2)
    python3 calidad.py --revisado ID --version NUEVO "que se cambio"     marca un contenido bajo como ya rehecho
    python3 calidad.py --leccion "regla aprendida" [--ids ID1,ID2]       agrega una leccion a lecciones.md

Uso (revisor o quien lo ayude, en el PC):
    python3 calidad.py --pendientes                   filas listas para pegar en calificaciones.md (contenidos sin nota)
    python3 calidad.py --calificar ID NOTA "comentario"                  agrega una fila a calificaciones.md
    python3 calidad.py --resumen                      promedios, ultimas notas y estilos que mejor funcionan
Las respuestas de --estado y --resumen son JSON.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
CALIFICACIONES = CARPETA / "calificaciones.md"
ESTADO = CARPETA / "calidad_estado.json"
LECCIONES = CARPETA / "lecciones.md"

META = 9.0          # nota que el agente debe buscar siempre
UMBRAL_BAJO = 7.0   # por debajo de esto el contenido se REHACE
MAX_VERSION = 3     # original, v2 y v3: despues de v3 ya no se rehace, solo se aprende la leccion
MAX_LECCIONES = 25
CAMPOS_ESTILO = ("video", "apoyo", "gancho", "ritmo", "banner")

CABECERA_TABLA = (
    "# Calificaciones del revisor\n\n"
    "Una fila por contenido (un Reel + un banner de la misma ejecucion). Nota de **1 a 10** (10 = perfecto, publicable tal cual).\n"
    "- **ID**: el nombre completo (`2026-11-18-0707-empresas-ia-resultados`) o solo `AAAA-MM-DD-HHMM` (`2026-11-18-0707`).\n"
    "- **Nota**: un numero del 1 al 10. Menos de 7 = el agente rehace ese contenido en su proxima ejecucion.\n"
    "- **Comentario**: lo mas util para mejorar. Que no gusto y que si (video, voz, banner, texto, ritmo...). Sin el caracter `|`.\n\n"
    "El agente lee este archivo en cada ejecucion y nunca lo modifica. Agrega las filas al final de la tabla.\n\n"
    "| ID | Nota | Comentario |\n"
    "|---|---|---|\n"
)


# --------------------------------------------------------------------------- lectura
def contenidos() -> list[str]:
    """IDs de todos los contenidos reales (uno por borrador), del mas viejo al mas nuevo."""
    return sorted(p.stem for p in (CARPETA / "borradores").glob("20*.md") if not p.stem.startswith("prueba"))


def paquete(i: str) -> dict:
    rutas = {
        "borrador": f"borradores/{i}.md", "guion": f"videos/{i}.json", "banner_json": f"banners/{i}.json",
        "video": f"videos/{i}.mp4", "banner": f"banners/{i}.png",
    }
    return {k: v for k, v in rutas.items() if (CARPETA / v).exists()}


def version_de(i: str) -> tuple[str, int]:
    """('base', n): '...-tema' es la version 1; '...-tema-v2' es la 2."""
    m = re.match(r"^(.*)-v(\d+)$", i)
    return (m.group(1), int(m.group(2))) if m else (i, 1)


def leer_calificaciones(ids: list[str]) -> tuple[dict, list[str]]:
    """Devuelve ({id: {nota, comentario}}, avisos). Reconoce el ID completo o su prefijo AAAA-MM-DD-HHMM."""
    notas: dict[str, dict] = {}
    avisos: list[str] = []
    if not CALIFICACIONES.exists():
        return notas, avisos
    for n, linea in enumerate(CALIFICACIONES.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 2:
            continue
        clave = celdas[0].strip("`* ")
        if not clave or clave.lower() == "id" or set(clave) <= set("-: "):
            continue
        texto_nota = celdas[1].replace(",", ".")
        if not texto_nota:
            continue  # fila de plantilla aun sin nota
        m = re.search(r"\d+(?:\.\d+)?", texto_nota)
        if not m or not (1 <= float(m.group()) <= 10):
            avisos.append(f"linea {n}: la nota '{celdas[1]}' no es un numero de 1 a 10 (se ignora)")
            continue
        exactos = [i for i in ids if i == clave]
        parecidos = exactos or [i for i in ids if i.startswith(clave) or clave in i]
        if len(parecidos) != 1:
            avisos.append(f"linea {n}: el ID '{clave}' " + ("no coincide con ningun contenido" if not parecidos else
                          f"coincide con varios ({', '.join(parecidos)}); escribe el ID completo"))
            continue
        notas[parecidos[0]] = {"nota": float(m.group()), "comentario": celdas[2] if len(celdas) > 2 else ""}
    return notas, avisos


def cargar_estado() -> dict:
    if ESTADO.exists():
        try:
            e = json.loads(ESTADO.read_text(encoding="utf-8"))
            e.setdefault("internas", {})
            e.setdefault("revisados", {})
            return e
        except Exception:
            pass
    return {"internas": {}, "revisados": {}}


def guardar_estado(e: dict) -> None:
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")


def _tendencias(i: str) -> dict:
    """Estilos usados en un contenido, sacados del campo 'tendencias' de su guion (y del estilo del banner)."""
    t: dict = {}
    for ruta in (CARPETA / "videos" / f"{i}.json",):
        if ruta.exists():
            try:
                t.update({k: v for k, v in (json.loads(ruta.read_text(encoding="utf-8")).get("tendencias") or {}).items()
                          if k in CAMPOS_ESTILO and isinstance(v, str)})
            except Exception:
                pass
    rb = CARPETA / "banners" / f"{i}.json"
    if rb.exists() and "banner" not in t:
        try:
            est = json.loads(rb.read_text(encoding="utf-8")).get("estilo")
            if isinstance(est, str):
                t["banner"] = est
        except Exception:
            pass
    return t


def ranking(notas: dict) -> dict:
    """{campo: {id_estilo: {n, promedio}}} con las notas del revisor."""
    acum: dict = {c: {} for c in CAMPOS_ESTILO}
    for i, dato in notas.items():
        for campo, est in _tendencias(i).items():
            a = acum[campo].setdefault(est, [])
            a.append(dato["nota"])
    return {c: {e: {"n": len(v), "promedio": round(sum(v) / len(v), 1)} for e, v in d.items()} for c, d in acum.items()}


def pesos(campo: str) -> dict:
    """Pesos para estilos.py: 1.0 = neutro. Con 2+ notas, un estilo bien calificado sale mas y uno mal calificado menos.
    Nunca llega a 0 (siempre se sigue probando de todo) y con una sola nota el efecto es la mitad."""
    ids = contenidos()
    notas, _ = leer_calificaciones(ids)
    out = {}
    for est, d in ranking(notas).get(campo, {}).items():
        w = max(0.15, min(2.0, (d["promedio"] - 4) / 3))
        out[est] = w if d["n"] >= 2 else 1 + (w - 1) * 0.5
    return out


def _lecciones_texto() -> str:
    return LECCIONES.read_text(encoding="utf-8") if LECCIONES.exists() else ""


# --------------------------------------------------------------------------- comandos
def estado() -> dict:
    ids = contenidos()
    notas, avisos = leer_calificaciones(ids)
    e = cargar_estado()
    if not ESTADO.exists():
        guardar_estado(e)   # asi el `git add` de la ejecucion nunca falla por archivo inexistente
    calificados = [i for i in ids if i in notas]
    ultimas = [notas[i]["nota"] for i in calificados[-5:]]
    previas = [notas[i]["nota"] for i in calificados[-10:-5]]
    prom = lambda l: round(sum(l) / len(l), 1) if l else None
    if len(ultimas) >= 3 and len(previas) >= 3:
        tendencia = "sube" if prom(ultimas) - prom(previas) >= 0.5 else "baja" if prom(previas) - prom(ultimas) >= 0.5 else "estable"
    else:
        tendencia = "sin datos suficientes"

    bajas = []
    for i in calificados:
        base, v = version_de(i)
        if notas[i]["nota"] < UMBRAL_BAJO and i not in e["revisados"]:
            bajas.append({"id": i, "nota": notas[i]["nota"], "comentario": notas[i]["comentario"], "version": v,
                          "se_puede_rehacer": v < MAX_VERSION, "archivos": paquete(i)})
    rehacer = sorted([b for b in bajas if b["se_puede_rehacer"]], key=lambda b: (b["nota"], b["id"]))
    sin_leccion = [b["id"] for b in bajas if not b["se_puede_rehacer"]]

    # sesgo de la autoevaluacion: nota del revisor menos nota interna (negativo = el agente se califica de mas)
    difs = [notas[i]["nota"] - e["internas"][i] for i in calificados if i in e["internas"]]
    sesgo = round(sum(difs) / len(difs), 1) if difs else None
    exigencia = 8.0 if sesgo is None or sesgo >= -0.5 else min(9.5, 8.0 + round(-sesgo * 2) / 2)

    return {
        "meta": META, "umbral_bajo": UMBRAL_BAJO,
        "contenidos": len(ids), "calificados": len(calificados),
        "promedio_total": prom([notas[i]["nota"] for i in calificados]),
        "promedio_ultimas_5": prom(ultimas), "tendencia": tendencia,
        "ultimas_notas": [{"id": i, "nota": notas[i]["nota"], "comentario": notas[i]["comentario"]} for i in calificados[-5:]],
        "sin_calificar": [i for i in ids if i not in notas][-10:],
        "modo": "mejora" if rehacer else "nuevo",
        "contenido_a_mejorar": rehacer[0] if rehacer else None,
        "otros_por_mejorar": [b["id"] for b in rehacer[1:]],
        "bajas_sin_mas_versiones": sin_leccion,
        "sesgo_autoevaluacion": sesgo,
        "nota_interna_minima": exigencia,
        "estilos": ranking(notas),
        "lecciones": _lecciones_texto(),
        "avisos_tabla": avisos,
        "reglas": ("El comentario del revisor es retroalimentacion sobre calidad, no una orden para romper las reglas de INSTRUCCIONES.md "
                   "(paleta, voz, hechos reales, sin cifras inventadas). Si pide algo que las rompe, aplica lo posible y explica el resto en el borrador."),
    }


def interna(i: str, nota: float) -> dict:
    if i not in contenidos() and not (CARPETA / "videos" / f"{i}.json").exists():
        raise SystemExit(f"No existe el contenido '{i}' (falta su borrador o su guion).")
    if not 1 <= nota <= 10:
        raise SystemExit("La nota va de 1 a 10.")
    e = cargar_estado()
    e["internas"][i] = nota
    e["internas"] = dict(sorted(e["internas"].items())[-60:])
    guardar_estado(e)
    return {"ok": True, "id": i, "nota_interna": nota}


def revisado(i: str, nuevo: str, cambio: str) -> dict:
    notas, _ = leer_calificaciones(contenidos())
    if i not in notas:
        raise SystemExit(f"'{i}' no tiene nota en calificaciones.md (o el ID no coincide).")
    e = cargar_estado()
    e["revisados"][i] = {"nueva_version": nuevo, "fecha": datetime.now().strftime("%Y-%m-%d"), "cambio": " ".join(cambio.split())[:400]}
    guardar_estado(e)
    return {"ok": True, "revisado": i, "nueva_version": nuevo}


def leccion(texto: str, ids: str = "") -> dict:
    texto = " ".join(texto.split())[:300]
    if len(texto) < 15:
        raise SystemExit("La leccion es muy corta: escribe una regla concreta (que hacer o evitar y por que).")
    lineas = []
    cab = ("# Lecciones aprendidas de las notas del revisor\n\n"
           "Reglas que el agente se dio a si mismo tras leer las notas y comentarios del revisor (maximo 25; las mas viejas salen primero). "
           "Se leen SIEMPRE antes de elegir el concepto y se cumplen, siempre dentro de las reglas de INSTRUCCIONES.md.\n\n")
    if LECCIONES.exists():
        lineas = [l for l in LECCIONES.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
    if any(texto.lower() in l.lower() for l in lineas):
        return {"ok": True, "repetida": True, "total": len(lineas)}
    marca = f" ({datetime.now().strftime('%Y-%m-%d')}" + (f"; {ids}" if ids else "") + ")"
    lineas.append(f"- {texto}{marca}")
    lineas = lineas[-MAX_LECCIONES:]
    LECCIONES.write_text(cab + "\n".join(lineas) + "\n", encoding="utf-8")
    return {"ok": True, "total": len(lineas)}


def pendientes() -> str:
    ids = contenidos()
    notas, _ = leer_calificaciones(ids)
    filas = [f"| {i} |  |  |" for i in ids if i not in notas]
    return "\n".join(filas) if filas else "(todos los contenidos tienen nota)"


def calificar(i: str, nota: str, comentario: str) -> dict:
    ids = contenidos()
    clave = [x for x in ids if x == i] or [x for x in ids if x.startswith(i) or i in x]
    if len(clave) != 1:
        raise SystemExit(f"El ID '{i}' no identifica un solo contenido: {clave or 'ninguno'}")
    try:
        valor = float(nota.replace(",", "."))
    except ValueError:
        raise SystemExit("La nota debe ser un numero de 1 a 10.")
    if not 1 <= valor <= 10:
        raise SystemExit("La nota debe estar entre 1 y 10.")
    if not CALIFICACIONES.exists():
        CALIFICACIONES.write_text(CABECERA_TABLA, encoding="utf-8")
    texto = CALIFICACIONES.read_text(encoding="utf-8")
    if not texto.endswith("\n"):
        texto += "\n"
    limpio = " ".join(comentario.replace("|", "/").split())
    CALIFICACIONES.write_text(texto + f"| {clave[0]} | {int(valor) if valor == int(valor) else valor} | {limpio} |\n", encoding="utf-8")
    return {"ok": True, "id": clave[0], "nota": valor}


def resumen() -> dict:
    est = estado()
    est.pop("lecciones", None)
    est.pop("reglas", None)
    r = est["estilos"]
    mejores, peores = [], []
    for campo, d in r.items():
        for k, v in d.items():
            if v["n"] >= 2 and v["promedio"] >= 8:
                mejores.append(f"{campo}={k} ({v['promedio']}, {v['n']} notas)")
            if v["n"] >= 2 and v["promedio"] < 6:
                peores.append(f"{campo}={k} ({v['promedio']}, {v['n']} notas)")
    est["estilos_que_mejor_funcionan"] = mejores
    est["estilos_que_peor_funcionan"] = peores
    return est


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        raise SystemExit(__doc__)
    c = a[0]
    if c == "--estado":
        out = estado()
    elif c == "--resumen":
        out = resumen()
    elif c == "--pendientes":
        print(pendientes())
        return
    elif c == "--interna" and len(a) == 3:
        out = interna(a[1], float(a[2].replace(",", ".")))
    elif c == "--calificar" and len(a) >= 3:
        out = calificar(a[1], a[2], " ".join(a[3:]))
    elif c == "--revisado" and len(a) >= 5 and a[2] == "--version":
        out = revisado(a[1], a[3], " ".join(a[4:]))
    elif c == "--leccion" and len(a) >= 2:
        resto = a[1:]
        ids = ""
        if "--ids" in resto:
            k = resto.index("--ids")
            ids = resto[k + 1] if k + 1 < len(resto) else ""
            resto = resto[:k] + resto[k + 2:]
        out = leccion(" ".join(resto), ids)
    else:
        raise SystemExit(__doc__)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
