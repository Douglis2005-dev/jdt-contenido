"""Motor 2 de banners de JDT TECHNOLOGICS: posts 1080x1350 (PNG) dibujados por Chrome con HTML/CSS.

Reemplaza a render_banner.py como motor por defecto: en vez de UNA plantilla fija ofrece 9 ESTILOS de moda
(2026), todos con la paleta JDT, para que cada banner se vea distinto y actual. render_banner.py queda de respaldo.

Uso:
    python3 render_banner_html.py banners/AAAA-MM-DD-HHMM-tema.json
    python3 render_banner_html.py --lista                      (estilos disponibles)
    python3 render_banner_html.py --muestra /tmp/muestra       (un banner de ejemplo por estilo, para verlos)

El JSON es el mismo del banner clasico, mas "estilo" (texto, uno de la lista) y campos opcionales:
{
  "salida": "banners/2026-11-19-0300-tema.png",
  "estilo": "vidrio-liquido",                 (el que entrega estilos.py; ver --lista)
  "titulo": "Tu marca no se compra hecha: *se ajusta*",   (max. 10 palabras; *asteriscos* = acento amarillo)
  "subtitulo": "Una frase corta que explica el problema",   (opcional, max. 14 palabras)
  "puntos": ["Beneficio 1", "Beneficio 2", "Beneficio 3"],  (2 a 3, max. 32 caracteres cada uno)
  "cta": "Hablemos de tu proyecto",                        (opcional)
  "icono": "robot",                                        (opcional: lista en iconos.NOMBRES)
  "etiqueta": "TENDENCIA"                                  (opcional, 1 a 2 palabras cortas en mayusculas; un rotulo, nunca una cifra)
}
Reglas que el script comprueba: paleta (si hay colores fuera de la marca se detiene), textos que no caben
(los reduce hasta un minimo; si aun asi no caben dice cual acortar) y limites de palabras/caracteres.
Fuente: Montserrat (recursos/fuentes). Sin internet, sin descargas.
"""
from __future__ import annotations

import base64
import html as _html
import io
import json
import re
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

CARPETA = Path(__file__).resolve().parent
CHROME = next((c for c in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser") if Path(c).exists()), None)
W, H = 1080, 1350

# colores de la marca (RGB) para los iconos
NAVY, AMARILLO, BLANCO, GRIS, AZUL = (10, 14, 39), (250, 204, 21), (255, 255, 255), (148, 163, 184), (84, 102, 180)

ESTILOS = {
    "vidrio-liquido": "Paneles de vidrio esmerilado sobre formas liquidas doradas y azules (liquid glass).",
    "tipografia-gigante": "Letras enormes que ocupan el banner, palabras repetidas de fondo y cinta amarilla (maximalismo tipografico).",
    "bento": "Cuadricula de tarjetas redondeadas de distintos tamanos, como un tablero de app (bento).",
    "amarillo-total": "Pantalla completa amarilla con tinta azul marino: minimalismo audaz, una idea, mucho aire.",
    "collage-recorte": "Tiras de papel recortado, cinta adhesiva, notas pegadas y puntos de trama: mixed media artesanal.",
    "neobrutal": "Tarjetas con borde grueso y sombra dura desplazada, pegatinas y rejilla visible (neobrutalismo).",
    "cromo-dorado": "Letras doradas con volumen 3D sobre cuadricula en perspectiva y sol dorado (retrofuturismo).",
    "editorial": "Pagina de revista clara con titular enorme, lineas finas, notas al pie y subrayado a mano (editorial / zine).",
    "terminal-ui": "Ventana de interfaz con lineas de codigo y cursor: producto en pantalla (UI en movimiento).",
}

# --------------------------------------------------------------------------- utilidades

def _uri(img: Image.Image) -> str:
    b = io.BytesIO()
    img.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def _logo_uri(lado: int = 200) -> str:
    ruta = CARPETA / "recursos" / "logo.jpeg"
    if not ruta.exists():
        return ""
    img = Image.open(ruta).convert("RGBA").resize((lado, lado), Image.LANCZOS)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, lado - 1, lado - 1], radius=int(lado * .15), fill=255)
    img.putalpha(m)
    return _uri(img)


def _icono_uri(nombre: str | None, color: tuple, tam: int = 600) -> str:
    if not nombre:
        return ""
    sys.path.insert(0, str(CARPETA))
    import iconos
    if nombre not in iconos.ICONOS:
        raise SystemExit(f"El icono '{nombre}' no existe. Disponibles: {', '.join(iconos.NOMBRES)}.")
    return _uri(iconos.icono(nombre, tam, color))


def _esc(t: str) -> str:
    return _html.escape(t, quote=False)


def _rico(t: str) -> str:
    """Texto con *asteriscos* -> <span class='k'>. Escapa el resto."""
    partes = re.split(r"\*", t)
    return "".join(f"<span class='k'>{_esc(p)}</span>" if i % 2 else _esc(p) for i, p in enumerate(partes))


def _plano(t: str) -> str:
    return t.replace("*", "")


GRANO = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix type='saturate' values='0'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")

