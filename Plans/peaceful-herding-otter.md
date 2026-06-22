# Plano: LAB-ENGINE — Runtime multi-agente garantista SOTA 2026

> **Rígido, orientado a atividades com gate.** Cada atividade (T0x) tem Definition of Done mensurável, um gate ECC/CCG, uma métrica e **bloqueia a próxima se falhar** (mandato **M1** do `INSTRUCTIONS.md`). Cumpre os **mandatos M0–M4** e o **contrato WAL + JSON Schema + workflow F1-F9 + 10 domínios** definidos em `INSTRUCTIONS.md`.

---

## Contexto

O motor multi-agente que produziu `workspace/motor-gerador-v1` (29 contextos, 7 agentes) e `workspace/pa-eolica-v3` (25 contextos) **emergiu bem** mas **não é reproduzível nem garantista** hoje:

- O runtime é **bash** (6 scripts, ~1760 linhas) **copiado por workspace** — `motor-gerador-v1` tem, `pa-eolica-v3` não, `template/` tem. Inconsistente.
- O `propagation-proto.sh publish` faz 4 quality gates mas **escreve só no `.events.log`** (vazio nos workspaces reais) — **não escreve no `lineage_db`**. O `lineage_db` (o rastro de emergência) foi populado por mecanismo externo/manual, em **2 formatos diferentes** (array `entries` vs dict top-level).
- Há **bug `${HOME}`** literal (paths não-expandidos) em ~7 arquivos — quebra reprodutibilidade.
- `pyproject.toml` é um **shell vazio** (sem `[project.scripts]`, sem deps). `src/` é monorepo Python de domínio não empacotado como CLI.
- `workspaces/` (plural = `cad-cae-platform`, `kdi-m3-bridge`, `physics-m3`) é **ferramental de lab** e confunde com `workspace/` (singular = projetos).

**Objetivo:** transformar o que emergiu no **LAB-ENGINE** — um runtime Python garantista, event-sourced, com WAL persistido em BD, cumprindo o contrato `INSTRUCTIONS.md`, capaz de **regenerar qualquer projeto de engenharia** (motor-gerador, pá eólica, ...) declarando domínios + problema.

---

## Arquitetura SOTA 2026 recomendada (declarada, justificada)

**LAB-ENGINE = runtime WAL event-sourced, Python-nativo, sem servidor externo.** Source of truth = **log WAL em banco de dados**, validado por schema **antes** de persistir.

| Pilar | Mecanismo | Atende requisito |
|---|---|---|
| **WAL em BD (source of truth)** | SQLAlchemy 2.0 + Alembic; cada ação = log WAL persistido. Nada em arquivos soltos. | CRUD total em BD + continuidade (WAL) |
| **Garantismo schema-enforced** | Pydantic v2 espelhando o JSON Schema (draft 2020-12) do `INSTRUCTIONS.md`; log **rejeitado antes** de persistir. | "Garantista", validação |
| **Event-driven** | Command bus + event store; handlers emitem eventos WAL; agentes reagem por subscription. | Arquitetura por evento + gatilhos |
| **Workflow F1-F9 (FSM)** | Máquina de estados com guards (`return_conditions`), transições persistidas, retry por fase. | BPM + contrato `INSTRUCTIONS.md` |
| **Resiliência** | retry + backoff exponencial, **timeout (15 min default, configurável)**, fallback (relatar+incerteza+alternativo), circuit breaker, dead-letter WAL, saga compensation. | "Retry se erro" + "captura se não retorna em N tempo" |
| **A2A contracts** | Agents comunicam via I/O Pydantic + correlation ID + reply-to; agent registry. Padrão Google A2A. | A2A |
| **12-factor / zero hardcoded** | `pydantic-settings` (env + `config.toml`); paths relativos; **lint gate que PROÍBE `${HOME}`/hardcoded**. | "Proibido setar variáveis" + reprodutibilidade |
| **API + CLI** | FastAPI (CRUD WAL + commands) + CLI Typer `lab-engine`. | API + CLI |
| **TDD + property-based** | pytest + hypothesis; mandato **M3** (pytest equivalente por implementação). | TDD + M3 |

**Stack:** Python ≥3.11 · `uv` · SQLAlchemy 2.0 + Alembic · Pydantic v2 + pydantic-settings · FastAPI · Typer · pytest + pytest-asyncio + hypothesis · structlog. **Engine de workflow:** event-sourcing custom leve (SQLite-able, reproduzível, TDD-friendly). *Upgrade path futuro:* Temporal se houver necessidade de escala multi-nodo.

