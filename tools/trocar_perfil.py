#!/usr/bin/env python3
"""Modelo "post com cabeçalho" (estilo Choquei) com o nosso perfil.

Pega um vídeo no layout avatar redondo + nome + texto em cima e vídeo embaixo, troca a foto
e o nome pelos nossos e entrega SEMPRE:
  1. <out>.mp4           vídeo FEED 4:5 (1080x1350), fundo branco, áudio AAC-LC;
  2. <out>-capa.png      capa 9:16 (1080x1920), post reduzido a 780px e centralizado, para a
                         grade do perfil (o Instagram trata capa de vídeo como 9:16 e dá zoom
                         de ~79%; com essa margem nada é cortado). Subir em "Editar capa" e
                         deixar o corte da grade centralizado.

Uso (padrão: perfil Pulso Político):
  python3 tools/trocar_perfil.py --video entrada.mp4 --out videos/2026-11-08-assunto-pulso-politico
  python3 tools/trocar_perfil.py --video entrada.mp4 --perfil folha --out videos/...
  # --capa-tempo 1.0  segundo do vídeo usado na capa (escolher um quadro bom)

As posições padrão valem para o vídeo 720x720 desse layout; em outro tamanho tudo é
escalado pela largura. Ajuste com --avatar-box e --nome-box (x,y,w,h em pixels de 720) se preciso.
"""
import argparse, json, pathlib, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

BASE = pathlib.Path(__file__).parent
AZUL = (25, 103, 247)
FONTE_NOME = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def avatar_folha(d, foto=None):
    """Avatar redondo d x d. Sem foto: círculo azul com o 'F' do logo."""
    ss = 4
    D = d * ss
    if foto:
        im = Image.open(foto).convert("RGB")
        s = min(im.size)
        im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2))
        img = im.resize((D, D), Image.LANCZOS).convert("RGBA")
    else:
        img = Image.new("RGBA", (D, D), AZUL + (255,))
        logo = Image.open(BASE / "assets" / "logo-folha-belford-roxo.png").convert("RGBA")
        f = logo.crop((0, 0, 162, logo.height))  # só o símbolo "F"
        f = f.crop(f.getbbox())
        alvo = int(D * 0.56)
        f = f.resize((int(f.width * alvo / f.height), alvo), Image.LANCZOS)
        img.alpha_composite(f, ((D - f.width) // 2 + int(D * 0.02), (D - f.height) // 2))
    mask = Image.new("L", (D, D), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    out = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out.resize((d, d), Image.LANCZOS)


def montar_overlay(w, h, nome, foto, avatar_box, nome_box):
    k = w / 720
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    ax, ay, ad, _ = [round(v * k) for v in avatar_box]
    # fundo branco por trás do avatar (apaga o original inteiro, com folga)
    dr.ellipse((ax - 3, ay - 3, ax + ad + 3, ay + ad + 3), fill=(255, 255, 255, 255))
    ov.alpha_composite(avatar_folha(ad, foto), (ax, ay))
    nx, ny, nw, nh = [round(v * k) for v in nome_box]
    dr.rectangle((nx, ny, nx + nw, ny + nh), fill=(255, 255, 255, 255))
    # nome: altura das maiúsculas igual à do original (~21px em 720)
    cap = 21 * k
    fs = round(cap / 0.727)
    font = ImageFont.truetype(FONTE_NOME, fs)
    top = font.getbbox("H")[1]
    dr.text((round(108 * k), round(10 * k) - top), nome, font=font, fill=(17, 17, 17, 255))
    return ov


PERFIS = {
    "pulso": ("PULSO POLÍTICO", BASE / "assets" / "perfis" / "pulso-politico.png"),
    "folha": ("FOLHA DE BEL", None),
}
AUDIO = ["-c:a", "aac", "-profile:a", "aac_low", "-b:a", "160k", "-ar", "44100", "-ac", "2"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True, help="caminho sem extensão (gera .mp4 e -capa.png)")
    ap.add_argument("--perfil", choices=PERFIS, default="pulso")
    ap.add_argument("--nome", help="sobrescreve o nome do perfil")
    ap.add_argument("--avatar", help="sobrescreve a foto do perfil")
    ap.add_argument("--capa-tempo", type=float, default=1.0)
    ap.add_argument("--avatar-box", default="9,11,81,81")
    ap.add_argument("--nome-box", default="100,3,300,36")
    a = ap.parse_args()

    nome, avatar = PERFIS[a.perfil]
    nome, avatar = a.nome or nome, a.avatar or avatar
    out = pathlib.Path(a.out)
    if out.suffix.lower() in (".mp4", ".mov"):
        out = out.with_suffix("")
    out.parent.mkdir(parents=True, exist_ok=True)
    mp4, capa = out.with_suffix(".mp4"), out.parent / (out.name + "-capa.png")

    info = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "json", a.video]))["streams"][0]
    w, h = info["width"], info["height"]
    box = lambda s: [int(v) for v in s.split(",")]
    ov = montar_overlay(w, h, nome, avatar, box(a.avatar_box), box(a.nome_box))
    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t) / "ov.png"
        ov.save(p)
        # vídeo 4:5 de feed: post 1080 de largura, centralizado em fundo branco
        sh = round(1080 * h / w)
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", str(p), "-filter_complex",
                               f"[0:v][1:v]overlay=0:0:format=auto,scale=1080:{sh}:flags=lanczos,"
                               f"pad=1080:1350:0:(1350-{sh})/2:white,format=yuv420p",
                               "-c:v", "libx264", "-crf", "18", "-preset", "medium", *AUDIO,
                               "-movflags", "+faststart", str(mp4)])
        # capa 9:16 para a grade do perfil
        q = pathlib.Path(t) / "q.png"
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", str(a.capa_tempo), "-i", a.video,
                               "-frames:v", "1", str(q)])
        fr = Image.open(q).convert("RGBA")
        fr.alpha_composite(ov)
        n = 780
        fr = fr.convert("RGB").resize((n, round(n * h / w)), Image.LANCZOS)
        c = Image.new("RGB", (1080, 1920), "white")
        c.paste(fr, ((1080 - fr.width) // 2, (1920 - fr.height) // 2))
        c.save(capa)
    print(mp4)
    print(capa)


if __name__ == "__main__":
    main()
