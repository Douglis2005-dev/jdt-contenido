/* Libreria JDT para el motor HTML. Todo es DETERMINISTA: las funciones reciben el tiempo (o un avance 0..1)
   y dibujan ese instante. Colores: solo la paleta de JDT. */
const JDT = (() => {
  const W = innerWidth, H = innerHeight;
  const PAL = { fondo: "#0A0E27", sup: "#131A3A", borde: "#2A3460", azul: "#5466B4", gris: "#94A3B8", amarillo: "#FACC15", dorado: "#EAB308", blanco: "#FFFFFF" };
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const E = {
    lineal: x => x,
    outExpo: x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
    inOutCubic: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
    outBack: x => { const c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
    outQuart: x => 1 - Math.pow(1 - x, 4),
    inExpo: x => x <= 0 ? 0 : Math.pow(2, 10 * x - 10),
    outElastic: x => x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - .75) * (2 * Math.PI / 3)) + 1,
  };
  /* progreso 0..1 de t entre a y b, con easing (por nombre o funcion) */
  const seg = (t, a, b, e = "outExpo") => (typeof e === "string" ? E[e] : e)(clamp((t - a) / (b - a)));
  const rnd = (s) => { const x = Math.sin(s * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const px = n => Math.round(n * 100) / 100;

  /* ---------- fondo: manchas de luz que se mueven, reticula de puntos y particulas ---------- */
  function fondo(ctx, t, o = {}) {
    const k = o.claro ?? 1;
    ctx.fillStyle = PAL.fondo; ctx.fillRect(0, 0, W, H);
    const manchas = [[.2, .25, 700, "84,102,180", .34], [.85, .55, 800, "250,204,21", .10 * k], [.4, .95, 900, "84,102,180", .28]];
    manchas.forEach(([x, y, r, c, a], i) => {
      const cx = W * x + Math.sin(t * .35 + i * 2) * 90, cy = H * y + Math.cos(t * .28 + i) * 110;
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0, `rgba(${c},${a})`); g.addColorStop(1, `rgba(${c},0)`);
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    });
    ctx.fillStyle = "rgba(255,255,255,.07)";
    for (let x = 30; x < W; x += 60) for (let y = 30; y < H; y += 60) ctx.fillRect(x, y, 3, 3);
    for (let i = 0; i < 46; i++) {
      const x = (rnd(i) * W + Math.sin(t * .6 + i) * 24) % W, y = ((rnd(i + 99) * H - t * (16 + rnd(i + 5) * 44)) % H + H) % H;
      ctx.fillStyle = i % 4 ? "rgba(255,255,255,.35)" : "rgba(250,204,21,.55)";
      ctx.beginPath(); ctx.arc(x, y, 2 + rnd(i + 7) * 3, 0, 7); ctx.fill();
    }
  }

  /* ---------- cuadricula en perspectiva estilo synthwave que avanza; opcional un camino dorado ---------- */
  function rejilla(ctx, t, o = {}) {
    const hor = o.horizonte ?? H * .46, vel = o.vel ?? .6, a = o.alfa ?? 1;
    const g = ctx.createLinearGradient(0, hor, 0, H);
    g.addColorStop(0, `rgba(84,102,180,${.0})`); g.addColorStop(1, `rgba(84,102,180,${.30 * a})`);
    ctx.fillStyle = g; ctx.fillRect(0, hor, W, H - hor);
    ctx.lineWidth = 2;
    for (let i = -14; i <= 14; i++) {                       // lineas que huyen al punto de fuga
      ctx.strokeStyle = `rgba(148,163,184,${.45 * a})`;
      ctx.beginPath(); ctx.moveTo(W / 2 + i * 26, hor); ctx.lineTo(W / 2 + i * 210, H); ctx.stroke();
    }
    for (let j = 0; j < 22; j++) {                          // lineas horizontales que avanzan hacia la camara
      const q = ((j + (t * vel) % 1) / 22), y = hor + Math.pow(q, 2.2) * (H - hor);
      ctx.strokeStyle = `rgba(250,204,21,${(.10 + .5 * q) * a})`;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    const gl = ctx.createLinearGradient(0, hor - 90, 0, hor + 40);
    gl.addColorStop(0, "rgba(250,204,21,0)"); gl.addColorStop(.7, `rgba(250,204,21,${.25 * a})`); gl.addColorStop(1, "rgba(250,204,21,0)");
    ctx.fillStyle = gl; ctx.fillRect(0, hor - 90, W, 130);
    if (o.camino != null && o.camino > 0) {                 // camino dorado que se dibuja (progreso 0..1)
      const pts = [[.5, 1.0], [.42, .86], [.6, .74], [.45, .64], [.55, .56], [.5, .47]];
      ctx.save(); ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.shadowColor = "#FACC15"; ctx.shadowBlur = 36;
      ctx.strokeStyle = "#FACC15"; ctx.lineWidth = 12; ctx.beginPath();
      const n = Math.max(1, Math.floor(o.camino * (pts.length - 1))), f = o.camino * (pts.length - 1) - n;
      pts.slice(0, n + 1).forEach(([x, y], i) => i ? ctx.lineTo(W * x, H * y) : ctx.moveTo(W * x, H * y));
      if (n < pts.length - 1) ctx.lineTo(W * lerp(pts[n][0], pts[n + 1][0], f), H * lerp(pts[n][1], pts[n + 1][1], f));
      ctx.stroke(); ctx.restore();
    }
  }

  /* ---------- metaball de vidrio: blobs que se funden. o = {x,y,r,n,k,blanco} ---------- */
  const _mb = document.createElement("canvas"); _mb.width = 270; _mb.height = 480;
  function metaballs(ctx, t, o = {}) {
    const w = 270, h = 480, c = _mb.getContext("2d"), n = o.n ?? 4, R = o.r ?? 90, cx = (o.x ?? .5) * w, cy = (o.y ?? .5) * h, esc = o.k ?? 1;
    const im = c.createImageData(w, h), d = im.data, bl = [];
    for (let i = 0; i < n; i++) bl.push([cx + Math.cos(t * .9 + i * 2.1) * R * .30 * esc, cy + Math.sin(t * 1.1 + i * 1.7) * R * .38 * esc, R * .27 * (1 - .1 * i) * Math.min(1, esc + .2)]);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      let f = 0; for (const [bx, by, br] of bl) { const dx = x - bx, dy = y - by; f += br * br / (dx * dx + dy * dy + 1); }
      const i = (y * w + x) * 4;
      if (f > 1) {                                           // dentro: vidrio azul con borde blanco y reflejo dorado
        const e = clamp((f - 1) * 3), borde = 1 - e, ref = clamp(((x - cx) * .7 + (y - cy) * -.7) / 60 + .5) * .6;
        d[i] = lerp(40, 255, borde * .9 + ref * .5); d[i + 1] = lerp(56, 250, borde * .9 + ref * .45); d[i + 2] = lerp(130, 255, borde * .85);
        if (f > 1.6) { d[i] = lerp(d[i], 250, .25); d[i + 1] = lerp(d[i + 1], 204, .25); d[i + 2] = lerp(d[i + 2], 21, .25); }
        d[i + 3] = 200 + 55 * borde;
      } else if (f > .55) { d[i] = 250; d[i + 1] = 204; d[i + 2] = 21; d[i + 3] = (f - .55) / .45 * 90; }   // halo
    }
    c.putImageData(im, 0, 0);
    ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high"; ctx.globalAlpha = o.alfa ?? 1;
    ctx.drawImage(_mb, 0, 0, W, H); ctx.restore();
  }

  /* ---------- texto ---------- */
  const letras = (el, texto, clase = "") => { el.innerHTML = [...texto].map(ch => ch === " " ? " " : `<span class="l ${clase}" style="display:inline-block">${ch}</span>`).join(""); return [...el.querySelectorAll(".l")]; };
  const revelar = (el, k, dir = "izq") => { el.style.clipPath = dir === "arriba" ? `inset(${(1 - k) * 100}% 0 0 0)` : `inset(0 ${(1 - k) * 100}% 0 0)`; el.style.opacity = k > 0 ? 1 : 0; };
  const tipear = (el, html, k) => {                          // escribe codigo con etiquetas <b class=k>..</b>; k = 0..1
    const plano = html.replace(/<[^>]+>/g, ""), n = Math.floor(plano.length * k); let vistos = 0, out = "", etiqueta = false, abre = "";
    for (let i = 0; i < html.length && vistos < n; i++) {
      const ch = html[i]; if (ch === "<") etiqueta = true; if (etiqueta) { out += ch; if (ch === ">") etiqueta = false; continue; }
      out += ch; vistos++;
    }
    el.innerHTML = out + (Math.floor(k * 40) % 2 || k >= 1 ? '<span style="color:#FACC15">▌</span>' : "");
  };
  /* ---------- efectos sobre un elemento ---------- */
  const camara = (el, { rx = 0, ry = 0, rz = 0, z = 0, s = 1, x = 0, y = 0, persp = 1400 } = {}) =>
    el.style.transform = `perspective(${persp}px) translate3d(${px(x)}px,${px(y)}px,${px(z)}px) rotateX(${px(rx)}deg) rotateY(${px(ry)}deg) rotateZ(${px(rz)}deg) scale(${px(s)})`;
  const desenfoque = (el, px_) => el.style.filter = px_ > .2 ? `blur(${px(px_)}px)` : "none";
  const aberracion = (el, k) => el.style.filter = k > .02 ? `drop-shadow(${px(8 * k)}px 0 0 rgba(250,204,21,.85)) drop-shadow(${px(-8 * k)}px 0 0 rgba(84,102,180,.9))` : "none";
  const glitch = (el, k, semilla = 1) => {                   // desplazamiento por franjas + doble imagen amarilla y azul
    if (k < .02) { el.style.clipPath = ""; el.style.transform = ""; return; }
    const y = rnd(semilla * 7.1) * 80, alto = 6 + rnd(semilla * 3.3) * 30;
    el.style.transform = `translateX(${px((rnd(semilla) - .5) * 70 * k)}px)`;
    el.style.filter = `drop-shadow(${px(10 * k)}px 0 0 rgba(250,204,21,.8)) drop-shadow(${px(-10 * k)}px 0 0 rgba(84,102,180,.9))`;
    el.style.clipPath = rnd(semilla * 2.2) > .5 ? `polygon(0 0,100% 0,100% ${y}%,0 ${y}%,0 ${y + alto}%,100% ${y + alto}%,100% 100%,0 100%)` : "";
  };
  /* ---------- capas globales ---------- */
  function grano(ctx, t, a = .06) {
    const n = 4000; ctx.save();
    for (let i = 0; i < n; i++) { const s = Math.floor(t * 30) * 9973 + i; ctx.fillStyle = rnd(s) > .5 ? `rgba(255,255,255,${a})` : `rgba(0,0,0,${a})`; ctx.fillRect(rnd(s + .5) * W, rnd(s + .7) * H, 3, 3); }
    ctx.restore();
  }
  function flash(el, k) { el.style.opacity = clamp(k); }          // un div blanco a pantalla completa
  /* barrido diagonal de bandas (azul, amarillo, fondo): k de 0 a 1 cubre y de 1 a 2 descubre */
  function barrido(ctx, k) {
    if (k <= 0 || k >= 2) return;
    const cols = ["#5466B4", "#FACC15", "#0A0E27"], pos = k <= 1 ? k : k - 1, ex = W + H * .6;
    cols.forEach((c, i) => {
      const a = clamp(pos * 1.4 - i * .18), ini = k <= 1 ? -ex : -ex + ex * clamp(pos * 1.4 - i * .18), fin = k <= 1 ? -ex + ex * a : 0;
      const x0 = k <= 1 ? 0 : ex * clamp(pos * 1.4 - i * .18), x1 = k <= 1 ? ex * a : ex;
      ctx.fillStyle = c; ctx.beginPath();
      ctx.moveTo(x0 - H * .6, 0); ctx.lineTo(x1, 0); ctx.lineTo(x1 - H * .6, H); ctx.lineTo(x0 - H * .6, H); ctx.closePath(); ctx.fill();
    });
  }
  /* capa fija tipo visor: esquinas, marca, timecode, nombre de la escena y barra de progreso */
  function hud(el, t, dur, escena = "") {
    if (!el.dataset.ok) {
      el.innerHTML = '<i class="esq" style="left:40px;top:40px;border-width:3px 0 0 3px"></i><i class="esq" style="right:40px;top:40px;border-width:3px 3px 0 0"></i><i class="esq" style="left:40px;bottom:40px;border-width:0 0 3px 3px"></i><i class="esq" style="right:40px;bottom:40px;border-width:0 3px 3px 0"></i><div class="marca mono">● JDT TECHNOLOGICS</div><div class="tc mono"></div><div class="esc mono"></div><div class="barra"><i></i></div>';
      el.dataset.ok = 1;
    }
    const m = Math.floor(t / 60), s = Math.floor(t % 60), f = Math.floor((t % 1) * 30);
    el.querySelector(".tc").textContent = `${String(m).padStart(2, 0)}:${String(s).padStart(2, 0)}:${String(f).padStart(2, 0)}`;
    el.querySelector(".esc").textContent = escena;
    el.querySelector(".barra i").style.width = `${clamp(t / dur) * 100}%`;
  }
  const lienzo = (z = 0) => { const c = document.createElement("canvas"); c.width = W; c.height = H; c.className = "capa"; c.style.zIndex = z; document.body.appendChild(c); return c.getContext("2d"); };   // z=0 fondo, z=5 efectos por encima
  return { W, H, PAL, clamp, lerp, E, seg, rnd, fondo, rejilla, metaballs, letras, revelar, tipear, camara, desenfoque, aberracion, glitch, grano, flash, barrido, hud, lienzo };
})();
