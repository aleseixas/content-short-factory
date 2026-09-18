# Content Short Factory

Fábrica automatizada de conteúdo short-form com IA, capaz de produzir vídeos verticais sobre praticamente qualquer tema ou nicho para TikTok, Instagram Reels e YouTube Shorts. Um agente editorial externo escolhe ou recebe o tópico, pesquisa, escreve e planeja; Python/FFmpeg executam de forma determinística as decisões registradas no episódio.

> A `main` é a fonte de verdade para schemas, enums, renderer, catálogos, validações e publishers.

## Arquitetura

```text
INPUT EDITORIAL
  ├─ topic presente ───────────────> Topic Mode
  └─ somente content_profile ──────> Profile Mode / seleção de pauta
                                      │
                                      v
histórico + diversidade + factualidade
  -> pesquisa/contexto
  -> roteiro short-form
  -> entidades + planejamento visual
  -> candidate pools + busca/inspeção
  -> assets + trims
  -> TTS + timings reais
  -> pacing + captions + background music/SFX
  -> render determinístico
  -> validação/media preflight
  -> metadados + queue
  -> publicação/retry + relatório terminal
```

O agente externo é o diretor/editor criativo. O runtime não usa um LLM para improvisar decisões durante o render: recebe `story.json`, `assets.json`, `timeline.json` e configuração, valida tudo e produz a mesma edição declarada.

## Modos de entrada

### Topic Mode

Use quando o assunto específico já é conhecido:

```json
{
  "topic": "Por que a Blockbuster recusou comprar a Netflix"
}
```

O agente preserva o tema, pesquisa fatos, extrai entidades e cria o episódio diretamente.

### Profile Mode

Use quando só existe um universo editorial:

```json
{
  "content_profile": "economia"
}
```

O agente monta um pool de pautas, consulta o histórico, evita duplicatas semânticas, busca diversidade dentro do profile e escolhe um tópico com potencial real de short.

`content_profile` aceita linguagem natural; não é enum:

```json
{
  "content_profile": "empresas que cometeram grandes erros",
  "additional_instructions": "Priorizar decisões surpreendentes com consequências mensuráveis.",
  "language": "pt-BR"
}
```

Outros profiles válidos incluem `tecnologia e histórias de empresas`, `grandes acontecimentos históricos`, `curiosidades científicas visualmente impressionantes` e `música e bastidores da indústria musical`. Trocar esse texto livre prepara a mesma arquitetura para futuros canais sem exigir regras de código por nicho.

Os campos opcionais podem incluir `category`, `angle`, `target_duration`, `language` e `additional_instructions`. Nenhum deles é requisito.

Quando `topic` e `content_profile` aparecem juntos, `topic` tem prioridade:

```json
{
  "topic": "Como a BlackBerry perdeu o mercado de smartphones",
  "content_profile": "empresas e tecnologia",
  "angle": "decisões estratégicas que levaram à queda"
}
```

Pelo menos um entre `topic` e `content_profile` deve existir. Esse objeto é o contrato público de entrada editorial. Depois que o tópico é resolvido, os campos aceitos são preservados em `story.json` para rastreabilidade; rankings, pools e raciocínio temporário não são persistidos.

A regra completa está em [`templates/content-topic-rule.md`](templates/content-topic-rule.md). O caminho antigo [`templates/music-universe-topic-rule.md`](templates/music-universe-topic-rule.md) é apenas uma ponte de compatibilidade. Música continua sendo um `content_profile` válido.

## Seleção e pesquisa editorial

No Profile Mode, o agente compara pautas por hook, conflito, transformação, consequência, payoff, clareza, potencial visual, documentação e distância do histórico recente. A diversidade é inferida do profile; não existe lista hardcoded de categorias por nicho.

Depois que o tópico é definido, o pipeline é topic-driven. Pessoas, empresas, produtos, marcas, países, cidades, eventos, tecnologias, lugares, obras, atletas, artistas, bandas e músicas são entidades do tema, não campos estruturais obrigatórios.

Factualidade prevalece sobre impacto. Rumor, acusação, estatística, valor, data, controvérsia e causalidade exigem fontes e linguagem compatíveis com o nível de certeza. `sources.txt` registra as fontes factuais e de mídia realmente usadas.

## Editor Mode

Para cada shot, o agente avalia:

```text
ASSET | TRECHO/TRIM | MOTION | TRANSITION | VISUAL FX | TEXT FX | HIGHLIGHT | OVERLAY | SFX
```

