# Regra obrigatória — seleção genérica de conteúdo

Esta é a regra editorial de entrada do **Content Short Factory**. Ela serve a qualquer nicho, inclusive música, e prevalece sobre instruções antigas que tornem `artist`, `band`, `song`, `album` ou `related_song` obrigatórios.

## Contrato de entrada

O agente editorial externo recebe um objeto conceitual com estes campos:

```json
{
  "topic": "assunto específico ou null",
  "content_profile": "universo editorial em linguagem natural ou null",
  "category": "opcional",
  "angle": "opcional",
  "target_duration": 75,
  "language": "pt-BR",
  "additional_instructions": "opcional"
}
```

`content_profile` é texto livre, não enum. Valores como `economia brasileira`, `empresas que cometeram grandes erros`, `mistérios da internet`, `cinema e bastidores de Hollywood` e `música` são igualmente válidos. `additional_instructions` refina a pauta sem virar requisito estrutural.

Pelo menos um entre `topic` e `content_profile` deve existir.

## Prioridade e modos

1. Se `topic` existir, use exatamente esse assunto. Esse é o **Topic Mode**.
2. Se não houver `topic`, mas houver `content_profile`, selecione automaticamente um tema inédito dentro desse universo. Esse é o **Profile Mode**.
3. Se ambos existirem, `topic` tem prioridade; `content_profile`, `angle` e `additional_instructions` servem apenas como contexto editorial.
4. Nunca troque silenciosamente um `topic` fornecido por outro assunto “melhor”. Se ele for inseguro, impossível de verificar ou inadequado, reporte o bloqueio concreto.

Depois que o tema é definido, todo o pipeline é **topic-driven**. Pessoas, empresas, produtos, marcas, países, locais, eventos, tecnologias, objetos, obras, atletas, artistas, bandas e músicas são entidades extraídas do tema — não campos universais obrigatórios.

## Topic Mode

No Topic Mode:

- preserve o núcleo semântico do assunto recebido;
- use `angle` para decidir o recorte, sem contradizer o tema;
- identifique entidades, eventos, locais, período, conflito, consequência e payoff;
- determine o que precisa de confirmação factual;
- transforme o tema em short-form storytelling, não em verbete enciclopédico;
- consulte o histórico para detectar duplicidade temática, mas não substitua o tema sem avisar.

## Profile Mode

No Profile Mode, o mesmo agente editorial externo que cria o episódio deve escolher o tema antes de pesquisar profundamente e escrever o roteiro.

Monte um pool real de aproximadamente 10–15 candidatos. O pool deve refletir a amplitude inferida dinamicamente do `content_profile`; não use taxonomias hardcoded por nicho. Para cada candidato, avalie mentalmente:

- força e rapidez do hook;
- surpresa, conflito ou transformação;
- consequência e payoff claros;
- reconhecimento ou escala;
- potencial visual concreto;
- possibilidade de explicar com clareza no tempo alvo;
- qualidade e diversidade de fontes;
- factualidade e nível de certeza;
- distância temática em relação ao histórico recente;
- aderência a `additional_instructions`.

Esse pool é uma etapa de comparação, não licença para promover uma pauta duplicada ou fraca.

### Loop obrigatório de candidatos no Profile Mode

Cada execução agendada em Profile Mode tem como objetivo produzir **exatamente um episódio novo**. Rejeição de uma candidata é falha da candidata, não falha da execução.

