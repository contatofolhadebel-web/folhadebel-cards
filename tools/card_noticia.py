#!/usr/bin/env python3
"""Folha de Belford Roxo — gerador do modelo "Card Notícia" (1080x1350, feed 4:5)."""
import argparse, base64, io, pathlib, html
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BASE = pathlib.Path(__file__).parent
W, H = 1080, 1350
LIMITE_AMPLIACAO = 1.6
ALTURA_FOTO_PEQUENA = 760
DIVISOR_DUPLA = 6


def cobrir(im, w, h, fx, fy):
    sc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


OLHOS_ALVO = 0.29


def dupla(fotos, foco_x, foco_y, rostos=None):
    fx = foco_x if isinstance(foco_x, (list, tuple)) else [foco_x] * 2
    fy = foco_y if isinstance(foco_y, (list, tuple)) else [foco_y] * 2
    if len(fx) == 1: fx = fx * 2
    if len(fy) == 1: fy = fy * 2
    wl = (W - DIVISOR_DUPLA) // 2; wr = W - DIVISOR_DUPLA - wl
    larg = [wl, wr]; x0s = [0, wl + DIVISOR_DUPLA]
    ims = [ImageOps.exif_transpose(Image.open(f)).convert("RGB") for f in fotos]
    base = Image.new("RGB", (W, H), (10, 10, 10))
    if not rostos:
        for i in range(2):
            base.paste(cobrir(ims[i], larg[i], H, fx[i], fy[i]), (x0s[i], 0))
        return base
    smin = [max(larg[i] / ims[i].width, H / ims[i].height) for i in range(2)]
    dist = [rostos[i][2] * ims[i].height for i in range(2)]
    alvo = max(dist[i] * smin[i] for i in range(2))
    esc = [alvo / dist[i] for i in range(2)]
    olho = [rostos[i][1] * ims[i].height * esc[i] for i in range(2)]
    faixas = [(olho[i] - (ims[i].height * esc[i] - H), olho[i]) for i in range(2)]
    lo = max(f[0] for f in faixas); hi = min(f[1] for f in faixas)
    y_olhos = min(max(OLHOS_ALVO * H, lo), hi) if lo <= hi else (lo + hi) / 2
    for i in range(2):
        im = ims[i].resize((round(ims[i].width * esc[i]), round(ims[i].height * esc[i])), Image.LANCZOS)
        cy = int(round(olho[i] - y_olhos)); cy = max(0, min(cy, im.height - H))
        cx = int(round(rostos[i][0] * im.width - larg[i] / 2)); cx = max(0, min(cx, im.width - larg[i]))
        base.paste(im.crop((cx, cy, cx + larg[i], cy + H)), (x0s[i], 0))
    return base


def tratar(foto, foco_x=0.5, foco_y=0.35, rostos=None, escuro=0.12, contraste=1.10, saturacao=1.04, grao=14, vinheta=0.28, seed=7, modo="auto", pb=False):
    if isinstance(foto, (list, tuple)) and len(foto) == 2:
        im = dupla(foto, foco_x, foco_y, rostos); modo = "dupla"
    else:
        foto = foto[0] if isinstance(foto, (list, tuple)) else foto
        foco_x = foco_x[0] if isinstance(foco_x, (list, tuple)) else foco_x
        foco_y = foco_y[0] if isinstance(foco_y, (list, tuple)) else foco_y
        im = None
    if im is None:
        im = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
        s_cover = max(W / im.width, H / im.height)
        if modo == "auto":
            modo = "pequena" if s_cover > LIMITE_AMPLIACAO else "cheia"
        if modo == "cheia":
            im = im.resize((round(im.width * s_cover), round(im.height * s_cover)), Image.LANCZOS)
            x = int((im.width - W) * foco_x); y = int((im.height - H) * foco_y)
            im = im.crop((x, y, x + W, y + H))
        else:
            s = max(W / im.width, min(ALTURA_FOTO_PEQUENA / im.height, s_cover))
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            x = int((im.width - W) * foco_x); hf = min(im.height, H)
            im = im.crop((x, 0, x + W, hf))
            fade = np.ones(hf, np.float32); n0 = int(hf * 0.34)
            t = np.linspace(0, 1, n0); fade[-n0:] = 1 - (t * t * (3 - 2 * t))
            base = Image.new("RGB", (W, H), (10, 10, 10))
            mask = Image.fromarray((np.repeat(fade[:, None], W, 1) * 255).astype(np.uint8))
            base.paste(im, (0, 0), mask); im = base
    if pb:
        im = ImageOps.grayscale(im).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(contraste)
    if not pb:
        im = ImageEnhance.Color(im).enhance(saturacao)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=2))
    a = np.asarray(im).astype(np.float32)
    a *= (1 - escuro)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    a *= (1 - vinheta * np.clip(d, 0, 1) ** 2)[..., None]
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)
    n = (n - 128) / 40
    lum = a.mean(axis=2, keepdims=True) / 255
    peso = 0.6 + 0.8 * lum * (1 - lum) * 4 / 4
    a += n[..., None] * grao * peso
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)), modo


