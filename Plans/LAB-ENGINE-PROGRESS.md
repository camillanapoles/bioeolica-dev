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

- **Atividade corrente:** T02 ✅ **CONCLUÍDA 100% (T02.D com T02.D++ VAZIO)** → liberada **T03**
- **Último commit:** `feat(wal): modelos Pydantic v2 do WAL 100% canônicos + gates permanentes (T02.D)` (sync origin/main após push)
- **Branch:** `main`
- **Grafo:** 8799 nodes / 13624 edges / 192 flows (gitnexus auto-update pós-T02)
- **Stack:** Pydantic v2 ✅ · SQLAlchemy 2.0 ✅ · `ruff`/`mypy`/`bandit` ✅ (instalados no `.venv`). Faltam p/ T03: `alembic`, `pydantic-settings`. Faltam p/ T07: `structlog`. Faltam p/ T10: `typer` (+ entry `[project.scripts] lab-engine`).
- **Gates permanentes (pyproject) TODOS VERDES em T02:** ruff (`E,F,W,I,UP,B`) · mypy `--strict` · bandit · pytest+cov. Rodar via `.venv/bin/python -m {ruff,mypy,bandit,pytest}` (NÃO `uv run` — trava em `vtk` cp313 sem wheel).

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

### T02 ✅ — Modelos Pydantic v2 do WAL (FASE 1) — T02.D concluído, T02.D++ VAZIO
- **Data:** 2026-06-22 (reabertura + resolução 100%)
- **Contexto da reabertura:** T02 havia sido marcado ✅ prematuramente (gaps: DoD round-trip JSON Schema não validado, mypy/bandit não rodados, ranges D-campos "0-100%" sem decisão registrada). Mandato T0x.D/T0x.D++ (ver plano) exige `D++` vazio para avançar — reaberto e **100% resolvido**.

#### T02.D — sucessos (validado, gates verdes)
- `lab_engine/wal/models.py` — 9 sub-modelos + `WalLog`, 5 `StrEnum` (`Domain`×10, `Scale`×3, `ValidationStatus`, `RigorStatus`, `SecurityClassification`), fiéis ao JSON Schema L2198-2320 do `INSTRUCTIONS.md`.
  - Fidelidade canônica: `extra="forbid"` onde schema declara; `extra="allow"` onde NÃO declara (`error_metrics`, `patches`).
  - `NumberOrStr = StrictInt | StrictFloat | str` (rejeita bool); timestamps tz-aware (`AfterValidator`); `frozen=True`; wire-format `"5w1h"` (`serialize_by_alias=True`, sem `populate_by_name`).
  - Enums em `enum.StrEnum` (Python 3.11+, satisfaz ruff UP042). `# nosec B105` nos 2 `PASS` (valor de enum, não credencial) — justificativa no docstring.
- `tests/lab_engine/wal/test_models.py` — **90 testes** em 11 classes + **`TestSchemaFidelity` (18 testes) validando o DoD "Round-trip JSON Schema"** — introspeção de `model_json_schema(by_alias=True)` ($defs, required, additionalProperties, patterns, enums, minLength). AAA comments nos testes multi-linha.
- `pyproject.toml` — gates permanentes declarados: `[tool.mypy] strict`, `[tool.ruff] E,F,W,I,UP,B`, `[tool.bandit]`; fix bug PEP 621 do remote (`dynamic=["version"]` removido); `lab_engine/*` em `packages.find`.
- **TDD (M3):** testes PRIMEIRO (RED) → implementação (GREEN) → expansão pós-gates (RED→GREEN) → `TestSchemaFidelity` (DoD round-trip) → `StrEnum` (UP042).
- **Gates (todos ✓ em `.venv`):**
  - `ruff` → **All checks passed!**
  - `mypy --strict` → **Success: no issues found in 1 source file**
  - `bandit -r lab_engine/wal/` → **0 issues** (Low/Med/High/Undefined 0; stderr limpo)
  - `pytest` → **90 passed** · cobertura **100%** (`models.py`: 117 stmts, 0 miss)
  - `python-reviewer`/`tdd-guide`/`verify-change`: bloqueadores C1/C2/H7 + recomendações R1-R4 — **TODOS endereçados** (StrictInt/Float, serialize_by_alias, AfterValidator tz-aware, frozen, TestSchemaFidelity, StrEnum, AAA).
- **Decisões de contrato registradas no plano** (`Plans/peaceful-herding-otter.md` § "Decisões de contrato registradas"): D-T02.1 (ranges não-inventados), D-T02.2 (parameters=object), D-T02.3 (StrEnum), D-T02.4 (forbid/allow por fidelidade).

#### T02.D++ — Todo pós-Done → **VAZIO** (todos resolvidos ou rastreados como Emenda não-bloqueante)
- ~~DoD round-trip JSON Schema não validado~~ → **RESOLVIDO**: `TestSchemaFidelity` (18 testes).
- ~~mypy/bandit não rodados~~ → **RESOLVIDO**: ambos verdes (mypy Success, bandit 0 issues).
- ~~H2 ranges D-campos "0-100%" sem decisão~~ → **DECIDIDO + EMENDA**: D-T02.1 (não inventar ranges) + **EMENDA-E001** (elevar description a `minimum/maximum` no INSTRUCTIONS.md, **pós-T13, não-bloqueante**).
- ~~UP042 `(str,Enum)`~~ → **RESOLVIDO**: adoção de `StrEnum` (D-T02.3 revisada).
- ~~AAA comments~~ → **RESOLVIDO** nos testes multi-linha.
- ~~bandit nosec stderr ruído~~ → **RESOLVIDO**: nosec isolado + justificativa no docstring.

#### Notas para T03+
- `models.py` pronto para consumo por `store.py` (serializar `by_alias=True` para wire-format; desserializar via `model_validate_json`).
- `auto_fix` (log_id/timestamp.created, L2325) fica para **T04** (`validator.py`).
- **EMENDA-E001** (ranges D-campos) — rastreada, pós-T13. Não bloqueia T03-T13.

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
