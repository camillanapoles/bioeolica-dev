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

- **Atividade corrente:** T02 ✅ CONCLUÍDA → próxima = **T03**
- **Último commit:** (a seguir — `feat(wal): modelos Pydantic v2 do WAL (T02)`)
- **Branch:** `main`
- **Grafo:** 8567 nodes / 13387 edges / 192 flows (gitnexus auto-update pós-T02)
- **Stack:** Pydantic v2 ✅ (em pyproject). Faltam p/ T03+: `alembic`, `pydantic-settings` (SQLAlchemy 2.0 já presente). Faltam p/ T07+: `structlog`. Faltam p/ T10: `typer` (+ entry `[project.scripts] lab-engine`).

## Próxima ação (retomar aqui)

**T03 — Persistência + CRUD WAL (SQLAlchemy 2.0 + Alembic)** (`lab_engine/wal/store.py`)
- Repository pattern: `create/read/update/list/by-parent/by-task` em SQLite
- Toda I/O do WAL via CRUD — **nunca** arquivos soltos (mandato: "CRUD em banco de dados")
- Migration inicial (Alembic) aplicável/reversível
- Adicionar `alembic` + `pydantic-settings` ao `pyproject.toml`
- **Consumir** `WalLog` de `lab_engine/wal/models.py` (T02 ✅): serializar via `model_dump_json(by_alias=True)` para persistir wire-format
- Gate: tdd-guide + security-reviewer (injection no repository) + verify-quality
- Métrica: transações testadas (commit/rollback); 0 string-concat em queries

### Decisões de fidelidade canônica estabelecidas em T02 (herdam para T03+)
- `additionalProperties: false` **onde** o schema INSTRUCTIONS.md declara (timestamp, 5w1h, where, how, map_index, validation, quality_metrics, top-level)
- `additionalProperties` **permitido** onde o schema NÃO declara forbid: `error_metrics` (L2274-2281) e `patches` (L2304-2311) — fidelidade ao contrato vence sobre garantismo implícito
- `NumberOrStr = StrictInt | StrictFloat | str` (rejeita bool — "number" ≠ bool)
- timestamps **timezone-aware** (format: date-time = RFC 3339)
- `frozen=True` em todos os modelos (WAL append-only)
- wire-format `"5w1h"` na entrada E saída (`serialize_by_alias=True`, sem `populate_by_name`)
- D-campos `"0-100%"` são só *description* — **não** inventar ranges (deferido: exigiria emenda ao INSTRUCTIONS.md)

---

## LOG DE ATIVIDADES

### T02 ✅ — Modelos Pydantic v2 do WAL (FASE 1, source of truth garantista)
- **Data:** 2026-06-22
- **Feito:**
  - `lab_engine/wal/models.py` — 9 sub-modelos + `WalLog`, 5 enums (`Domain`×10, `Scale`×3, `ValidationStatus`, `RigorStatus`, `SecurityClassification`), espelhando fielmente o JSON Schema L2198-2320 do `INSTRUCTIONS.md`
  - `tests/lab_engine/wal/test_models.py` — 72 testes em 10 classes (aceitação parametrizada, patterns, minLength, enums, extra-forbid/allowed, strict-types, tz-aware, wire-format, round-trip, frozen)
  - Fix `pyproject.toml`: bug PEP 621 do remote (`version` estático **e** em `dynamic` simultâneo — bloqueava builds); + `lab_engine/*` em `packages.find`
- **TDD (M3):** testes PRIMEIRO (RED: `ModuleNotFoundError`) → implementação (GREEN) → expansão pós-gates (RED→GREEN)
- **Gates:**
  - `python-reviewer`: 3 bloqueadores C1 (bool em number), C2 (wire-format `by_alias`), H7 (tz-aware) + demais — **TODOS endereçados** (StrictInt/StrictFloat, serialize_by_alias, AfterValidator tz-aware, frozen, remover populate_by_name, D9_vies→NumberOrStr)
  - `tdd-guide`: APROVADO c/ recomendações R1-R4 (timestamp-forbid test, alias-literal assert, enum positive coverage, error_metrics spec-drift) — **TODAS endereçadas**
  - `verify-change` (detect_changes): risk LOW, 0 processos afetados
  - `ruff`: All checks passed! (F401 resolvidos pela reescrita dos testes)
- **Métricas (todas ✓):** 72/72 testes ✅ · cobertura **100%** (`models.py`: 117 stmts, 0 miss) · ruff clean · probe canônico 8/8 ✅
- **Decisões de fidelidade (registradas em "ESTADO ATUAL"):** ver acima. Destaque: `error_metrics`/`patches` aceitam extras (schema não declara forbid) — fidelidade ao contrato vence.
- **Notas para T03+:**
  - `models.py` pronto para consumo por `store.py` (serializar `by_alias=True` para wire-format).
  - `auto_fix` (log_id/timestamp.created, L2325) fica para **T04** (`validator.py`).
  - Rodar testes via `.venv/bin/python -m pytest` (não `uv run` — trava em `vtk` cp313 sem wheel).
  - `pyproject.toml`: ainda faltam `alembic`, `pydantic-settings` para T03; `structlog` p/ T07; `typer` p/ T10.

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
