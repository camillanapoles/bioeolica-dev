# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão Geral — O PRODUTO É META

Este repositório **não** é um "modelo para especificação de agentes" — ele é a **META** (metaclasse/metafunção) que define **um time de agentes orquestrados**, capazes de **auto-criar-se** com base na própria metodologia que norteia o "HOW TO".

O ciclo é auto-referente:
1. A metodologia (Ciclo de Produção + KDI) define **como** criar agentes
2. Os agentes criados aplicam a mesma metodologia para se **auto-modificar e evoluir**
3. O produto final não é um agente estático — é o **próprio loop de autogeração**

Ou seja: o Metodo é o Produto. O conteúdo (domínio de engenharia, escrita acadêmica) é variável; o **metodo de criar agentes que se auto-criam** é o invariante.

## Estrutura do Repositório

```
/
├── AGENTS.md                  # Meta-instrução: Ciclo de Produção para auto-criação de agentes
├── INSTRUCTIONS.md            # ~2268 linhas — Especificação KDI do time de agentes orquestrados
│                              # Inclui: identidade, capacidades, metodologia KDI v2.0,
│                              # mapeamento holístico de domínios, métricas, checklists
├── .repos.txt                 # Inventário de repositórios GitHub do usuário
├── .claude/skill/             # Diretório para skills instaladas (vazio)
├── Research-Paper-Writing-Skills/
│   └── research-paper-writing/  # Skill de escrita acadêmica (exemplo de skill reutilizável)
│       ├── SKILL.md           # Core workflow e regras de uso
│       ├── references/        # Guias por seção (abstract, introduction, method, etc.)
│       └── agents/openai.yaml # Metadados do agente
└── MathematicalEngineeringDeepLearning.git/
    └── (bare git repo — camillanapoles/MathematicalEngineeringDeepLearning)
```

## Meta-Workflow: O Ciclo de Auto-Produção

Definido em `AGENTS.md` e detalhado em `INSTRUCTIONS.md`. Não é um "workflow de desenvolvimento" — é o **algoritmo de autogeração** que os próprios agentes usam para se criar e evoluir:

1. **PLANEJAMENTO** — Definir tema, necessidades e objetivos dos agentes
2. **PESQUISA** — Coletar artigos, livros, ferramentas e fontes relevantes
3. **PROJETO** — Projetar agentes usando formato KDI (Knowledge Definition Interface)
4. **DESENVOLVIMENTO** — Implementar agentes e habilidades
5. **TESTE** — Verificar funcionamento e corrigir problemas
6. **IMPLEMENTAÇÃO** — Implantar em ambiente adequado
7. **AVALIAÇÃO** — Avaliar desempenho e identificar melhorias (realimenta o ciclo)

## Formato KDI (Knowledge Definition Interface)

O "DNA" dos agentes — blueprint auto-referente no formato Omnibus Engine v3.0+:

- `identity` — Papel, domínios, nível de expertise SOTA
- `core_capabilities` — Habilidades computacionais por domínio (FEM, CFD, materiais, energia...)
- `socratic_behavior` — Regras de interação (ensinar a pescar, nunca limitar quantidade)
- `context_engine` — Mapeamento de contexto 5W1H+, auto-instrução por perguntas socráticas
- `output_standards` — Formato, unidades (SI), precisão, validação
- `knowledge_update` — Prioridade de fontes (peer-reviewed 2024-2026, normas, open source)

O KDI é tanto **especificação** quanto **código genético** — um agente lê seu próprio KDI, identifica gaps, e aplica o Ciclo de Produção para se auto-melhorar.

## Habilidade: Research-Paper-Writing

Skill reutilizável em `Research-Paper-Writing-Skills/research-paper-writing/`. Instalar com:

```bash
cp -R Research-Paper-Writing-Skills/research-paper-writing .claude/skills/
```

Guias para Abstract, Introduction, Related Work, Method, Experiments, Conclusion — com exemplos e templates. Exemplo de como skills complementam o time de agentes orquestrados.

## Regras do Meta-Sistema

- **Português primeiro** — Toda comunicação, documentação e respostas em português
- **Método socrático** — Ensinar a pescar, nunca dar o peixe. Explicar o "porquê" antes do "como"
- **Exaustão holística** — Nunca limitar quantidade de itens. Cobertura de 75-90% conforme relevância
- **VVV** — Validação, Verificação e Validação em toda ação (tríplice barreira)
- **5W1H logs** — Rastreabilidade total: What, Why, Who, When, Where, How
- **Single Source of Truth** — Dados versionados (Git LFS + DVC), sem duplicação
- **RAG Knowledge** — Fontes reais verificadas (livros, artigos peer-reviewed, normas vigentes)
- **Normas técnicas** — ISO, ASTM, ASME, ABNT, DIN sempre que aplicável
- **"Build over ask"** — Ações reversíveis executar diretamente; perguntar só para irreversíveis/alto impacto

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/001-physics-m3-workspace/plan.md
<!-- SPECKIT END -->

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **bioeolica-dev** (4684 symbols, 7926 relationships, 167 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/bioeolica-dev/context` | Codebase overview, check index freshness |
| `gitnexus://repo/bioeolica-dev/clusters` | All functional areas |
| `gitnexus://repo/bioeolica-dev/processes` | All execution flows |
| `gitnexus://repo/bioeolica-dev/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
