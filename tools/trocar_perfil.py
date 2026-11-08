#!/usr/bin/env python3
"""Folha de Bel: troca o perfil (avatar + nome) de vídeos no layout "post com cabeçalho"
(avatar redondo, nome em negrito e texto em cima, vídeo embaixo; ex.: posts da Choquei).

Mantém o texto e o vídeo originais e cobre só o avatar e o nome com os da Folha de Bel.

Uso:
  python3 tools/trocar_perfil.py --video entrada.mp4 --out videos/saida.mp4
  # outro nome ou outra foto de perfil
  python3 tools/trocar_perfil.py --video entrada.mp4 --nome "FOLHA DE BEL" --avatar minha_foto.jpg --out saida.mp4

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--nome", default="FOLHA DE BEL")
    ap.add_argument("--avatar", help="foto de perfil (opcional; padrão: símbolo da Folha)")
    ap.add_argument("--avatar-box", default="9,11,81,81")
    ap.add_argument("--nome-box", default="100,3,300,36")
    a = ap.parse_args()

    info = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "json", a.video]))["streams"][0]
    w, h = info["width"], info["height"]
    box = lambda s: [int(v) for v in s.split(",")]
    ov = montar_overlay(w, h, a.nome, a.avatar, box(a.avatar_box), box(a.nome_box))
    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t) / "ov.png"
        ov.save(p)
        pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", str(p),
                               "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
                               "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                               "-c:a", "copy", "-movflags", "+faststart", a.out])
    print(a.out)


if __name__ == "__main__":
    main()
