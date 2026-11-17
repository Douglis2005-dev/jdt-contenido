"""Musica y efectos de sonido generados por codigo (numpy/scipy), mezclados con la voz en off. Sin musica de terceros.

Uso:
    python3 musica.py --voz videos/X.mp3 --salida videos/X-mezcla.mp3 --cortes 4.2,8.2,12.2,16.2 --logo 16.2 [--duracion 26] [--retardo 0.3]
  --cortes   segundos donde hay transicion: lleva un "whoosh" en cada uno
  --logo     segundo en que aparece el logo: riser antes e impacto grave al llegar (opcional)
  --ritmo    t_ini,t_fin  (opcional) bombo y hi-hat en ese tramo (por ejemplo la parte de servicios)
La musica baja sola cuando habla la voz (sidechain) y hay un limitador al final. Luego se usa la mezcla como --audio
en render_html.py (con --retardo 0, porque la mezcla ya incluye el retardo de la voz).
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


def env(n, a=.01, r=.3):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] = np.linspace(1, 0, nr) if nr < n else e[-nr:]
    return e


def ruido_filtrado(n, f0, f1, q=3):
    x = np.random.default_rng(7).normal(0, 1, n)
    y = np.zeros(n)
    bloques = 40
    for i in range(bloques):
        a, b = i * n // bloques, (i + 1) * n // bloques
        f = f0 * (f1 / f0) ** (i / bloques)
        bb, aa = butter(2, [max(30, f * .7) / (SR / 2), min(.99, f * 1.3 / (SR / 2))], btype="band")
        y[a:b] = lfilter(bb, aa, x[a:b])
    return y / (np.abs(y).max() + 1e-9)


def main():
    voz = arg("--voz")
    if not voz:
        raise SystemExit(__doc__)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, "-i", voz], capture_output=True, text=True, errors="replace")
    import re
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    retardo = float(arg("--retardo", .3))
    dur = float(arg("--duracion", 0)) or (int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) + retardo + 1.2)
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # pad: acordes suaves (La menor - Fa - Do - Sol), cada 4 s
    acordes = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    for i in range(int(dur // 4) + 1):
        a, b = int(i * 4 * SR), min(n, int((i + 1) * 4 * SR + .5 * SR))
        if a >= n:
            break
        seg = np.zeros(b - a)
        tt = np.arange(b - a) / SR
        for f in acordes[i % 4]:
            seg += np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.003 * tt)
        out[a:b] += .10 * seg / 3 * env(b - a, .6, .8)
    # arpegio
    notas = [440, 523.3, 659.3, 523.3, 784, 659.3, 523.3, 659.3]
    paso = .25
    for i in range(int(dur / paso)):
        a = int(i * paso * SR)
        f = notas[(i + 4 * (int(i * paso // 4) % 4)) % 8] * [1, .79, 1.19, 1.5][int(i * paso // 4) % 4]
        L = int(.3 * SR)
        if a + L < n:
            tt = np.arange(L) / SR
            out[a:a + L] += .035 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9)
    # ritmo opcional
    if arg("--ritmo"):
        r0, r1 = (float(x) for x in arg("--ritmo").split(","))
        k = 0
        while r0 + k * .5 < r1:
            a = int((r0 + k * .5) * SR)
            L = int(.28 * SR)
            if a + L < n:
                tt = np.arange(L) / SR
                out[a:a + L] += .55 * np.sin(2 * np.pi * (48 + 90 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9)
                h = int((r0 + k * .5 + .25) * SR)
                if h + 2000 < n:
                    out[h:h + 2000] += .05 * np.random.default_rng(k).normal(0, 1, 2000) * np.exp(-np.arange(2000) / 300)
            k += 1
    # whooshes en cada corte
    for c in [float(x) for x in (arg("--cortes") or "").split(",") if x]:
        L = int(.7 * SR)
        a = int((c - .35) * SR)
        if 0 <= a and a + L < n:
            out[a:a + L] += .22 * ruido_filtrado(L, 400, 5000) * np.sin(np.linspace(0, np.pi, L)) ** 2
    # riser + impacto del logo
    if arg("--logo"):
        lg = float(arg("--logo"))
        L = int(1.6 * SR)
        a = int((lg - 1.6) * SR)
        if a >= 0:
            out[a:a + L] += .18 * ruido_filtrado(L, 300, 6000) * np.linspace(0, 1, L) ** 2
        b = int(lg * SR)
        L = int(1.4 * SR)
        if b + L < n:
            tt = np.arange(L) / SR
            out[b:b + L] += .8 * np.sin(2 * np.pi * (38 + 60 * np.exp(-tt * 14)) * tt) * np.exp(-tt * 3.2)
            out[b:b + L] += .06 * ruido_filtrado(L, 2000, 9000) * np.exp(-tt * 3)
    # shimmer de cierre
    for i, f in enumerate((1568, 2093, 2637)):
        a = int((dur - 2.2 + i * .12) * SR)
        L = int(1.2 * SR)
        if a > 0 and a + L < n:
            tt = np.arange(L) / SR
            out[a:a + L] += .03 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3)
    out = np.tanh(out * 1.2)
    base = Path(arg("--salida", "mezcla.mp3")).resolve()
    wav = base.with_suffix(".musica.wav")
    wavfile.write(wav, SR, (out / (np.abs(out).max() + 1e-9) * .9 * 32767).astype(np.int16))
    ms = int(retardo * 1000)
    filtro = (f"[0:a]adelay={ms}|{ms},apad,asplit=2[v1][v2];[1:a]volume=0.9[m];[m][v2]sidechaincompress=threshold=0.03:ratio=10:attack=20:release=400[md];"
              f"[v1][md]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[o]")
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", voz, "-i", str(wav), "-filter_complex", filtro, "-map", "[o]", "-t", f"{dur:.2f}",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(base)], check=True)
    wav.unlink(missing_ok=True)
    print(f"Mezcla lista: {base} ({dur:.1f} s). Usala como --audio con --retardo 0 en render_html.py")


if __name__ == "__main__":
    main()