1. Monte inicialmente um pool de **10 candidatas reais e distintas** seguindo integralmente o profile, o histórico, a proximidade cotidiana, a clareza para público brasileiro, a factualidade e o potencial visual.
2. Ordene as candidatas editorialmente e teste a melhor no duplicate preflight técnico **antes da autoria**.
3. Se retornar duplicata, similaridade proibida, candidata já tentada ou qualquer reprovação editorial de unicidade, descarte somente essa candidata e teste imediatamente a próxima.
4. **Nunca encerre a execução porque uma, duas ou várias candidatas falharam duplicate preflight.**
5. Continue candidata -> duplicate preflight -> próxima candidata até obter `UNIQUE_CANDIDATE`.
6. Se as 10 candidatas iniciais forem consumidas sem `UNIQUE_CANDIDATE`, gere **um novo lote de candidatas**, evitando semanticamente as já rejeitadas, e continue. Não reutilize paráfrases do mesmo fato.
7. Só é permitido encerrar sem episódio quando houver bloqueio objetivo externo/de infraestrutura que impeça novas verificações, ou quando todas as tentativas autorizadas pelo contrato operacional vigente estiverem realmente esgotadas. "Os primeiros temas eram duplicados" nunca é motivo terminal.
8. Assim que houver `UNIQUE_CANDIDATE`, **trave tema e slug** e continue na MESMA execução: autoria -> validação/schema -> media preflight -> queue -> publish -> verificação terminal das plataformas. `UNIQUE_CANDIDATE`, commit criado, autoria pronta, media PASS ou queue criada são estados intermediários, nunca conclusão.
9. Depois que a autoria começar, falha de asset, mídia, render, schema ou publicação **não autoriza trocar de tema**. Repare o mesmo episódio/slug segundo os contratos de recovery e publicação.
10. Uma candidata rejeitada no duplicate **não consome a vaga do episódio daquela execução agendada**.

Contrato mental obrigatório:

```text
10 candidatas distintas
  -> testar melhor candidata
  -> DUPLICATE? descartar só ela e testar a próxima
  -> esgotou 10? gerar novo lote
  -> UNIQUE_CANDIDATE
  -> AUTORIA
  -> MEDIA PREFLIGHT
  -> QUEUE
  -> PUBLISH
  -> VERIFICAR PLATAFORMAS
  -> exatamente 1 episódio novo
```

Descarte individualmente candidatas fracas ou duplicadas e avance pelas alternativas; o objetivo do Profile Mode não é apenas escolher uma pauta, mas **encontrar uma pauta inédita e levá-la até um episódio completo**.

Favoreça histórias específicas. Em economia, por exemplo, `Como uma corrida aos bancos derruba uma instituição em dias` tende a ter mais força narrativa que `O que é inflação?`. Isso é princípio de seleção, não uma lista fixa nem proibição de temas educativos.

O perfil pode produzir conteúdo evergreen, histórico, atual ou ligado a tendências. Atualidade só recebe bônus quando for relevante para o perfil, verificável e ainda útil na data de publicação.


## Acessibilidade imediata para público brasileiro

Quando o `content_profile` for voltado ao público geral brasileiro, trate **facilidade de entendimento na primeira escuta** como critério editorial central, não como detalhe de redação.

Prefira temas que um brasileiro médio consiga compreender e achar interessante **sem conhecimento técnico, científico, histórico ou cultural prévio**. A curiosidade pode ser inteligente e surpreendente, mas a ideia central precisa caber em uma frase simples e concreta.

Na seleção do pool:

- dê forte preferência a assuntos universais, concretos, visualizáveis e fáceis de explicar;
- favoreça animais, corpo humano, lugares, objetos, hábitos, fenômenos visíveis, acontecimentos históricos claros, invenções, situações do cotidiano, feitos humanos e fatos do planeta quando houver surpresa forte;
- penalize temas que dependam de muitos conceitos prévios, siglas, fórmulas, terminologia acadêmica, mecanismos abstratos ou longas explicações para o espectador entender por que aquilo é interessante;
- se o hook só funcionar depois de explicar 20–30 segundos de contexto, normalmente escolha outra candidata;
- se duas candidatas tiverem força parecida, escolha a que possa ser entendida mais rapidamente por uma pessoa comum;
- tema complexo só deve vencer quando puder ser traduzido para linguagem cotidiana sem perder a verdade nem exigir aula prévia.

Use o teste mental: **“uma pessoa comum no Brasil, ouvindo isso distraída no celular, entende em até poucos segundos o que está acontecendo e por que é surpreendente?”** Se a resposta for não, rebaixe ou descarte a candidata.

Não confunda simplicidade com banalidade. O objetivo é **curiosidade forte + explicação simples**, não fato óbvio ou infantilizado.


### Proximidade cotidiana e potencial de clique

Para o **Além do Óbvio** e outros perfis de curiosidades para público geral brasileiro, trate **proximidade com a vida real do espectador** como um sinal editorial forte de potencial de view. Não escolha pauta apenas porque é rara, distante ou intelectualmente sofisticada.

