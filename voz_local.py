"""Voz en off LOCAL de respaldo para los Reels de JDT TECHNOLOGICS.

Sirve para que NINGUN video salga sin locucion: no usa internet ni creditos. Lee las
frases "voz" del guion, las dice con una voz en espanol (motor Piper, modelo guardado
en recursos/voz) y deja el guion listo para render_video.py:
  - "audio": ruta del MP3 generado
  - "duracion" de cada escena = lo que dura su frase (sincronia exacta voz-imagen)
  - "sincronia": "exacta" y "voz_motor": "local"

Uso:
    python3 voz_local.py videos/2026-11-16-0300-tema.json
    python3 voz_local.py videos/2026-11-16-0300-tema.json --velocidad 1.0   (por defecto 1.1; 1 = ritmo normal)

La primera vez instala solo el paquete piper-tts (de PyPI). Si algo falla, el mensaje
dice que hacer; el script termina con codigo 1.
"""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import wave
from array import array
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
MODELO = CARPETA / "recursos" / "voz" / "es_MX-claude-high.onnx"
PAUSA, ENTRADA, COLA = 0.24, 0.30, 0.9      # silencio entre escenas, al inicio y al final (s)
MIN_ESCENA, MIN_CIERRE = 2.6, 3.4           # una escena no dura menos que esto

# Como se LEE lo que en pantalla se escribe distinto (siglas, marca, anglicismos).
PRONUNCIA = [
    (r"\[[^\]]*\]", " "),                               # etiquetas de interpretacion de ElevenLabs
    (r"\*", ""),
    (r"@technologicsjdt", "arroba tecnolóyics jota de te"),
    (r"\bJDT\s+TECHNOLOGICS\b", "jota de te tecnolóyics"),
    (r"\bTECHNOLOGICS\b", "tecnolóyics"),
    (r"\bJDT\b", "jota de te"),
    (r"\bIA\b", "í a"),
    (r"\bTI\b", "te í"),
    (r"\bAPIs?\b", "a pe í"),
    (r"\bCRM\b", "ce erre eme"),
    (r"\bERP\b", "e erre pe"),
    (r"\bSEO\b", "seo"),
    (r"\bMVP\b", "eme uve pe"),
    (r"\bWhatsApp\b", "guatsap"),
    (r"\bsoftware\b", "sóftuer"),
    (r"\bonline\b", "onláin"),
    (r"\be-?mails?\b", "correo"),
    (r"\bapps\b", "aps"),
    (r"\bapp\b", "ap"),
]


def normalizar(texto: str) -> str:
    for patron, cambio in PRONUNCIA:
        texto = re.sub(patron, cambio, texto, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", texto).strip()


def cargar_motor():
    try:
        from piper import PiperVoice, SynthesisConfig
    except ImportError:
        for extra in ([], ["--break-system-packages"]):
            r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *extra, "piper-tts"], capture_output=True, text=True)
            if r.returncode == 0:
                break
        try:
            from piper import PiperVoice, SynthesisConfig
        except ImportError:
            raise SystemExit("No pude instalar piper-tts (pip install piper-tts). Detalle:\n" + r.stderr[-600:])
    if not MODELO.exists() or not MODELO.with_suffix(".onnx.json").exists():
        raise SystemExit(f"Falta el modelo de voz local: {MODELO} (y su .onnx.json). Debe venir en el repositorio.")
    return PiperVoice.load(str(MODELO)), SynthesisConfig


def decir(voz, config, texto: str) -> tuple[array, int]:
    """Devuelve (muestras de 16 bits, frecuencia) de una frase, sin silencios largos en las puntas."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voz.synthesize_wav(texto, w, syn_config=config)
    buf.seek(0)
    with wave.open(buf) as w:
        hz, canales = w.getframerate(), w.getnchannels()
        datos = array("h", w.readframes(w.getnframes()))
    if canales == 2:
        datos = array("h", datos[::2])
    umbral, n = 350, len(datos)
    ini = next((i for i in range(0, n, 32) if abs(datos[i]) > umbral), 0)
    fin = next((i for i in range(n - 1, 0, -32) if abs(datos[i]) > umbral), n - 1)
    margen = int(hz * 0.04)
    return datos[max(0, ini - margen): min(n, fin + margen)], hz


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    velocidad = float(sys.argv[sys.argv.index("--velocidad") + 1]) if "--velocidad" in sys.argv else 1.1
    args = [a for a in args if not re.fullmatch(r"[\d.]+", a)]
    ruta = Path(args[0]).resolve()
    guion = json.loads(ruta.read_text(encoding="utf-8"))
    escenas = guion.get("escenas") or []
    faltan = [i for i, e in enumerate(escenas, 1) if not str(e.get("voz", "")).strip()]
    if faltan:
        raise SystemExit(f"Las escenas {faltan} no tienen \"voz\". Cada escena debe traer la frase que dice la locucion.")

    voz, Config = cargar_motor()
    config = Config(length_scale=1 / max(0.7, min(1.4, velocidad)))
    hz, pista, duraciones = 22050, array("h"), []
    for i, e in enumerate(escenas):
        muestras, hz = decir(voz, config, normalizar(str(e["voz"])))
        ultima = i == len(escenas) - 1
        antes = int(hz * ENTRADA) if i == 0 else 0
        despues = int(hz * (COLA if ultima else PAUSA))
        minimo = int(hz * (MIN_CIERRE if ultima else MIN_ESCENA))
        total = max(minimo, antes + len(muestras) + despues)
        pista.extend(array("h", bytes(2 * antes)))
        pista.extend(muestras)
        pista.extend(array("h", bytes(2 * (total - antes - len(muestras)))))
        duraciones.append(round(total / hz, 3))

    pico = max((abs(x) for x in pista[::16]), default=0)
    if pico < 800:
        raise SystemExit("La voz local salio en silencio; revisa el modelo de recursos/voz.")

    salida = ruta.with_suffix(".mp3")
    wav = ruta.with_suffix(".voz.wav")
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(hz)
        w.writeframes(pista.tobytes())
    try:
        import imageio_ffmpeg
        r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(wav),
                            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-codec:a", "libmp3lame", "-b:a", "160k", str(salida)],
                           capture_output=True, text=True, errors="replace")
        if r.returncode != 0 or not salida.exists():
            raise RuntimeError(r.stderr[-400:])
        wav.unlink()
    except Exception as err:            # sin ffmpeg el WAV tambien sirve para render_video.py
        salida = wav.rename(ruta.with_suffix(".wav"))
        print(f"AVISO: no se pudo pasar a MP3 ({err}); queda en WAV.")

    try:
        relativa = salida.relative_to(CARPETA).as_posix()
    except ValueError:
        relativa = str(salida)
    guion["audio"] = relativa
    guion["sincronia"] = "exacta"
    guion["voz_motor"] = "local"
    for e, dur in zip(escenas, duraciones):
        e["duracion"] = dur
    ruta.write_text(json.dumps(guion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audio": relativa, "voz": "local (Piper es_MX)", "duracion_s": round(sum(duraciones), 2),
                      "escenas_s": duraciones, "guion_actualizado": str(ruta)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
