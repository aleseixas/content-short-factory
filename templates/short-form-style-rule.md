# Regra obrigatória — linguagem de alta retenção + ritmo visual contextual

Esta regra complementa `templates/editorial-direction-prompt.md` e deve ser aplicada na autoria de novos episódios enquanto a `main` continuar compatível com os contratos abaixo.

## 1) Objetivo editorial

O objetivo é maximizar retenção, curiosidade, comentários, compartilhamentos e reconhecimento imediato do tópico sem sacrificar factualidade.

O episódio deve parecer um Short/Reel/TikTok pensado por um editor agressivo em retenção: história forte, hook imediato, progressão constante e visual que realmente ajude a contar o que está sendo narrado.

Sensacionalismo é desejado na forma. A barreira é factual: não invente fatos, não distorça fonte, não transforme teoria em certeza e não prometa algo que o episódio não entrega.

## 2) Linguagem: 80% narrativa + 20% reação/conversa

Mire aproximadamente:

- 80% narrativa clara, eficiente e progressiva;
- 20% reação/conversa.

Use com naturalidade, sem quota mecânica, expressões como:

- `cara`;
- `olha isso`;
- `só que`;
- `e aí`;
- `o mais doido é que`;
- `pensa nisso`;
- `e aqui fica absurdo`;
- `detalhe`;
- `e não para por aí`.

O narrador deve soar como alguém muito envolvido contando para um amigo uma história marcante que acabou de descobrir.

Evite linguagem acadêmica, enciclopédica, institucional ou excessivamente neutra quando houver uma forma mais viva de dizer a mesma coisa.

### Hook

A primeira frase deve identificar rapidamente o tópico ou a entidade principal e já abrir tensão, conflito, consequência, surpresa ou uma promessa forte.

Prefira premissa inesperada em vez de resumo seco.

Exemplo de direção:

`Beat It, do Michael Jackson, nasceu de uma missão meio absurda: colocar rock pesado dentro de Thriller sem deixar de soar como Michael Jackson.`

O hook deve criar a sensação de que existe uma segunda camada que será revelada nos próximos segundos.

### Desenvolvimento

Transforme informação em progressão narrativa:

`fato → detalhe inesperado → consequência → nova virada`.

Evite sequência de fatos independentes. Use conectores conversados quando ajudarem a empurrar a história adiante.

## 3) Primeiro visual — reconhecimento específico obrigatório

Nos primeiros **0,0–1,5s**, mostre a entidade principal ou uma evidência diretamente ligada ao hook: pessoa, empresa, produto, logo histórico, documento, interface, lugar, objeto, obra, artista, banda ou capa quando pertinente.

A regra existe para o espectador reconhecer imediatamente o assunto. Não use stock genérico se houver representação real adequada. Quando houver mais de uma opção forte, escolha a que comunicar melhor a promessa, funcionar no 9:16 e suportar o texto sem conflito.

## 4) Ritmo visual: agressivo, mas não aleatório

Para Shorts/Reels/TikTok na faixa de aproximadamente 60–90 segundos, mire normalmente **20–30 takes principais**. Em um episódio de ~72–82s, prefira normalmente **22–28 takes**, ajustando quando a duração real da narração e a qualidade dos visuais justificarem.

O objetivo é sensação constante de avanço visual, mas **contexto vale mais do que troca vazia de imagem**.

Para novos episódios, use `"smart_visual_pacing": {"enabled": true}` no topo de
`timeline.json` quando quiser o ajuste conservador de fronteiras antes do render.
O recurso preserva assets, ordem, áudio e duração total; ele não substitui o
planejamento de segmentos/shots nem autoriza depender do pipeline para corrigir
uma montagem semanticamente fraca. Campo ausente ou desativado mantém o pacing
legado.

### HARD GATE — imagens estáticas obrigatoriamente entre 2 e 4 segundos

Esta é uma **regra obrigatória de pacing**, não uma recomendação. Ela prevalece sobre qualquer redação genérica ou antiga do projeto que diga `normalmente 2–4s`, que permita imagem estática longa por “força editorial” ou que trate 2–4s apenas como referência.