Essa matriz é checklist mental, não campo do schema. A autoria passa por montagem shot a shot, acabamento e polimento global. Uma camada só entra quando melhora retenção, clareza, ritmo, surpresa ou payoff.

Veja [`docs/editorial-direction.md`](docs/editorial-direction.md) e [`templates/editorial-direction-prompt.md`](templates/editorial-direction-prompt.md).

## Visual Search

O fluxo de autoria é:

```text
frase + entidades + evento + local + período + visual_intent
  -> múltiplas queries
  -> candidate pools
  -> comparação semântica
  -> inspeção técnica
  -> ranking
  -> asset/trim escolhido
```

Wikimedia Commons, Openverse Images e descoberta web/YouTube são usados conforme o suporte atual. Vídeo tem preferência quando movimento real acrescenta valor; imagem diretamente ligada à frase vence vídeo genérico.

Para slots ricos, até oito candidatos úteis e de fontes distintas é uma boa direção. `semantic_fit` (`exact`, `direct`, `contextual`, `generic`), `visual_intent`, queries, scores e diagnósticos pertencem ao pool/relatório de autoria e não aos JSONs finais.

Exemplo de busca:

```bash
python search_visual.py "Blockbuster Netflix Reed Hastings interview" "Blockbuster store archive" --kind video --external --limit 20 --inspect-top 5
```

Leia [`docs/visual-search.md`](docs/visual-search.md) e veja [`templates/visual-candidates.example.json`](templates/visual-candidates.example.json).

### Unicidade visual

- uma imagem nunca pode aparecer em dois shots;
- uma fonte de vídeo pode abastecer normalmente até três shots;
- cada uso deve ter trim temporal distinto, seguro e não sobreposto;
- crop, speed, motion ou FX não transformam o mesmo trecho em take novo;
- URL normalizada, provider ID, SHA-256, hashes perceptuais e histórico ajudam a detectar aliases/repetição.

Best Segment respeita as reservas de outros shots da mesma fonte. Veja [`docs/visual-uniqueness.md`](docs/visual-uniqueness.md).

### Best Segment Selection

`source_start_seconds`/`source_end_seconds` definidos pelo agente são baseline e fallback. Depois dos timings reais, o engine pode comparar janelas próximas e substituir o trim apenas quando encontra ganho material, confiança e segurança.

Ele considera duração do shot, speed, freeze e crossfade; não muda asset, áudio ou duração final, não usa loop e não cria sobreposição entre trims da mesma fonte. Falha, empate ou ganho pequeno preservam o baseline. O diagnóstico temporário fica em `work/<slug>/best_segment_selection.json`.

### Smart Visual Pacing

É opt-in. Quando habilitado, pode redistribuir conservadoramente fronteiras dos shots depois do TTS, sem trocar/reordenar assets, alterar áudio ou mudar a duração total. Não corrige asset ruim, repetição ou trim inválido. Ausente, `null` ou desabilitado preserva o pacing legado.

## Áudio

Background music e SFX têm políticas distintas.

### Background music — external-first

Durante a autoria com web disponível, pesquise e compare trilhas adequadas ao tema. Valide origem, autoria, licença, duração, formato e URL/host compatível. Um profile externo aprovado pode ser registrado em `assets/audio/music/catalog.json` quando o contrato atual permitir. Profiles locais são fallback.

`timeline.json` aponta apenas para o nome do profile. Serviços comerciais podem informar estética/tendência, mas previews não são automaticamente arquivos autorizados para o renderer.

### SFX — catálogo curado

SFX vêm apenas de `assets/audio/sfx/catalog.json` durante a criação do episódio. Use `type` existente; não pesquise nem invente efeitos por episódio. Trims de SFX precisam caber na duração real.

Voz permanece dominante; background e SFX reforçam beats sem prejudicar inteligibilidade. Leia [`docs/audio-search.md`](docs/audio-search.md).

## Requisitos e instalação

- Python 3.10+;
- FFmpeg e ffprobe;
- internet quando TTS, busca ou mídia remota forem necessários;
- credenciais somente para providers/publicações utilizados.

```bash
python -m pip install -r requirements.txt
```

## CLI

Crie o esqueleto de um episódio pelo tópico; o slug é derivado automaticamente:

```bash
python new_episode.py --topic "Por que a Blockbuster recusou comprar a Netflix"
```

Passe contexto opcional quando útil:

```bash
python new_episode.py --topic "Como a BlackBerry perdeu o mercado de smartphones" --content-profile "empresas e tecnologia" --angle "decisões estratégicas que levaram à queda" --language pt-BR
```

