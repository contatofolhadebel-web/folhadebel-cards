---
name: post-folha-de-bel
description: Fluxo completo de post da Folha de Bel a partir de um link ou tema — sugestão de título (com aprovação), card estático (com aprovação), legenda, envio para a mLabs e pergunta se publica agora ou programa. Use sempre que o usuário mandar um link, print ou tema e pedir para montar/criar/fazer um post.
---

# Post da Folha de Bel: do link à mLabs

O usuário manda um **link** (Instagram, portal de notícia) ou um **tema**. Este fluxo
leva até o post na mLabs, com aprovação do usuário em cada etapa por **caixa de seleção**
(ferramenta `AskUserQuestion`). Nada é publicado sem a resposta dele na etapa 5.

Todas as aprovações usam `AskUserQuestion` — nunca pedir aprovação só em texto.
Se o usuário escolher "Other" e escrever um ajuste, aplicar e perguntar de novo.

## 1. Apuração
- **Link do Instagram**: baixar `https://www.instagram.com/p/<código>/embed/captioned/`
  com `curl -A "Mozilla/5.0"`, tirar a legenda e a URL da imagem em tamanho cheio
  (a que tem `dst-jpg_e35_tt6`, trocando `&amp;` por `&`). Ler a imagem para ver texto
  sobreposto (título, logo do veículo).
- **Link de portal**: ler a página (agente `web-fetch`).
- **Tema**: pesquisar (`WebSearch`, modo extended).
- Conferir os fatos principais em pelo menos duas fontes quando for notícia quente.
  Números que variam entre veículos: atribuir ("segundo levantamento do X").
- **Foto**, nesta ordem: a que o usuário mandar → a do post de origem, recortando logo e
  texto de outros veículos → foto da Agência Brasil (uso livre com crédito; pegar a URL
  `imagens.ebc.com.br/.../1600x800/...` da matéria e o crédito "Foto: Nome/Agência Brasil").
  Print pequeno (menos de ~700 px de largura) fica borrado: avisar e pedir a original.
- Guardar o crédito da foto para a legenda. Sem crédito conhecido: "Foto: Reprodução".

## 2. Título (aprovação por seleção)
Regras de título: português, caixa normal, até ~80 caracteres (o card comporta 4 linhas),
só fatos apurados, sem clickbait, sujeito e verbo claros.

Chamar `AskUserQuestion` com **3 opções de título** (label = o título; description = ângulo
e nº de caracteres; a recomendada primeiro, com "(Recomendado)"). Antes, em uma ou duas
linhas, avisar ressalvas da apuração (ex.: dado não confirmado pelo boletim oficial).
O título aprovado não muda mais, a não ser que o usuário peça.

## 3. Card (aprovação por seleção)
Gerar com o script do repositório:
```
python3 tools/card_feed.py --foto FOTO --titulo "TÍTULO" --fontes tools/fonts \
  --tag "TAG" --out cards/AAAA-MM-DD-slug.png [--encaixar] [--degrade leve] \
  [--foco-x 0.5] [--foco-y 0.35] [--urgente]
```
- `--encaixar`: foto inteira no topo, sem cortar — usar quando a foto for quadrada ou
  deitada e o assunto ficaria escondido atrás do título.
- `--degrade leve`: degradê inferior mais fraco.
- Tag de editoria curta (ex.: SAÚDE, POLÍTICA, BELFORD ROXO, EMAGRECEU 35 QUILOS).
  `--urgente` só quando o usuário pedir.
- Ler o PNG gerado e conferir: rosto inteiro, nada importante atrás do título, sem
  corte reto aparente. Corrigir antes de mostrar.

Mostrar o card com `SendUserFile` e, junto, a **legenda** (seção 4) em texto.
Depois chamar `AskUserQuestion`: "Aprovar card e legenda?" com opções
**Aprovar** / **Ajustar o card** (foco, degradê, tag, foto) / **Ajustar a legenda**.
Repetir até aprovar.

## 4. Legenda (padrão de portal)
- Abrir com o fato principal (quem, o que, quando, onde) nos primeiros ~125 caracteres.
- Frases curtas, parágrafos de 1 a 3 frases, toda afirmação atribuída, sem sensacionalismo,
  sem caixa alta no corpo, sem exclamação. Polêmica: os dois lados, sem julgar.
- Terminar com o próximo passo ou o que ainda não se sabe; pergunta ao leitor é opcional.
- "Foto: ..." e "Fonte(s): ..." no fim; 3 a 5 hashtags (sempre #FolhaDeBel).
- Máximo 2.200 caracteres. Sem link no corpo.

## 5. mLabs — publicar agora ou programar
Seguir também a skill `publicar-mlabs-folha-de-bel` (canais, collabs, IDs).
1. `git add` o card em `cards/`, commit e push na branch atual; usar a URL
   `https://raw.githubusercontent.com/contatofolhadebel-web/folhadebel-cards/<branch>/cards/<arquivo>`
   em `upload_media` (canais `instagram`, `facebook`) e esperar `get_media_upload` = completed.
2. Chamar `AskUserQuestion`: "Publicar agora ou programar?" com opções
   **Publicar agora** / **Programar**. Se programar, perguntar o horário — sugerir os melhores
   horários do dia (`get_best_posting_times` do Instagram) como opções; aceitar horário livre.
3. `create_post` com:
   - `channels`: `["instagram", "facebook"]` (card estático);
   - `collabs` no Instagram: @girobelfordroxo (65731250691), @maisbelfordroxo (69386224579),
     @noticias_debel (13697051988) — sempre;
   - `status: "scheduled"`; `scheduledAt` = horário escolhido, ou agora + 3 min
     (`TZ=America/Sao_Paulo date -Iseconds`) para "publicar agora";
   - `requestId` estável do post (ex.: `slug-AAAAMMDD-ig-fb`), reutilizado em nova tentativa.
4. Responder com os links "Ver agendamento na mLabs" de cada canal e avisos.

## Regras
- Uma pausa por etapa: título, card+legenda, publicar/programar. O resto roda sem perguntar.
- Nunca publicar sem a resposta "Publicar agora" ou "Programar" da etapa 5.
- Não usar o Postador (Metricool) — a publicação é pela mLabs.
