#!/usr/bin/env python3
"""Folha de Belford Roxo — modelo STORY (1080x1920) com espaço para o adesivo de link.

Mesma identidade do Card Notícia: foto tratada, logo, marca d'água, selo www.folhadebel.com,
tag, título em CAIXA ALTA (Saira) e uma área livre com chamada "Leia a matéria completa"
logo acima da zona segura do Instagram, para colar o adesivo de link.

Uso:
  python3 story.py --foto foto.jpg --tag "EDUCAÇÃO | SERVIÇO" --titulo "..." --out story.jpg [--foco-x 0.5] [--foco 0.35] [--pb]
"""
import argparse, base64, html, io, pathlib
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BASE = pathlib.Path(__file__).parent
W, H = 1080, 1920


def b64(p_or_img, fmt="PNG"):
    if isinstance(p_or_img, Image.Image):
        buf = io.BytesIO(); p_or_img.save(buf, fmt, quality=92); data = buf.getvalue()
    else:
        data = pathlib.Path(p_or_img).read_bytes()
    return f"data:image/{'jpeg' if fmt == 'JPEG' else 'png'};base64," + base64.b64encode(data).decode()


def tratar(foto, fx=0.5, fy=0.35, pb=False, escuro=0.12, grao=14, seed=7):
    im = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int((im.width - W) * fx); y = int((im.height - H) * fy)
    im = im.crop((x, y, x + W, y + H))
    if pb: im = ImageOps.grayscale(im).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.10)
    if not pb: im = ImageEnhance.Color(im).enhance(1.04)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=2))
    a = np.asarray(im).astype(np.float32) * (1 - escuro)
    n = np.random.default_rng(seed).normal(0, 1, (H, W)).astype(np.float32)
    a += n[..., None] * grao * 0.7
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def html_story(fundo, tag, titulo):
    fonts = "".join(
        f"@font-face{{font-family:Saira;src:url('{(BASE/'fonts'/f'Saira-{n}.ttf').as_uri()}');font-weight:{w}}}"
        for n, w in [("Regular", 400), ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800)])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#0a0a0a;font-family:Saira,sans-serif;color:#fff}}
.s{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
.fundo{{position:absolute;inset:0;width:100%;height:100%}}
.sombra-topo{{position:absolute;inset:0 0 auto 0;height:420px;background:linear-gradient(rgba(0,0,0,.6),rgba(0,0,0,0))}}
.sombra-base{{position:absolute;inset:auto 0 0 0;height:1250px;background:linear-gradient(rgba(10,10,10,0) 0%,rgba(10,10,10,.55) 22%,rgba(10,10,10,.9) 45%,#0a0a0a 70%)}}
.logo{{position:absolute;left:72px;top:150px;width:230px}}
.marca{{position:absolute;left:0;right:0;top:640px;height:24px;background:url('{b64(BASE/'assets'/'marca-dagua.png')}') left center/auto 24px repeat-x}}
.conteudo{{position:absolute;left:72px;right:72px;top:860px}}
.site{{display:flex;justify-content:center;margin-bottom:40px}}
.site span{{display:inline-block;padding:10px 34px 12px;border-radius:999px;background:#1967f7;font-size:34px;line-height:1;box-shadow:0 6px 18px rgba(0,0,0,.28)}}
.site b{{font-weight:700}}
.tag{{display:flex;align-items:center;gap:20px;font-weight:700;font-size:28px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:32px}}
.tag::after{{content:"";width:80px;height:3px;background:#fff;flex:none}}
.titulo{{font-weight:800;font-size:80px;line-height:1.03;text-transform:uppercase;letter-spacing:-.012em;text-shadow:0 2px 18px rgba(0,0,0,.35)}}
.chamada{{position:absolute;left:0;right:0;top:1440px;display:flex;flex-direction:column;align-items:center;gap:14px}}
.chamada p{{font-size:34px;font-weight:600;letter-spacing:.02em}}
.seta{{width:46px;height:46px;animation:none}}
.espaco{{position:absolute;left:50%;top:1560px;width:560px;height:130px;transform:translateX(-50%);
  border:3px dashed rgba(255,255,255,.35);border-radius:28px}}
</style></head><body><div class="s">
<img class="fundo" src="{fundo}">
<div class="sombra-topo"></div><div class="sombra-base"></div>
<div class="marca"></div>
<img class="logo" src="{b64(BASE/'assets'/'logo-folha-belford-roxo.png')}">
<div class="conteudo">
  <div class="site"><span>www.<b>folhadebel</b>.com</span></div>
  {'<div class="tag">'+html.escape(tag)+'</div>' if tag else ''}
  <div class="titulo" id="t">{html.escape(titulo)}</div>
</div>
<div class="chamada"><p>Leia a matéria completa</p>
<svg class="seta" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v15M5 12l7 7 7-7"/></svg></div>
<div class="espaco"></div>
</div><script>
// título: no máximo 5 linhas e sem invadir a chamada do link
const t=document.getElementById('t');let s=80;
const lim=()=>t.getBoundingClientRect().bottom>1400||Math.round(t.getBoundingClientRect().height/(s*1.03))>5;
while(lim()&&s>56){{s-=2;t.style.fontSize=s+'px'}}
document.body.dataset.ok=1;
</script></body></html>"""


def render(foto, tag, titulo, out, **trat):
    from playwright.sync_api import sync_playwright
    page = html_story(b64(tratar(foto, **trat), "JPEG"), tag, titulo)
    (BASE / "out").mkdir(exist_ok=True)
    tmp = BASE / "out" / "_story.html"; tmp.write_text(page, encoding="utf-8")
    png = pathlib.Path(out).with_suffix(".png")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(tmp.as_uri()); pg.wait_for_selector("body[data-ok]"); pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(png), type="png"); b.close()
    if pathlib.Path(out).suffix.lower() in (".jpg", ".jpeg"):
        Image.open(png).convert("RGB").save(out, quality=92); png.unlink()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", required=True); ap.add_argument("--tag", default="")
    ap.add_argument("--titulo", required=True); ap.add_argument("--out", default="story.jpg")
    ap.add_argument("--foco-x", type=float, default=0.5); ap.add_argument("--foco", type=float, default=0.35)
    ap.add_argument("--pb", action="store_true")
    a = ap.parse_args()
    print(render(a.foto, a.tag, a.titulo, a.out, fx=a.foco_x, fy=a.foco, pb=a.pb))
