"""Motor 2 de JDT: videos hechos con HTML/CSS/JS dibujados por Chrome, cuadro a cuadro.

Es para cuando se quiere un acabado de "motion graphics premium": paneles de vidrio en 3D, metaballs,
cuadricula en perspectiva, mix-blend-mode, desenfoque de movimiento, aberracion cromatica, glitch, grano,
mascaras, particulas y camara 3D. El agente escribe una pagina HTML por video (ver html/jdt.js, html/jdt.css y
html/ejemplo.html) con una funcion render(t) DETERMINISTA: dibuja el estado exacto del instante t (en segundos).
Nada de animaciones CSS ni temporizadores.

Uso:
    python3 render_html.py videos/AAAA-MM-DD-HHMM-tema.html --audio videos/AAAA-MM-DD-HHMM-tema.mp3 --salida videos/AAAA-MM-DD-HHMM-tema.mp4
    python3 render_html.py pagina.html --duracion 24 --fotos 1.5,4,9,14,20 --salida /tmp/prueba   (solo cuadros de prueba PNG)
Opciones: --w 1080 --h 1920 (por defecto vertical) --fps 30 --retardo 0.3 (segundos antes de que empiece la voz)

La pagina debe definir:  window.DURACION = 24;  window.render = (t) => { ... };
Reglas que el script comprueba:
  * PALETA: se miran los cuadros renderizados; si hay colores fuera de la marca (azul marino, amarillo/dorado,
    blanco, grises azulados) el script se detiene. Nada de cian, rojo, violeta ni verde.
  * VOZ: sin --audio no genera el video (salvo --sin-audio para pruebas).
  * PESO: el MP4 sale con tope de bitrate (<= ~8 MB) para que Google Drive lo reciba.
"""
from __future__ import annotations

import colorsys
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

CARPETA = Path(__file__).resolve().parent
CHROME = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser") if Path(c).exists()), None)


def arg(nombre, defecto=None):
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else defecto


