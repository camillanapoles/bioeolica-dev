# Spec 008 — Evolution Priorities (FDC-U Ranked)

> Source: `/fdc-u` invocation 2026-06-17 + GitNexus audit (7,386 symbols, 11,775 relationships, 178 execution flows)
> Method: FDC-U scoring (Σw_i = 1.00), 5 attributes, 5 phases sequential guarantee
> Principle: Aplicável a tudo sob contexto (agnostic per INSTRUCTIONS.md)

## 1. Objetivo

Garantir evolução contínua, sequencial e garantista do projeto **bioeolica-dev2** —
aplicativo profissional de projeto/desenvolvimento de materiais e equipamentos com:
dimensionamento, cálculos macro/meso/micro, CAD com report, múltiplas visualizações
na peça em análise, gráficos e interação com a peça.

## 2. Atributos FDC-U (Critérios)

| A_i | Critério | Função | Peso | Racional |
|-----|----------|--------|------|----------|
| A1 | Impacto no objetivo final | + | 0.25 | Direto ao objetivo do produto |
| A2 | Ganho de mantabilidade | + | 0.20 | Critério explícito do usuário |
| A3 | Esforço de implementação (invertido) | - | 0.20 | Quick wins primeiro |
| A4 | Risco bloqueante | + | 0.20 | Sequenciamento garantista |
| A5 | Visibilidade para usuário final | + | 0.15 | Valor percebido |

Σ pesos = **1.00** ✓ (CR < 0.10 por pairwise dominância)

## 3. Candidatos Avaliados (10 gaps da auditoria)

| ID | Gap | A1 | A2 | A3⁻ | A4 | A5 | Score | Rank |
|----|-----|----|----|-----|----|----|-------|------|
| C8 | CAD + relatório integrado (CRSLR end-to-end) | 10 | 8 | 6 | 9 | 10 | **0.820** | 🥇 |
| C10 | Dimensionamento multi-domínio (10 domínios) | 9 | 7 | 4 | 8 | 8 | **0.765** | 🥈 |
| C2 | M9 CRSLR report generator (lib) | 8 | 9 | 7 | 9 | 9 | **0.755** | 🥉 |
| C1 | Domínio termo + Cantera/CoolProp | 9 | 8 | 4 | 8 | 5 | 0.740 | 4 |
| C9 | Vis 3D avançada (interação peça + corte + animação) | 9 | 6 | 5 | 6 | 10 | 0.715 | 5 |
| C5 | preCICE coupling adapter (CFD↔FEM) | 7 | 6 | 3 | 5 | 6 | 0.625 | 6 |
| C3 | Retificar specs 002 (topopt) e 006 (validação) | 6 | 10 | 8 | 7 | 3 | 0.575 | 7 |
| C4 | M8 FMEA + S1/S2/S3 centralizado | 5 | 7 | 6 | 6 | 4 | 0.525 | 8 |
| C6 | Vector DB p/ knowledge (M6 RAG real) | 6 | 5 | 5 | 4 | 3 | 0.475 | 9 |
| C7 | Unificação DBs + pyproject deps (R3/R4/R9) | 4 | 10 | 9 | 6 | 2 | 0.470 | 10 |

Ties: nenhum dentro de ±0.05. Discriminação boa.

## 4. Plano de Execução Sequencial Contínuo

**Princípio garantista:** cada fase só inicia após a anterior ter testes PASS + commit.
Fases não-bloqueantes entre si são marcadas como paralelizáveis.

### Fase 0 — Fundação Mantável (BLOCKER — faz primeiro)

Score FDC-U baixo (0.47) mas é pré-requisito de tudo. Débito técnico que corrompe M4.

| Ordem | Item | Ação | Entrega |
|-------|------|------|---------|
| 0.1 | C7 Unificação DBs | Consolidar `bioeolica.db` (0B) + `database.db` → `data/bioeolica.db`; deps em `pyproject.toml` | 1 PR, migrations testadas |
| 0.2 | C3 Retificar specs 002/006 | Reescrever `002-topopt-avancada/spec.md` (escopo OpenMDAO/Dakota); preencher `006-validacao-experimental/` mapeando `tests/validation/` | 2 specs, F1-F9 auditável |

### Fase 1 — Core Product Value (sequencial, alto score)

Aqui mora o "aplicativo profissional" — o que o usuário vê e usa.

