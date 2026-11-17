"""Sincronia voz-escenas: calcula en que segundo del VIDEO empieza cada escena segun la voz en off real.

Por que existe: ElevenLabs hace pausas dentro de una misma frase (comas, puntos suspensivos, etiquetas como
[sighs] o [chuckles]), asi que «una pausa = un cambio de escena» falla y las escenas quedan corridas una frase.
Este script mira TODAS las pausas del audio y elige, entre ellas, las que mejor reparten el texto de cada escena
(cada escena debe hablarse a un ritmo de caracteres por segundo parecido al del resto). Las pausas largas pesan
mas, por eso en la locucion de ElevenLabs se pone [short pause] entre escena y escena.

METODO PREFERIDO (exacto): pasar --palabras con la transcripcion palabra por palabra de la voz (ElevenLabs Scribe,
creative_transcribe_audio conectado al nodo de la voz; guardar la lista "words" en videos/X.palabras.json). Entonces
cada escena se ubica por sus propias palabras. Sin --palabras se usa el metodo por pausas (aproximado).

Revision previa de la locucion (ANTES de gastar en voz):
    python3 sincronia.py videos/X.json --revisar
    Falla si la voz menciona marcas de terceros (marca.md lo prohibe) o si es muy larga para 15-24 s.

Uso:
    python3 sincronia.py videos/X.json [--palabras videos/X.palabras.json] [--audio videos/X.mp3] [--retardo 0.3] [--guardar]
Imprime JSON con:
    "inicios":  segundo del video en que debe entrar cada escena (ya incluye el retardo)
    "frases":   inicio y fin de la voz de cada escena en el video
    "cortes":   valor listo para musica.py --cortes (inicios sin el 0)
    "logo":     inicio de la ultima escena (cierre) para musica.py --logo
    "duracion": duracion recomendada para window.DURACION (fin de la voz + 1,2 s)
    "confianza": "alta" (por palabras), "media" o "baja" (por pausas; baja = el ritmo de alguna escena es raro)
Con --guardar escribe "tiempos" en el guion JSON. En el HTML usa exactamente esos inicios para las escenas.
"""
import json
import re
import subprocess
import sys

import imageio_ffmpeg


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


def tramos_de_voz(audio):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, "-hide_banner", "-i", audio, "-af", "silencedetect=noise=-35dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r)
    total = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    silencios = list(zip(ini, fin + [total] * (len(ini) - len(fin))))
    tramos, cur = [], 0.0
    for a, b in silencios:
        if a - cur > 0.05:
            tramos.append([cur, a])
        cur = b
    if total - cur > 0.05:
        tramos.append([cur, total])
    return tramos


def letras(s):
    s = re.sub(r"\[[^\]]*\]", "", s)
    return max(1, len(re.sub(r"[^\wáéíóúñü]", "", s, flags=re.I)))


def norm(w):
    return re.sub(r"[^\wáéíóúñü]", "", w.lower())


