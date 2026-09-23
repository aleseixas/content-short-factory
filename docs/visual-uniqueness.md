# Unicidade visual — contrato compatível com o validator atual

Esta documentação descreve a regra efetivamente aceita pelo Media Preflight da `main`.

## Fonte da verdade

No estado atual, `check_episode_media.py` chama `_assert_intra_episode_visuals_unique` e bloqueia dois shots que compartilhem qualquer identidade principal por:

- `asset_id`;
- `file`;
- URL normalizada.

O validator não considera trims diferentes suficientes para liberar o mesmo arquivo de vídeo em dois shots.

## Regra operacional

### Imagens

Zero reuso. Cada imagem principal é exclusiva de um shot.

### Vídeos

Zero reuso da fonte física no episódio.

Mesmo que dois shots usem intervalos temporais diferentes e não sobrepostos, eles NÃO devem resolver para o mesmo arquivo/URL de vídeo enquanto o validator atual permanecer assim.

Logo:

- mesmo YouTube `provider_id` → reserve para um único shot principal;
- mesmo arquivo baixado → não repetir;
- mesma URL normalizada → não repetir;
- aliases diferentes → não contornam a regra;
- crop, speed, motion, freeze, FX e Best Segment → não criam uma nova identidade de visual.

## Relação com o resolver

O resolver pode tecnicamente conhecer reservas temporais e trims distintos, mas a autoria não deve depender disso para reutilização intraepisódio enquanto o gate final continuar source-level.

Ao montar `visual_candidates.json`, faça deduplicação global do episódio. Se um `provider_id` aparecer em vários slots, escolha o slot em que ele é mais valioso e substitua os demais por fontes diferentes antes do primeiro Media Preflight.

## Gate antes do primeiro episode-check

Audite o conjunto final esperado:

1. todos os shots têm `asset_id` diferentes;
2. nenhum asset usado compartilha o mesmo `file`;
3. nenhum asset usado compartilha a mesma URL normalizada;
4. nenhum `provider_id` de vídeo foi planejado para mais de um shot;
5. não existem trims diferentes da mesma fonte sendo tratados como visuais independentes.

Se uma colisão for previsível, corrija antes de criar `.episode-check/<slug>-<nonce>.json`.

## Por que esta regra existe

O objetivo é evitar desperdiçar um ciclo externo de Media Preflight com `INTRA_EPISODE_VISUAL_REUSE` quando a colisão já pode ser detectada durante a autoria.

Quando o validator mudar para reconhecer unicidade por segmento temporal, esta documentação deve mudar junto. A `main` executável sempre prevalece sobre documentação antiga.
