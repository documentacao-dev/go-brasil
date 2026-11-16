# CLAUDE.md

Tradução PT-BR da documentação de **Go (go.dev)**, fork de `golang/website`, parte da org [`documentacao-dev`](https://github.com/documentacao-dev).

- Conteúdo traduzível: `_content/doc/**/*.{md,html}` (primeiro os tutoriais e guias; `_content/blog/` e as notas de versão `go1.*.md` ficam de fora por enquanto)
- Site: servidor Go do próprio repositório: `go run ./cmd/golangorg` e abrir http://localhost:6060/doc/
- Sync: branch `sync/upstream-AAAA-MM` com merge de `upstream/master`, retradução só do que mudou, atualização de `tool/traducao/ultimo-sync-upstream.txt`.

## Modelo da tradução: sempre Haiku

Toda tradução e retradução de página (tradução nova, sync com o upstream, revisão de trecho) roda no **Haiku** (`model: haiku`, hoje Claude Haiku 5.5), local ou na nuvem (Claude Code na web, GitHub App, rotinas agendadas).

- Os agentes em `.claude/agents/` já declaram `model: haiku`. Não troque.
- Se um orquestrador disparar subagentes para traduzir, passe `model: "haiku"` na ferramenta Agent.
- O modelo principal da sessão fica só com a orquestração: merge do upstream, scripts de conferência, commits e PR. Ele não traduz páginas.

## Convenções do go.dev

- O front matter é um bloco JSON em comentário (`<!--{ "Title": "...", ... }-->`) e tem de continuar sendo a primeira coisa do arquivo. Traduza só o valor de `"Title"` (e `"Summary"`, se houver); o resto das chaves fica igual.
- O marcador `<!-- ia-translate: true -->` vai na linha logo **depois** do bloco de front matter, nunca antes.
- Arquivos `.html` são HTML com template Go: `{{...}}`, `<pre>`, `<code>`, atributos `id`, `href` e `class` ficam idênticos. Traduza só o texto entre as tags.
- Arquivos `.md` são Markdown (goldmark) com o mesmo front matter JSON.