def b64(path_or_img, fmt="PNG"):
    if isinstance(path_or_img, Image.Image):
        buf = io.BytesIO(); path_or_img.save(buf, fmt, quality=92); data = buf.getvalue()
    else:
        data = pathlib.Path(path_or_img).read_bytes()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def html_card(fundo_uri, tag, titulo, avatares, modo="cheia", urgente=False, linha_fina="", subir=0):
    fonts = "".join(
        f"@font-face{{font-family:Saira;src:url('{(BASE/'fonts'/f'Saira-{n}.ttf').as_uri()}');font-weight:{w}}}"
        for n, w in [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800), ("Black", 900)])
    av = "".join(f'<span class="av"><img src="{b64(a)}"></span>' for a in avatares)
    lf = f'<div class="linha-fina">{html.escape(linha_fina)}</div>' if linha_fina else ''
    hb = 820 + subir; hlf = 900 + subir
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#0a0a0a;font-family:Saira,sans-serif;color:#fff}}
.card{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
.fundo{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.sombra-topo{{position:absolute;inset:0 0 auto 0;height:300px;background:linear-gradient(rgba(0,0,0,.55),rgba(0,0,0,0))}}
.sombra-base{{position:absolute;inset:auto 0 0 0;height:{hb}px;background:linear-gradient(rgba(0,0,0,0) 0%,rgba(0,0,0,.28) 30%,rgba(0,0,0,.62) 62%,rgba(0,0,0,.84) 100%)}}
.com-lf .sombra-base{{height:{hlf}px;background:linear-gradient(rgba(0,0,0,0) 0%,rgba(0,0,0,.32) 28%,rgba(0,0,0,.68) 58%,rgba(0,0,0,.88) 100%)}}
.forte .sombra-base{{height:{hb}px;background:linear-gradient(rgba(10,10,10,0) 0%,rgba(10,10,10,.5) 18%,rgba(10,10,10,.92) 36%,#0a0a0a 52%)}}
.urgente{{display:flex;align-items:center;height:74px;margin:0 -64px 46px 162px;padding-left:0;overflow:hidden;white-space:nowrap;
  border-radius:8px 0 0 8px;background:linear-gradient(90deg,#d8132b 0%,#ea1c34 55%,#ee1f3c 100%);box-shadow:0 8px 22px rgba(0,0,0,.35)}}
.urgente span{{font-weight:800;font-style:italic;font-size:50px;line-height:1;letter-spacing:-.005em;text-transform:uppercase;flex:none;padding-right:6px}}
.urgente .b{{color:#fff}}
.urgente .t{{color:#a90f1d;opacity:.75}}
.logo{{position:absolute;left:64px;top:46px;width:200px}}
.marca{{position:absolute;left:0;right:0;top:50%;height:22px;transform:translateY(-50%);
  background:url('{b64(BASE/'assets'/'marca-dagua.png')}') left center/auto 22px repeat-x}}
.conteudo{{position:absolute;left:64px;right:64px;bottom:66px}}
.tag{{display:flex;align-items:center;gap:20px;font-weight:700;font-size:25px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:30px}}
.tag::after{{content:"";width:72px;height:3px;background:#fff;flex:none}}
.titulo{{font-weight:800;font-size:72px;line-height:1.03;text-transform:uppercase;letter-spacing:-.012em;text-shadow:0 2px 18px rgba(0,0,0,.35)}}
.linha-fina{{margin-top:26px;font-weight:400;font-size:36px;line-height:1.22;color:rgba(255,255,255,.92);text-shadow:0 2px 14px rgba(0,0,0,.4)}}
.siga{{display:flex;align-items:center;justify-content:center;gap:16px;margin-top:58px;font-size:29px;font-style:italic;font-weight:400}}
.com-lf .siga{{margin-top:46px}}
.siga b{{font-weight:700}}
.avs{{display:flex;gap:14px;margin-right:8px}}
.av{{position:relative;width:62px;height:62px;border-radius:50%;border:2px solid #fff;overflow:visible}}
.av img{{width:100%;height:100%;border-radius:50%;object-fit:cover}}
.av::after{{content:"";position:absolute;right:-6px;bottom:-4px;width:24px;height:24px;border-radius:50%;background:#7b3fe4;border:2px solid #fff}}
.ig{{width:36px;height:36px;flex:none}}
</style></head><body><div class="card {"forte" if modo=="pequena" else ""} {"com-lf" if linha_fina else ""}">
<img class="fundo" src="{fundo_uri}">
<div class="sombra-topo"></div><div class="sombra-base"></div>
<div class="marca"></div>
<img class="logo" src="{b64(BASE/'assets'/'logo-folha-belford-roxo.png')}">
<div class="conteudo">
  {('<div class="urgente"><span class="t" style="margin-left:-14px">TE</span>' + '<span class="b">URGENTE</span><span class="t">URGENTE</span>'*3 + '</div>') if urgente else ('<div class="tag">'+html.escape(tag)+'</div>' if tag else '')}
  <div class="titulo" id="t">{html.escape(titulo)}</div>
  {lf}
  <div class="siga">{'<span class="avs">'+av+'</span>' if av else ''}
    <svg class="ig" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.3"/><circle cx="17.6" cy="6.4" r="1.1" fill="#fff" stroke="none"/></svg>
    <span>Siga <b>@folhadebel</b> no Instagram</span></div>
</div></div>
<script>
const t=document.getElementById('t');let s=72;
const linhas=()=>Math.round(t.getBoundingClientRect().height/(s*1.03));
while(linhas()>4&&s>54){{s-=2;t.style.fontSize=s+'px'}}
document.body.dataset.ok=1;
</script></body></html>"""


def render(foto, tag, titulo, out, avatares=(), urgente=False, linha_fina="", subir=0, **trat):
    from playwright.sync_api import sync_playwright
    fundo, modo = tratar(foto, **trat)
    page_html = html_card(b64(fundo, "JPEG"), tag, titulo, list(avatares), modo, urgente, linha_fina, subir)
    (BASE / "out").mkdir(exist_ok=True)
    tmp = BASE / "out" / "_card.html"; tmp.write_text(page_html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(tmp.as_uri()); pg.wait_for_selector("body[data-ok]"); pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(out), type="png"); b.close()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", nargs="+", required=True); ap.add_argument("--tag", default="")
    ap.add_argument("--urgente", action="store_true")
    ap.add_argument("--titulo", required=True); ap.add_argument("--out", default="card.png")
    ap.add_argument("--linha-fina", default="")
    ap.add_argument("--avatar", action="append", default=[])
    ap.add_argument("--foco-x", type=float, nargs="+", default=[0.5]); ap.add_argument("--foco", type=float, nargs="+", default=[0.35])
    ap.add_argument("--escuro", type=float, default=0.12); ap.add_argument("--contraste", type=float, default=1.10)
    ap.add_argument("--saturacao", type=float, default=1.04); ap.add_argument("--grao", type=float, default=14)
    ap.add_argument("--vinheta", type=float, default=0.28)
    ap.add_argument("--rosto", action="append", default=[])
    ap.add_argument("--modo", choices=["auto", "cheia", "pequena"], default="auto")
    ap.add_argument("--pb", action="store_true")
    ap.add_argument("--subir-degrade", type=int, default=0)
    a = ap.parse_args()
    render(a.foto, a.tag, a.titulo, a.out, a.avatar, a.urgente, a.linha_fina, a.subir_degrade, foco_x=a.foco_x, foco_y=a.foco, escuro=a.escuro,
           contraste=a.contraste, saturacao=a.saturacao, grao=a.grao, vinheta=a.vinheta, modo=a.modo, pb=a.pb,
           rostos=[tuple(map(float, r.split(','))) for r in a.rosto] or None)
    print(a.out)
