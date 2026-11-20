---
name: "orquestrador-folha-de-bel"
description: "Use para montar um post completo da Folha de Bel, checagem, título, card ou reels e legenda, e entregar o arquivo pronto. Não publica nada."
---

# Orquestrador da Folha de Bel

Conduz o post inteiro: checagem, título, card ou reels e legenda. Entrega o arquivo pronto ao final. Não publica, não agenda e não usa o Postador. Não reescreve as regras das outras skills: carrega cada uma na hora de usar.

## 1. Pauta (uma vez)
Coletar do usuário, em uma mensagem só:
- Texto-base: resumo da matéria ou roteiro do reels (obrigatório). Sem ele, pedir antes de seguir.
- Foto(s): uma ou duas, para o card. Para reels, o material que o usuário indicar.
- Formato: card estático ou reels.
- Tag ou editoria (opcional).
- Links da pauta (opcional): qualquer site, inclusive Instagram, e prints ou vídeos de apoio.

Guardar tudo num único objeto de pauta: título, texto-base, links, fonte, foto(s), tag e formato. Esse objeto alimenta as etapas seguintes, para que card e legenda falem da mesma matéria.

## 1b. Checagem
Carregar a skill `checagem-folha-de-bel` e checar a pauta pelos links e pela busca. Guardar no objeto de pauta os fatos confirmados, as divergências e as fontes. Seguir direto se o fato principal estiver confirmado; parar só nos casos que a skill de checagem manda parar.

## 2. Título
Carregar a skill `titulo-folha-de-bel` e gerar as três opções a partir do texto-base e dos fatos confirmados na checagem. Esta é a única pausa do fluxo: mostrar as opções e esperar a escolha do usuário, porque o título é decisão dele. O título escolhido vira o título da pauta e não muda mais.

## 3. Card ou reels
- Card estático: carregar `card-feed-estatico-folha-de-bel-v2` e gerar o card com o título da pauta, as fotos e a tag. Não gerar a capa.
- Reels: carregar `reels-folha-de-bel` e montar o vídeo com o título da pauta.

Se a prévia tiver problema (rosto cortado, texto ilegível), ajustar dentro da própria skill, sem mudar o título.

## 4. Legenda
Carregar `legenda-instagram-folha-de-bel` e passar o objeto de pauta completo: título final, texto-base, fatos confirmados, fontes da checagem e formato. Com a checagem feita, a legenda usa essas fontes e não pergunta o modo. A legenda segue o título aprovado, sem reescrevê-lo.

## 5. Entrega
Ao final, sem pedir aprovação:
1. Enviar o arquivo pronto (card PNG ou vídeo) com SendUserFile.
2. Enviar a legenda em texto, pronta para copiar, na resposta.
3. Dizer em uma frase o que foi entregue. Não recontar as etapas.

## Regras
- Nunca publicar, agendar ou usar o Postador.
- Nunca depender do computador do usuário: o fluxo roda só pelo celular.
- A única pausa é a escolha do título. Todo o resto roda sem perguntar, exceto quando a checagem não confirma o fato principal ou acha alerta grave.