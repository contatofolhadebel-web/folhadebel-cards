#!/usr/bin/env python3
"""Folha de Belford Roxo — modelo REELS (1080x1920).

Duas camadas transparentes aplicadas sobre o vídeo com ffmpeg:
  intro  -> os 5 primeiros segundos: topo azul com "FOLHA" vazado, marca d'água no meio e na base,
            título e assinatura (ícones das redes).
  fixo   -> o resto do vídeo: título, marca d'água no meio e assinatura.

Título: linhas separadas por "/", a linha marcada com * fica em caixa azul, as outras em caixa branca.
  "JORGE ARAGÃO / *IDENTIDADE* / NO DIA DA CONSCIÊNCIA NEGRA"

Layouts:
  pe       vídeo em pé, tela cheia (padrão)
  deitado  vídeo deitado: recorte em pé em cima, vídeo deitado inteiro embaixo
  foto     foto em cima (--foto) e vídeo embaixo, título na emenda entre as duas

Uso:
  python3 reels.py --titulo "LINHA 1 / *LINHA 2*" --video entrada.mp4 --out-dir saida/
  python3 reels.py --titulo "..." --video show.mp4 --foto retrato.jpg --layout foto --out-dir saida/
"""
import argparse, base64, html, pathlib, subprocess, json

BASE = pathlib.Path(__file__).parent
W, H = 1080, 1920
INTRO_SEG = 5.0
FADE_SEG = 0.35
AZUL = "#1967f7"

# Geometria de cada layout (px no canvas 1080x1920)
LAYOUTS = {
    # titulo_base: onde termina (bottom) o bloco do título; redes: topo da assinatura
    "pe":      dict(titulo_base=1345, redes=1460, marca=960),
    # faixa de cima (recorte em pé) 0..1312, vídeo deitado inteiro 1312..1920
    "deitado": dict(titulo_base=1280, redes=1840, marca=960, emenda=1312),
    # foto 0..emenda, vídeo emenda..1920
    "foto":    dict(titulo_base=None, redes=1830, marca=None, emenda=900),
}


def b64(p):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def redes_b64():
    """redes-linha.png é uma tela 1080x1350 com os ícones num ponto só: recorta a área visível."""
    import io
    from PIL import Image
    im = Image.open(BASE / 'assets' / 'redes-linha.png').convert("RGBA")
    im = im.crop(im.split()[-1].getbbox())
    buf = io.BytesIO(); im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def linhas_titulo(titulo):
    """Retorna [(texto, destaque_azul)]. Sem '/', vira uma linha só (quebra automática)."""
    out = []
    for parte in titulo.split("/"):
        p = parte.strip()
        if not p:
            continue
        azul = p.startswith("*") and p.endswith("*") and len(p) > 1
        out.append((p.strip("*").strip(), azul))
    return out