Quando duas ou mais candidatas forem igualmente verdadeiras, surpreendentes e visualmente fortes, prefira a que faça o público pensar imediatamente **“isso está na minha casa”, “eu vejo isso todo dia”, “eu tenho um desses”, “meu cachorro/gato faz isso”, “isso acontece no Brasil” ou “como eu nunca percebi isso?”**.

Dê bônus editorial, sem virar whitelist fixa, para curiosidades fortes envolvendo:
- cachorros, gatos e outros animais muito presentes na vida das pessoas;
- comportamentos estranhos ou surpreendentes de pets;
- objetos e fenômenos dentro de casa;
- cozinha, alimentos, geladeira, banheiro, quarto, eletrônicos, roupas e itens cotidianos;
- corpo humano, sono, sentidos, hábitos e comportamentos comuns;
- rua, carro, trânsito, elevador, mercado, escola, trabalho e situações reconhecíveis;
- fatos surpreendentes sobre o Brasil, cidades brasileiras, natureza brasileira, costumes, objetos, alimentos ou situações familiares ao público daqui;
- coisas comuns que escondem uma explicação inesperada.

### Prioridade editorial brasileira — Além do Óbvio

Para o **Além do Óbvio**, o público brasileiro não é apenas o idioma-alvo: é o centro da seleção editorial. Ao montar e ordenar o pool, dê preferência real a pautas que tenham conexão direta com o Brasil ou com a vida cotidiana de quem vive no Brasil.

Priorize, quando houver histórias fortes e verificáveis:
- curiosidades do Brasil, de cidades e regiões brasileiras;
- histórias pouco conhecidas da história do Brasil, com conflito, virada, consequência ou detalhe surpreendente;
- acontecimentos, personagens, invenções, obras, costumes, comidas, lugares, empresas, esportes e fenômenos brasileiros;
- fatos históricos brasileiros que tenham imagens, documentos, locais ou personagens visualmente fortes;
- assuntos brasileiros atuais que possam ser explicados como história/curiosidade, e não apenas como notícia;
- cachorros, gatos e outros animais com alta proximidade emocional e reconhecimento imediato;
- comportamentos curiosos de pets, animais urbanos e fauna brasileira;
- casa, comida, carro, trânsito, corpo humano, escola, trabalho, tecnologia cotidiana e objetos que brasileiros veem ou usam com frequência.

**Política e eleições também são permitidas**, inclusive em períodos eleitorais, desde que o episódio seja estritamente informativo, factual e neutro. Pode explorar, por exemplo, histórias de eleições brasileiras, fatos curiosos sobre presidentes e instituições, origem de regras eleitorais, urna eletrônica, Congresso, Constituição, campanhas históricas, acontecimentos políticos passados e funcionamento de instituições. Não faça propaganda, não peça voto, não recomende candidato/partido, não tente persuadir politicamente o público e não transforme opinião partidária em fato. Em temas atuais ou controversos, use fontes fortes, atribua alegações contestadas e deixe claro o que é fato documentado versus interpretação.

Temas globais continuam permitidos, mas **não devem vencer por padrão**. Para superar uma boa pauta brasileira/cotidiana, o tema global precisa ter hook, surpresa, relevância e potencial visual claramente superiores para o público daqui.

Na prática, ao ordenar candidatas do Além do Óbvio, use esta preferência editorial:
**Brasil/história brasileira/assunto brasileiro forte → pets e animais próximos → cotidiano reconhecível → tema global excepcional**.

Isso não é uma quota rígida nem exige que todo episódio seja brasileiro. É uma prioridade de interesse: **reconhecimento brasileiro + surpresa real + explicação simples + bons visuais + vontade de compartilhar**.

Antes de promover o vencedor, faça também o teste mental: **“uma pessoa comum no Brasil teria motivo para parar o scroll porque reconhece isso na própria vida, no próprio país ou numa história brasileira que vale descobrir?”** Se sim, isso é um diferencial relevante na seleção.

## História, diversidade e duplicidade

Antes de promover um candidato:

1. leia títulos, roteiros, slugs, filas e retries existentes;
2. compare tema, entidades centrais, evento, recorte, conflito e payoff;
3. descarte o mesmo fato com título reescrito ou paráfrase semântica;
4. penalize sequências concentradas no mesmo subtema, tipo de personagem ou payoff;
5. preserve variedade de época, geografia, escala, formato narrativo e tipo de entidade quando o perfil permitir;
6. execute também o duplicate preflight técnico vigente; ele complementa, mas não substitui, a checagem editorial.

