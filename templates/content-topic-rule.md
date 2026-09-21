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

Esse pool é uma etapa de comparação, não licença para promover uma pauta duplicada ou fraca. Descarte individualmente as candidatas que falharem e avance pelas alternativas permitidas pelo fluxo; só encerre sem pauta quando as tentativas válidas estiverem realmente esgotadas.

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

Isso NÃO significa que todo episódio deve ser sobre pets, casa ou Brasil. Temas globais continuam válidos quando forem claramente mais fortes. A regra é: **reconhecimento imediato + surpresa real + explicação simples + bons visuais** tende a vencer curiosidade distante que exija muito contexto para o público se importar.

Antes de promover o vencedor, faça também o teste mental: **“uma pessoa comum no Brasil teria motivo para parar o scroll porque reconhece isso na própria vida ou no próprio país?”** Se sim, isso é um diferencial relevante na seleção.

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