BASE_CSS = f"""
@font-face {{ font-family:"Montserrat"; src:url("{(CARPETA/'recursos'/'fuentes'/'Montserrat-Bold.ttf').as_uri()}"); font-weight:600 900; }}
@font-face {{ font-family:"Montserrat"; src:url("{(CARPETA/'recursos'/'fuentes'/'Montserrat-Regular.ttf').as_uri()}"); font-weight:400 500; }}
:root {{ --fondo:#0A0E27; --fondo2:#0D1230; --sup:#131A3A; --borde:#2A3460; --azul:#5466B4; --gris:#94A3B8;
        --amarillo:#FACC15; --dorado:#EAB308; --blanco:#FFFFFF; --papel:#F4F6FB; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:{W}px; height:{H}px; overflow:hidden; background:var(--fondo); }}
body {{ font-family:"Montserrat","Segoe UI",sans-serif; color:var(--blanco); position:relative; }}
.abs {{ position:absolute; }}
.t {{ font-weight:900; letter-spacing:-.035em; line-height:1.02; }}
.mono {{ font-family:"DejaVu Sans Mono","Consolas",monospace; text-transform:uppercase; letter-spacing:.16em; }}
.k {{ color:var(--amarillo); }}
.grano {{ position:absolute; inset:0; background:url("{GRANO}"); opacity:.07; mix-blend-mode:overlay; pointer-events:none; z-index:50; }}
.marca {{ position:absolute; display:flex; align-items:center; gap:16px; font-weight:800; font-size:30px; letter-spacing:.04em; z-index:20; }}
.marca i {{ width:22px; height:22px; border-radius:50%; background:var(--amarillo); display:block; }}
.pie {{ position:absolute; left:70px; right:70px; bottom:60px; height:150px; display:flex; align-items:center; gap:28px; z-index:20; }}
.pie img {{ width:130px; height:130px; border-radius:20px; flex:none; }}
.pie .txt {{ flex:1; display:flex; flex-direction:column; align-items:flex-end; }}
.pie .cta {{ font-weight:800; font-size:40px; letter-spacing:-.01em; }}
.pie .usr {{ display:inline-block; margin-top:12px; padding:10px 28px; border-radius:999px; background:var(--amarillo); color:var(--fondo); font-weight:800; font-size:32px; }}
"""

# --------------------------------------------------------------------------- estilos
# Cada funcion devuelve (css, html). Los elementos con data-fit se reducen solos hasta caber.

def _pie(b, logo, invertido=False, color_cta=None):
    cta = _esc(b.get("cta") or "Hablemos de tu proyecto")
    estilo = f" style='color:{color_cta}'" if color_cta else ""
    return (f"<div class='pie'><img src='{logo}'><div class='txt'><div class='cta' data-fit data-min='26' style='white-space:nowrap;max-width:560px'{estilo}>{cta}</div>"
            f"<span class='usr'>@technologicsjdt</span></div></div>")


def _sub(b, cls="sub", minimo=22, extra=""):
    return (f"<div class='{cls}' data-fit data-min='{minimo}' {extra}>{_esc(b['subtitulo'])}</div>") if b.get("subtitulo") else ""


def _sub_span(b):
    return f"<div class='sub' data-fit data-min='20'><span>{_esc(b['subtitulo'])}</span></div>" if b.get("subtitulo") else ""


def _linea_fit(texto, minimo=24, ancho=800):
    return f"<span data-fit data-min='{minimo}' style='white-space:nowrap;max-width:{ancho}px;display:block'>{_esc(texto)}</span>"


def estilo_vidrio_liquido(b, logo, ico):
    css = """
body { background:radial-gradient(120% 80% at 20% 0%, #131A3A 0%, #0A0E27 60%); }
.blob { position:absolute; border-radius:50%; filter:blur(64px); }
.panel { position:absolute; left:70px; right:70px; top:230px; height:540px; padding:48px 52px; border-radius:56px; display:flex; flex-direction:column; justify-content:center; gap:26px;
  background:linear-gradient(145deg, rgba(255,255,255,.20), rgba(255,255,255,.05)); border:2px solid rgba(255,255,255,.28);
  box-shadow:0 50px 120px rgba(0,0,0,.5), inset 0 3px 0 rgba(255,255,255,.35); backdrop-filter:blur(28px); }
.panel .t { font-size:92px; flex:0 1 auto; max-height:380px; min-height:0; }
.panel .k { color:#FDE68A; text-shadow:0 0 40px rgba(250,204,21,.55); }
.sub { flex:none; max-height:100px; font-size:34px; line-height:1.3; color:#E2E8F0; font-weight:500; }
.pill { position:absolute; left:70px; right:70px; height:92px; padding:0 44px; border-radius:999px; font-weight:700; font-size:38px; display:flex; align-items:center; gap:24px;
  background:linear-gradient(145deg, rgba(255,255,255,.16), rgba(255,255,255,.04)); border:2px solid rgba(255,255,255,.24); backdrop-filter:blur(18px); box-shadow:0 20px 60px rgba(0,0,0,.35); }
.pill b { width:24px; height:24px; border-radius:50%; background:var(--amarillo); flex:none; box-shadow:0 0 24px var(--amarillo); }
.ico { position:absolute; right:60px; top:70px; width:190px; height:190px; filter:drop-shadow(0 0 40px rgba(250,204,21,.45)); z-index:15; }
"""
    pts = "".join(f"<div class='pill' style='top:{800 + i * 104}px'><b></b>{_linea_fit(p, 26, 780)}</div>" for i, p in enumerate(b["puntos"]))
    ico_h = f"<img class='ico' src='{ico}'>" if ico else ""
    h = f"""
<div class='blob' style='width:600px;height:600px;left:-220px;top:760px;background:#FACC15;opacity:.62'></div>
<div class='blob' style='width:620px;height:620px;right:-200px;top:140px;background:#5466B4;opacity:.9'></div>
<div class='blob' style='width:420px;height:420px;left:-120px;top:150px;background:#5466B4;opacity:.7'></div>
<div class='blob' style='width:420px;height:420px;right:-60px;top:880px;background:#EAB308;opacity:.5'></div>
<div class='marca' style='left:70px;top:130px'><i></i>JDT TECHNOLOGICS</div>{ico_h}
<div class='panel'><div class='t' data-fit data-min='50'>{_rico(b['titulo'])}</div>{_sub(b)}</div>
{pts}{_pie(b, logo)}"""
    return css, h


