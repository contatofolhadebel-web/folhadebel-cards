---
name: "checagem-folha-de-bel"
description: "Use para checar uma pauta da Folha de Bel antes de fazer título, card, reels ou legenda: abre os links que o usuário mandar (qualquer site, inclusive Instagram), confere os fatos em outras fontes e devolve o que está confirmado, o que não está e as fontes."
---

# Checagem de pauta (Folha de Bel)

Confere a pauta antes de qualquer peça ser feita. Não escreve título, card nem legenda: entrega um relatório curto e os fatos confirmados para as outras skills usarem.

## 1. O que o usuário manda
- Texto-base ou resumo da pauta.
- Links: quantos quiser, de qualquer site (portal, órgão público, Diário Oficial, YouTube, X, Facebook, TikTok, Instagram etc.).
- Prints, fotos, vídeos ou legenda copiada, quando houver.

Se não vier nenhum link, checar só pela busca (seção 3).

## 2. Abrir cada link
Para cada link, nesta ordem:
1. Baixar a página com `curl -sL` (com timeout) e ler título, data de publicação, autor e texto principal. Se o HTML vier vazio ou cheio de script, tentar o agente `web-fetch` com a mesma URL.
2. Anotar de cada link: veículo ou perfil, data e hora de publicação, o que ele afirma e se é fonte primária (quem fez, órgão oficial, documento) ou só repercussão.

**Instagram (e outras redes que exigem login):**
- Tentar abrir o link do post como qualquer outro. Se vier bloqueio (erro 429, tela de login ou página sem a legenda), não insistir e não tentar contornar.
- Pedir ao usuário, em uma frase, o print, o vídeo ou a legenda copiada daquele post. Com o material em mãos, checar pelo conteúdo e usar o link como fonte.
- Vídeo: extrair frames com ffmpeg (um a cada cinco segundos) e ler o que aparece. Não inventar falas: se a fala importar e não houver transcrição, pedir a transcrição.
- Conferir o perfil que postou: é o perfil oficial da pessoa ou do órgão, ou um repost?

Se um link não abrir por bloqueio de rede do ambiente, dizer qual site foi bloqueado e seguir com o resto.

## 3. Conferir em outras fontes
- Fazer WebSearch (modo extended quando o fato for recente) para cada afirmação central da pauta.
- Considerar confirmado só o que aparecer em pelo menos duas fontes independentes, ou em uma fonte primária oficial (órgão, documento, declaração da própria pessoa).
- Procurar sinais de problema: notícia antiga recirculando, data ou local diferente do que a pauta diz, foto ou vídeo de outro fato, número divergente entre fontes, desmentido oficial.
- Fato só da cidade, sem registro em veículo nenhum: marcar como "sem registro externo" e listar o que o usuário precisa confirmar (quem, documento, foto).

## 4. Resultado
Responder em formato curto, sem texto antes:

**Checagem**
- ✅ Confirmado: afirmação — fontes
- ⚠️ Parcial ou divergente: afirmação — o que diverge e onde
- ❌ Não confirmado ou desmentido: afirmação — motivo
- ❓ Sem registro externo: afirmação — o que falta

**Alertas**: data antiga, foto de outro fato, perfil não oficial etc. (omitir se não houver).

**Fontes**: lista de links usados, com veículo e data.

Depois, guardar no objeto de pauta: os fatos confirmados, as divergências e a lista de fontes. Título, card e legenda usam só os fatos confirmados.

## 5. Quando parar
- Seguir direto quando o fato principal estiver confirmado. Pontos parciais viram atribuição na legenda ("segundo", "informou").
- Parar e perguntar ao usuário só quando o fato principal estiver ❌ ou ❓, ou houver alerta grave (notícia antiga, foto de outro fato). Mostrar o relatório e perguntar se segue, ajusta a pauta ou para.

## Regras
- Nunca afirmar como confirmado o que não foi lido numa fonte.
- Nunca inventar data, número, nome ou cargo.
- Não publicar nada nem usar o Postador.
- Toda alteração pedida na conversa sobre a checagem vai direto para esta skill, na mesma sessão, via proposta de edição.