O mesmo contrato pode vir de um arquivo JSON:

```bash
python new_episode.py --request request.json
```

```json
{
  "topic": "O erro de software da Knight Capital",
  "content_profile": "tecnologia e histórias de empresas",
  "target_duration": 75,
  "language": "pt-BR"
}
```

`new_episode.py` também aceita `--category`, `--target-duration`, `--additional-instructions`, `--entity`, `--event`, `--location`, `--time-period` e `--visual-keyword`. O slug posicional continua disponível como override quando o request informa `topic` ou `content_profile`. A dupla legada completa `--artist` + `--song` também continua aceita e é convertida em tópico.

Profile Mode puro usa um `TopicSelector` externo injetado na API de `main()`; por isso, a CLI standalone não inventa um tópico sem esse agente. O seletor recebe o request livre — inclusive `additional_instructions` — e o histórico de tópicos. O tópico retornado é validado, passa pela checagem de duplicidade e só então cria o episódio. Automações podem chamar `new_episode.main(..., topic_selector=seletor)` com `--content-profile` ou `--request`.

`--song` e `--artist` permanecem apenas para duplicate preflight legado. Não são requisitos editoriais.

Gere o vídeo:

```bash
python generate.py <slug>
```

Prepare/valide capa e metadados:

```bash
python prepare_post.py <slug>
```

Pesquise visualmente:

```bash
python search_visual.py "query principal" "query alternativa" --kind any --external
```

Valide publicação sem enviar:

```bash
python publish.py <slug> --platform all --dry-run
```

Publicação real exige autorização explícita e credenciais válidas:

```bash
python publish.py <slug> --platform all --live
```

Use `--help` em cada comando para os argumentos aceitos pela versão atual.

## Estrutura de um episódio

```text
episodes/<slug>/
├── story.json
├── timeline.json
├── assets.json
├── sources.txt
├── post.json
└── assets/
```

### `story.json`

Roteiro declarativo. Contém `schema_version`, `title`, `slug`, `target_duration_seconds`, `topic` resolvido, contexto editorial opcional e segmentos ordenados com `id`, `text` e delivery opcional suportado.

```json
{
  "schema_version": 1,
  "title": "A decisão da Blockbuster",
  "slug": "blockbuster_netflix",
  "target_duration_seconds": 75,
  "topic": "Por que a Blockbuster recusou comprar a Netflix",
  "content_profile": "empresas e tecnologia",
  "angle": "a decisão e suas consequências",
  "language": "pt-BR",
  "entities": ["Blockbuster", "Netflix", "Reed Hastings"],
  "events": ["proposta de parceria"],
  "locations": ["Estados Unidos"],
  "time_period": "2000",
  "visual_keywords": ["Blockbuster store", "early Netflix website", "DVD rental"],
  "segments": [
    {
      "id": "hook",
      "text": "A Blockbuster teve a chance de negociar com sua futura rival.",
      "delivery": "hook"
    }
  ]
}
```

Campos editoriais opcionais também incluem `category` e `additional_instructions`. Listas de entidades/eventos/locais/keywords contêm strings não vazias. IDs de segmento são únicos e o slug corresponde à pasta.

### `assets.json`

Registra somente mídia final, não candidate pools:

```json
{
  "schema_version": 1,
  "assets": [
    {
      "id": "blockbuster_store",
      "file": "blockbuster_store.jpg",
      "url": "https://host.exemplo/blockbuster-store.jpg",
      "credit": "Autor",
      "license": "Licença",
      "focus": {"x": 0.5, "y": 0.5}
    }
  ]
}
```

### `timeline.json`

Relaciona segmentos a shots e registra apenas capacidades suportadas:

```json
{
  "schema_version": 1,
  "smart_visual_pacing": {"enabled": true},
  "background_music": {"profile": "profile_existente", "volume": 0.1},
  "sfx_cues": [],
  "visual_fx_cues": [],
  "text_fx_cues": [],
  "overlay_cues": [],
  "shots": [
    {
      "id": "shot_hook",
      "segment": "hook",
      "asset": "blockbuster_store",
      "motion": "push_in",
      "transition_out": "cut"
    }
  ]
}
```

Vídeos podem usar `source_start_seconds`, `source_end_seconds`, `speed` e `freeze_frame` conforme os limites reais. Motions, transitions e efeitos são enums validados; não invente valores.

### `sources.txt`

Lista fontes factuais, páginas de origem, créditos/licenças e background externa quando aplicável.

