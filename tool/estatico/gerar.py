#!/usr/bin/env python3
"""Gera a versão estática das páginas traduzidas para o Firebase Hosting.

O go.dev é servido por um programa em Go (cmd/golangorg) que monta as páginas
na hora. O Firebase Hosting só serve arquivos, então este script:

1. pede ao servidor local (já rodando em --servidor) cada página de
   _content/doc/ que tem o marcador `<!-- ia-translate: true -->`, como se
   fosse o host go.dev em https (assim os links saem no formato de produção);
2. baixa o CSS, o JS, as imagens e as fontes que essas páginas usam
   (inclusive os url(...) de dentro do CSS);
3. grava tudo em --saida (padrão: public/).

O que não foi traduzido (pacotes, blog, downloads, páginas de /doc/ ainda em
inglês) não entra: o firebase.json redireciona os prefixos conhecidos para o
go.dev e o 404.html leva qualquer outro caminho para a mesma página no go.dev.

Uso: go run ./cmd/golangorg -http=localhost:6060 &
     python3 tool/estatico/gerar.py --servidor http://localhost:6060
"""
import argparse
import re
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / '_content' / 'doc'
MARCADOR = '<!-- ia-translate: true -->'
ASSET = re.compile(r'(?:href|src)="(/(?:css|js|images|fonts|favicon|static)[^"#?]*)')
CSS_URL = re.compile(r'url\(\s*[\'"]?([^\'")]+)')
HEADERS = {'Host': 'go.dev', 'X-Forwarded-Proto': 'https'}


def baixar(servidor, caminho):
    req = urllib.request.Request(servidor + caminho, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return r.read()


def paginas():
    """URL e arquivo de saída de cada página traduzida."""
    for p in sorted(DOC.rglob('*')):
        if p.suffix not in ('.md', '.html') or MARCADOR not in p.read_text(errors='ignore'):
            continue
        rel = p.relative_to(ROOT / '_content').with_suffix('')
        if rel.name == 'index':
            url = '/' + str(rel.parent) + '/'
            saida = rel.parent / 'index.html'
        else:
            url = '/' + str(rel)
            saida = rel.with_suffix('.html')
        yield url, saida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--servidor', default='http://localhost:6060')
    ap.add_argument('--saida', default=str(ROOT / 'public'))
    a = ap.parse_args()
    out = Path(a.saida)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)

    pendentes = set()
    n = 0
    for url, saida in paginas():
        html = baixar(a.servidor, url).decode()
        html = html.replace('<html lang="en">', '<html lang="pt-BR">')
        (out / saida).parent.mkdir(parents=True, exist_ok=True)
        (out / saida).write_text(html)
        pendentes |= set(ASSET.findall(html))
        n += 1

    feitos = set()
    while pendentes:
        caminho = pendentes.pop()
        if caminho in feitos:
            continue
        feitos.add(caminho)
        try:
            dados = baixar(a.servidor, caminho)
        except Exception as e:  # asset referenciado mas inexistente: só avisa
            print(f'aviso: {caminho}: {e}')
            continue
        destino = out / caminho.lstrip('/')
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(dados)
        if caminho.endswith('.css'):
            for ref in CSS_URL.findall(dados.decode(errors='ignore')):
                if ref.startswith('data:'):
                    continue
                alvo = urlparse(urljoin(caminho, ref)).path
                if alvo.startswith('/'):
                    pendentes.add(alvo)

    for extra in ('404.html', 'robots.txt'):
        shutil.copy(Path(__file__).parent / extra, out / extra)
    print(f'{n} páginas e {len(feitos)} arquivos de apoio em {out}')


if __name__ == '__main__':
    main()
