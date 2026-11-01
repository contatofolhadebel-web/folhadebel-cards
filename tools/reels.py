#!/usr/bin/env python3
"""Folha de Belford Roxo — modelo REELS (1080x1920).

Duas camadas transparentes:
  intro  -> os 5 primeiros segundos: topo azul com "FOLHA" vazado + logo grande, marca d'água no meio,
            título, ícones das redes e degradê inferior.
  fixo   -> o resto do vídeo: só marca d'água no meio, degradê inferior fraquinho e ícones das redes.

Uso:
  # só os PNGs transparentes (sempre os dois)
  python3 reels.py --titulo "MOTORISTA DE ÔNIBUS..." --out-dir saida/
  # direto no vídeo
  python3 reels.py --titulo "..." --video entrada.mp4 --out-dir saida/
"""
import argparse, base64, html, pathlib, subprocess, json

BASE = pathlib.Path(__file__).parent
W, H = 1080, 1920
INTRO_SEG = 5.0
FADE_SEG = 0.35


def b64(p):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def html_reels(titulo, tipo):
    fonts = "".join(
        f"@font-face{{font-family:Saira;src:url('{(BASE/'fonts'/f'Saira-{n}.ttf').as_uri()}');font-weight:{w}}}"
        for n, w in [("Regular", 400), ("Bold", 700), ("ExtraBold", 800), ("Black", 900)])
    intro = tipo == "intro"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:transparent}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Saira,sans-serif;color:#fff}}
.r{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
.topo{{position:absolute;inset:0 0 auto 0;height:820px;
  background:linear-gradient(180deg,#4189ff 0%,#2a76fb 22%,#1967f7 42%,rgba(25,103,247,.55) 62%,rgba(25,103,247,0) 100%)}}
.vazado{{position:absolute;left:-4px;top:40px;font-weight:900;font-size:600px;line-height:1;letter-spacing:-.02em;white-space:nowrap;
  transform-origin:left top;color:transparent;-webkit-text-stroke:3px rgba(255,255,255,.30)}}
.logo{{position:absolute;left:50%;top:318px;width:390px;transform:translateX(-50%)}}
.base{{position:absolute;inset:auto 0 0 0;height:{1150 if intro else 760}px;
  background:linear-gradient(180deg,rgba(18,34,92,0) 0%,rgba(18,34,92,{.45 if intro else .22}) 35%,rgba(14,26,72,{.72 if intro else .42}) 100%)}}
.marca{{position:absolute;left:0;right:0;top:50%;height:24px;transform:translateY(-50%);
  background:url('{b64(BASE/'assets'/'marca-dagua.png')}') left center/auto 24px repeat-x}}
.titulo{{position:absolute;left:86px;right:86px;bottom:{H-1345}px;font-weight:800;font-size:62px;line-height:1.06;
  text-transform:uppercase;letter-spacing:-.008em;text-shadow:0 2px 18px rgba(0,0,0,.35)}}
.redes{{position:absolute;left:50%;top:1410px;width:282px;transform:translateX(-50%)}}
</style></head><body><div class="r">
{'<div class="topo"></div><div class="vazado">FOLHA</div>' if intro else ''}
<div class="base"></div>
<div class="marca"></div>
{f'<img class="logo" src="{b64(BASE/"assets"/"logo-folha-belford-roxo.png")}">' if intro else ''}
{f'<div class="titulo" id="t">{html.escape(titulo)}</div>' if intro else ''}
<img class="redes" src="{b64(BASE/'assets'/'redes-linha.png')}">
</div><script>
const v=document.querySelector('.vazado');if(v){{v.style.transform='scaleX('+(1290/v.getBoundingClientRect().width)+')'}}
const t=document.getElementById('t');
if(t){{let s=62;const n=()=>Math.round(t.getBoundingClientRect().height/(s*1.06));while(n()>4&&s>46){{s-=2;t.style.fontSize=s+'px'}}}}
document.body.dataset.ok=1;
</script></body></html>"""


def render_pngs(titulo, out_dir):
    from playwright.sync_api import sync_playwright
    out_dir = pathlib.Path(out_dir).resolve(); out_dir.mkdir(parents=True, exist_ok=True)
    outs = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for tipo in ("intro", "fixo"):
            tmp = out_dir / f"_{tipo}.html"; tmp.write_text(html_reels(titulo, tipo), encoding="utf-8")
            pg = b.new_page(viewport={"width": W, "height": H})
            pg.goto(tmp.as_uri()); pg.wait_for_selector("body[data-ok]"); pg.evaluate("document.fonts.ready")
            outs[tipo] = out_dir / f"reels-{'1-intro-5s' if tipo == 'intro' else '2-fixo'}.png"
            pg.screenshot(path=str(outs[tipo]), type="png", omit_background=True); pg.close(); tmp.unlink()
        b.close()
    return outs


def aplicar_no_video(video, intro_png, fixo_png, saida):
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                               "-show_streams", "-of", "json", str(video)]))
    dur = float(info["format"]["duration"])
    tem_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    st = INTRO_SEG - FADE_SEG
    fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v];"
          f"[1:v]format=rgba,fade=t=out:st={st}:d={FADE_SEG}:alpha=1[a];"
          f"[2:v]format=rgba,fade=t=in:st={st}:d={FADE_SEG}:alpha=1[b];"
          f"[v][a]overlay=0:0:shortest=1[va];[va][b]overlay=0:0:shortest=1,format=yuv420p[out]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video),
           "-loop", "1", "-t", f"{dur}", "-i", str(intro_png),
           "-loop", "1", "-t", f"{dur}", "-i", str(fixo_png),
           "-filter_complex", fc, "-map", "[out]"]
    if tem_audio: cmd += ["-map", "0:a", "-c:a", "copy"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)
    return saida


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--out-dir", default="saida")
    ap.add_argument("--video", help="se informado, aplica as camadas direto no vídeo")
    a = ap.parse_args()
    outs = render_pngs(a.titulo, a.out_dir)
    for o in outs.values(): print(o)
    if a.video:
        saida = pathlib.Path(a.out_dir) / (pathlib.Path(a.video).stem + "-folhadebel.mp4")
        print(aplicar_no_video(a.video, outs["intro"], outs["fixo"], saida))