Exemplo de duplicidade: `Por que a Blockbuster recusou comprar a Netflix` e `O dia em que a Blockbuster disse não para a Netflix` representam a mesma história.

Vários episódios podem citar a mesma entidade quando os acontecimentos e payoffs forem realmente diferentes. Não rejeite automaticamente outra história sobre a mesma empresa, pessoa, país, franquia ou artista.

## Pesquisa e factualidade

Para o tema vencedor, descubra:

- o que aconteceu, com quem, quando e onde;
- por que isso importa;
- qual é o conflito, a surpresa e a consequência;
- quais fatos são essenciais e quais são distração;
- qual promessa o hook pode fazer sem exagerar a evidência;
- qual payoff responde à promessa;
- o que pode ser demonstrado visualmente.

Use fontes primárias e secundárias confiáveis quando disponíveis. Rumores, acusações, números, datas, causalidade, controvérsias e fatos recentes exigem confirmação proporcional ao risco. Não converta correlação em causa, hipótese em certeza ou consenso parcial em afirmação absoluta para melhorar o hook.

Conteúdo de fóruns e redes pode sugerir pistas, nunca servir sozinho como confirmação de um fato sensível. Registre em `sources.txt` as fontes factuais realmente usadas.

## Hook, roteiro e retenção

O hook parte do aspecto mais interessante e verificável do tema. Não force todos os episódios ao mesmo molde. Estruturas como decisão cara, oportunidade recusada, erro invisível, produto quase cancelado ou linha de código desastrosa são possibilidades, não templates a repetir.

O roteiro deve ter:

```text
promessa concreta -> contexto mínimo -> progressão -> viradas/micro-payoffs -> consequência -> payoff -> CTA contextual, quando configurado
```

Evite voz de documentário genérico, resumo de Wikipédia e listas soltas de curiosidades. Preserve linguagem natural, clareza de primeira escuta, densidade informativa e ritmo de short.

## Entidades e planejamento visual

Extraia do tema e de cada frase:

- entidades principais e secundárias;
- ações e acontecimentos;
- lugares e período;
- objetos, documentos, produtos ou interfaces;
- evidências e consequências visualizáveis;
- `visual_intent` específico do beat.

As queries visuais devem combinar, conforme aplicável:

```text
topic + current narration + entities + event/action + location + time period + specific visual intent
```

Exemplos:

- pessoa: a pessoa no evento, contexto ou período correto;
- empresa: produto, logo histórico, fundador, sede, documento, anúncio ou acontecimento;
- tecnologia: hardware, software, interface, criadores, demonstração ou falha concreta;
- história: personagens, mapas, locais, registros, objetos e documentos adequados à época;
- economia: instituições, moedas, mercados, edifícios, pessoas, jornais, gráficos ou objetos reais;
- música: artista, banda, capa, estúdio, performance, contrato ou evento musical quando forem realmente o assunto.

Um visual genérico de “pessoa vendo TV” não representa a recusa da Blockbuster à Netflix. Prefira loja Blockbuster, marca/website da época, Reed Hastings, DVDs, documentos ou cobertura contemporânea diretamente ligada à história.

Relevância semântica vence movimento, resolução e estética. Vídeo é preferível quando acrescenta informação ou movimento real; imagem exata vence vídeo vagamente relacionado.

## Integração com a engine existente

Não persista rankings editoriais, scores temporários, queries ou campos inventados em `story.json`, `assets.json`, `timeline.json` ou `post.json`. Traduza a decisão final apenas para o schema real da `main`.

Preserve integralmente:

- pools de candidatos, ranking, vídeo/imagem e fallbacks;
- Best Segment Selection e trims seguros;
- Smart Visual Pacing opt-in;
- enquadramento 9:16, crop, focus e background blur;
- unicidade, normalização de URL, SHA-256, hashes perceptuais e histórico visual;
- TTS, legendas, background music, SFX e mix;
- media preflight, auto repair, retries, queue e publishing completion.

Leia também:

- `templates/editorial-direction-prompt.md`;
- `templates/short-form-style-rule.md`;
- `templates/visual-uniqueness-rule.md`;
- `docs/visual-search.md`;
- `templates/publishing-completion-rule.md`.