| Ordem | Item | Ação | Entrega |
|-------|------|------|---------|
| 1.1 | C2 CRSLR generator | `src/common/report/crslr.py` (template Jinja2: Contexto→Resultados→Síntese→Limitações→Recomendações) + 6 testes | lib + testes |
| 1.2 | C8 CAD + relatório integrado | Conectar `ai_assist_cad/analysis_orchestrator.py` → `crslr.py` → saída PDF/HTML com gráficos + 3D snapshot | pipeline end-to-end |
| 1.3 | C10 Dimensionamento multi-domínio | Ampliar `knowledge_engine.py` de 2 fórmulas (shaft, stator) para 10 domínios (miecz, fluidos, termo, energia, etc.) | API + 10 testes |

### Fase 2 — Universalidade (paralelizável)

Cobertura dos 10 domínios do KDI — atender P1 "Aplicável a tudo".

| Ordem | Item | Ação | Entrega |
|-------|------|------|---------|
| 2.1 | C1 termo | Adicionar subdomínios termo (condução, convecção, radiação, mudança de fase); integrar Cantera/CoolProp | módulo + testes |
| 2.2 | C5 preCICE | Adapter preCICE para FSI (OpenFOAM↔CalculiX); 1 benchmark | adapter + benchmark |
| 2.3 | C4 FMEA | `src/common/safety/fmea.py` com S1/S2/S3 + RPN = S×O×D; centralizar lógica dispersa | lib + 5 testes |

### Fase 3 — Visualização e Conhecimento (paralelizável)

| Ordem | Item | Ação | Entrega |
|-------|------|------|---------|
| 3.1 | C9 Vis 3D avançada | Estender `viewer_templates.html` (Three.js): clipping plane, section view, animation timeline, part interaction | viewer + 4 testes |
| 3.2 | C6 Vector DB | Substituir RAG baseado em PDFs por vector DB (ChromaDB/FAISS); embeddings por sentence-transformers | pipeline + 3 testes |

## 5. Critérios de Aceitação por Fase

- **Fase 0:** migrations aplicadas sem perda de dados; specs 002/006 com F1-F9 completos
- **Fase 1:** pipeline CAD→CRSLR→PDF executável E2E; ≥10 fórmulas de dimensionamento
- **Fase 2:** cobertura ≥9 domínios com relevance_check; preCICE adapter validado em benchmark
- **Fase 3:** interação 3D funcional no browser; busca semântica retorna top-5 relevante

## 6. Mantabilidade (critério explícito usuário)

| Métrica | Target |
|---------|--------|
| Cobertura de testes | ≥80% por módulo novo |
| Duplicação de DBs | 0 (single source of truth após Fase 0) |
| Débitito técnico documentado | 0 specs quebradas após Fase 0 |
| PQMS por entrega | ≥9.0/10 |

## 7. Rastreabilidade

## 8. Clarificações

### Session 2026-06-17

**DB Canonical (C7):** Por auditoria factual GitNexus + ls. `data/bioeolica.db` (3.5MB, 16 tabelas, ~9.8k linhas, dados reais) é a DB canônica. `database.db` e `./bioeolica.db` são vazias (schemas sem dados, abandonadas). Decisão: unificar em `data/bioeolica.db`, remover as vazias após migração validada. Afeta Fase 0.1, atualiza plan.md.

**pyproject.toml (C7):** `[project]` block existe mas `dependencies = []` vazio — 0 dependências declaradas, apesar do código importar numpy, scipy, matplotlib, sqlalchemy, jinja2, fastapi, streamlit e outros. Decisão: extrair de `requirements.txt` ou `pip freeze` e popular `[project.dependencies]`. Adicionar `[project.optional-dependencies]` para dev/test/docs. Afeta Fase 0.1.

**Spec 002 — TopOpt (C3):** plan.md + spec.md + tasks.md + contracts/ intactos. tasks T001-T011 marcados completos. Escopo (OpenMDAO/Dakota topology optimization) está correto. Decisão: C3 = suplementar módulos específicos de análise topológica, não reescrever. Validar convergência com malhas 007. Afeta Fase 0.2.

**Spec 006 — Validação Experimental (C3):** Apenas `contracts/` existe (protocolos_hidrologia.md, protocolos_materiais.md). spec.md, plan.md, tasks.md ausentes. `tests/validation/` existe com conftest.py + test files. Decisão: criar spec.md + plan.md + tasks.md mapeando `tests/validation/` para os protocolos. Validar contra M3 VVV (6 critérios de certificação). Afeta Fase 0.2.

**Projeto Geral:** 839 testes existentes em `tests/`. Layout misto (`src/` para physics_m3, raiz para cad/, scripts/ para CLI). Decisão: manter layout existente, não forçar reestruturação. Adicionar entry_points em pyproject.toml para CLIs. Afeta Fase 0.1 (scaffold).
