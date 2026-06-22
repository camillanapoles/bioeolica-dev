# LAB-ENGINE — Log de Execução Persistente

> **Checkpoint de retomada.** Este arquivo é o estado persistente do trabalho LAB-ENGINE,
> desenhado para **sobreviver a compactações de contexto e pequenas resoluções**.
> Lê-lo no início de qualquer sessão deve permitir retomar EXATAMENTE de onde parou.
>
> Atualizado a cada atividade concluída + commitado (M4).

---

## Ponteiros canônicos (leia primeiro)

| O quê | Onde |
|---|---|
| **Plano orientado T01-T13** (gates, métricas, DoD) | `Plans/peaceful-herding-otter.md` |
| **Contrato canônico** (WAL schema, 10 domínios, F1-F9, resiliência) | `docs/LAB-ENGINE-ARCHITECTURE.md` |
| **Especificação KDI fonte** (2268 linhas, schema WAL em L2128-2267) | `INSTRUCTIONS.md` |
| **Progresso detalhado** (este arquivo) | `Plans/LAB-ENGINE-PROGRESS.md` |
| **Tasks no harness** | TaskList: T01..T13 (cadeia blockedBy, M2) |

## Mandatos ativos (M0-M4, governam TODO o trabalho)

- **M0** — `gitnexus analyze` + `impact` ANTES de editar qualquer símbolo.
- **M1** — NUNCA avançar se a atividade teve erro/incompleta/não validada. Avanço = código executado + teste passado.
- **M2** — Uma atividade por vez, sem pular sequência (T01→T02→...→T13).
- **M3** — Reimplementar de fato + pytest equivalente + executar. Cobertura ≥80%.
- **M4** — Commit + sync remoto ao concluir cada atividade.

## Gate por atividade (ECC/CCG)

Cada T termina com gate: `verify-change`/`verify-quality`/`verify-security` + reviewer apropriado
(python-reviewer / code-reviewer / security-reviewer / tdd-guide). CRITICAL/HIGH ou teste falha →
atividade permanece in_progress, próxima NÃO inicia.

---

## ESTADO ATUAL

- **Atividade corrente:** T01 ✅ CONCLUÍDA → próxima = **T02**
- **Último commit:** `2d91da6` (sync origin/main)
- **Branch:** `main` (local == remote)
- **Grafo:** 8557 nodes / 13377 edges / 192 flows (reindexado pós-T01)
- **Stack a instalar em T02:** `uv`, SQLAlchemy 2.0 + Alembic, Pydantic v2 + pydantic-settings, FastAPI, Typer, pytest + pytest-asyncio + hypothesis, structlog

## Próxima ação (retomar aqui)

**T02 — Modelos Pydantic do WAL** (`lab_engine/wal/models.py`)
- Espelhar o JSON Schema do `INSTRUCTIONS.md:2198-2267` em Pydantic v2
- `WalLog` com: log_id (UUID pattern), timestamp (created/started/finished), 5w1h (what/why min 10), map_index (project ^PRODUTO-, domain enum 10, scale macro/meso/micro, task ^TASK-), validation (PASS/FAIL/PENDING), quality_metrics D1-D10, patches
- TDD: testes de schema PRIMEIRO (aceita válidos, REJEITA inválidos)
- Gate: tdd-guide + python-reviewer
- Métrica: 100% casos do JSON Schema cobertos; ≥80% módulo
- **Atenção:** T03 precisa de `pyproject.toml` com deps — checar se commit remoto `1e2004e` (DB unify, pyproject deps) já preencheu o shell vazio.

---

## LOG DE ATIVIDADES

### T01 ✅ — Rename `workspaces/`→`instruments/` + contrato LAB-ENGINE (FASE 0)
- **Data:** 2026-06-22
- **Commit:** `2d91da6` (após rebase sobre 8 commits remotos)
- **Feito:**
  - `git mv workspaces instruments` (411 arquivos, renames 100% preservados)
  - Replace `workspaces→instruments` em 58 arquivos de conteúdo (Makefile, Dockerfile.ci, ci.yml, docs/INSTALL, docs/USAGE_GUIDE, MANUAL_COMPLETO, CONVENTIONS, specs/*, 2 testes .py)
  - Criada `docs/LAB-ENGINE-ARCHITECTURE.md` (207 linhas — contrato canônico derivado do INSTRUCTIONS.md)
  - Versionado `Plans/peaceful-herding-otter.md`
  - `.gitignore` preservado (`workspace/` singular = projetos, intocado)
- **Rebase:** divergência remota (8 commits 17/06: spec-008 DB unify, TopOpt, FMEA, preCICE, 3D viewer, Knowledge Engine, AI Assist CAD). 3 conflitos resolvidos (AGENTS.md, CLAUDE.md, specs/002/plan.md) adotando versão remote (já limpa de `workspaces/`, preserva features novas).
- **Métricas (todas ✓):** 0 ocorrências funcionais `workspaces/` · gitnexus analyze OK (8557 nodes) · detect_changes risk LOW / 0 processos afetados · 3 instruments empacotáveis · todos .py compilam
- **Gate:** verify-change (via detect_changes: LOW) + python-reviewer (py_compile OK)
- **Notas para T02+:**
  - O remote (commit `1e2004e`) fez "DB unify, pyproject deps" — **verificar pyproject.toml antes de T03/T10** (pode já ter deps; o `src/` raiz tem domínio existente: cad, thermo, gpu, common, coupling, crslr, retrieval).
  - O remote (commit `1e0f28a`) criou "Knowledge Engine v2 — 10 engineering domains" — **possível sobreposição com o map_index.domain do WAL**; checar `ai_assist_cad/knowledge_engine.py` em T02/T08.
  - `workspace/` (singular) = projetos emergidos (motor-gerador-v1, pa-eolica-v3) — são as FIXTURES para T12 (reprodutibilidade). Preservar.

---

## COMO RETOMAR (instruções para qualquer sessão)

1. Leia este arquivo + `Plans/peaceful-herding-otter.md` + `docs/LAB-ENGINE-ARCHITECTURE.md`.
2. Confirme `git status` limpo e `git rev-parse HEAD` == origin/main.
3. `TaskList` → identifique a primeira tarefa `pending` (sem blockedBy aberto).
4. M0: rode `node .gitnexus/run.cjs analyze` se o índice estiver stale.
5. Execute a atividade sob seus gates (M1/M3); ao concluir, commit + push (M4) e **atualize a seção "ESTADO ATUAL" + "LOG DE ATIVIDADES" aqui, e commit este arquivo junto**.

---

*Este arquivo É a persistência do plano. Atualizá-lo + commitá-lo a cada atividade é o mecanismo que garante continuidade através de compactações de contexto.*