---

## Mandatos que governam TODO o plano (do `INSTRUCTIONS.md`)

- **M0** — `gitnexus` analyze + `impact` **antes** de editar qualquer símbolo.
- **M1** — **Nunca** avançar se a atividade teve erro / ficou incompleta / não validada. Avanço = código executado + teste passado = ✅.
- **M2** — **Uma atividade por vez**, sem pular sequência (T01 → T02 → ...).
- **M3** — Reimplementar de fato + gerar **pytest equivalente** + executar. Sucesso é a única métrica.
- **M4** — Commit + sync remoto ao concluir cada atividade.

---

## Gate ECC/CCG aplicado a CADA atividade

Conforme regras ECC (`~/.claude/rules/ecc/`) e gates CCG:

1. **tdd-guide** — teste primeiro (M3), cobertura ≥80% (`testing.md`).
2. **python-reviewer** — padrões Python, tipos, async.
3. **code-reviewer** — qualidade geral (`code-review.md`).
4. **security-reviewer** — quando há I/O de BD, input externo, contracts (`security.md`).
5. **verify-change** — impacto (GitNexus) + sincronia de docs.
6. **verify-quality** + **verify-security** — scan final da atividade.

**Convenção de bloqueio:** cada T termina com um **command** de gate. Se qualquer gate retorna CRITICAL/HIGH ou teste falha → **atividade permanece `in_progress`**, próxima **NÃO inicia** (TaskUpdate `addBlockedBy`).

---

## Atividades

### FASE 0 — Fundação & higiene (M0)

**T01 — M0: reindex GitNexus + declarar contrato + rename `workspaces/`→`instruments/`**
- **Faixa:** mover `workspaces/` → `instruments/`; atualizar `.gitignore`/refs; escrever `docs/LAB-ENGINE-ARCHITECTURE.md` (contrato canônico: WAL schema, F1-F9, domínios).
- **DoD:** `instruments/` existe; zero referência a `workspaces/` no repo; GitNexus reindexado sem erro; doc aprovada.
- **Gate:** `verify-change` (impacto do rename) + `python-reviewer` (imports).
- **Métrica:** 0 ocorrências de `workspaces/` em código/docs; `gitnexus analyze` ✅.

### FASE 1 — Contrato (source of truth garantista)

**T02 — Modelos Pydantic do WAL (espelham JSON Schema do `INSTRUCTIONS.md`)**
- **Faixa:** `lab_engine/wal/models.py` — `WalLog` (log_id UUID, timestamp, 5w1h, map_index com enum dos 10 domínios, validation PASS/FAIL/PENDING, quality_metrics D1-D10, patches). Round-trip JSON Schema ↔ Pydantic.
- **DoD:** `WalLog.model_validate` aceita logs válidos e **rejeita** inválidos (UUID fora do pattern, domínio fora do enum, `what`<10 chars).
- **Gate:** `tdd-guide` (testes de schema primeiro) + `python-reviewer`.
- **Métrica:** 100% dos casos do JSON Schema do `INSTRUCTIONS.md` cobertos por teste; ≥80% no módulo.

**T03 — Persistência + CRUD WAL (SQLAlchemy 2.0 + Alembic)**
- **Faixa:** `lab_engine/wal/store.py` (repository pattern) + migration inicial. Toda I/O do WAL via CRUD — nunca arquivos soltos.
- **DoD:** CRUD (create/read/update/list/by-parent/by-task) funcional em SQLite; migration aplicável/reversível.
- **Gate:** `tdd-guide` + `security-reviewer` (injection no repositório) + `verify-quality`.
- **Métrica:** transações testadas (commit/rollback); 0 string-concat em queries.

**T04 — Validador garantista + Auditor WAL**
- **Faixa:** `lab_engine/wal/validator.py` (rejeita antes de persistir) + `lab_engine/wal/auditor.py` (detecta `PENDING > 24h`, órfãos de `parent_log`, breaches de schema — L2005/L2006).
- **DoD:** nenhum log inválido entra no BD; auditor emite relatório de anomalias.
- **Gate:** `tdd-guide` (property-based com hypothesis nos invariantes) + `code-reviewer`.
- **Métrica:** 0 logs inválidos persistidos (teste negativo); auditor cobre 4 anomalias.

### FASE 2 — Runtime event-driven