def estilo_tipografia_gigante(b, logo, ico):
    palabras = _plano(b["titulo"]).upper().split()
    fondo = ""
    for i in range(7):
        w = palabras[i % len(palabras)]
        fondo += f"<div class='fila' style='top:{40 + i * 150}px;{'left:-140px' if i % 2 else 'left:-20px'};{'-webkit-text-stroke:3px rgba(148,163,184,.30);color:transparent' if i % 2 else 'color:rgba(255,255,255,.06)'}'>{_esc(w)} {_esc(w)} {_esc(w)}</div>"
    css = """
.fila { position:absolute; white-space:nowrap; font-weight:900; font-size:190px; letter-spacing:-.04em; line-height:1; }
.tit { position:absolute; left:60px; right:60px; top:215px; height:640px; font-size:150px; text-shadow:0 12px 50px rgba(10,14,39,.9); display:flex; align-items:center; }
.tit .t { width:100%; max-height:100%; }
.tit .k { background:var(--amarillo); color:var(--fondo); padding:0 18px; border-radius:12px; box-decoration-break:clone; -webkit-box-decoration-break:clone; text-shadow:none; }
.cinta { position:absolute; left:-80px; right:-80px; top:890px; height:140px; background:var(--amarillo); color:var(--fondo); transform:rotate(-3deg);
  display:flex; align-items:center; justify-content:center; box-shadow:0 30px 80px rgba(0,0,0,.5); }
.cinta .in { width:1000px; display:flex; align-items:center; justify-content:space-between; font-weight:900; font-size:40px; letter-spacing:-.01em; white-space:nowrap; }
.cinta em { font-style:normal; font-size:28px; margin:0 20px; }
.sub { position:absolute; left:70px; width:940px; top:1075px; font-size:28px; color:var(--gris); font-weight:500; white-space:nowrap; }
.ico { position:absolute; right:60px; top:70px; width:170px; height:170px; z-index:12; transform:rotate(8deg); }
"""
    pc = b["puntos"] if sum(len(x) for x in b["puntos"]) <= 66 else b["puntos"][:2]   # la cinta es angosta: si son largos, muestra 2
    cinta = "".join(f"<span>{_esc(p)}</span>" + ("<em>✦</em>" if i < len(pc) - 1 else "") for i, p in enumerate(pc))
    ico_h = f"<img class='ico' src='{ico}'>" if ico else ""
    h = f"""{fondo}
<div class='marca' style='left:70px;top:120px'><i></i>JDT TECHNOLOGICS</div>
<div class='tit'><div class='t' data-fit data-min='70'>{_rico(b['titulo'])}</div></div>
<div class='cinta'><div class='in' data-fit data-min='22'>{cinta}</div></div>{ico_h}{_sub(b)}{_pie(b, logo)}"""
    return css, h


