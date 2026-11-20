---
name: publicar-mlabs-folha-de-bel
description: Use para publicar ou agendar posts da Folha de Bel pela mLabs (MCP MLABS) — card estático, carrossel ou reels. Define canais padrão, collabs fixas e a confirmação obrigatória antes de publicar.
---

# Publicar pela mLabs (Folha de Bel)

## Regra de ouro
Nunca publicar, agendar nem criar post sem o OK explícito do usuário na conversa.
Antes de chamar `create_post`, mostrar um resumo: canais, horário (agora ou data/hora),
legenda, mídia e collabs. Só publicar depois da confirmação.
Subir mídia com `upload_media` é permitido antes do OK (não publica nada).

## Perfil
- Perfil mLabs: FOLHA DE BEL — `profileId` em `list_profiles` (busca "FOLHA DE BEL").
- Fuso: America/Sao_Paulo.

## Canais padrão
- **Card estático (foto ou carrossel): sempre Instagram + Facebook** (`instagram`, `facebook`).
- Reels: seguir o padrão dos posts anteriores (`instagram_reels`, `facebook`, `tiktok_business`),
  salvo pedido diferente do usuário.

## Collabs fixas no Instagram (sempre, feed ou reels)
Em todo post com `instagram` ou `instagram_reels`, convidar as três contas abaixo
(limite da mLabs/Instagram: 3 collabs). IDs conferidos com `search_social_users` em 20/11/2026;
se a mLabs recusar algum, buscar de novo pelo @ exato.

| Conta | collabId |
|---|---|
| @girobelfordroxo (Giro Belford Roxo \| Notícias de Bel) | 65731250691 |
| @maisbelfordroxo (MAIS BELFORD ROXO \| Notícias de Bel) | 69386224579 |
| @noticias_debel (Belford Roxo Notícias) | 13697051988 |

No campo `collabs` do `create_post`, um item por conta e por canal do Instagram, com
`channelSourceKey` (`instagram` ou `instagram_reels`), `collabId` e `collabName` (o @ sem arroba).
Facebook feed não tem collab na mLabs (só `facebook_reels`, máx. 1) — não enviar collab no Facebook.

## Mídia
- Card gerado localmente: salvar em `cards/`, fazer commit/push e usar a URL
  `https://raw.githubusercontent.com/contatofolhadebel-web/folhadebel-cards/<branch>/cards/<arquivo>`
  em `upload_media`. Esperar `get_media_upload` = completed e usar o `imageId`.
- Sem URL pública: usar `attach_media` e pedir para o usuário enviar pelo link.

## Música
- Música do Instagram só em `instagram_reels` (`search_instagram_audio`, máx. 1).
- Música do TikTok só em `tiktok`/`tiktok_business` (`search_tiktok_music`).
- Card estático no feed não aceita música.

## Depois de publicar
Mostrar o `scheduleLink.url` como "Ver agendamento na mLabs" e repassar avisos (`warnings`).