### `post.json`

Contém `cover` e blocos por plataforma (`youtube`, `instagram`, `facebook`, `tiktok`) conforme o schema atual. Títulos, captions, descriptions, categoria e hashtags são topic-driven. Hashtags ficam nos arrays em minúsculas, sem `#` quando o publisher assim espera e sem repetição na caption. Arquivos antigos sem `facebook` continuam compatíveis: o publisher deriva título/caption de YouTube e Instagram.

## Render, preflight e publicação

O pipeline resolve TTS, assets remotos, trims, background music e SFX; monta timeline; gera captions; renderiza com FFmpeg; aplica mix/loudness; registra diagnósticos e valida a saída.

Antes da queue, `Episode media preflight` carrega os JSONs com parsers reais, baixa e valida mídia, resolve os visuais finais, renderiza o vídeo, prepara a capa e executa o dry-run de todas as plataformas. HTTP 403/404/429/5xx, payload inválido, imagem ilegível, vídeo inválido, trim insuficiente ou profile sem faixa resolvível impedem a queue até correção.

Depois desses gates, o preflight cria o artefato `publish-ready-<slug>` e grava em `.publish-queue/<slug>.txt` o slug e o `run_id` que produziu o bundle. `Publish episode` verifica a procedência, baixa e publica exatamente esses bytes; ele não resolve visuais nem renderiza novamente. Se asset, timeline ou background mudar, execute um novo preflight para gerar outro bundle validado.

Uma queue ou upload iniciado não é publicação concluída. A automação acompanha jobs/logs/artefatos, aplica retry somente quando seguro e emite estados verificáveis por plataforma conforme [`templates/publishing-completion-rule.md`](templates/publishing-completion-rule.md) e [`docs/publishing-retry.md`](docs/publishing-retry.md).

## Estrutura principal

```text
assets/                 catálogos e mídia global
config/                 configuração e estilo
docs/                   contratos e operação
engine/                 parsers, TTS, timeline, renderer e busca
episodes/               episódios declarativos
publishing/             metadata e publishers
templates/              regras do agente editorial externo
cache/, work/, output/  dados regeneráveis
```

## Credenciais

Copie `.env.example` para `.env` se esse arquivo existir na versão atual e configure somente integrações utilizadas. `.env` não deve entrar no Git. Sem autorização válida, publicação live deve falhar claramente ou terminar como não verificada/bloqueada — nunca como sucesso simulado.

## Validação e testes

```bash
python -m unittest discover -s tests -v
```

O pipeline valida schema, slug, segmentos/shots, assets, mídia remota, enums, trims, timings, áudio e compatibilidade com FFmpeg/ffprobe. Warnings editoriais pedem revisão, mas não viram hard errors sem suporte no código.

## Limitações atuais

- A seleção automática do Profile Mode acontece no agente editorial externo; o renderer não escolhe pauta.
- A CLI standalone exige `topic` já resolvido; Profile Mode puro depende de um `TopicSelector` injetado pela automação.
- Disponibilidade, direitos e qualidade de mídia dependem das fontes e providers acessíveis.
- Best Segment e Smart Pacing são melhorias conservadoras, não substitutos para boa autoria.
- Publicação depende de credenciais, permissões, quotas, revisão de app e APIs das plataformas.
- A engine aceita somente campos/enums implementados na `main`; documentação e prompts não criam capacidade runtime.
- Música permanece suportada como tema e como camada técnica de background, sem ser requisito estrutural.

## Documentação

- [`templates/content-topic-rule.md`](templates/content-topic-rule.md): seleção Topic/Profile.
- [`templates/editorial-direction-prompt.md`](templates/editorial-direction-prompt.md): prompt operacional completo.
- [`templates/short-form-style-rule.md`](templates/short-form-style-rule.md): retenção, pacing e preflights.
- [`docs/editorial-direction.md`](docs/editorial-direction.md): contrato de direção.
- [`docs/narration-delivery.md`](docs/narration-delivery.md): roteiro e delivery.
- [`docs/visual-search.md`](docs/visual-search.md): descoberta, ranking e inspeção.
- [`docs/visual-uniqueness.md`](docs/visual-uniqueness.md): imagens únicas e até três trims por vídeo.
- [`docs/audio-search.md`](docs/audio-search.md): background music e SFX.
- [`docs/publishing-retry.md`](docs/publishing-retry.md): retries seguros.

Quando qualquer texto divergir do código atual, a `main` continua sendo a fonte de verdade.