def estilo_bento(b, logo, ico):
    css = """
.g { position:absolute; left:60px; right:60px; top:215px; width:960px; height:890px; display:grid; grid-template-columns:1fr 1fr; grid-template-rows:350px 270px 222px; gap:24px; }
.c { border-radius:44px; padding:36px; position:relative; overflow:hidden; border:2px solid var(--borde); background:linear-gradient(160deg,#131A3A,#0D1230); display:flex; flex-direction:column; justify-content:center; }
.c > .in { min-height:0; flex:1; display:flex; flex-direction:column; justify-content:center; }
.c.tit { grid-column:1 / 3; background:var(--amarillo); border-color:transparent; color:var(--fondo); }
.c.tit .t { font-size:96px; flex:1; min-height:0; } .c.tit .k { background:var(--fondo); color:var(--amarillo); padding:0 14px; border-radius:12px; -webkit-box-decoration-break:clone; box-decoration-break:clone; }
.c.ic { align-items:center; background:radial-gradient(circle at 50% 40%, #2A3460, #131A3A); } .c.ic img { width:74%; }
.c.sub { font-size:34px; line-height:1.3; font-weight:500; color:#E2E8F0; }
.c.pt { font-weight:800; font-size:40px; line-height:1.15; justify-content:space-between; }
.c.pt small { font-family:"DejaVu Sans Mono",monospace; color:var(--amarillo); font-size:26px; letter-spacing:.14em; flex:none; }
.c.pt .x { flex:1; min-height:0; margin-top:10px; display:flex; align-items:flex-end; }
.c.pt.a { background:linear-gradient(160deg,#5466B4,#2A3460); border-color:transparent; }
"""
    pts = list(b["puntos"])
    celdas = [f"<div class='c tit'><div class='t' data-fit data-min='48'>{_rico(b['titulo'])}</div></div>",
              f"<div class='c ic'>{'<img src=' + chr(39) + ico + chr(39) + '>' if ico else ''}</div>"]
    if b.get("subtitulo"):
        celdas.append(f"<div class='c sub'><div data-fit data-min='20' style='flex:1;min-height:0;display:flex;align-items:center'>{_esc(b['subtitulo'])}</div></div>")
        usar = pts[:2]; n0 = 1
    else:
        usar = pts[:3]; n0 = 1
    for i, p in enumerate(usar):
        celdas.append(f"<div class='c pt {'a' if i == 0 else ''}'><small>0{n0 + i}</small><div class='x'><div data-fit data-min='22' style='max-height:100%;width:100%'>{_esc(p)}</div></div></div>")
    h = f"""<div class='marca' style='left:70px;top:120px'><i></i>JDT TECHNOLOGICS</div>
<div class='g'>{''.join(celdas[:5])}</div>{_pie(b, logo)}"""
    return css, h


def estilo_amarillo_total(b, logo, ico):
    css = """
body { background:#FACC15; color:var(--fondo); }
.marca { color:var(--fondo); } .marca i { background:var(--fondo); }
.col { position:absolute; left:70px; right:70px; top:210px; height:900px; display:flex; flex-direction:column; gap:24px; }
.t { flex:1; min-height:0; font-size:150px; color:var(--fondo); }
.t .k { background:var(--fondo); color:var(--amarillo); padding:0 18px; border-radius:14px; -webkit-box-decoration-break:clone; box-decoration-break:clone; }
.fila { flex:none; display:flex; align-items:center; gap:30px; min-height:0; }
.sub { flex:1; max-height:130px; font-size:34px; font-weight:600; line-height:1.3; }
.ico { width:150px; height:150px; flex:none; margin-left:auto; }
.lista div { display:flex; gap:28px; align-items:center; border-top:4px solid var(--fondo); padding:12px 0; font-weight:800; font-size:38px; }
.lista small { font-family:"DejaVu Sans Mono",monospace; font-size:24px; font-weight:700; width:56px; }
.pie .usr { background:var(--fondo); color:var(--amarillo); } .pie .cta { color:var(--fondo); }
"""
    lista = "".join(f"<div><small>0{i + 1}</small>{_linea_fit(p, 24, 860)}</div>" for i, p in enumerate(b["puntos"]))
    ico_h = f"<img class='ico' src='{ico}'>" if ico else ""
    h = f"""<div class='marca' style='left:70px;top:120px'><i></i>JDT TECHNOLOGICS</div>
<div class='col'><div class='t' data-fit data-min='64'>{_rico(b['titulo'])}</div>
<div class='fila'>{_sub(b)}{ico_h}</div><div class='lista'>{lista}</div></div>{_pie(b, logo)}"""
    return css, h


def estilo_collage(b, logo, ico):
    css = """
body { background:#0D1230; background-image:radial-gradient(rgba(250,204,21,.22) 3px, transparent 3.5px); background-size:34px 34px; }
.tira { position:absolute; left:50px; top:225px; width:900px; height:400px; transform:rotate(-2.5deg); }
.tira .t { display:inline; font-size:92px; line-height:1.38; background:var(--papel); color:var(--fondo); padding:6px 22px; -webkit-box-decoration-break:clone; box-decoration-break:clone; box-shadow:0 10px 30px rgba(0,0,0,.45); }
.tira .k { background:var(--amarillo); color:var(--fondo); padding:0 8px; }
.cinta { position:absolute; width:190px; height:52px; background:rgba(250,204,21,.72); box-shadow:0 4px 14px rgba(0,0,0,.35); z-index:9; }
.nota { position:absolute; width:312px; padding:24px 26px 28px; background:var(--amarillo); color:var(--fondo); font-weight:800; font-size:32px; line-height:1.18; box-shadow:0 22px 50px rgba(0,0,0,.5); }
.nota small { display:block; font-family:"DejaVu Sans Mono",monospace; font-size:20px; margin-bottom:8px; letter-spacing:.14em; }
.nota.b { background:var(--papel); } .nota.c { background:#2A3460; color:#fff; }
.foto { position:absolute; width:290px; height:290px; border-radius:50%; background:var(--papel); border:10px solid var(--papel); box-shadow:0 20px 50px rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; }
.foto img { width:78%; }
.sub { position:absolute; left:80px; width:560px; top:690px; height:130px; font-size:32px; color:#E2E8F0; font-weight:600; line-height:1.3; transform:rotate(1.2deg); }
"""
    pos = [(52, 880, -3), (384, 905, 2), (716, 880, -2)]
    notas = ""
    for i, p in enumerate(b["puntos"]):
        x, y, r = pos[i]
        notas += (f"<div class='nota {['', 'b', 'c'][i]}' style='left:{x}px;top:{y}px;transform:rotate({r}deg)'><small>NOTA 0{i + 1}</small>"
                  f"<div data-fit data-min='22' style='max-height:76px'>{_esc(p)}</div></div>")
    ico_h = f"<div class='foto' style='right:70px;top:610px;transform:rotate(6deg)'><img src='{ico}'></div>" if ico else ""
    h = f"""<div class='marca' style='left:70px;top:110px'><i></i>JDT TECHNOLOGICS</div>
<div class='cinta' style='left:30px;top:200px;transform:rotate(-14deg)'></div><div class='cinta' style='right:50px;top:215px;transform:rotate(16deg)'></div>
<div class='tira' style='height:400px'><span class='t' data-fit-inline data-min='50'>{_rico(b['titulo'])}</span></div>{_sub(b, 'sub', 20)}{ico_h}{notas}
{_pie(b, logo)}"""
    return css, h


