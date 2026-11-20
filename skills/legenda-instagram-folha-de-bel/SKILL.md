---
name: "legenda-instagram-folha-de-bel"
description: "Use para escrever a legenda de Instagram de matérias e vídeos da Folha de Bel, no estilo de redação de grandes portais e respeitando o limite de caracteres, com pesquisa ou pedido de contexto conforme o caso."
---

# Legenda de Instagram (Folha de Bel)

Escreve só a legenda (o corpo que vai abaixo do card). Não gera imagem: para o card, use a skill card-feed-estatico-folha-de-bel-v2.

## 1. Antes de escrever: escolher o modo

Se a pauta já passou pela skill `checagem-folha-de-bel`, não perguntar o modo: escrever com os fatos confirmados e as fontes da checagem, como no modo busca, sem refazer a pesquisa.

Sem checagem, o usuário diz qual modo usar. Se ele não disser, perguntar uma vez: "faz busca ou não faz?".

- **Faz busca**: fazer uma varredura ampla (WebSearch, em modo extended quando o assunto for recente), conferir os fatos em pelo menos duas fontes e citar as fontes ao final da resposta. Se a busca não achar nada, dizer isso e cair no modo sem busca.
- **Não faz busca**: não pesquisar. Ativar o modo de contexto (seção 2) e só escrever depois que o usuário responder.

Se o usuário disser que o fato é só da cidade e não saiu em nenhum veículo, usar o modo sem busca mesmo que ele não diga isso expressamente.

## 2. Modo de contexto (sem busca)

Antes de escrever, perguntar só o que faltar, em uma mensagem curta, por exemplo:
- O que aconteceu, em uma ou duas frases, e quando?
- Quem são as pessoas citadas, com cargo e nome completo como devem aparecer?
- Quem falou o quê? Há declaração oficial ou resposta das pessoas citadas?
- Qual é o lugar exato (bairro, prédio, órgão)?
- Há documento, foto ou vídeo que comprove?
- Qual a polêmica, em termos neutros?

Não inventar detalhe que não foi informado. Se faltar dado essencial, não escrever a legenda ainda.

## 3. Padrão de redação de portal

O tom segue o de grandes portais de notícia (G1, Terra, UOL, GloboNews, R7):
- Abrir com o fato principal: quem, o que, quando, onde. Sem suspense nem pergunta retórica.
- Frases curtas e diretas, parágrafos de uma a três frases.
- Atribuir toda afirmação: "segundo", "informou", "disse em nota". Separar fato de opinião.
- Sem adjetivo sensacionalista, sem caixa-alta no corpo, sem exclamação.
- Se houver polêmica, apresentar os lados com o que cada um disse, sem julgar.
- Dar o contexto mínimo para quem não acompanhou o assunto.
- Terminar com o que ainda não se sabe ou o próximo passo, quando houver.
- Nomes e cargos como o usuário informou; sem inventar título ou cargo.

## 4. Limites do Instagram

- Máximo de 2.200 caracteres na legenda, contando espaços, quebras de linha e hashtags. Conferir antes de entregar.
- As primeiras cerca de 125 caracteres aparecem antes do "mais": a abertura precisa conter o fato principal.
- Hashtags: no máximo 30, mas usar poucas (de três a cinco), relevantes ao assunto e à cidade.
- Sem link clicável no corpo da legenda (o Instagram não abre). Se houver link, dizer que ele vai no perfil.
- Conferir o padrão de legenda da página em /projects/01a18dda-9fb3-77f6-af66-8141afed0a98/areas/folha-de-belford-roxo.md antes de escrever. Se houver conflito entre o padrão da página e este guia, vale o da página.

## 5. Vídeo

- **Se há registro de notícia sobre o fato**: pesquisar e escrever com base nas fontes, como no modo busca.
- **Se não há registro**: a legenda vem do que o usuário informar e do que aparece nos frames. Extrair frames com ffmpeg (por exemplo, um a cada cinco segundos) e ler as imagens para conferir o que mostram.
- **Áudio**: não há transcrição automática por padrão. Se o vídeo tiver fala relevante e não houver transcrição, pedir ao usuário a fala transcrita ou as legendas do vídeo, em vez de inventar o que foi dito.
- Não afirmar nada que os frames e o texto do usuário não sustentem.

## 6. Entrega

- Entregar a legenda pronta para colar, sem comentário extra antes ou depois.
- Informar o total de caracteres na última linha, se estiver perto do limite.
- Se o modo busca ou a checagem foi usado, listar as fontes ao final, em formato de link.
- Se o modo sem busca foi usado, não citar fontes externas.

## Manutenção

Toda alteração pedida na conversa sobre a legenda (tom, tamanho, regras, perguntas do modo de contexto) vai direto para esta skill, na mesma sessão, via proposta de edição.