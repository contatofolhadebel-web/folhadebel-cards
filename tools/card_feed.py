#!/usr/bin/env python3
"""Card estático de feed da Folha de Bel (1080x1350).

Script único: a logo está embutida em base64; a marca d'água é lida de 'MARCA DAGUA - FOLHA DE BEL.png' na pasta de trabalho.
As fontes Saira (Regular, Bold, ExtraBold) vêm da pasta passada em --fontes.
Sem tratamento de imagem: as fotos só são recortadas para o quadro.
Uma foto cobre o quadro. Duas fotos ficam lado a lado, cada uma com seu foco.
"""
import argparse, base64, io, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1350
AZUL = (25, 103, 247, 255)
VERMELHO = (234, 28, 52, 255)
BRANCO = (255, 255, 255, 255)
MARGEM = 64
SIG_CENTRO_Y = 1190      # assinatura centralizada em ~88% da altura
GAP_SIG = 90             # distância do bloco de texto até o centro da assinatura
GAP_TAG_TITULO = 40      # centro da tag até o topo do título (menor desce o selo)
TITULO_TAM_MAX, TITULO_TAM_MIN, TITULO_MAX_LINHAS = 72, 54, 4
BANDA_X1 = W             # fim horizontal da faixa URGENTE (encosta na borda direita)
DIVISOR_DUPLA = 6        # faixa escura entre as duas fotos
AZUL_DESTAQUE = (74, 114, 191, 255)   # azul da faixa atrás do título (aproximação)
TITULO_FUNDO_AZUL = True
SHEAR_ITALICO = 0.2      # inclinação sintética (Itálico da Saira não está no projeto)

LOGO_B64 = "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"
MARCA_B64 = "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"


def img_de_b64(s):
    return Image.open(io.BytesIO(base64.b64decode(s))).convert("RGBA")


def fonte(pasta, nome, tam):
    return ImageFont.truetype(str(pasta / f"Saira-{nome}.ttf"), tam)


def cobrir(caminho, foco_x, foco_y):
    im = ImageOps.exif_transpose(Image.open(caminho)).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int((im.width - W) * foco_x)
    y = int((im.height - H) * foco_y)
    return im.crop((x, y, x + W, y + H)).convert("RGBA")


