# Regra obrigatória — conclusão real da publicação

Esta regra define quando uma execução do **Content Short Factory** pode ser considerada concluída.

Ela é autoritativa para **queue, acompanhamento da Publish Action, status final, recuperação de falhas e verificação por plataforma**. Em qualquer conflito com instruções antigas equivalentes a `queue -> STOP`, `a criação da queue encerra a tarefa`, `não acompanhe a Action`, `pare na primeira falha de workflow` ou `ACTION: SUCESSO` baseado apenas no media preflight, **esta regra prevalece**.

A `main` continua sendo a fonte da verdade para capacidades técnicas, workflows, publishers, schemas e estados realmente disponíveis.

## 0. Gatilhos automáticos por push — ausência de workflow dispatch NÃO é bloqueio

Antes de declarar `BLOQUEADO` por não existir uma operação/ferramenta explícita de `workflow_dispatch`, leia o `on:` do workflow atual na `main`.

Quando `.github/workflows/episode-media-preflight.yml` estiver configurado com `on: push` para `.episode-check/*.json`, **NÃO existe necessidade de disparar o workflow manualmente**. O contrato correto é:

`criar novo .episode-check/<slug>-<nonce>.json -> commit/push na main -> GitHub Actions dispara Episode media preflight automaticamente -> localizar o run associado ao commit/request -> acompanhar até estado terminal`.

A mesma interpretação vale para `duplicate-preflight.yml` quando o `on:` atual mostrar que `.duplicate-check/*.json` dispara por push.

Portanto:

- falta de ferramenta `workflow_dispatch` NÃO é `BLOQUEADO` quando o workflow é acionado por `push`;
- não procure nem exija uma operação manual de dispatch nesse caso;
- se a escrita do request na `main` retornar sucesso, considere o gatilho solicitado e passe a localizar/acompanhar o run;
- se o run ainda não apareceu, trate como estado transitório e consulte novamente enquanto houver capacidade de leitura; não converta simples atraso de criação da Action em bloqueio;
- só reporte bloqueio operacional se a própria escrita/push exigida pelo gatilho falhar, se GitHub Actions estiver efetivamente indisponível/inacessível, ou se a `main` atual tiver mudado para um gatilho que realmente exija uma ação não disponível;
- aplique a mesma regra aos demais gates/workflows cujo `on:` atual demonstre disparo automático por escrita/push.

## 1. Queue não é conclusão

A criação de `.publish-queue/<slug>.txt` significa apenas que o episódio foi entregue ao pipeline de publicação.

Nunca considere a execução concluída apenas porque o media preflight passou, a queue foi criada ou o workflow de publicação foi disparado. Estados `queued`, `pending`, `waiting`, `requested` ou `in_progress` são transitórios enquanto o mesmo run/job puder ser consultado.

## 2. Fluxo obrigatório até publicação

Depois de o episódio passar pelo media preflight e a queue ser criada, não escolha outro tema e não crie outro episódio.

Acompanhe a execução exata de `.github/workflows/publish-episode.yml` correspondente ao mesmo slug até obter evidência real do estado do job e das etapas por plataforma.

`tema -> duplicate preflight -> autoria -> media preflight PASS -> queue -> Publish episode -> YouTube -> Instagram -> Facebook -> TikTok -> verificar resultados -> STOP`

## 3. Estados separados

Use sempre estados separados para `MEDIA PREFLIGHT`, `QUEUE`, `PUBLISH ACTION`, `YOUTUBE`, `INSTAGRAM`, `FACEBOOK` e `TIKTOK`. É proibido tratar sucesso do media preflight como sucesso da Publish Action.

## 4. Critério para STATUS: PUBLICADO

Só use `STATUS: PUBLICADO` quando houver evidência real acessível de que a Publish Action chegou a estado terminal e todas as etapas de plataforma que a `main` realmente executa terminaram com sucesso. Uma primeira falha de Media Preflight ou Publish Action não é automaticamente terminal, e status genérico como `failure`, `exit code 1`, nome de step vermelho ou `MEDIA_PREFLIGHT_RESULT=FAIL` nunca é causa raiz suficiente.

## 5. Status por plataforma

Reporte separadamente usando apenas evidência real. Nunca diga que uma plataforma publicou apenas porque o workflow geral foi disparado.

## 6. Falhas e retries — recuperação automática obrigatória

Uma GitHub Action com `failure` é estado intermediário enquanto existir diagnóstico ou recuperação segura e autorizada. Quando a causa concreta for corrigível nos arquivos do próprio episódio, aplique a correção na `main`, dispare nova validação do MESMO slug pelo mecanismo definido pelo `on:` atual e acompanhe o resultado.

### 6.0 Escada obrigatória de diagnóstico

Antes de considerar uma falha terminal: identifique run/job/commit/step; procure outputs/summaries/annotations e campos `MEDIA_PREFLIGHT_*`; consulte artefatos quando acessíveis; se não forem acessíveis, reproduza a validação determinística lendo workflow/scripts/validators e os arquivos do mesmo slug; cruze a causa com o SHA da main usado no run. Erro genérico nunca basta para encerrar.

### 6.1 Falha no Media Preflight antes da queue

O comportamento desejado é `validar tudo possível -> coletar lote de erros -> corrigir lote inteiro -> revalidar uma vez -> corrigir somente erros novos/dependentes`.

Ao precisar de nova Action, crie novo `.episode-check/<slug>-<nonce>.json`. **Se o workflow atual usar `on: push`, a criação/commit desse arquivo é o próprio disparo da Action; não exija `workflow_dispatch`.** Acompanhe a Action exata até terminal. Só PASS autoriza queue/publicação.

Não classifique como bloqueio um erro determinístico do próprio episódio que possa ser resolvido editando arquivos, escolhendo outro asset válido ou ajustando timeline/trims/metadata.

### 6.2 Falha na Publish Action

Se a Publish Action falhar, identifique a causa concreta. Retry só é permitido conforme `docs/publishing-retry.md` e somente quando comprovadamente seguro contra republicação.

### 6.3 Segurança contra duplicação

Não republique cegamente uma plataforma que já possa ter concluído. Uma falha de Media Preflight ou publicação não autoriza escolher outro tema dentro da mesma execução.

## 7. Limite de episódio continua valendo

A regra de no máximo 1 episódio por execução continua absoluta. Depois que um slug recebe `UNIQUE_CANDIDATE` e a autoria começa, toda a execução permanece dedicada a esse slug até estado final verificável, falha real após recuperação permitida ou bloqueio operacional concreto.

## 8. Regra de ouro

**Uma passada de preflight = descobrir o máximo de erros independentes possível.**

**Lote recuperável = corrigir todos os itens conhecidos antes da próxima validação.**

**Ausência de workflow_dispatch != bloqueio quando o workflow atual é acionado por push.**

**Erro genérico de Action = continuar diagnóstico; não encerrar.**

**Queue criada = publicação solicitada, não publicação concluída.**