## Gate final de seleção

Só avance quando:

- um tema específico estiver definido;
- a prioridade `topic > content_profile` tiver sido respeitada;
- no Profile Mode, o tema vencedor superar alternativas reais e não duplicar o histórico;
- o recorte tiver hook, progressão, consequência e payoff;
- os fatos essenciais forem verificáveis e expressos no nível correto de certeza;
- existirem entidades e intenções visuais concretas;
- o tema couber no tempo e no schema atuais;
- música permanecer uma possibilidade editorial, nunca uma dependência estrutural.

## CAMADA DE OPORTUNIDADE ATUAL PARA SHORTS — DEMANDA + CONCORRÊNCIA

Antes de autorizar uma candidata do Além do Óbvio, faça uma pesquisa atual de oportunidade para descobrir quais assuntos têm atenção crescente e ainda não estão saturados. Esta camada serve para PRIORIZAR o pool; não substitui factualidade, duplicate preflight, relevância brasileira, surpresa real, qualidade visual nem os demais hard gates da main.

### Objetivo
Encontrar temas que combinem:
- interesse/demanda crescendo AGORA;
- concorrência/saturação ainda administrável;
- vídeos recentes mostrando tração/outlier;
- forte proximidade ou curiosidade para público brasileiro;
- história/explicação que sustente retenção em Short.

### Fontes e sinais
Use, quando acessíveis nesta execução:
1. vidIQ público: Rising Keywords, páginas de tendências, crescimento recente, outliers, views/hour e outros sinais públicos;
2. dados do vidIQ autenticado SOMENTE se estiverem realmente acessíveis — nunca invente Search Volume, Competition ou Overall Score;
3. YouTube/Shorts: quantidade e idade de vídeos recentes sobre o MESMO assunto/ângulo, tamanho dos canais concorrentes, velocidade de views e presença de canais pequenos/médios obtendo desempenho acima do normal;
4. Google Trends e pesquisas recentes no Brasil quando ajudarem;
5. notícias, Reddit e outras fontes de descoberta podem indicar pauta, mas o fato final deve ser confirmado por fontes adequadas ao tema.

Se Search Volume ou Competition exatos do vidIQ não estiverem disponíveis, NÃO bloqueie a seleção e NÃO fabrique números. Estime demanda e saturação qualitativamente a partir de evidências públicas.

### Como medir concorrência para Shorts
Priorize SATURAÇÃO RECENTE, não apenas keyword competition:
- quantidade de vídeos/Shorts recentes sobre o mesmo tema e sobretudo o mesmo ângulo;
- número e tamanho dos canais que já cobriram;
- repetição da mesma narrativa;
- idade dos vídeos que ainda estão ganhando velocidade;
- presença de canais pequenos/médios conseguindo outliers;
- existência de um ângulo factual forte ainda pouco explorado.

Tema extremamente popular mas já repetido por muitos criadores deve perder prioridade. Tema em aceleração com poucos vídeos equivalentes e boa resposta recente deve ganhar prioridade.

### Priorização interna sugerida
Use como guia flexível:
- 35% tendência/crescimento recente;
- 25% baixa saturação/concorrência recente;
- 20% desempenho de vídeos recentes/outliers;
- 15% força da história/curiosidade para retenção;
- 5% volume de busca/search intent.

Quando houver dados confiáveis, use-os. Quando não houver, classifique sinais como ALTO/MÉDIO/BAIXO com evidência observável.

### Regra de decisão
Entre candidatas que já passam pelos filtros editoriais do Além do Óbvio, prefira a melhor combinação de:
`MOMENTUM ALTO + SATURAÇÃO BAIXA/MÉDIA + OUTLIERS RECENTES + RELEVÂNCIA PARA BRASILEIROS + HISTÓRIA FORTE`.

A prioridade editorial já definida para Brasil/história brasileira/pets/cotidiano continua valendo. A camada de oportunidade ajuda a decidir ENTRE boas pautas; ela não deve empurrar um assunto global irrelevante para brasileiros só porque está trending.

Temas políticos/eleitorais, quando considerados, continuam sujeitos integralmente às exigências de neutralidade, factualidade e fontes fortes já definidas neste arquivo e no prompt do agendamento.

