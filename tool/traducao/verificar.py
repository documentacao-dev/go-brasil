#!/usr/bin/env python3
"""Confere as páginas traduzidas do go.dev contra o inglês do upstream.

Para cada arquivo em _content/doc/ com o marcador `<!-- ia-translate: true -->`:

- o front matter JSON continua sendo a primeira coisa do arquivo e é JSON válido,
  com as mesmas chaves do inglês;
- o marcador vem logo depois do front matter;
- blocos de código (`<pre>` e cercas ```), `href`, `id` e `{{...}}` são idênticos
  ao inglês, na mesma ordem;
- sobrou pouco texto em inglês.

O inglês é lido do commit em tool/traducao/ultimo-sync-upstream.txt.
Uso: python3 tool/traducao/verificar.py [caminhos...]
Sai com código 1 se houver erro.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = (ROOT / 'tool' / 'traducao' / 'ultimo-sync-upstream.txt').read_text().strip()
MARCADOR = '<!-- ia-translate: true -->'
FM = re.compile(r'\A<!--(\{.*?\})-->\s*\n', re.S)
PRE = re.compile(r'<pre\b.*?</pre\s*>', re.S)
CERCA = re.compile(r'^```.*?^```', re.S | re.M)
HREF = re.compile(r'href="([^"]*)"')
ID = re.compile(r'\bid="([^"]*)"')
MDLINK = re.compile(r'\]\(([^)\s]+)')
TEMPLATE = re.compile(r'\{\{.*?\}\}', re.S)
EN = set('the and of to is are you your this that with for in it be can when '
         'will from have which an by on as at or'.split())


def ingles(caminho):
    r = subprocess.run(['git', 'show', f'{BASE}:{caminho}'], cwd=ROOT,
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def partes(texto):
    return {
        'blocos de código': PRE.findall(texto) + CERCA.findall(texto),
        'href': HREF.findall(texto) + MDLINK.findall(texto),
        'id': ID.findall(texto),
        'template {{...}}': TEMPLATE.findall(texto),
    }


def prosa_em_ingles(texto):
    sem_codigo = CERCA.sub('', PRE.sub('', texto))
    sem_codigo = re.sub(r'<code>.*?</code>|`[^`]*`|<[^>]+>', ' ', sem_codigo)
    palavras = re.findall(r'[a-zà-ú]+', sem_codigo.lower())
    if not palavras:
        return 0.0
    return sum(p in EN for p in palavras) / len(palavras)


def conferir(caminho):
    erros = []
    pt = (ROOT / caminho).read_text()
    en = ingles(caminho)
    if en is None:
        return [f'{caminho}: não existe no upstream ({BASE[:9]})']

    m_pt, m_en = FM.match(pt), FM.match(en)
    if m_en and not m_pt:
        erros.append('front matter JSON não está mais no início do arquivo')
    elif m_en and m_pt:
        try:
            k_pt, k_en = json.loads(m_pt.group(1)).keys(), json.loads(m_en.group(1)).keys()
            if set(k_pt) != set(k_en):
                erros.append(f'chaves do front matter mudaram: {sorted(k_en)} → {sorted(k_pt)}')
        except json.JSONDecodeError as e:
            erros.append(f'front matter não é JSON válido: {e}')
        resto = pt[m_pt.end():].lstrip('\n')
        if not resto.startswith(MARCADOR):
            erros.append('marcador ia-translate não está logo depois do front matter')

    a, b = partes(en), partes(pt)
    for nome in a:
        if a[nome] != b[nome]:
            erros.append(f'{nome}: {len(a[nome])} no inglês, {len(b[nome])} na tradução'
                         + ('' if len(a[nome]) != len(b[nome]) else ' (conteúdo diferente)'))

    taxa = prosa_em_ingles(pt)
    if taxa > 0.08:
        erros.append(f'prosa ainda parece inglês ({taxa:.0%} de palavras comuns em inglês)')
    return [f'{caminho}: {e}' for e in erros]


def main():
    if len(sys.argv) > 1:
        arquivos = sys.argv[1:]
    else:
        arquivos = sorted(str(p.relative_to(ROOT)) for p in (ROOT / '_content' / 'doc').rglob('*')
                          if p.suffix in ('.md', '.html') and MARCADOR in p.read_text(errors='ignore'))
    erros = [e for a in arquivos for e in conferir(a)]
    for e in erros:
        print('ERRO', e)
    print(f'{len(arquivos)} arquivo(s) traduzido(s), {len(erros)} erro(s)')
    sys.exit(1 if erros else 0)


if __name__ == '__main__':
    main()
