# Regras do repositório

## Vídeo no modelo "post com cabeçalho" (estilo Choquei): padrão aprovado

Quando o usuário mandar um vídeo nesse layout (foto redonda + nome + texto em cima, vídeo embaixo)
para postar com o nosso perfil, use SEMPRE `tools/trocar_perfil.py` e entregue nesta ordem:

1. **Vídeo de feed 4:5** (1080x1350), fundo branco, áudio AAC-LC: `videos/AAAA-MM-DD-assunto-pulso-politico.mp4`
2. **Capa PNG 9:16** (1080x1920), com o post reduzido a 780px de largura e centralizado no branco:
   `videos/AAAA-MM-DD-assunto-pulso-politico-capa.png`. O Instagram trata a capa de vídeo como 9:16
   e a grade do perfil mostra só ~79% da largura; com essa margem nada é cortado. Orientar:
   subir em "Editar capa" e deixar o corte da grade centralizado, sem arrastar.
3. **Legenda** para Instagram (notícia com nomes/fatos confirmados, CTA para comentar,
   "📲 Siga o @pulsopolitico", hashtags).

```
python3 tools/trocar_perfil.py --video entrada.mp4 --out videos/AAAA-MM-DD-assunto-pulso-politico --capa-tempo 1
```
- Perfil padrão: Pulso Político (`tools/assets/perfis/pulso-politico.png`). `--perfil folha` para a Folha de Bel.
- `--capa-tempo`: escolher um quadro bom (rosto expressivo). Conferir a capa antes de entregar.
- Não usar Reels 9:16 com o vídeo quadrado (aparecem faixas pretas). Não adicionar selo de verificado.