def html_reels(titulo, subtitulo, tipo, layout):
    fonts = "".join(
        f"@font-face{{font-family:Saira;src:url('{(BASE/'fonts'/f'Saira-{n}.ttf').as_uri()}');font-weight:{w}}}"
        for n, w in [("Regular", 400), ("Bold", 700), ("ExtraBold", 800), ("Black", 900)])
    g = LAYOUTS[layout]
    intro = tipo == "intro"
    marca_png = b64(BASE / 'assets' / 'marca-dagua.png')

    caixas = "".join(
        f'<div class="ln{" az" if az else ""}"><span>{html.escape(t)}</span></div>'
        for t, az in linhas_titulo(titulo))
    sub = f'<div class="sub"><span>{html.escape(subtitulo)}</span></div>' if subtitulo else ""

    if layout == "foto":
        e = g["emenda"]
        # título centrado verticalmente na emenda foto/vídeo; marca d'água vira a linha da emenda
        bloco_pos = f"top:{e}px;transform:translateY(-50%)"
        marca_top = e
        sombra = (f'<div class="sombra" style="top:{e-360}px;height:360px;'
                  f'background:linear-gradient(180deg,rgba(14,26,72,0),rgba(14,26,72,.55))"></div>')
        base_h, base_a1, base_a2 = (560, .30, .60) if intro else (420, .18, .40)
    else:
        bloco_pos = f"bottom:{H-g['titulo_base']}px"
        marca_top = g["marca"]
        sombra = ""
        base_h, base_a1, base_a2 = (1150, .45, .72) if intro else (760, .22, .42)

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:transparent}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Saira,sans-serif;color:#fff}}
.r{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
.topo{{position:absolute;inset:0 0 auto 0;height:820px;
  background:linear-gradient(180deg,#4189ff 0%,#2a76fb 22%,#1967f7 42%,rgba(25,103,247,.55) 62%,rgba(25,103,247,0) 100%)}}
.vazado{{position:absolute;left:-4px;top:40px;font-weight:900;font-size:600px;line-height:1;letter-spacing:-.02em;white-space:nowrap;
  transform-origin:left top;color:transparent;-webkit-text-stroke:3px rgba(255,255,255,.30)}}
.base{{position:absolute;inset:auto 0 0 0;height:{base_h}px;
  background:linear-gradient(180deg,rgba(18,34,92,0) 0%,rgba(18,34,92,{base_a1}) 35%,rgba(14,26,72,{base_a2}) 100%)}}
.sombra{{position:absolute;left:0;right:0}}
.marca{{position:absolute;left:0;right:0;height:24px;transform:translateY(-50%);
  background:url('{marca_png}') left center/auto 24px repeat-x}}
.bloco{{position:absolute;left:70px;right:70px;{bloco_pos};display:flex;flex-direction:column;align-items:flex-start;gap:10px}}
.ln span,.sub span{{display:inline-block;font-weight:800;font-size:62px;line-height:1.08;text-transform:uppercase;
  letter-spacing:-.008em;white-space:nowrap;padding:4px 20px 6px;background:#fff;color:{AZUL};box-shadow:0 6px 24px rgba(0,0,0,.28)}}
.ln.az span{{background:{AZUL};color:#fff}}
.sub{{margin-top:8px}}
.sub span{{display:inline;font-weight:700;font-size:38px;line-height:1.5;padding:4px 14px;text-transform:none;
  -webkit-box-decoration-break:clone;box-decoration-break:clone}}
.redes{{position:absolute;left:50%;top:{g['redes']}px;width:380px;transform:translateX(-50%)}}
</style></head><body><div class="r">
{'<div class="topo"></div><div class="vazado">FOLHA</div>' if intro else ''}
{sombra}
<div class="base"></div>
<div class="marca" style="top:{marca_top}px"></div>
{f'<div class="marca" style="top:{H-60}px;opacity:.55"></div>' if intro else ''}
<div class="bloco" id="t">{caixas}{sub}</div>
<img class="redes" src="{redes_b64()}">
</div><script>
const v=document.querySelector('.vazado');if(v){{v.style.transform='scaleX('+(1290/v.getBoundingClientRect().width)+')'}}
// encolhe a fonte das caixas até a linha mais larga caber em 940px
const spans=[...document.querySelectorAll('.ln span')];let s=62;
const larg=()=>Math.max(0,...spans.map(e=>e.getBoundingClientRect().width));
while(larg()>940&&s>40){{s-=2;spans.forEach(e=>e.style.fontSize=s+'px')}}
document.body.dataset.ok=1;
</script></body></html>"""


def render_pngs(titulo, subtitulo, layout, out_dir):
    from playwright.sync_api import sync_playwright
    out_dir = pathlib.Path(out_dir).resolve(); out_dir.mkdir(parents=True, exist_ok=True)
    outs = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for tipo in ("intro", "fixo"):
            tmp = out_dir / f"_{tipo}.html"; tmp.write_text(html_reels(titulo, subtitulo, tipo, layout), encoding="utf-8")
            pg = b.new_page(viewport={"width": W, "height": H})
            pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_selector("body[data-ok]")
            outs[tipo] = out_dir / f"reels-{'1-intro-5s' if tipo == 'intro' else '2-fixo'}.png"
            pg.screenshot(path=str(outs[tipo]), type="png", omit_background=True); pg.close(); tmp.unlink()
        b.close()
    return outs


def cover(lbl_in, w, h, lbl_out, foco_y=0.5):
    """scale+crop 'cover' para w x h; foco_y escolhe a altura do recorte (0 topo, 1 base)."""
    return (f"[{lbl_in}]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}:(iw-{w})/2:(ih-{h})*{foco_y},setsar=1[{lbl_out}]")


def aplicar_no_video(video, intro_png, fixo_png, saida, layout="pe", foto=None, foco_foto=0.3):
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                               "-show_streams", "-of", "json", str(video)]))
    dur = float(info["format"]["duration"])
    tem_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    st = INTRO_SEG - FADE_SEG
    g = LAYOUTS[layout]

    inputs = ["-i", str(video),
              "-loop", "1", "-t", f"{dur}", "-i", str(intro_png),
              "-loop", "1", "-t", f"{dur}", "-i", str(fixo_png)]
    if layout == "pe":
        fc = cover("0:v", W, H, "v") + ";"
    elif layout == "deitado":
        e = g["emenda"]
        fc = (f"[0:v]split[s1][s2];" + cover("s1", W, e, "cima") + ";"
              + cover("s2", W, H - e, "baixo") + ";"
              f"[cima]pad={W}:{H}:0:0:black[c];[c][baixo]overlay=0:{e}[v];")
    elif layout == "foto":
        if not foto:
            raise SystemExit("layout foto precisa de --foto")
        e = g["emenda"]
        inputs += ["-loop", "1", "-t", f"{dur}", "-i", str(foto)]
        fc = (cover("3:v", W, e, "ft", foco_foto) + ";"
              + cover("0:v", W, H - e, "vd") + ";"
              f"[ft]pad={W}:{H}:0:0:black[c];[c][vd]overlay=0:{e}:shortest=1[v];")
    else:
        raise SystemExit(f"layout desconhecido: {layout}")

    fc += (f"[1:v]format=rgba,fade=t=out:st={st}:d={FADE_SEG}:alpha=1[a];"
           f"[2:v]format=rgba,fade=t=in:st={st}:d={FADE_SEG}:alpha=1[b];"
           f"[v][a]overlay=0:0:shortest=1[va];[va][b]overlay=0:0:shortest=1,format=yuv420p[out]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[out]"]
    if tem_audio: cmd += ["-map", "0:a", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-t", f"{dur}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30",
            "-movflags", "+faststart", str(saida)]
    subprocess.run(cmd, check=True)
    return saida


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--titulo", required=True, help='linhas com "/", destaque azul com *linha*')
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--layout", choices=list(LAYOUTS), default="pe")
    ap.add_argument("--foto", help="foto de cima (layout foto)")
    ap.add_argument("--foco-foto", type=float, default=0.3, help="0 topo .. 1 base, altura do recorte da foto")
    ap.add_argument("--out-dir", default="saida")
    ap.add_argument("--video", help="se informado, aplica as camadas direto no vídeo")
    a = ap.parse_args()
    outs = render_pngs(a.titulo, a.subtitulo, a.layout, a.out_dir)
    for o in outs.values(): print(o)
    if a.video:
        saida = pathlib.Path(a.out_dir) / f"{pathlib.Path(a.video).stem}-folhadebel-{a.layout}.mp4"
        print(aplicar_no_video(a.video, outs["intro"], outs["fixo"], saida, a.layout, a.foto, a.foco_foto))
