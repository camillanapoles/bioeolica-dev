#!/usr/bin/env python3
"""Generate paper markdown from CRSLR template for KDI/Omnibus v3.0."""
import os
import sys
import json
import datetime

def main():
    project = os.environ.get('PROJECT', 'unknown')
    title = os.environ.get('TITLE', 'Untitled')
    authors = os.environ.get('AUTHORS', 'Agente Multidisciplinar')
    paper_dir = os.environ.get('PAPER_DIR', '/tmp/paper')
    now = datetime.datetime.now().strftime('%Y-%m-%d')

    os.makedirs(os.path.join(paper_dir, 'figures'), exist_ok=True)
    os.makedirs(os.path.join(paper_dir, 'data'), exist_ok=True)

    lines = [
        '---',
        f'title: "{title}"',
        f'author: "{authors}"',
        f'date: {now}',
        f'project: "{project}"',
        '---',
        '',
        f'# {title}',
        '',
        f'**Autores:** {authors}',
        f'**Projeto:** {project}',
        f'**Data:** {now}',
        '',
        '## Resumo',
        '',
        '<!-- Gerado a partir do contexto do projeto e resultados VVV -->',
        '',
        f'Este artigo apresenta a analise computacional do sistema {project}',
        'utilizando a metodologia KDI/Omnibus v3.0 com aplicacao dos 10 dominios',
        'de engenharia e validacao VVV.',
        '',
        '_Resumo a ser preenchido com base nos resultados do projeto._',
        '',
        '## 1. Introducao',
        '',
        '### 1.1 Contexto',
        '<!-- F1 do workflow -- contextualizacao do problema de engenharia -->',
        '',
        '### 1.2 Estado da Arte',
        '<!-- Revisao baseada no RAG Knowledge (M6) -- fontes coletadas durante a analise -->',
        '',
        '## 2. Metodologia',
        '',
        '### 2.1 Dominios e Escalas',
        '<!-- F2-F3 -- dominios relevantes com M3 (macro, meso, micro) -->',
        '',
        '### 2.2 Ferramentas Computacionais',
        '<!-- F4 -- ferramentas open source selecionadas com versoes e parametros -->',
        '',
        '### 2.3 Validacao VVV',
        '<!-- F5 -- verificacao, validacao e certificacao com metricas de erro -->',
        '',
        '## 3. Resultados',
        '',
        '### 3.1 Analise Macro',
        '<!-- Resultados na escala macro -- sistema completo -->',
        '',
        '### 3.2 Analise Meso',
        '<!-- Resultados na escala meso -- interfaces e subsistemas -->',
        '',
        '### 3.3 Analise Micro',
        '<!-- Resultados na escala micro -- componentes e materiais -->',
        '',
        '## 4. Discussao',
        '',
        '### 4.1 Interpretacao dos Resultados',
        '### 4.2 Limitacoes',
        '<!-- Limitacoes documentadas no F8 -- suposicoes, simplificacoes, gaps -->',
        '### 4.3 Comparacao com Literatura',
        '',
        '## 5. Conclusao',
        '',
        '### 5.1 Contribuicoes',
        '### 5.2 Trabalhos Futuros',
        '',
        '## Agradecimentos',
        '',
        '## Referencias',
        '',
        '<!-- Geradas a partir do RAG Knowledge -- todas as fontes utilizadas no ciclo F1-F9 -->',
    ]

    outpath = os.path.join(paper_dir, 'paper.md')
    with open(outpath, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'Paper generated: {outpath}')


def gen_record():
    """Generate publication.json record."""
    paper_dir = os.environ.get('PAPER_DIR', '/tmp/paper')
    safe_title = os.environ.get('SAFE_TITLE', 'paper')
    title = os.environ.get('TITLE', 'Untitled')
    authors = os.environ.get('AUTHORS', 'Unknown')
    project = os.environ.get('PROJECT', 'unknown')
    now = datetime.datetime.now().isoformat()

    record = {
        "id": f"PUB-{datetime.date.today().strftime('%Y%m%d')}-{safe_title[:16]}",
        "title": title,
        "authors": authors,
        "project": project,
        "date": now,
        "status": "draft",
        "files": {
            "markdown": "paper.md",
            "pdf": f"{safe_title}.pdf"
        },
        "vvv_certification": "PENDING"
    }

    outpath = os.path.join(paper_dir, 'publication.json')
    with open(outpath, 'w') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print(f'Publication record: {outpath}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'paper' or cmd == 'all':
        main()
    if cmd == 'record' or cmd == 'all':
        gen_record()
