# Override obrigatório — unicidade visual compatível com o Media Preflight

Leia esta regra antes de fechar `assets.json`, `visual_candidates.json` e `timeline.json`.

Esta regra é autoritativa para a autoria e **SOBREPÕE qualquer orientação anterior que permita reutilizar o mesmo vídeo-fonte em mais de um shot por usar trims diferentes**.

## Regra atual da main — ZERO REUSO DE VISUAL PRINCIPAL

No estado atual da `main`, o Media Preflight executa `_assert_intra_episode_visuals_unique` em `check_episode_media.py` e considera repetição qualquer visual principal que compartilhe uma identidade por:

- `asset_id`;
- nome físico de `file`;
- URL normalizada.

Portanto, para a autoria agendada, a regra operacional é simples:

**cada shot principal deve terminar com um asset visual diferente.**

Isso vale para imagem E vídeo.

### Vídeos — trims diferentes NÃO tornam o arquivo único

Enquanto o validator atual continuar comparando identidade de asset/arquivo/URL:

- NÃO use o mesmo vídeo-fonte em dois shots principais, mesmo que os `source_start_seconds` sejam diferentes;
- NÃO trate dois trims não sobrepostos do mesmo YouTube `provider_id` como visuais distintos;
- NÃO crie aliases ou nomes de asset diferentes que acabem resolvendo para o mesmo arquivo baixado;
- crop, focus, speed, motion, transition, freeze, visual FX, overlay e Best Segment NÃO transformam a mesma fonte física em outro visual para esse gate;
- se um vídeo excelente já foi reservado para um shot, os outros shots precisam usar outra fonte de vídeo ou uma imagem diferente.

**Até o validator da `main` mudar, zero reuso da fonte física vence qualquer regra antiga de até 3 usos por vídeo.**

## Imagens — zero reuso

A mesma imagem principal NUNCA pode ser usada em dois shots do episódio.

Crop, focus, zoom, motion, transition, visual FX, overlay ou qualquer outro tratamento NÃO transforma a mesma imagem em um visual novo.

URLs, aliases ou nomes diferentes que resolvam para o mesmo arquivo continuam sendo duplicata.

## visual_candidates.json — deduplicação GLOBAL antes do primeiro episode-check

O erro deve ser prevenido na autoria, não descoberto pela primeira Action.

Antes de criar o primeiro `.episode-check/<slug>-<nonce>.json`:

1. monte o pool de candidatos por slot;
2. normalize todos os candidatos de vídeo pela fonte real, usando prioritariamente `provider_id`, URL canônica e arquivo resolvido previsível;
3. revise o episódio inteiro, não slot por slot isoladamente;
4. um mesmo `provider_id`/URL de vídeo não deve permanecer como candidato selecionável principal em vários slots;
5. se o mesmo vídeo aparecer em vários slots, escolha editorialmente UM único slot para ele e substitua os demais por fontes diferentes antes do Media Preflight;
6. faça a mesma revisão para imagens por URL/arquivo;
7. confirme que a resolução esperada não pode produzir dois assets com o mesmo `file` ou URL.

Não confie no fato de os trims serem diferentes. O gate atual não usa trim para liberar reuso intraepisódio.

## Pool de candidatos — diversidade antes do resolver

O resolver só consegue escolher entre o que recebeu. Para slots visualmente ricos, mire normalmente em até **8 candidatos reais por slot**, preferindo **fontes diferentes no episódio inteiro**, não apenas dentro do slot.

Regras obrigatórias:

- cada slot deve pesquisar a partir de `topic`, frase, entidades, evento, local, período e `visual_intent`;
- quando a primeira busca trouxer vídeos repetidos, genéricos ou pouco ligados à fala, faça novas consultas semanticamente diferentes;
- um mesmo YouTube `provider_id` conta como uma única fonte global e deve ser reservado para no máximo UM shot principal;
- não deixe poucos IDs populares dominarem muitos slots;
- prefira candidatos `exact` e `direct`; use `contextual` conscientemente e `generic` apenas como último recurso;
- não trate cinco trims do mesmo vídeo como cinco candidatos diferentes;
- antes de fechar `visual_candidates.json`, faça uma auditoria global dos IDs/URLs/files e elimine colisões previsíveis.

## Gate editorial ANTES do Media Preflight

Antes do PRIMEIRO `.episode-check`, confirme explicitamente:

- cada shot principal aponta para um asset_id exclusivo;
- nenhum `file` é compartilhado entre dois assets usados por shots;
- nenhuma URL normalizada é compartilhada entre dois assets usados por shots;
- nenhum vídeo `provider_id` está planejado para vencer em mais de um slot;
- nenhum alias mascara a mesma fonte física;
- nenhum trim diferente do mesmo vídeo está sendo usado como justificativa de unicidade;
- o primeiro Media Preflight não deverá descobrir `INTRA_EPISODE_VISUAL_REUSE` por algo que já era verificável na autoria.

Se houver qualquer colisão, corrija o pool/timeline/assets ANTES de disparar a Action.

## Regra de ouro

**Na main atual: 1 shot principal = 1 fonte visual física exclusiva.**

Se futuramente `check_episode_media.py` passar a validar unicidade por intervalo temporal de vídeo, esta regra deverá ser atualizada novamente com base no código real. Até lá, o validator atual prevalece.