def fuera_de_paleta(img: Image.Image) -> float:
    """Fraccion de pixeles con color que no es de la marca. Marca = grises/blancos/negros, azul marino (matiz 205-250)
    y amarillo/dorado (matiz 35-55). Un pixel cuenta como 'fuera' si tiene color vivo y otro matiz."""
    a = np.asarray(img.convert("RGB").resize((270, 480)), dtype=np.float32) / 255
    mx, mn = a.max(2), a.min(2)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    vivo = (s > 0.38) & (mx > 0.30)
    ok = ((h >= 28) & (h <= 62)) | ((h >= 200) & (h <= 252))
    return float((vivo & ~ok).mean())


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        raise SystemExit(__doc__)
    if not CHROME:
        raise SystemExit("No hay Chrome/Chromium instalado en este entorno: usa render_video.py (motor 1).")
    from playwright.sync_api import sync_playwright
    html = Path(sys.argv[1]).resolve()
    W, H, FPS = int(arg("--w", 1080)), int(arg("--h", 1920)), int(arg("--fps", 30))
    audio = Path(arg("--audio")).resolve() if arg("--audio") else None
    fotos = [float(x) for x in arg("--fotos").split(",")] if arg("--fotos") else None
    sin_audio = "--sin-audio" in sys.argv
    if not fotos and not audio and not sin_audio:
        raise SystemExit("Falta --audio: TODO video lleva voz en off (genera la voz primero).")
    if audio and not fotos:
        guion = Path("videos") / (html.stem + ".json")
        if guion.exists():
            import json as _json
            datos_guion = _json.load(open(guion, encoding="utf-8"))
            if "--sin-validacion" not in sys.argv:
                val = str(datos_guion.get("validacion", ""))
                if not val:
                    raise SystemExit("Falta la validacion 3b con el modelo capaz ANTES del render completo. Hazla con los cuadros de "
                                     "prueba (--fotos) y escribe en el guion JSON \"validacion\": \"APROBADO\" o \"corregido: ...\".")
            try:
                from retencion import validar as validar_retencion
            except ImportError as exc:
                raise SystemExit(f"No se pudo cargar retencion.py; no se autoriza el render final sin validar el storyboard: {exc}")
            revision_retencion = validar_retencion(datos_guion)
            if not revision_retencion["ok"]:
                detalle = "; ".join(revision_retencion["errores"])
                raise SystemExit("Storyboard de retención no aprobado. Corrige videos/" + html.stem +
                                 ".json antes del render final: " + detalle)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    retardo = float(arg("--retardo", 0.3))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--disable-gpu", "--force-color-profile=srgb",
                                                            "--allow-file-access-from-files", "--hide-scrollbars"])
        pg = b.new_page(viewport={"width": W, "height": H})
        errores = []
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.goto(html.as_uri())
        pg.wait_for_function("typeof window.render === 'function'", timeout=15000)
        pg.evaluate("document.fonts && document.fonts.ready")
        if errores:
            raise SystemExit("La pagina tiene errores de JavaScript:\n  " + "\n  ".join(errores[:5]))
        dur = float(pg.evaluate("window.DURACION || 0"))
        if audio:
            r = subprocess.run([ff, "-i", str(audio)], capture_output=True, text=True, errors="replace")
            m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
            if m:
                dur = max(dur, int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) + retardo + (1.2 if retardo > 0 else 0.1))  # una mezcla de musica.py (retardo 0) ya trae su cola
        if not dur:
            dur = float(arg("--duracion", 20))
        if arg("--duracion"):
            dur = float(arg("--duracion"))

        def cuadro(t):
            pg.evaluate("t => window.render(t)", t)
            return pg.screenshot(type="jpeg", quality=92)

        if fotos:
            base = Path(arg("--salida", "/tmp/prueba"))
            base.parent.mkdir(parents=True, exist_ok=True)
            malos = []
            for t in fotos:
                ruta = f"{base}_{t:g}.png"
                Image.open(__import__("io").BytesIO(cuadro(t))).convert("RGB").save(ruta)
                f = fuera_de_paleta(Image.open(ruta))
                if f > 0.004:
                    malos.append((t, round(f * 100, 2)))
                print(ruta)
            if errores:
                print("AVISO JS:", errores[:3])
            if malos:
                raise SystemExit(f"Colores fuera de la paleta de JDT en los cuadros (segundo, % de pixeles): {malos}. "
                                 "Usa solo azul marino, amarillo/dorado, blanco y grises azulados (incluye glitch y aberracion).")
            return
        salida = Path(arg("--salida", "videos/salida.mp4"))
        salida.parent.mkdir(parents=True, exist_ok=True)
        tmp = salida.with_name(salida.stem + ".tmp.mp4")
        cmd = [ff, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "mjpeg", "-i", "-"]
        if audio:
            ms = int(retardo * 1000)
            cmd += ["-i", str(audio), "-af", f"adelay={ms}|{ms},apad", "-c:a", "aac", "-b:a", "192k"]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "2600k", "-bufsize", "5200k",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{dur:.3f}", str(tmp)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(dur * FPS)
        for i in range(n):
            img = cuadro(i / FPS)
            if i % 60 == 30:
                f = fuera_de_paleta(Image.open(__import__("io").BytesIO(img)))
                if f > 0.006:
                    proc.kill()
                    tmp.unlink(missing_ok=True)
                    raise SystemExit(f"Cuadro {i} (t={i / FPS:.1f}s): {f * 100:.1f}% de pixeles fuera de la paleta de JDT.")
            proc.stdin.write(img)
        proc.stdin.close()
        if proc.wait() != 0:
            tmp.unlink(missing_ok=True)
            raise SystemExit("FFmpeg fallo al codificar el video.")
        b.close()
    tmp.replace(salida)
    peso = salida.stat().st_size / 1e6
    if audio:
        r = subprocess.run([ff, "-i", str(salida), "-af", "volumedetect", "-vn", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
        m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
        if "Audio:" not in r.stderr or not m or float(m[1]) < -50:
            raise SystemExit("El video quedo SIN voz audible.")
    print(json.dumps({"video": str(salida), "duracion_s": round(dur, 2), "cuadros": n, "con_audio": bool(audio),
                      "peso_mb": round(peso, 2), "motor": "html"}, ensure_ascii=False))
    if peso > 9:
        print("AVISO: pesa mas de 9 MB; comprimelo antes de subir a Drive (ver INSTRUCCIONES paso 11).")


if __name__ == "__main__":
    main()