def estilo_neobrutal(b, logo, ico):
    css = """
body { background:#0A0E27; background-image:linear-gradient(rgba(148,163,184,.14) 2px, transparent 2px), linear-gradient(90deg, rgba(148,163,184,.14) 2px, transparent 2px); background-size:60px 60px; }
.col { position:absolute; left:60px; right:100px; top:235px; height:880px; display:flex; flex-direction:column; gap:26px; }
.card { background:#fff; color:var(--fondo); border:6px solid #000A2A; border-radius:22px; box-shadow:14px 14px 0 var(--amarillo); flex:none; }
.card.tit { flex:1; min-height:0; padding:34px 42px; display:flex; }
.card.tit .t { font-size:96px; flex:1; min-height:0; } .card.tit .k { background:var(--amarillo); color:var(--fondo); padding:0 10px; }
.card.sub { padding:20px 32px; font-size:32px; font-weight:700; line-height:1.28; background:#E2E8F0; max-height:140px; }
.card.pt { padding:0 32px; height:84px; font-weight:800; font-size:36px; display:flex; gap:24px; align-items:center; }
.card.pt b { width:44px; height:44px; border:5px solid var(--fondo); border-radius:10px; background:var(--amarillo); flex:none; display:flex; align-items:center; justify-content:center; font-size:28px; }
.sticker { position:absolute; width:170px; height:170px; border-radius:50%; background:var(--amarillo); border:6px solid #000A2A; box-shadow:8px 8px 0 #fff; display:flex; align-items:center; justify-content:center; transform:rotate(12deg); z-index:12; }
.sticker img { width:68%; }
.etq { position:absolute; left:80px; top:190px; background:var(--fondo); color:var(--amarillo); border:4px solid var(--amarillo); padding:8px 20px; font-family:"DejaVu Sans Mono",monospace; font-weight:700; font-size:26px; letter-spacing:.14em; z-index:14; transform:rotate(-3deg); }
.pie .usr { border:5px solid #000A2A; box-shadow:6px 6px 0 #fff; border-radius:14px; }
"""
    pts = "".join(f"<div class='card pt'><b>✓</b>{_linea_fit(p, 22, 700)}</div>" for p in b["puntos"])
    sub = f"<div class='card sub' data-fit data-min='20'>{_esc(b['subtitulo'])}</div>" if b.get("subtitulo") else ""
    st = f"<div class='sticker' style='right:24px;top:95px'><img src='{ico}'></div>" if ico else ""
    h = f"""<div class='marca' style='left:70px;top:105px'><i></i>JDT TECHNOLOGICS</div><div class='etq'>{_esc(b.get('etiqueta') or 'JDT')}</div>
<div class='col'><div class='card tit'><div class='t' data-fit data-min='50'>{_rico(b['titulo'])}</div></div>{sub}{pts}</div>{st}{_pie(b, logo)}"""
    return css, h


