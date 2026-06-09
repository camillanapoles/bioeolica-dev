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
