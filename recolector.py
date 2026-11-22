"""Recolector de tendencias de tecnologia y desarrollo de software.

Lee fuentes publicas con API abierta (Hacker News, dev.to, Lobsters, GitHub), descarta lo
que ya se uso en videos anteriores (historial.json) e imprime un JSON con los
temas mas populares del dia. Solo usa la biblioteca estandar de Python.

Uso:
    py recolector.py                  -> imprime los 15 mejores temas
    py recolector.py --max 25         -> cambia la cantidad
    py recolector.py --marcar URL "titulo"   -> registra un tema como usado
    py recolector.py --voz            -> voz que toca (Douglas pupi, Teno pupi, Juan, en ese orden; una por dia)
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
HISTORIAL = CARPETA / "historial.json"
ESTADO_VOZ = CARPETA / "voz_estado.json"
AGENTE = "tendencias-tech/1.0"
# Voces de la locucion (clonadas en la cuenta de ElevenLabs). Se alternan en este orden.
VOCES = [
    {"nombre": "Douglas pupi", "voice_id": "Qvk5mDvl4UUK5PrXXheQ"},
    {"nombre": "Teno pupi", "voice_id": "uxgGF2sgmrmx7FWDZmtU"},
    {"nombre": "Juan", "voice_id": "rX5fO2VkGJYiYGyfqt8r"},
]


def _get_json(url: str, timeout: int = 15):
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(peticion, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def hacker_news(limite: int = 30) -> list[dict]:
    ids = _get_json("https://hacker-news.firebaseio.com/v0/topstories.json")[:limite]

    def uno(i):
        try:
            return _get_json(f"https://hacker-news.firebaseio.com/v0/item/{i}.json")
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=10) as pool:
        items = [x for x in pool.map(uno, ids) if x and x.get("title")]
    return [
        {
            "fuente": "Hacker News",
            "titulo": x["title"],
            "url": x.get("url") or f"https://news.ycombinator.com/item?id={x['id']}",
            "puntos": x.get("score", 0),
            "comentarios": x.get("descendants", 0),
        }
        for x in items
    ]


def dev_to(limite: int = 20) -> list[dict]:
    datos = _get_json(f"https://dev.to/api/articles?top=1&per_page={limite}")
    return [
        {
            "fuente": "dev.to",
            "titulo": x["title"],
            "url": x["url"],
            "puntos": x.get("positive_reactions_count", 0),
            "comentarios": x.get("comments_count", 0),
            "resumen": x.get("description", ""),
            "etiquetas": x.get("tag_list", []),
        }
        for x in datos
    ]


def lobsters(limite: int = 25) -> list[dict]:
    datos = _get_json("https://lobste.rs/hottest.json")[:limite]
    return [
        {
            "fuente": "Lobsters",
            "titulo": x["title"],
            "url": x.get("url") or x["short_id_url"],
            "puntos": x.get("score", 0),
            "comentarios": x.get("comment_count", 0),
            "etiquetas": x.get("tags", []),
        }
        for x in datos
    ]


def github_nuevos(limite: int = 15) -> list[dict]:
    """Repositorios creados en los ultimos 7 dias con mas estrellas."""
    desde = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    datos = _get_json(
        "https://api.github.com/search/repositories"
        f"?q=created:%3E{desde}&sort=stars&order=desc&per_page={limite}"
    )
    return [
        {
            "fuente": "GitHub",
            "titulo": f"{x['full_name']}: {x.get('description') or ''}".strip(),
            "url": x["html_url"],
            "puntos": x.get("stargazers_count", 0),
            "comentarios": 0,
            "etiquetas": [x["language"]] if x.get("language") else [],
        }
        for x in datos.get("items", [])
    ]


# Temas propios de JDT: dolores reales del cliente ideal (marca.md) que se conectan con un
# servicio. No dependen de noticias ni de cifras externas, asi que SIEMPRE hay tema para
# promocionar a JDT aunque las fuentes de la nube fallen o ninguna noticia se pueda verificar.
# Al usarlos se marcan con su url "jdt:slug" como cualquier tema.
TEMAS_JDT = [
    ("hojas-de-calculo-dispersas", "Tu negocio vive en diez hojas de cálculo que nadie cuadra", "Software a medida"),
    ("sistemas-que-no-se-hablan", "Contabilidad, ERP y CRM que no se hablan: copiar y pegar todo el día", "Software a medida (integraciones por API)"),
    ("reportes-a-mano-gerencia", "El informe para gerencia que alguien arma a mano cada lunes", "Automatización de procesos (reportes automáticos)"),
    ("equipo-en-campo-sin-app", "Tu equipo en campo reporta por WhatsApp y fotos sueltas", "Apps móviles (apps internas para equipos en campo)"),
    ("web-que-no-aparece", "Tu página web existe, pero nadie la encuentra en Google", "Desarrollo web (SEO)"),
    ("reservas-por-chat", "Citas y reservas que se pierden entre mensajes de chat", "Apps móviles (reservas y citas)"),
    ("aprobaciones-por-correo", "Aprobaciones que se quedan atascadas en una cadena de correos", "Automatización de procesos (aprobaciones y notificaciones)"),
    ("software-generico-se-queda-corto", "Cuando el software genérico te obliga a cambiar tu proceso", "Software a medida («se adapta a tu proceso, no al revés»)"),
    ("portal-de-clientes", "Clientes que llaman diez veces para saber cómo va su pedido", "Software a medida (portales para clientes)"),
    ("documentos-a-mano", "Facturas y documentos que alguien transcribe dato por dato", "Automatización con IA (extraer datos de documentos, con revisión humana)"),
    ("catalogo-y-tienda-online", "Vender por catálogo en PDF cuando podrías tener tienda online", "Desarrollo web (catálogos y tiendas online)"),
    ("mvp-para-validar", "Tienes la idea de una app: pruébala con un MVP antes de gastar de más", "Apps móviles (prototipos y MVP)"),
    ("pagas-funciones-que-no-usas", "Pagas licencias llenas de funciones que nunca usas", "Software a medida (pagas solo lo que necesitas)"),
    ("control-de-tus-datos", "¿Quién controla los datos de tu negocio?", "Software a medida (más control sobre tus datos)"),
    ("como-trabaja-jdt", "Analizamos, desarrollamos, entregamos: así se construye tu sistema", "Proceso JDT en tres pasos"),
]


def temas_propios(limite: int = 5) -> list[dict]:
    """Temas propios de JDT aun no usados; si ya se usaron todos, los usados hace mas tiempo."""
    historial = cargar_historial()
    ultima_vez = {h["url"]: h.get("fecha", "") for h in historial}
    candidatos = [
        {
            "fuente": "JDT (marca.md)",
            "titulo": titulo,
            "url": f"jdt:{slug}",
            "servicio": servicio,
            "requiere_fuente_externa": False,
        }
        for slug, titulo, servicio in TEMAS_JDT
    ]
    # Primero los nunca usados (fecha vacia), luego los mas antiguos.
    candidatos.sort(key=lambda t: ultima_vez.get(t["url"], ""))
    return candidatos[:limite]


def cargar_historial() -> list[dict]:
    if HISTORIAL.exists():
        return json.loads(HISTORIAL.read_text(encoding="utf-8"))
    return []


def voz_de_turno() -> dict:
    """La voz que toca en esta ejecucion.

    Guarda en voz_estado.json la ultima voz asignada y cuando. Cada ejecucion nueva
    avanza a la siguiente voz; si se vuelve a pedir dentro de los 20 minutos
    siguientes, repite la misma (asi una ejecucion que pregunta dos veces no salta
    una voz). Las ejecuciones estan separadas por al menos una hora, y cada una pide la voz una sola vez.
    """
    ahora = datetime.now()
    estado = {}
    if ESTADO_VOZ.exists():
        estado = json.loads(ESTADO_VOZ.read_text(encoding="utf-8"))
    ids = [v["voice_id"] for v in VOCES]
    ultima = estado.get("voice_id")
    try:
        antes = datetime.fromisoformat(estado.get("asignada", ""))
    except ValueError:
        antes = None
    if ultima in ids and antes and ahora - antes < timedelta(minutes=20):
        return VOCES[ids.index(ultima)]
    siguiente = (ids.index(ultima) + 1) % len(VOCES) if ultima in ids else 0
    voz = VOCES[siguiente]
    ESTADO_VOZ.write_text(
        json.dumps({**voz, "asignada": ahora.isoformat(timespec="seconds")}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return voz


def marcar(url: str, titulo: str) -> None:
    historial = cargar_historial()
    historial.append(
        {"url": url, "titulo": titulo, "fecha": datetime.now(timezone.utc).isoformat()}
    )
    HISTORIAL.write_text(json.dumps(historial, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registrado: {titulo}")


def recolectar(maximo: int) -> dict:
    usados = {h["url"] for h in cargar_historial()}
    temas, errores = [], []
    for nombre, funcion in (
        ("Hacker News", hacker_news),
        ("dev.to", dev_to),
        ("Lobsters", lobsters),
        ("GitHub", github_nuevos),
    ):
        try:
            temas.extend(funcion())
        except Exception as e:
            errores.append(f"{nombre}: {e}")

    # Normaliza la popularidad dentro de cada fuente para poder compararlas.
    por_fuente: dict[str, int] = {}
    for t in temas:
        clave = t["fuente"]
        por_fuente[clave] = max(por_fuente.get(clave, 1), t["puntos"] + 2 * t["comentarios"])
    for t in temas:
        clave = t["fuente"]
        t["popularidad"] = round((t["puntos"] + 2 * t["comentarios"]) / por_fuente[clave], 3)

    vistos, unicos = set(), []
    for t in sorted(temas, key=lambda t: t["popularidad"], reverse=True):
        if t["url"] in usados or t["url"] in vistos:
            continue
        vistos.add(t["url"])
        unicos.append(t)

    return {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "total_encontrados": len(temas),
        "ya_usados_omitidos": len(usados),
        "errores": errores,
        "titulos_usados_recientes": [h["titulo"] for h in cargar_historial()[-20:]],
        "temas": unicos[:maximo],
        # Respaldo garantizado: si ningun tema de "temas" cumple los criterios o no se puede
        # verificar, se usa uno de estos (no necesitan fuente externa). Ver INSTRUCCIONES.md paso 3.
        "temas_propios_jdt": temas_propios(),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--max", type=int, default=15)
    parser.add_argument("--marcar", nargs=2, metavar=("URL", "TITULO"))
    parser.add_argument("--voz", action="store_true", help="imprime la voz que toca en esta ejecucion")
    args = parser.parse_args()
    if args.voz:
        print(json.dumps(voz_de_turno(), ensure_ascii=False))
    elif args.marcar:
        marcar(*args.marcar)
    else:
        print(json.dumps(recolectar(args.max), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