def estilo_cromo_dorado(b, logo, ico):
    css = """
body { background:linear-gradient(180deg,#0A0E27 0%,#131A3A 55%,#0A0E27 100%); }
.sol { position:absolute; left:50%; top:560px; width:620px; height:620px; margin-left:-310px; border-radius:50%;
  background:linear-gradient(180deg,#FACC15 0%,#EAB308 45%,#5466B4 100%); opacity:.9;
  -webkit-mask-image:repeating-linear-gradient(180deg,#000 0 38px,transparent 38px 50px); mask-image:repeating-linear-gradient(180deg,#000 0 38px,transparent 38px 50px); }
.suelo { position:absolute; left:-30%; right:-30%; top:870px; height:600px; transform-origin:50% 0; transform:perspective(520px) rotateX(62deg);
  background-image:linear-gradient(rgba(250,204,21,.75) 3px, transparent 3px), linear-gradient(90deg, rgba(250,204,21,.75) 3px, transparent 3px); background-size:90px 90px;
  -webkit-mask-image:linear-gradient(180deg,#000,transparent 92%); mask-image:linear-gradient(180deg,#000,transparent 92%); }
.horizonte { position:absolute; left:0; right:0; top:866px; height:6px; background:var(--amarillo); box-shadow:0 0 40px var(--amarillo); }
.tit { position:absolute; left:50px; right:50px; top:200px; height:360px; display:flex; align-items:center; }
.tit .t { width:100%; max-height:100%; text-align:center; font-size:124px;
  background:linear-gradient(180deg,#FFFFFF 0%,#FDE68A 38%,#FACC15 55%,#B45309 100%); -webkit-background-clip:text; background-clip:text; color:transparent;
  filter:drop-shadow(0 3px 0 #8a5a00) drop-shadow(0 7px 0 #6b4400) drop-shadow(0 11px 0 #4a2f00) drop-shadow(0 24px 30px rgba(0,0,0,.6)); }
.tit .k { background:linear-gradient(180deg,#FFFFFF 0%,#F4F6FB 40%,#94A3B8 60%,#5466B4 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.sub { position:absolute; left:90px; right:90px; top:585px; height:80px; text-align:center; font-size:30px; color:#E2E8F0; font-weight:600; line-height:1.3; text-shadow:0 4px 20px #0A0E27; z-index:5; }
.sub span { background:rgba(10,14,39,.72); padding:4px 18px; border-radius:14px; -webkit-box-decoration-break:clone; box-decoration-break:clone; line-height:1.6; }
.chips { position:absolute; left:50px; right:50px; top:882px; display:flex; flex-direction:column; gap:12px; align-items:center; z-index:6; }
.chip { padding:12px 48px; border-radius:999px; background:rgba(10,14,39,.82); border:3px solid var(--amarillo); color:#fff; font-weight:800; font-size:34px; box-shadow:0 0 30px rgba(250,204,21,.35); backdrop-filter:blur(6px); }
.ico { position:absolute; left:50%; top:680px; width:180px; height:180px; margin-left:-90px; z-index:4; filter:drop-shadow(0 0 30px rgba(250,204,21,.6)); }
"""
    chips = "".join(f"<div class='chip'>{_linea_fit(p, 22, 780)}</div>" for p in b["puntos"])
    ico_h = f"<img class='ico' src='{ico}'>" if ico else ""
    h = f"""<div class='sol'></div><div class='suelo'></div><div class='horizonte'></div>
<div class='marca' style='left:70px;top:105px'><i></i>JDT TECHNOLOGICS</div>
<div class='tit'><div class='t' data-fit data-min='60'>{_rico(b['titulo'])}</div></div>{_sub_span(b)}{ico_h}
<div class='chips'>{chips}</div>{_pie(b, logo)}"""
    return css, h


def estilo_editorial(b, logo, ico):
    css = """
body { background:var(--papel); color:var(--fondo); }
.marca { color:var(--fondo); } .marca i { background:var(--fondo); }
.vert { position:absolute; left:34px; top:300px; transform-origin:0 0; transform:rotate(90deg) translateY(-100%); font-size:22px; color:#5466B4; white-space:nowrap; }
.num { position:absolute; right:70px; top:120px; font-size:26px; color:#5466B4; }
.linea { position:absolute; left:70px; right:70px; height:3px; background:var(--fondo); }
.col { position:absolute; left:90px; right:60px; top:215px; height:560px; display:flex; flex-direction:column; gap:18px; }
.t { flex:1; min-height:0; font-size:132px; color:var(--fondo); letter-spacing:-.045em; }
.t .k { color:var(--fondo); background:linear-gradient(180deg,transparent 56%,var(--amarillo) 56%,var(--amarillo) 92%,transparent 92%); padding:0 4px; -webkit-box-decoration-break:clone; box-decoration-break:clone; }
.sq { flex:none; width:300px; height:30px; }
.sub { position:absolute; left:90px; width:540px; top:795px; height:190px; font-size:34px; font-weight:600; line-height:1.3; }
.circ { position:absolute; right:-80px; top:760px; width:400px; height:400px; border-radius:50%; background:var(--fondo); display:flex; align-items:center; justify-content:center; }
.circ img { width:54%; margin-left:-70px; }
.notas { position:absolute; left:90px; right:70px; top:1022px; font-size:26px; font-weight:600; line-height:1.4; }
.notas div { display:flex; gap:16px; } .notas sup { color:#5466B4; font-weight:800; }
.pie .usr { background:var(--fondo); color:var(--amarillo); } .pie .cta { color:var(--fondo); }
.pie { height:120px; bottom:36px; } .pie img { width:110px; height:110px; }
"""
    notas = "".join(f"<div><sup>{['¹', '²', '³'][i]}</sup>{_linea_fit(p, 20, 600)}</div>" for i, p in enumerate(b["puntos"]))
    circ = f"<div class='circ'><img src='{ico}'></div>" if ico else ""
    sq = "<svg class='sq' viewBox='0 0 300 30'><path d='M4 18 Q 40 2 75 16 T 150 14 T 225 16 T 296 10' fill='none' stroke='#FACC15' stroke-width='9' stroke-linecap='round'/></svg>"
    h = f"""<div class='marca' style='left:70px;top:105px'><i></i>JDT TECHNOLOGICS</div>
<div class='num mono'>{_esc(b.get('etiqueta') or 'EDICIÓN JDT')}</div><div class='vert mono'>SOFTWARE A MEDIDA · AUTOMATIZACIONES</div>
<div class='linea' style='top:190px'></div>
<div class='col'><div class='t' data-fit data-min='64'>{_rico(b['titulo'])}</div>{sq if not b.get('subtitulo') else ''}</div>{_sub(b, 'sub', 20)}{circ}
<div class='linea' style='top:1000px'></div><div class='notas'>{notas}</div>{_pie(b, logo)}"""
    return css, h