def cobrir_coluna(caminho, largura, foco_x, foco_y):
    im = ImageOps.exif_transpose(Image.open(caminho)).convert("RGB")
    s = max(largura / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int((im.width - largura) * foco_x)
    y = int((im.height - H) * foco_y)
    return im.crop((x, y, x + largura, y + H)).convert("RGBA")


def encaixar(caminho):
    """Foto inteira na largura do card, no topo, com a base emendada numa cor de fundo."""
    im = ImageOps.exif_transpose(Image.open(caminho)).convert("RGB")
    h = round(im.height * W / im.width)
    ph = np.asarray(im.resize((W, h), Image.LANCZOS)).astype(float)
    if h >= H:
        return Image.fromarray(ph[:H].astype("uint8")).convert("RGBA")
    fundo = ph[h - 60:h - 5].reshape(-1, 3).mean(0)
    out = np.tile(fundo, (H, W, 1))
    out[:h] = ph
    f = min(220, h)
    a = np.linspace(1, 0, f)[:, None, None]
    out[h - f:h] = ph[h - f:h] * a + fundo * (1 - a)
    return Image.fromarray(out.clip(0, 255).astype("uint8")).convert("RGBA")


def montar_base(fotos, foco_x, foco_y, modo_encaixar=False):
    if modo_encaixar and len(fotos) == 1:
        return encaixar(fotos[0])
    """Uma foto: cobre o quadro. Duas fotos: lado a lado, cada uma com seu foco."""
    if len(fotos) == 1:
        return cobrir(fotos[0], foco_x[0], foco_y[0])
    wl = (W - DIVISOR_DUPLA) // 2
    wr = W - DIVISOR_DUPLA - wl
    base = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    base.alpha_composite(cobrir_coluna(fotos[0], wl, foco_x[0], foco_y[0]), (0, 0))
    base.alpha_composite(cobrir_coluna(fotos[1], wr, foco_x[1], foco_y[1]), (wl + DIVISOR_DUPLA, 0))
    return base


DEGRADE = {"normal": [0, 0.34, 0.72, 0.92], "leve": [0, 0.22, 0.52, 0.76]}
DEGRADE_ATUAL = "normal"


def sombras(card):
    """Degradê castanho escuro só na base, sem escurecer o topo. Começa na altura ~54% do quadro."""
    alfa = np.zeros((H, W), np.float32)
    base = 620
    f = np.linspace(0, 1, base)
    alfa_base = np.interp(f, [0, 0.3, 0.62, 1], DEGRADE[DEGRADE_ATUAL])
    alfa[H - base:] = alfa_base[:, None]
    cor = np.zeros((H, W, 4), np.uint8)
    cor[..., 0], cor[..., 1], cor[..., 2] = 34, 26, 20
    cor[..., 3] = (alfa * 255).astype(np.uint8)
    return Image.alpha_composite(card, Image.fromarray(cor, "RGBA"))


def listras(card, periodo=12, espessura=3, alfa=0.10):
    """Textura de listras diagonais escuras sobre a foto, para dar o acabamento do feed."""
    yy, xx = np.indices((H, W))
    mascara = ((xx - yy) % periodo) < espessura
    camada = np.zeros((H, W, 4), np.uint8)
    camada[mascara] = (0, 0, 0, int(alfa * 255))
    return Image.alpha_composite(card, Image.fromarray(camada, "RGBA"))


def texto_com_sombra(card, xy, texto, font, fill=BRANCO, sombra=True):
    if sombra:
        camada = Image.new("RGBA", card.size, (0, 0, 0, 0))
        ImageDraw.Draw(camada).text((xy[0], xy[1] + 3), texto, font=font, fill=(0, 0, 0, 90), anchor="la")
        camada = camada.filter(ImageFilter.GaussianBlur(7))
        card = Image.alpha_composite(card, camada)
    ImageDraw.Draw(card).text(xy, texto, font=font, fill=fill, anchor="la")
    return card


def texto_italico(largura_total, altura, partes, tam, pasta):
    """Renderiza partes [(texto, nome_fonte, cor)] numa camada e inclina."""
    camada = Image.new("RGBA", (largura_total + int(altura * SHEAR_ITALICO) + 10, altura), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    x = 0
    for texto, nome, cor in partes:
        f = fonte(pasta, nome, tam)
        d.text((x, altura // 2), texto, font=f, fill=cor, anchor="lm")
        x += f.getlength(texto)
    s = SHEAR_ITALICO
    return camada.transform(camada.size, Image.AFFINE, (1, s, -s * altura, 0, 1, 0), resample=Image.BICUBIC)


def quebrar(draw, texto, font, largura):
    linhas, atual = [], ""
    for palavra in texto.upper().split():
        teste = (atual + " " + palavra).strip()
        if draw.textlength(teste, font=font) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def titulo_ajustado(draw, pasta, texto, largura):
    for tam in range(TITULO_TAM_MAX, TITULO_TAM_MIN - 1, -2):
        f = fonte(pasta, "ExtraBold", tam)
        linhas = quebrar(draw, texto, f, largura)
        if len(linhas) <= TITULO_MAX_LINHAS:
            break
    return f, linhas, tam


def gerar(fotos, titulo, pasta, out, tag="", urgente=False, foco_x=(0.5,), foco_y=(0.35,), modo_encaixar=False, degrade="normal"):
    global DEGRADE_ATUAL
    DEGRADE_ATUAL = degrade
    pasta = pathlib.Path(pasta)
    fotos = list(fotos)
    if len(fotos) > 2:
        raise SystemExit("Use uma ou duas fotos.")
    fx = list(foco_x) * (2 if len(fotos) == 2 and len(foco_x) == 1 else 1)
    fy = list(foco_y) * (2 if len(fotos) == 2 and len(foco_y) == 1 else 1)
    card = montar_base(fotos, fx, fy, modo_encaixar)
    card = sombras(card)
    card = listras(card)
    draw = ImageDraw.Draw(card)
    largura_util = W - 2 * MARGEM

    # Marca d'água: faixa centralizada verticalmente, altura 22 px
    marca = Image.open(pathlib.Path(__file__).resolve().parent / "assets" / "marca-dagua.png").convert("RGBA")
    marca = marca.resize((round(marca.width * 22 / marca.height), 22), Image.LANCZOS)
    card.alpha_composite(marca, (0, H // 2 - 11))

    # Logo no topo esquerdo
    logo = img_de_b64(LOGO_B64)
    logo = logo.resize((200, round(logo.height * 200 / logo.width)), Image.LANCZOS)
    card.alpha_composite(logo, (MARGEM, 46))

    # Bloco de texto de baixo para cima
    ancora_titulo = SIG_CENTRO_Y - GAP_SIG

    f_tit, linhas_tit, tam_tit = titulo_ajustado(draw, pasta, titulo, largura_util)
    lh_tit = round(tam_tit * 1.03)
    titulo_topo = ancora_titulo - len(linhas_tit) * lh_tit

    for i, linha in enumerate(linhas_tit):
        y = titulo_topo + i * lh_tit
        if TITULO_FUNDO_AZUL:
            d = ImageDraw.Draw(card)
            x0, y0, x1, y1 = d.textbbox((MARGEM, y), linha, font=f_tit, anchor="la")
            d.rectangle([x0 - 12, y0 - 6, x1 + 12, y1 + 6], fill=AZUL_DESTAQUE)
            d.text((MARGEM, y), linha, font=f_tit, fill=BRANCO, anchor="la")
        else:
            card = texto_com_sombra(card, (MARGEM, y), linha, f_tit)
    draw = ImageDraw.Draw(card)

    # Tag ou faixa URGENTE, acima do título
    if urgente:
        bar_base = titulo_topo - 46
        bar_topo = bar_base - 74
        bar_x0, bar_x1 = MARGEM + 162, BANDA_X1
        draw.rectangle([bar_x0, bar_topo, bar_x1, bar_base], fill=VERMELHO)
        dim = (160, 14, 30, 255)
        partes_urg = [("TE", "ExtraBold", dim)] + [
            ("URGENTE", "ExtraBold", BRANCO if i % 2 == 0 else dim) for i in range(6)]
        faixa = texto_italico(W, 74, partes_urg, 50, pasta).crop((0, 0, bar_x1 - bar_x0, 74))
        card.alpha_composite(faixa, (bar_x0, bar_topo))
    elif tag:
        tag_cy = titulo_topo - GAP_TAG_TITULO
        f_tag = fonte(pasta, "Bold", 25)
        x = MARGEM
        espaco = 3.5
        for ch in tag.upper():
            draw.text((x, tag_cy), ch, font=f_tag, fill=BRANCO, anchor="lm")
            x += f_tag.getlength(ch) + espaco
        draw.rectangle([x + 20, tag_cy - 1, x + 92, tag_cy + 1], fill=BRANCO)

    # Assinatura: ícone do Instagram + "Siga @folhadebel no Instagram", centralizada em SIG_CENTRO_Y
    icone = 36
    gap = 16
    partes_sig = [("Siga ", "Regular", BRANCO), ("@folhadebel", "Bold", BRANCO), (" no Instagram", "Regular", BRANCO)]
    largura_sig = sum(fonte(pasta, n, 29).getlength(t) for t, n, _ in partes_sig)
    total = round(icone + gap + largura_sig)
    sx = (W - total) // 2
    ic = Image.new("RGBA", (icone * 4, icone * 4), (0, 0, 0, 0))
    di = ImageDraw.Draw(ic)
    k = icone * 4 / 24
    di.rounded_rectangle([2.5 * k, 2.5 * k, 21.5 * k, 21.5 * k], 5.5 * k, outline=BRANCO, width=int(2 * k))
    di.ellipse([(12 - 4.3) * k, (12 - 4.3) * k, (12 + 4.3) * k, (12 + 4.3) * k], outline=BRANCO, width=int(2 * k))
    di.ellipse([(17.6 - 1.1) * k, (6.4 - 1.1) * k, (17.6 + 1.1) * k, (6.4 + 1.1) * k], fill=BRANCO)
    ic = ic.resize((icone, icone), Image.LANCZOS)
    card.alpha_composite(ic, (sx, SIG_CENTRO_Y - icone // 2))
    row = texto_italico(round(largura_sig) + 4, 44, partes_sig, 29, pasta)
    card.alpha_composite(row, (sx + icone + gap, SIG_CENTRO_Y - 22))

    card.convert("RGB").save(out, quality=95)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Card estático de feed da Folha de Bel")
    ap.add_argument("--foto", required=True, nargs="+", help="uma ou duas fotos (duas ficam lado a lado)")
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--fontes", required=True, help="pasta com Saira-Regular.ttf, Saira-Bold.ttf, Saira-ExtraBold.ttf")
    ap.add_argument("--out", default="card.png")
    ap.add_argument("--tag", default="")
    ap.add_argument("--urgente", action="store_true")
    ap.add_argument("--foco-x", type=float, nargs="+", default=[0.5], help="0 a 1, um valor por foto")
    ap.add_argument("--foco-y", type=float, nargs="+", default=[0.35], help="0 a 1, um valor por foto")
    ap.add_argument("--encaixar", action="store_true", help="foto inteira no topo, sem cortar (bom para foto quadrada ou deitada)")
    ap.add_argument("--degrade", choices=["normal", "leve"], default="normal")
    a = ap.parse_args()
    print(gerar(a.foto, a.titulo, a.fontes, a.out, a.tag, a.urgente, a.foco_x, a.foco_y, a.encaixar, a.degrade))
