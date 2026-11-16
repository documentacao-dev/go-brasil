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

## Publicação: go.documentacao.dev

O go.dev é montado por um servidor Go, e o Firebase Hosting só serve arquivos. Por isso o deploy gera uma versão estática:

- `go run ./cmd/golangorg -http=localhost:6060 &` e depois `python3 tool/estatico/gerar.py` salvam em `public/` só as páginas com o marcador `ia-translate`, com o CSS, o JS e as imagens que elas usam.
- `firebase.json` (site `go-documentacao` no projeto `transliteradu`): `/` vai para `/doc/`, os prefixos que não traduzimos (`/pkg`, `/blog`, `/dl`…) redirecionam para o go.dev, e o `404.html` leva qualquer página ainda não traduzida para a mesma página no go.dev.
- Página nova traduzida entra no site sozinha no próximo deploy (workflow `deploy-firebase.yml`, a cada push na `master`).