def por_palabras(textos, ruta_palabras):
    import difflib
    data = json.load(open(ruta_palabras, encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("words") or data.get("transcripts", [{}])[0].get("words", [])
    pal = [w for w in data if w.get("type", "word") == "word" and not w["text"].startswith("[") and norm(w["text"])]
    trans = [norm(w["text"]) for w in pal]
    guion, dueno = [], []
    for k, t in enumerate(textos):
        for w in re.sub(r"\[[^\]]*\]", "", t).split():
            if norm(w):
                guion.append(norm(w)); dueno.append(k)
    sm = difflib.SequenceMatcher(None, guion, trans, autojunk=False)
    mapa = {}
    for a, b, size in sm.get_matching_blocks():
        for d in range(size):
            mapa[a + d] = b + d
    if len(mapa) < 0.7 * len(guion):
        raise SystemExit("La transcripcion no coincide con el guion (menos del 70 % de palabras): usa el metodo por pausas.")
    out = []
    for k in range(len(textos)):
        idx = [mapa[i] for i in range(len(guion)) if dueno[i] == k and i in mapa]
        if not idx:
            raise SystemExit(f"No se encontraron en la transcripcion las palabras de la escena {k + 1}.")
        out.append((pal[min(idx)]["start"], pal[max(idx)]["end"]))
    return out


MARCAS = ["github", "google", "microsoft", "openai", "chatgpt", "gemini", "claude", "anthropic", "meta", "facebook",
          "instagram", "tiktok", "apple", "iphone", "amazon", "aws", "nvidia", "hugging", "youtube", "linkedin", "x.com",
          "twitter", "tesla", "samsung", "netflix", "spotify", "shopify", "notion", "slack", "zoom", "canva", "figma"]
PERMITIDAS = ["excel", "correo", "whatsapp"]


def revisar(textos):
    voz = " ".join(textos)
    pal = set(norm(w) for w in voz.split())
    malas = sorted(m for m in MARCAS if norm(m) in pal or (("." in m) and m in voz.lower()))
    letras_total = len(re.sub(r"\s+", " ", voz))
    errores = []
    if malas:
        errores.append(f"La voz nombra marcas de terceros: {', '.join(malas)}. Reescribe esas frases (ej.: 'un desarrollador', 'una herramienta abierta').")
    if not 220 <= letras_total <= 340:
        errores.append(f"La locucion tiene {letras_total} caracteres; debe tener entre 220 y 340 para durar 15-24 s.")
    print(json.dumps({"ok": not errores, "caracteres": letras_total, "errores": errores}, ensure_ascii=False, indent=2))
    if errores:
        raise SystemExit(1)


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        raise SystemExit(__doc__)
    ruta = sys.argv[1]
    g = json.load(open(ruta, encoding="utf-8"))
    audio = arg("--audio", g.get("audio"))
    retardo = float(arg("--retardo", 0.3))
    textos = [e.get("voz", "") for e in g["escenas"]]
    if "--revisar" in sys.argv:
        return revisar(textos)
    n = len(textos)
    if arg("--palabras"):
        tramos = por_palabras(textos, arg("--palabras"))
        frases, inicios = [], []
        for k, (a, b) in enumerate(tramos):
            a, b = a + retardo, b + retardo
            frases.append({"escena": k + 1, "voz_desde": round(a, 2), "voz_hasta": round(b, 2), "texto": textos[k]})
            inicios.append(0.0 if k == 0 else round(max(frases[k - 1]["voz_hasta"], a - 0.15), 2))
        return salida(ruta, g, frases, inicios, retardo, "alta", "palabras")
    tr = tramos_de_voz(audio)
    m = len(tr)
    if m < n:
        raise SystemExit(f"El audio tiene {m} tramos de voz y el guion {n} escenas: no se puede repartir. Revisa el audio.")
    habla = sum(b - a for a, b in tr)
    ritmo = sum(letras(t) for t in textos) / habla

    def costo(i, j, k):  # escena k = tramos i..j-1
        dur = tr[j - 1][1] - tr[i][0]
        esperado = letras(textos[k]) / ritmo
        c = ((dur - esperado) / max(esperado, 0.8)) ** 2
        if j < m:  # premio a cortar en una pausa larga
            c -= 0.6 * min(tr[j][0] - tr[j - 1][1], 1.0)
        return c

    INF = float("inf")
    best = [[INF] * (m + 1) for _ in range(n + 1)]
    prev = [[0] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for k in range(1, n + 1):
        for j in range(k, m - (n - k) + 1):
            for i in range(k - 1, j):
                if best[k - 1][i] < INF:
                    v = best[k - 1][i] + costo(i, j, k - 1)
                    if v < best[k][j]:
                        best[k][j], prev[k][j] = v, i
    cortes, j = [], m
    for k in range(n, 0, -1):
        i = prev[k][j]
        cortes.append((i, j))
        j = i
    cortes.reverse()

    frases, inicios, rara = [], [], False
    for k, (i, j) in enumerate(cortes):
        a, b = tr[i][0] + retardo, tr[j - 1][1] + retardo
        frases.append({"escena": k + 1, "voz_desde": round(a, 2), "voz_hasta": round(b, 2), "texto": textos[k]})
        r = letras(textos[k]) / (b - a)
        if not (0.55 * ritmo <= r <= 1.6 * ritmo):
            rara = True
        # la escena entra un poco antes de que empiece su frase (en la pausa previa)
        if k == 0:
            inicios.append(0.0)
        else:
            fin_prev = frases[k - 1]["voz_hasta"]
            inicios.append(round(max(fin_prev, a - 0.15), 2))
    return salida(ruta, g, frases, inicios, retardo, "baja" if rara else "media", "pausas")


def salida(ruta, g, frases, inicios, retardo, confianza, metodo):
    out = {
        "metodo": metodo,
        "inicios": inicios,
        "frases": frases,
        "cortes": ",".join(f"{x:.2f}" for x in inicios[1:]),
        "logo": inicios[-1],
        "duracion": round(frases[-1]["voz_hasta"] + 1.2, 2),
        "confianza": confianza,
    }
    if "--guardar" in sys.argv:
        g["tiempos"] = {"inicios": inicios, "retardo": retardo, "duracion": out["duracion"]}
        json.dump(g, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
