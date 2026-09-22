# Regra autoritativa — exatamente um episódio por execução

Esta regra define a identidade de uma **execução** do agente e o limite absoluto de episódios do Além do Óbvio / Content Short Factory.

Em qualquer conflito sobre identidade da execução, troca de slug, continuidade após queue ou possibilidade de iniciar outro tema, **esta regra prevalece** sobre regras editoriais e de publicação antigas. A `main` continua sendo a fonte da verdade para contratos técnicos.

## 1. Definição absoluta de execução

**Uma execução = uma única invocação/chamada do agente disparada pelo agendamento.**

A execução começa quando o agente recebe a tarefa e termina somente quando devolve a resposta final daquela chamada.

NÃO começa uma nova execução quando um commit é criado, o duplicate preflight termina, o media preflight passa, uma publish queue é criada, uma GitHub Action começa/termina, uma plataforma publica ou muda a hora do relógio.

Somente um **novo disparo real do agendamento** inicia outra execução.

## 2. Snapshot obrigatório no início

Antes de pesquisar temas ou criar arquivos, registre:
- `EXECUTION_START_HEAD`: SHA atual de `main`;
- `QUEUES_AT_START`: arquivos já existentes em `.publish-queue/`;
- `EXECUTION_SLUG=UNSET`.

Queue existente no snapshot pode ser herdada. Queue criada depois pertence à execução atual e nunca autoriza um segundo episódio.

## 3. Travamento imutável do slug

Enquanto `EXECUTION_SLUG=UNSET`, avalie candidatas e execute duplicate preflights.

Fixe `EXECUTION_SLUG=<slug>` no primeiro destes eventos:
1. retomada legítima de episódio incompleto;
2. candidata recebe `UNIQUE_CANDIDATE` e autoria começa;
3. qualquer arquivo é escrito em `episodes/<slug>/`.

Depois disso o slug é **IMUTÁVEL até a resposta final**. É proibido voltar ao pool, autorizar outra candidata, criar duplicate-check para outro tema, iniciar outro episódio, fazer media preflight de outro slug ou criar queue para outro slug.

Toda correção, retry, media preflight e publicação permanece no mesmo `EXECUTION_SLUG`.

## 4. EM_ANDAMENTO nunca é estado final

`queued`, `pending`, `waiting`, `requested` e `in_progress` são estados transitórios.

Nunca encerre a chamada apenas porque `Content candidate duplicate preflight`, `Episode media preflight` ou `Publish episode` ainda está executando.

Enquanto o GitHub conectado permitir consultar o mesmo run/job, **continue acompanhando** até resultado terminal verificável.

Em particular:
- duplicate preflight em andamento = aguardar/consultar até `UNIQUE_CANDIDATE` ou `DUPLICATE_CANDIDATE`;
- `DUPLICATE_CANDIDATE` = descartar somente a candidata e continuar o loop, enquanto `EXECUTION_SLUG=UNSET`;
- media preflight em andamento = continuar acompanhando;
- Publish Action em andamento = continuar acompanhando;
- simples demora, número de consultas ou step ainda executando NÃO constituem bloqueio.

`PUBLICAÇÃO_EM_ANDAMENTO` pode existir internamente, mas não deve ser resposta final enquanto o run continuar consultável.

## 5. Estados realmente terminais

A resposta final só é permitida quando ocorrer:
- `PUBLICADO`: Publish Action terminal e plataformas executadas pela `main` verificadas;
- `FALHA_PUBLICAÇÃO`: causa concreta + recuperação/retries seguros esgotados ou impedidos;
- `SEM_CANDIDATO`: somente após o limite real de candidatas definido pela regra editorial;
- `BLOQUEADO`: causa técnica concreta que realmente impeça continuar;
- `FALHA`: causa terminal concreta;
- `PUBLICAÇÃO_NÃO_VERIFICADA`: somente quando uma limitação técnica real de acesso impedir continuar verificando nesta invocação.

Estado de workflow em andamento nunca satisfaz essas condições.

## 6. Falha recuperável não encerra a chamada

Uma Action com `failure` é intermediária enquanto houver diagnóstico ou correção segura.

No mesmo slug:
`diagnosticar -> corrigir em lote -> persistir na main -> novo request permitido -> acompanhar até terminal -> repetir dentro dos limites atuais`.

Ausência do antigo log bruto não é, sozinha, `DIAGNÓSTICO_INACESSÍVEL`. Use metadados, outputs, summaries, annotations, artefatos e, se necessário, reproduza deterministicamente o validator lendo workflow/scripts/arquivos do mesmo slug.

Erro novo revelado depois de uma correção é continuação normal do reparo, não autorização para parar nem trocar de tema.

## 7. Queue não libera segundo episódio

Queue significa publicação solicitada. Não limpa `EXECUTION_SLUG`, não reinicia a execução e não autoriza nova seleção editorial.

Depois da queue, acompanhe somente publicação/recovery do mesmo slug até estado terminal.

## 8. Regra de ouro

**UMA CHAMADA DO AGENDAMENTO = NO MÁXIMO UM EPISÓDIO AUTORADO.**

**DUPLICATE DE CANDIDATA = CONTINUAR O POOL, NÃO ENCERRAR A EXECUÇÃO.**

**PRIMEIRO SLUG AUTORIZADO/RETOMADO = EXECUTION_SLUG IMUTÁVEL.**

**EM_ANDAMENTO != ESTADO FINAL.**

**MEDIA PREFLIGHT EM_ANDAMENTO = CONTINUAR ACOMPANHANDO.**

**PUBLISH ACTION EM_ANDAMENTO = CONTINUAR ACOMPANHANDO.**

**SÓ RESPONDER ANTES DO TERMINAL SE HOUVER BLOQUEIO TÉCNICO REAL QUE IMPEÇA CONTINUAR.**

**QUEUE/PASS/PUBLICAÇÃO NÃO REINICIAM A EXECUÇÃO.**
