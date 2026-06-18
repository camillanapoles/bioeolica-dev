USE CICLO DE PRODUCAO PARA CRIAR AGENTES DE FORMA EFICIENTE ACERCA DE UM TEMA ESPECÍFICO. O CICLO DE PRODUÇÃO ENVOLVE AS SEGUINTES ETAPAS:
1. PLANEJAMENTO: DEFINA O TEMA ESPECÍFICO PARA O QUAL VOCÊ DESEJA CRIAR AGENTES. IDENTIFIQUE AS NECESSIDADES E OBJETIVOS DOS AGENTES QUE VOCÊ QUER CRIAR.
2. PESQUISA: REALIZE PESQUISAS PARA OBTER INFORMAÇÕES REALIZE SOBRE O TEMA ESPECÍFICO. COLETE DADOS, ARTIGOS, LIVROS E OUTRAS FONTES DE INFORMAÇÃO RELEVANTES PARA O TEMA.
3. PROJETO: COM BASE NAS INFORMAÇÕES COLETADAS, PROJETAR OS AGENTES. DEFINA AS CARACTERÍSTICAS, HABILIDADES E FUNCIONALIDADES DOS AGENTES. CERTIFIQUE-SE DE QUE OS AGENTES SE ALINHEM COM OS OBJETIVOS DEFINIDOS NA ETAPA DE PLANEJAMENTO.
4. DESENVOLVIMENTO: UTILIZE FERRAMENTAS DE DESENVOLVIMENTO ADEQUADAS PARA CRIAR OS AGENTES. ISSO PODE INCLUIR PROGRAMAS ANALISE COMPUTACIONAL, PLATAFORMAS DE DESENVOLVIMENTO DE AGENTES OU OUTRAS FERRAMENTAS TECNOLÓGICAS. CERTIFIQUE-SE DE QUE OS AGENTES SEJAM FUNCIONAIS E EFICIENTES.
5. TESTE: REALIZE TESTES PARA GARANTIR QUE OS AGENTES FUNCIONEM CORRETAMENTE. IDENTIFIQUE E CORRIJA QUAISQUER PROBLEMAS OU BUGS QUE POSSAM SURGIR DURANTE O TESTE.
6. IMPLEMENTAÇÃO: APÓS TESTAR E CORRIGIR OS AGENTES, IMPLANTE-OS EM UM AMBIENTE ADEQUADO. CERTIFIQUE-SE DE QUE OS AGENTES E OS MODELOS PRODUZIDOD E ANALISE COMPUTACAO ESTEJAM FUNCIONANDO CORRETAMENTE E ATENDENDO AOS OBJETIVOS E CRITERIOS DEFINIDOS NA ETAPA DE PLANEJAMENTO.
7. AVALIAÇÃO: AVALIE O DESEMPENHO DOS AGENTES E SE A METODOLOGIA APLICADA FOI CONFORME REQUISITOS DO ESCOPO. ANALISE OS RESULTADOS OBTIDOS E IDENTIFIQUE ÁREAS DE MELHORIA PARA FUTURAS ITERAÇÕES DO CICLO DE PRODUÇÃO.

LEIA O DOCUMENTO DE REFERÊNCIA PARA OBTER MAIS DETALHES SOBRE CADA ETAPA DO CICLO DE PRODUÇÃO E COMO APLICÁ-LO DE FORMA EFICIENTE NA CRIAÇÃO DE AGENTES PARA UM TEMA ESPECÍFICO.
@./INSTRUCTIONS.md

MANDATORY: # AGENTES
└─ 1. COMECE ANALISANDO O DOC @./INSTRUCTIONS.md PARA ENTENDER O CICLO DE PRODUÇÃO E COMO APLICÁ-LO NA CRIAÇÃO DE AGENTES PARA UM TEMA ESPECÍFICO. SIGA AS ETAPAS DO CICLO DE PRODUÇÃO, INCLUINDO PLANEJAMENTO, PESQUISA, PROJETO, DESENVOLVIMENTO, TESTE, IMPLEMENTAÇÃO E AVALIAÇÃO. CERTIFIQUE-SE DE QUE OS AGENTES CRIADOS SE ALINHEM COM OS OBJETIVOS DEFINIDOS E ATENDAM AOS REQUISITOS DO ESCOPO.
└─ 2. EXTRAIR DO ESCOPO DO DOCUMENTO OBJETIVO, REGRAS, ENTREGAVEIS, CRITÉRIOS DE AVALIAÇÃO E OUTROS ELEMENTOS RELEVANTES PARA O PROJETO DE CRIAÇÃO DE AGENTES. UTILIZE ESSAS INFORMAÇÕES PARA ORIENTAR O PROCESSO DE CRIAÇÃO DOS AGENTES E GARANTIR QUE ELES ESTEJAM ALINHADOS COM AS EXPECTATIVAS DO PROJETO.
└─ 3. DURANTE O PLANEJAMENTO, DEFINA CLARAMENTE O TEMA ESPECÍFICO PARA O QUAL VOCÊ DESEJA CRIAR OS AGENTES. IDENTIFIQUE AS NECESSIDADES E OBJETIVOS DOS AGENTES PARA GARANTIR QUE ELES SE ALINHEM COM O PROPÓSITO DO PROJETO.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **bioeolica-dev** (8177 symbols, 12912 relationships, 184 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

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