def estilo_terminal(b, logo, ico):
    css = """
body { background:#0A0E27; background-image:linear-gradient(rgba(84,102,180,.14) 2px, transparent 2px), linear-gradient(90deg, rgba(84,102,180,.14) 2px, transparent 2px); background-size:54px 54px; }
.tit { position:absolute; left:70px; right:70px; top:215px; height:340px; display:flex; align-items:center; }
.tit .t { width:100%; max-height:100%; font-size:100px; }
.win { position:absolute; left:60px; right:60px; top:660px; border-radius:30px; background:#0D1230; border:2px solid #2A3460; box-shadow:0 40px 100px rgba(0,0,0,.6), 0 0 0 10px rgba(250,204,21,.07); overflow:hidden; }
.bar { height:64px; background:#131A3A; display:flex; align-items:center; gap:14px; padding:0 26px; border-bottom:2px solid #2A3460; }
.bar i { width:18px; height:18px; border-radius:50%; background:#94A3B8; display:block; } .bar i:first-child { background:#FACC15; }
.bar span { margin-left:auto; font-family:"DejaVu Sans Mono",monospace; font-size:22px; color:#94A3B8; }
.cod { padding:30px 38px 34px; font-family:"DejaVu Sans Mono","Consolas",monospace; font-size:34px; line-height:1.75; }
.cod .c { color:#5466B4; filter:brightness(1.6); } .cod .y { color:#FACC15; } .cod .g { color:#94A3B8; }
.cur { display:inline-block; width:20px; height:36px; background:#FACC15; vertical-align:-6px; margin-left:6px; }
.ico { position:absolute; right:70px; top:70px; width:130px; height:130px; }
.sub { position:absolute; left:70px; width:940px; top:585px; font-size:28px; color:#94A3B8; font-weight:500; white-space:nowrap; }
"""
    lin = "".join(f"<div><span class='y'>✓</span> <span class='g'>{i + 1:02d}</span>  <span data-fit data-min='20' style='white-space:nowrap;max-width:740px;display:inline-block;vertical-align:bottom'>{_esc(p)}</span></div>" for i, p in enumerate(b["puntos"]))
    ico_h = f"<img class='ico' src='{ico}'>" if ico else ""
    h = f"""<div class='marca' style='left:70px;top:105px'><i></i>JDT TECHNOLOGICS</div>
<div class='tit'><div class='t' data-fit data-min='56'>{_rico(b['titulo'])}</div></div>{_sub(b, 'sub', 18)}
<div class='win'><div class='bar'><i></i><i></i><i></i><span>jdt — proyecto</span></div>
<div class='cod'><div class='c'>// {_esc(b.get('etiqueta') or 'listo para tu negocio')}</div>{lin}<div><span class='y'>$</span> <span class='g'>jdt</span> hablemos<span class='cur'></span></div></div></div>
{ico_h}{_pie(b, logo)}"""
    return css, h


FUNCIONES = {
    "vidrio-liquido": estilo_vidrio_liquido, "tipografia-gigante": estilo_tipografia_gigante, "bento": estilo_bento,
    "amarillo-total": estilo_amarillo_total, "collage-recorte": estilo_collage, "neobrutal": estilo_neobrutal,
    "cromo-dorado": estilo_cromo_dorado, "editorial": estilo_editorial, "terminal-ui": estilo_terminal,
}
# color del icono segun el fondo de cada estilo
COLOR_ICONO = {"vidrio-liquido": AMARILLO, "tipografia-gigante": AMARILLO, "bento": NAVY, "amarillo-total": NAVY,
               "collage-recorte": NAVY, "neobrutal": NAVY, "cromo-dorado": NAVY, "editorial": AMARILLO, "terminal-ui": AMARILLO}

