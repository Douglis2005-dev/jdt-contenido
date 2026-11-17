"""Version liviana de un MP4 para subirlo a Google Drive con el conector (limite ~3 MB por archivo).

Uso:  python3 liviano.py videos/X.mp4 [--max-mb 2.8]
Escribe videos/X-liviano.mp4 (720x1280, voz intacta) calculando la tasa de bits para no pasar del tope, y
verifica el peso final. El MP4 original (alta calidad) NO se toca: ese es el que se queda en el repositorio.
Sube a Drive el -liviano.mp4 con el titulo del original (X.mp4).
"""
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ff = imageio_ffmpeg.get_ffmpeg_exe()
src = Path(sys.argv[1])
tope = float(sys.argv[sys.argv.index("--max-mb") + 1]) if "--max-mb" in sys.argv else 2.8
r = subprocess.run([ff, "-i", str(src)], capture_output=True, text=True, errors="replace")
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
audio_k = 64
video_k = int((tope * 8 * 1000 * 1000 / dur) / 1000 * 0.93 - audio_k)
dest = src.with_name(src.stem + "-liviano.mp4")
for intento in range(3):
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(src), "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
                    "-b:v", f"{video_k}k", "-maxrate", f"{int(video_k * 1.25)}k", "-bufsize", f"{video_k * 2}k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", f"{audio_k}k", "-ac", "2", "-movflags", "+faststart", str(dest)], check=True)
    mb = dest.stat().st_size / 1e6
    if mb <= tope:
        break
    video_k = int(video_k * tope / mb * 0.92)
print(f"{dest} {mb:.2f} MB ({dur:.1f} s, video {video_k} kbps)")
if mb > 3.0:
    raise SystemExit("Sigue pasando de 3 MB: baja --max-mb o acorta el video.")
