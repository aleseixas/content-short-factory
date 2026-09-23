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

Queue existente no snapshot pertence a uma execução anterior por padrão e serve apenas como histórico operacional.

### 2.1 Histórico fechado NÃO pode virar resultado da nova execução

No início de CADA nova chamada, classifique como `CLOSED_HISTORY` qualquer slug que, antes de `EXECUTION_START_HEAD`:

- já possuía `.publish-queue/<slug>.txt` e Publish Action terminal;
- já estava `PUBLICADO` / publicado nas plataformas previstas;
- já tinha estado terminal de geração/publicação e não há trabalho incompleto seguro pendente;
- ou aparece apenas porque é o episódio mais recente do repositório.

Um `CLOSED_HISTORY`:

- NÃO pode virar `EXECUTION_SLUG`;
- NÃO pode ser reportado como o episódio produzido pela chamada atual;
- NÃO satisfaz o objetivo da nova execução;
- NÃO pode fazer a chamada responder `STATUS: PUBLICADO` sem que um novo episódio desta chamada tenha sido criado ou uma retomada realmente incompleta tenha sido comprovada.

**Se todos os episódios anteriores estão terminais/fechados, a nova chamada DEVE manter `EXECUTION_SLUG=UNSET` e iniciar uma NOVA seleção editorial.**

É proibido usar “o último episódio já foi publicado com sucesso” como resposta de uma nova execução criadora.

Queue criada depois de `EXECUTION_START_HEAD` pertence à execução atual e nunca autoriza um segundo episódio.

## 3. Travamento imutável do slug

Enquanto `EXECUTION_SLUG=UNSET`, avalie candidatas e execute duplicate preflights.

Fixe `EXECUTION_SLUG=<slug>` no primeiro destes eventos:
1. **retomada legítima e comprovadamente incompleta** de episódio anterior;
2. candidata recebe `UNIQUE_CANDIDATE` e autoria começa;
3. qualquer arquivo é escrito em `episodes/<slug>/`.

### 3.1 Definição estrita de retomada legítima

“Retomada” só é válida quando existe evidência concreta de geração anterior INCOMPLETA que ainda precisa continuar, por exemplo:
- autoria iniciada sem queue e sem publicação terminal;
- Media Preflight falhou/ficou incompleto antes da queue;
- queue/publicação da geração anterior ainda é não terminal e pertence inequivocamente a uma execução que não chegou a concluir.

NÃO é retomada legítima:
- último episódio simplesmente ser o mais recente;
- último episódio já ter Publish Action terminal com sucesso;
- slug já publicado aparecer em `.publish-queue/`;
- encontrar run antigo `success`;
- encontrar episódio saudável sem erro pendente.

Se o episódio anterior já terminou com sucesso, **ignore-o para identidade da nova chamada e crie um novo episódio**.

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

Antes de responder, aplique também o **CURRENT-RUN EVIDENCE GATE**:

Para uma execução criadora nova sem retomada incompleta, deve existir evidência posterior a `EXECUTION_START_HEAD` de:
1. duplicate preflight desta chamada;
2. `UNIQUE_CANDIDATE`;
3. autoria de um slug novo;
4. continuidade desse mesmo slug até o estado terminal.

Run/queue/publicação anterior ao início da chamada pode ser citado apenas como histórico e NUNCA como prova de sucesso desta execução.

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

**EPISÓDIO JÁ PUBLICADO ANTES DE EXECUTION_START_HEAD = CLOSED_HISTORY, NUNCA RESULTADO DA NOVA CHAMADA.**

**NOVA CHAMADA + NENHUM INCOMPLETO REAL = EXECUTION_SLUG=UNSET -> NOVO DUPLICATE LOOP -> NOVO EPISÓDIO.**

**STATUS: PUBLICADO EXIGE EVIDÊNCIA DO SLUG DESTA EXECUÇÃO, NÃO DE UM RUN ANTIGO.**