Para TODO shot cujo asset principal seja uma **imagem estática**:

- a duração final do shot deve ficar **entre 2,0s e 4,0s**;
- **nunca** mantenha uma imagem estática por mais de 4,0s;
- **nunca** use uma imagem estática por menos de 2,0s apenas para acelerar artificialmente o vídeo;
- zoom, crop, pan, `push_in`, `pull_out`, text FX, highlight, overlay, transição ou SFX sobre a mesma imagem **não reiniciam a contagem** e não autorizam ultrapassar 4,0s;
- se a fala associada a uma imagem ficaria acima de 4s, **divida a narração em segmentos menores antes de finalizar `story.json`/`timeline.json` e use outro visual principal no segmento seguinte**;
- no contrato atual `1 segment = 1 shot`, a segmentação do roteiro deve ser planejada para tornar essa regra possível; não aceite um segmento longo com imagem e espere que motion/FX resolvam o pacing;
- se houver dúvida entre prolongar a imagem e trocar para outro asset semanticamente correto, **troque a imagem**.

O primeiro visual continua precisando aparecer imediatamente nos primeiros 0,0–1,5s; se ele for imagem estática, pode começar em 0,0s e permanecer até completar a janela obrigatória de 2–4s.

### Vídeos — podem respirar mais

Vídeo **não usa o hard cap de 4s das imagens**. Pode permanecer por mais tempo quando houver movimento útil, contexto real e relação clara com a narração.

- 4–6s continua sendo uma faixa comum para vídeos fortes;
- vídeos podem passar de 6s quando a ação/performance/entrevista/bastidor/demonstração realmente sustentar o plano e a narração continuar semanticamente alinhada;
- não alongue vídeo só por ser vídeo;
- vídeo genérico, pouco relacionado ou semanticamente fraco deve ser curto, rebaixado ou substituído;
- um vídeo longo deve estar mostrando algo que vale acompanhar: performance específica, entrevista, bastidor, ação, reação, trecho de evento, demonstração, contexto histórico ou outra informação visual relevante.

Hooks, reveals, montagens, reações e viradas podem usar cortes mais rápidos quando isso aumentar retenção, mas **uma imagem estática individual continua sujeita ao mínimo obrigatório de 2,0s**.

`motion`, zoom, crop, speed, transição, text FX, highlight, overlay ou SFX sobre o mesmo asset NÃO contam como troca de take.

## 5) Pool visual: 100–120 candidatos e relevância temática obrigatória

Não pesquise apenas a quantidade de assets que entrará no render.

Para cada take/slot importante, mire em média **4–5 candidatos reais**; em slots visualmente ricos, procure até **8 opções úteis e de fontes distintas**, conforme disponibilidade.

Para episódios com 20–30 takes finais:

- o **alvo editorial padrão é 100–120 candidatos visuais totais**;
- **80 candidatos é o mínimo aceitável** quando a disponibilidade real limitar a busca;
- em temas ricos visualmente, pode ultrapassar 120 quando isso melhorar de verdade a seleção;
- a seleção final só acontece depois de comparar candidatos do mesmo tipo por slot.

Não confunda `assets finais usados no render` com `candidatos pesquisados`.

### Regra crítica: o pool deve contar a história

O pool visual NÃO pode ser inflado com material genérico apenas para bater quantidade.

Cada candidato precisa ter relação clara com pelo menos um elemento relevante do episódio, como:

- o próprio tópico ou acontecimento;
- a entidade principal;
- produto, logo, obra, documento, interface ou registro diretamente relacionado;
- demonstração, reportagem, entrevista, performance ou ação ligada ao tópico;
- pessoa citada na narração;
- fundador, pesquisador, criador, técnico, atleta, artista ou colaborador citado;
- bastidor, arquivo histórico ou processo documentado;
- entrevista relacionada;
- época ou evento específico;
- objeto, instrumento, edifício ou lugar citado;
- prêmio, indicador, evento, lançamento ou acontecimento mencionado;
- conceito visual que represente diretamente o que está sendo explicado naquele take.