AJUSTAR_JS = """
() => {
  const malos = [];
  const sobra = e => { const tol = Math.max(2, parseFloat(getComputedStyle(e).fontSize) * 0.09); return e.scrollHeight > e.clientHeight + tol || e.scrollWidth > e.clientWidth + 1; };
  document.querySelectorAll('[data-fit]').forEach(e => {
    const min = parseFloat(e.dataset.min || 24);
    let s = parseFloat(getComputedStyle(e).fontSize), n = 0;
    while (sobra(e) && s > min && n++ < 200) { s -= 2; e.style.fontSize = s + 'px'; }
    if (sobra(e)) malos.push((e.textContent || '').trim().slice(0, 40));
  });
  document.querySelectorAll('[data-fit-inline]').forEach(e => {
    const lim = parseFloat(e.parentElement.style.height || 470);
    const min = parseFloat(e.dataset.min || 40); let s = parseFloat(getComputedStyle(e).fontSize), n = 0;
    while (e.getBoundingClientRect().height > lim && s > min && n++ < 100) { s -= 2; e.style.fontSize = s + 'px'; }
    if (e.getBoundingClientRect().height > lim) malos.push((e.textContent || '').trim().slice(0, 40));
  });
  return malos;
}
"""


def validar(b: dict) -> None:
    if not str(b.get("titulo", "")).strip():
        raise SystemExit("Falta 'titulo'.")
    if len(_plano(b["titulo"]).split()) > 10:
        raise SystemExit("El titulo tiene mas de 10 palabras; acortalo.")
    if b.get("subtitulo") and len(b["subtitulo"].split()) > 14:
        raise SystemExit("El subtitulo tiene mas de 14 palabras; acortalo.")
    puntos = b.get("puntos") or []
    if not 2 <= len(puntos) <= 3:
        raise SystemExit("'puntos' debe tener 2 o 3 frases.")
    for p in puntos:
        if len(p) > 32:
            raise SystemExit(f"El punto '{p}' pasa de 32 caracteres; acortalo.")
    if b.get("etiqueta") and (len(b["etiqueta"]) > 22 or re.search(r"\d", b["etiqueta"])):
        raise SystemExit("'etiqueta' debe ser un rotulo corto (max. 22 caracteres) y sin cifras.")
    if b.get("estilo") not in FUNCIONES:
        raise SystemExit(f"'estilo' debe ser uno de: {', '.join(FUNCIONES)}.")


def pagina(b: dict) -> str:
    est = b["estilo"]
    css, cuerpo = FUNCIONES[est](b, _logo_uri(), _icono_uri(b.get("icono"), COLOR_ICONO[est]))
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{BASE_CSS}{css}</style></head>"
            f"<body>{cuerpo}<div class='grano'></div></body></html>")


def renderizar(b: dict, salida: Path) -> None:
    if not CHROME:
        raise SystemExit("No hay Chrome en este entorno: usa render_banner.py (motor clasico).")
    from playwright.sync_api import sync_playwright
    validar(b)
    with tempfile.TemporaryDirectory() as tmp:
        ruta = Path(tmp) / "banner.html"
        ruta.write_text(pagina(b), encoding="utf-8")
        with sync_playwright() as p:
            nav = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--disable-gpu", "--force-color-profile=srgb",
                                                                  "--allow-file-access-from-files", "--hide-scrollbars"])
            pg = nav.new_page(viewport={"width": W, "height": H})
            errores = []
            pg.on("pageerror", lambda e: errores.append(str(e)))
            pg.goto(ruta.as_uri())
            pg.evaluate("document.fonts && document.fonts.ready")
            pg.wait_for_timeout(150)
            malos = pg.evaluate(AJUSTAR_JS)
            pg.wait_for_timeout(100)
            salida.parent.mkdir(parents=True, exist_ok=True)
            pg.screenshot(path=str(salida), type="png")
            nav.close()
    if errores:
        raise SystemExit("Errores de JavaScript en la pagina: " + "; ".join(errores[:3]))
    if malos:
        raise SystemExit(f"No caben estos textos aunque se reduzcan: {malos}. Acortalos y vuelve a ejecutar.")
    sys.path.insert(0, str(CARPETA))
    try:
        from render_html import fuera_de_paleta
        f = fuera_de_paleta(Image.open(salida))
        if f > 0.004:
            raise SystemExit(f"Colores fuera de la paleta de JDT ({f * 100:.2f}% de pixeles) en el estilo '{b['estilo']}'. Prueba otro estilo.")
    except ImportError:
        pass


MUESTRA = {"titulo": "Tu negocio crece cuando tus procesos *se conectan*", "subtitulo": "Software a la medida que se adapta a tu forma de trabajar.",
           "puntos": ["Sin copiar y pegar", "Reportes automáticos", "Se adapta a tu proceso"], "cta": "Hablemos de tu proyecto",
           "icono": "robot", "etiqueta": "TENDENCIA"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if sys.argv[1] == "--lista":
        for k, v in ESTILOS.items():
            print(f"{k}: {v}")
        return
    if sys.argv[1] == "--muestra":
        carpeta = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/muestra")
        for k in FUNCIONES:
            renderizar({**MUESTRA, "estilo": k}, carpeta / f"{k}.png")
            print(carpeta / f"{k}.png")
        return
    ruta = Path(sys.argv[1]).resolve()
    b = json.loads(ruta.read_text(encoding="utf-8"))
    salida = Path(b.get("salida") or f"banners/{ruta.stem}.png")
    if not salida.is_absolute():
        salida = CARPETA / salida
    renderizar(b, salida)
    print(f"Banner guardado: {salida} (estilo {b['estilo']})")


if __name__ == "__main__":
    main()
