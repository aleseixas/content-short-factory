# Regra autoritativa — um episódio válido por execução

Esta regra define o contrato de uma execução do Além do Óbvio / Content Short Factory. Em conflitos sobre identidade da execução, troca de candidato, continuidade e critério de saída, esta regra prevalece sobre instruções editoriais antigas. A `main` continua sendo a fonte da verdade para contratos técnicos.

## 1. Contrato da execução

**Uma execução = uma invocação do agendamento cujo objetivo é entregar EXATAMENTE 1 episódio NOVO, válido e publicável para o slot atual, sempre que tecnicamente possível.**

A execução NÃO termina apenas porque um candidato foi escolhido, autorado, bloqueado ou reprovado. Falha de candidato não é automaticamente falha do job.

No início registre `EXECUTION_START_HEAD`, `QUEUES_AT_START`, `EXECUTION_SLUG=UNSET` e `DELIVERED_EPISODE=NO`.

## 2. Anti-duplicação absoluta

Nunca publique novamente episódio/slug que já tenha qualquer evidência de publisher iniciado, concluído, parcial, falho após início ou incerto. Esse slug é `CLOSED_HISTORY`.

Duplicate de candidata descarta somente a candidata e obriga a continuar o pool. Episódio já publicado nunca satisfaz uma nova execução.

## 3. Candidato ativo e substituição segura

`EXECUTION_SLUG` identifica o candidato ativo. Depois de iniciar autoria, tente reparar o MESMO slug enquanto houver correção materialmente segura e razoável.

Se o candidato se tornar **PRE_PUBLISH_UNRECOVERABLE** e houver evidência positiva de `EVER_PUBLISHED_OR_ATTEMPTED=NO`, ele pode ser abandonado sem publicação e a execução DEVE voltar à seleção editorial para criar um NOVO candidato.

Considere `PRE_PUBLISH_UNRECOVERABLE` quando, antes de qualquer publisher iniciar, o candidato falhar definitivamente em gate editorial/técnico, media preflight, assets, render/schema ou outra validação e as tentativas/correções seguras previstas tiverem sido esgotadas ou a causa tornar aquele candidato inviável.

Ao abandonar candidato pré-publicação:
- marque-o `ABANDONED_PRE_PUBLISH`;
- nunca crie queue para ele depois;
- defina `EXECUTION_SLUG=UNSET`;
- volte ao pool e escolha tema realmente novo;
- refaça duplicate/history checks completos;
- continue a MESMA execução.

Isso é proibido se qualquer publisher já iniciou ou puder ter iniciado.

## 4. Limites

A execução pode avaliar até 15 candidatas e autorar candidatos substitutos quando necessário, mas deve publicar **no máximo 1 episódio**. Use no máximo 5 candidatos autorados/substitutos por execução, salvo regra mais restritiva da main. Para cada candidato, respeite os limites técnicos de reparo/preflight da main.

## 5. Publicação fecha a substituição

Imediatamente antes da queue, reconstrua novamente todo o histórico. Só publique com evidência positiva de `EVER_PUBLISHED_OR_ATTEMPTED=NO`.

No instante em que qualquer publisher iniciar ou puder ter iniciado, o slug fica fechado para republicação automática e **não deve ser criado episódio substituto para o mesmo slot**, evitando duplicação editorial.

## 6. Critério de saída

A execução só termina normalmente quando ocorrer:
1. `SUCCESS/PUBLICADO`: episódio novo desta execução passou pelos gates e chegou ao terminal exigido pela main;
2. `PARTIAL_NO_TOUCH`: publisher iniciou e resultado ficou parcial/misto/incerto;
3. `HARD_FAILURE/BLOCKED`: bloqueio externo/técnico real impede continuar ou todos os limites globais foram realmente esgotados.

**É proibido usar Media Preflight FAIL/BLOQUEADO, semantic gate reprovado, asset ruim ou candidato inviável como resultado final enquanto ainda for pré-publicação e houver capacidade de selecionar outro candidato.**

## 7. Fluxo obrigatório

`início -> selecionar -> duplicate check -> autorar -> validar ->`

- `PASS -> queue -> publicação -> terminal -> fim`
- `FAIL recuperável -> reparar mesmo candidato -> revalidar`
- `FAIL pré-publicação irrecuperável -> abandonar -> novo tema -> duplicate check -> autorar -> validar`

## 8. Regra de ouro

**O JOB ENTREGA UM EPISÓDIO; ELE NÃO ENTREGA UMA TENTATIVA.**

**FALHA DE CANDIDATO != FALHA DA EXECUÇÃO.**

**DUPLICATE = DESCARTAR E CONTINUAR.**

**PRE_PUBLISH_UNRECOVERABLE + NENHUM PUBLISHER INICIADO = SUBSTITUIR POR NOVO CANDIDATO.**

**QUALQUER PUBLISHER INICIADO = ZERO REPUBLICAÇÃO E ZERO SUBSTITUTO AUTOMÁTICO PARA O MESMO SLOT.**

**NO MÁXIMO 1 EPISÓDIO PUBLICADO POR EXECUÇÃO.**