**T05 — Command bus + event store + handlers**
- **Faixa:** `lab_engine/runtime/bus.py` (commands: `new_project`, `publish_context` [4 gates], `allocate_task`, `derive_team`) + event store append-only no BD + pub/sub.
- **DoD:** cada command produz ≥1 evento WAL; handlers reagem; replay de eventos reconstroi estado.
- **Gate:** `tdd-guide` + `python-reviewer` (async/concorrência) + `verify-change`.
- **Métrica:** replay idempotente; eventos cobrem os 4 commands.

**T06 — Workflow F1-F9 como FSM**
- **Faixa:** `lab_engine/runtime/workflow.py` — 9 fases com guards (`return_conditions`), transições, estado persistido por projeto. F1 `problem_statement` → ... → F8 comunicar → F9 fechar.
- **DoD:** transição bloqueada se guard falha; `return_conditions` volta à fase correta; state sobrevive a restart.
- **Gate:** `tdd-guide` (cada fase + cada guard) + `code-reviewer`.
- **Métrica:** 9 fases × guards testados; 0 estado em memória não-persistido.

**T07 — Resiliência (retry/timeout/fallback/circuit-breaker/dead-letter)**
- **Faixa:** `lab_engine/runtime/resilience.py` — decorator de retry+backoff, **timeout configurável (default 15 min)**, fallback (relatar aprendizado + incerteza + método alternativo), circuit breaker, dead-letter WAL, saga compensation (L644-649, L965-968).
- **DoD:** agente que excede timeout é capturado + fallback registrado + workflow não trava.
- **Gate:** `tdd-guide` (testes de falha/timeOut) + `security-reviewer` + `verify-quality`.
- **Métrica:** 5 modos de falha testados (timeout, exceção, loop, circuit-open, compensação).

### FASE 3 — Agentes & A2A

**T08 — A2A contracts + agent registry + agent-factory declarativo (zero hardcoded)**
- **Faixa:** `lab_engine/agents/` — contracts Pydantic (input/output, correlation_id, reply_to), registry, e `agent-factory` reescrito do bash: lê domínios → deriva agentes com proficiência (do `relevance_check`), **sem variáveis hardcoded** (config externa).
- **DoD:** factory gera time a partir de config declarativa; agents trocam mensagens via contracts; 0 path/valor hardcoded.
- **Gate:** `tdd-guide` + `python-reviewer` + `verify-security`.
- **Métrica:** factory reproduz o time de `motor-gerador-v1` a partir do seu `relevance_check.md`.

### FASE 4 — Interface

**T09 — FastAPI (CRUD WAL + commands)**
- **Faixa:** `lab_engine/api/` — endpoints: `POST /projects`, `POST /contexts/publish` (4 gates), `GET /wal/{log_id}`, `GET /workflow/{project}/status`, `POST /agents/allocate`. Validação Pydantic na borda.
- **DoD:** OpenAPI gerada; endpoints validam I/O; erros padronizados (envelope `patterns.md`).
- **Gate:** `tdd-guide` (TestClient) + `security-reviewer` + `verify-quality`.
- **Métrica:** 100% endpoints com teste; 0 endpoints sem validação de entrada.

**T10 — CLI `lab-engine` (Typer)**
- **Faixa:** `lab_engine/cli.py` + entrada em `pyproject.toml` `[project.scripts]`. Comandos: `new <nome> --domains`, `run <projeto>`, `status <projeto>`, `report <projeto>`, `audit`, `doctor`.
- **DoD:** `uv run lab-engine new demo --domains "Mecânica,Fluidos"` cria projeto + deriva time + escreve WAL no BD.
- **Gate:** `tdd-guide` (CLI tests com CliRunner) + `code-reviewer` + `verify-change` (pyproject).
- **Métrica:** 5 comandos testados end-to-end.

### FASE 5 — Validação garantista final

**T11 — Lint gate zero-hardcoded + unificação do `lineage_db`**
- **Faixa:** gate CI/lint que **PROÍBE** `${HOME}`/paths absolutos/valores hardcoded em qualquer script ou config; migra os `lineage_db` existentes ao formato canônico (Pydantic WAL) via script de migração idempotente.
- **DoD:** lint reprova PR com hardcoded; migração converte motor-gerador-v1 + pa-eolica-v3 sem perda; diff semântico ≈ 0.
- **Gate:** `verify-security` + `verify-change` + `python-reviewer`.
- **Métrica:** 0 ocorrências de `${HOME}`/abs-path após migração; 2 workspaces migrados validados.