Antes de buscar cada slot, pergunte editorialmente:

**`O que está sendo dito neste exato momento e qual visual prova, mostra ou reforça essa ideia?`**

Só depois considere estética.

### Rebaixamento obrigatório de visuais sem contexto

Rebaixe fortemente candidatos que sejam:

- genéricos;
- abstratos;
- decorativos;
- apenas vagamente ligados à entidade;
- performances aleatórias que não ajudam a história;
- multidões/palcos/estúdios sem ligação com o trecho narrado;
- vídeos visualmente bonitos, mas semanticamente vazios;
- imagens de qualidade técnica alta que poderiam servir para qualquer tópico.

Em caso de dúvida, prefira **um asset mais contextual e menos bonito** a um asset mais bonito que não tenha conexão clara com a história.

Qualidade visual é importante, mas a ordem editorial é:

1. **relevância semântica para o take**;
2. **reconhecimento e clareza**;
3. **qualidade técnica/visual**;
4. **movimento/estética**.

O pool deve ser WEB-FIRST e seguir `docs/visual-search.md`.

Vídeo compete com vídeo e imagem compete com imagem. Reserve o vencedor de cada slot e faça deduplicação global antes da queue.

## 6) Proporção de vídeo e imagem

Como referência editorial, tente fechar aproximadamente **60–80% dos takes finais com vídeo** e **20–40% com imagem**, mas somente quando os vídeos realmente agregarem contexto.

Em ~24 takes, algo como **15–19 vídeos e 5–9 imagens** é uma referência, não hard gate.

Não escolha vídeo inferior apenas para cumprir proporção. Se imagens mais contextuais contarem melhor determinado trecho, use imagens.

Todo episódio deve mostrar claramente a entidade principal quando houver representação visual real adequada — além da regra específica do primeiro visual.

Nunca reutilize a mesma imagem. Uma mesma fonte de vídeo pode alimentar normalmente até 3 shots, somente com trims disjuntos, não sobrepostos e semanticamente próprios; crop/FX sobre o mesmo trecho não cria take novo.

## 7) Relação com texto na tela

A maior densidade de cortes não autoriza poluição textual.

Siga `templates/caption-layout-rule.md`: legenda falada tem prioridade; text FX/highlight/overlay devem respeitar as zonas e sair do caminho quando disputarem leitura.

Não use texto editorial para compensar um visual fraco ou sem contexto.

## 8) Fechamento — CTA contextual sem end card visual

O fechamento segue `templates/end-card-cta-rule.md`, que apesar do nome histórico do arquivo agora define **CTA contextual sem end card visual**.

A arte `assets/branding/end_card_template.jpg` está **desativada para novos episódios** e não deve ser usada, copiada para a pasta do episódio nem substituída por outra arte genérica.

Fluxo esperado:

`hook reconhecível → história visual contextual → payoff → CTA contextual curto sobre o último visual da própria história`

O payoff deve vir antes do CTA.

O último visual deve continuar sendo um asset real e relevante do episódio — idealmente algo forte ligado ao tópico, à entidade ou ao payoff. O CTA pode ser falado e, quando houver espaço visual claro, reforçado com `text_fx` curto.

Escolha apenas UMA ação principal no CTA, priorizando comentário ou compartilhamento. Não encerre com pedido triplo genérico.

## 9) Checklist editorial antes da queue

Antes de finalizar, confirme obrigatoriamente:

- primeiro visual = entidade/evidência principal claramente reconhecível;
- 20–30 takes quando a duração do episódio comportar esse ritmo;
- **toda imagem estática dura entre 2,0s e 4,0s, sem exceção editorial acima de 4s**;
- quando uma imagem exigiria >4s, o roteiro foi dividido em segmentos menores e houve troca real do visual principal;
- vídeos podem durar mais que imagens e podem ultrapassar ~6s somente quando movimento/contexto real sustentarem o plano;
- pool normalmente entre 100–120 candidatos;
- pool não foi inflado com visuais genéricos;
- cada slot possui candidatos relacionados ao que está sendo narrado;
- visuais genéricos/sem contexto foram rebaixados;
- maioria dos takes finais é vídeo quando houver vídeos contextuais suficientes;
- zero reuso de imagens e do mesmo trecho de vídeo; no máximo 3 trims disjuntos por fonte;
- entidade principal aparece claramente quando houver representação real adequada;
- legenda/texto editorial não competem;
- `assets/branding/end_card_template.jpg` NÃO foi usado;
- não foi criada end card genérica substituta;
- CTA final é contextual, curto e pede uma única ação;
- último visual continua pertencendo à história e reforça o encerramento.

## 10) HARD GATE técnico — duplicate preflight por GitHub Action

Antes da PRIMEIRA escrita em `episodes/<slug>/`, a candidata deve passar pelo preflight técnico de duplicidade da `main`.

Fluxo obrigatório para o agente via GitHub:

1. consulte `episodes/`, `.publish-queue/` e `.publish-retry/` semanticamente;
2. depois de definir o topic final e slug, crie exatamente UM `.duplicate-check/<slug>-<nonce>.json`:

```json
{
  "topic": "Tema específico final",
  "content_profile": "perfil livre opcional",
  "slug": "slug_normalizado"
}
```

3. localize a execução `Duplicate candidate preflight` associada ao commit exato;
4. só `PREFLIGHT_RESULT=UNIQUE_CANDIDATE` autoriza iniciar o episódio;
5. `PREFLIGHT_RESULT=DUPLICATE_CANDIDATE` descarta somente a candidata; no Profile Mode, avance no pool;
6. falha de infraestrutura, request inválido ou ausência de marker deixa a candidata `BLOQUEADA`;
7. busca vazia e ausência do slug exato não substituem o gate;
8. o request não conta como episódio ou queue;
9. use nonce novo por candidata;
10. sem evidência de unicidade, não escreva `episodes/<slug>/`.

`song` e `artist` podem ser aceitos por compatibilidade legada, mas novos requests usam `topic`. Profile Mode precisa resolver o tópico antes do preflight.

## 11) HARD GATE técnico — media preflight antes da publish queue

Depois que o episódio estiver completamente autorado e imediatamente ANTES de criar `.publish-queue/<slug>.txt`, execute obrigatoriamente o preflight técnico real de mídia.

Fluxo obrigatório:

1. crie exatamente UM arquivo novo `.episode-check/<slug>-<nonce>.json` com:

```json
{
  "slug": "slug_normalizado"
}
```

2. essa escrita dispara `.github/workflows/episode-media-preflight.yml`;
3. localize a Action `Episode media preflight` associada ao commit exato do request e leia o job/log;
4. o preflight usa `check_episode_media.py`, que carrega o episódio com os parsers reais do engine, baixa/valida todos os assets com o mesmo `AssetManager` usado no render e resolve o background music com o mesmo `resolve_background_music` usado no pipeline;
5. só `MEDIA_PREFLIGHT_RESULT=PASS` autoriza criar `.publish-queue/<slug>.txt`;
6. HTTP 403, 404, 429, 5xx/525, payload inválido, imagem que o Pillow não reconhece, vídeo inválido no ffprobe, profile de música sem faixa resolvível ou qualquer outra falha de mídia = NÃO criar queue ainda;
7. quando o preflight falhar, corrija apenas os assets/background do mesmo episódio e rode um NOVO `.episode-check/<slug>-<nonce>.json`; isso não conta como queue nem retry de publicação;
8. nunca crie `.publish-queue` por suposição, mesmo que as URLs pareçam válidas no navegador;
9. após um PASS, não altere `assets.json`, `timeline.json` ou o background antes da queue; se alterar, rode o media preflight novamente;
10. objetivo: erros de download/mídia devem ser descobertos antes da primeira tentativa de publicação, preservando queue/retry para falhas reais posteriores.
