# Folha de Bel: gerador de cards

Gera o card 1080x1350 (feed 4:5) usado nas publicações.

## Uso
```
pip install pillow numpy playwright && playwright install chromium
python3 tools/card_noticia.py --foto foto1.jpg foto2.jpg --tag "POLÍCIA | CIDADE" --titulo "TÍTULO DO CARD" --out cards/saida.jpg
```
- 1 foto: enquadramento automático. 2 fotos: card duplo, lado a lado.
- `--pb` tons de cinza (luto, tragédia, polícia). `--urgente` selo URGENTE no lugar da tag.

Fontes: Saira (SIL OFL 1.1, ver `tools/OFL.txt`).