**T12 — Prova de reprodutibilidade (regenerar os 2 projetos)**
- **Faixa:** rodar `lab-engine new` + `run` declarando os domínios/problemas de `motor-gerador-v1` e `pa-eolica-v3`; comparar WAL/contextos gerados contra os existentes (fixtures).
- **DoD:** LAB-ENGINE regera a **mesma topologia de contextos** (mesmas classes, mesmo número, mesma cadeia parent/child) dos projetos originais.
- **Gate:** `tdd-guide` (teste de regressão de reprodutibilidade) + `code-reviewer`.
- **Métrica:** ≥90% de match estrutural vs fixtures; 0 diferença semântica nos contextos-raiz.

**T13 — Cobertura + property-based + security review + sync remoto (M4)**
- **Faixa:** cobertura ≥80% global, bateria property-based (hypothesis) nos invariantes WAL, `security-reviewer` final, commit + sync remoto.
- **DoD:** cobertura ≥80%; 0 CRITICAL/HIGH aberto; `main` sincronizado com remoto.
- **Gate:** `verify-security` + `verify-quality` + `python-reviewer` (final).
- **Métrica:** cobertura ≥80%; 0 CRITICAL/HIGH; `git status` limpo + push ✅.

---

## Master de atividades (scan rápido)

| ID | Atividade | Gate principal | Métrica-chave | Bloqueia |
|----|-----------|----------------|---------------|----------|
| T01 | Rename `workspaces/`→`instruments/` + doc contrato | verify-change | 0 refs a `workspaces/` | T02 |
| T02 | Modelos Pydantic WAL (JSON Schema) | tdd + python | 100% casos schema | T03 |
| T03 | Persistência + CRUD WAL (SQLA+Alembic) | tdd + security | 0 concat em queries | T04 |
| T04 | Validador + Auditor WAL | tdd + property | 4 anomalias auditor | T05 |
| T05 | Command bus + event store | tdd + python | replay idempotente | T06 |
| T06 | Workflow F1-F9 FSM | tdd + review | 9 fases+guards | T07 |
| T07 | Resiliência retry/timeout/fallback | tdd + security | 5 modos falha | T08 |
| T08 | A2A contracts + agent-factory declarativo | tdd + security | 0 hardcoded | T09 |
| T09 | FastAPI CRUD+commands | tdd + security | 100% c/ teste | T10 |
| T10 | CLI `lab-engine` (Typer) | tdd + review | 5 cmds E2E | T11 |
| T11 | Lint zero-hardcoded + migrar lineage | verify-security | 0 `${HOME}` | T12 |
| T12 | Reprodutibilidade (regenerar 2 projetos) | tdd + review | ≥90% match | T13 |
| T13 | Cobertura 80% + security final + sync (M4) | verify-security+quality | 0 CRITICAL | — |

---

## Verification (como validar o produto pronto)

1. **Unit + property:** `uv run pytest --cov=lab_engine --cov-fail-under=80` → verde, cobertura ≥80%.
2. **CLI end-to-end:** `uv run lab-engine new demo --domains "Mecânica,Fluidos"` → cria projeto, deriva time, WAL persistido no BD.
3. **Garantismo:** tentar persistir log WAL inválido → **rejeitado** pelo validador (teste negativo).
4. **Resiliência:** simular agente que excede 15 min → capturado, fallback registrado, workflow não trava.
5. **Reprodutibilidade:** `lab-engine run` regera `motor-gerador-v1` e `pa-eolica-v3` com ≥90% de match estrutural vs fixtures.
6. **Auditoria:** `lab-engine audit` → relatório de WAL sem órfãos/PENDING>24h.
7. **Higiene:** lint gate reprova qualquer `${HOME}`/hardcoded; 0 refs a `workspaces/`.
8. **API:** `uv run uvicorn lab_engine.api:app` → OpenAPI em `/docs`, endpoints validados.

---

## Riscos & mitigações

- **Risco:** regressão ao portar lógica bash → Python. **Mitigação:** T12 (reprodutibilidade vs fixtures) é o gate final; reuso do `src/` de domínio existente (cad/thermo/gpu).
- **Risco:** over-engineering do event-sourcing. **Mitigação:** escopo SQLite local; Temporal só como upgrade path.
- **Risco:** doc-canônico (`INSTRUCTIONS.md`) divergir da implementação. **Mitigação:** T02 deriva modelos **do** JSON Schema do doc; `verify-change` a cada T garante sincronia.
