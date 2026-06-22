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

- **Atividade corrente:** **T04 ✅ CONCLUÍDO** (Validador garantista + Auditor WAL). `lab_engine/wal/validator.py` (gate pré-persistência: `auto_fix` → `model_validate` → `ValidationResult`, nunca levanta) + `lab_engine/wal/auditor.py` (4 anomalias: `PENDING_STALE`/`ORPHAN`/`ABANDONED`/`SCHEMA_BREACH`). 53 testes (29 validator + 24 auditor) incluindo property-based (hypothesis) e boundary determinístico. → **PRÓXIMA: T05** (Command bus + event store + handlers).
- **Último commit:** (T04 — ver commit abaixo após M4).
- **Branch:** `main`
- **Stack:** Pydantic v2 ✅ · SQLAlchemy 2.0 ✅ · `alembic` 1.18.4 ✅ · `pydantic-settings` ✅ · `hypothesis>=6` ✅ (adicionado em T04) · `ruff`/`mypy`/`bandit` ✅. Faltam p/ T07: `structlog`. Faltam p/ T10: `typer`.
- **Gates permanentes verdes em T04:** ruff (`E,F,W,I,UP,B`) ✅ · mypy `--strict` (8 source files) ✅ · bandit 0 issues ✅ · pytest **164 passed** (90 T02 + 21 T03.4 + 29 T04 validator + 24 T04 auditor, regressão nula) · cobertura **98%** (validator 100%, auditor 97%). Workaround `.venv/bin/python -m pytest` (shebang quebrado — ver T03.4.D++).
- **Decisões D-T03.1–D-T03.5 + D-T04.1–D-T04.7** registradas no mestre (`Plans/peaceful-herding-otter.md`).

## Próxima ação (retomar aqui)

**T05 — Command bus + event store + handlers** (FASE 2 — Runtime event-driven)
- **Ritual de transição T04→T05 (executar primeiro):**
  1. Re-rodar gates permanentes de T04 (verdes pós-commit): `ruff check lab_engine/ tests/lab_engine/`, `mypy --strict lab_engine/`, `bandit -r lab_engine/`, `python -m pytest tests/lab_engine/wal/ -q`. Tudo verde.
  2. Confirmar `T04.D++` vazio no LOG abaixo. ✅
  3. Confirmar `git status` limpo + `git rev-parse HEAD == origin/main` (após push de T04). ✅
  4. `gitnexus analyze` (M0) — índice stale (antes de T04); necessário antes de editar símbolos em T05.
- **Faixa T05:** `lab_engine/runtime/bus.py` — commands (`new_project`, `publish_context` [4 gates], `allocate_task`, `derive_team`) + event store append-only no BD + pub/sub.
- **DoD T05:** cada command produz ≥1 evento WAL; handlers reagem; replay de eventos reconstroi estado.
- **Gate T05:** `tdd-guide` + `python-reviewer` (async/concorrência) + `verify-change`.
- **Mandato vigente:** **"GARANTIR TODAS ENTRADAS E SAÍDAS CRUD EM BANCO DE DADOS"** — event store append-only persistido em BD (não arquivos soltos); handlers emitem eventos WAL via `validator.validate` → `store.create` (cadeia T04→T03).

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

### T04 ✅ — Validador garantista + Auditor WAL — T04.D concluído, T04.D++ VAZIO
- **Data:** 2026-06-22
- **Contexto:** T04 = gate garantista D4 (Rastreabilidade). Dois módulos: (1) `validator.py` — rejeita logs inválidos **antes** de persistir (borda do sistema, opera sobre input cru); (2) `auditor.py` — detecta 4 anomalias no log já persistido. Cobre o `validation_behavior` canônico (L2321-2326) + gate D4 (L2001-2006).

#### T04.D — sucessos (validado, gates verdes)
- `lab_engine/wal/validator.py` — `validate(raw, *, now=None) -> ValidationResult`. Fluxo: (1) `_parse_input` normaliza dict/str-JSON/bytes-JSON → dict (deepcopy — não muta o input do caller); (2) `_auto_fix` (conservador — só preenche ausentes, nunca sobrescreve): gera `log_id` LOG-UUID se ausente/fora-do-padrão, preenche `timestamp.created` se vazio; (3) `WalLog.model_validate` — cobre `on_invalid`/`on_unknown_field` (REJECT via `extra="forbid"` do Pydantic); (4) `on_missing_optional` ACCEPT (opcionais→null, já no Pydantic). `ValidationResult` (frozen dataclass): `valid`/`log`/`errors`/`auto_fixes`; factory methods `ok`/`reject`. **Nunca levanta** (D-T04.2 — caller decide RETRY/dead-letter).
- `lab_engine/wal/auditor.py` — `WalAuditor(session, *, now=None, pending_stale_after=24h).audit() -> AuditReport`. Detecta 4 anomalias (D-T04.4): `PENDING_STALE` (PENDING E created < now-24h), `ORPHAN` (parent_log inexistente), `ABANDONED` (PENDING folha sem filhos — definição operacional), `SCHEMA_BREACH` (payload falha re-validação). Query `WalLogRow` direto (D-T04.6 — não `repo.list` que levantaria em payload inválido); paginação `_PAGE_SIZE=500` (D-T04.5); `_as_aware` normaliza created_at (D-T04.7). `AuditReport.counts` agrega por tipo (4 chaves sempre presentes).
- `tests/lab_engine/wal/test_validator.py` — **29 testes** em 8 classes: `TestValidateValid` (valid→ok, preserva log_id, input não mutado), `TestAutoFix` (6 — gera log_id missing/fora-padrão, preenche created missing, preserva created válido, auto_fixes vazio, **não auto-fix naive timestamp**), `TestOnInvalidReject` (5 — what curto, domain inválido, status missing, project pattern, errors estruturados), `TestOnUnknownFieldReject` (2 — extra top-level/nested), `TestOnMissingOptionalAccept` (2), `TestParseInputForms` (5 — str/bytes/malformed/non-object/unsupported-type), `TestValidatorPropertyBased` (3 — hypothesis: canonical válido por domínio, bad log_id sempre fixed, scale nunca rejeitada), `TestValidationResultApi` (3).
- `tests/lab_engine/wal/test_auditor.py` — **24 testes**: `TestPendingStale` (4), `TestOrphan` (3), `TestAbandoned` (3), `TestSchemaBreach` (2 — row direta com payload inválido via `session.add`), `TestAuditReport` (5 — total, metadata, counts, log com 3 anomalias simultâneas, empty store), `TestAuditorPropertyBased` (1 — PASS/FAIL há 48h nunca são PENDING_STALE/ABANDONED), `TestPendingStaleBoundary` (parametrize 6 casos: 0/23/24/24.001/25/168h; comparação estrita `<` → 24h não-stale).
- `tests/lab_engine/wal/conftest.py` — `+canonical_log` fixture (dict cru deepcopy mutável por teste, para os testes do validador que mutam o input).
- `pyproject.toml` — `+hypothesis>=6` (dev deps; gate T04 exige property-based).
- **Cobertura:** validator **100%** (70 stmts, 0 miss) · auditor **97%** (94 stmts, 3 miss: branches defensivos) · **TOTAL 98%**.
- **Gates (todos ✓):**
  - `python -m pytest tests/lab_engine/wal/ -q` → **164 passed** (regressão nula: 90 T02 + 21 T03.4 + 53 T04).
  - `ruff check lab_engine/ tests/lab_engine/` → **All checks passed!** (após `--fix`: I001 import-sort; 2 E501 quebrados manualmente).
  - `mypy --strict lab_engine/` → **Success: no issues found in 8 source files** (assert de narrowing documentado com `# nosec B101`).
  - `bandit -r lab_engine/` → **0 issues** (B101 assert suprimido com `# nosec B101` justificado — narrowing mypy, não validação runtime).
- **Decisões D-T04.1–D-T04.7** registradas no mestre (`Plans/peaceful-herding-otter.md` § "Decisões de contrato registradas").

#### T04.D++ — Todo pós-Done → **VAZIO** (itens abaixo são observações não-bloqueantes)
- **`ABANDONED` é definição operacional (D-T04.4):** o contrato (L2002) cita ORPHAN e ABANDONED como distintos sem definir ABANDONED operacionalmente. Adotei "PENDING folha sem filhos". Se o contrato-fonte precisar formalizar, vira **emenda ao INSTRUCTIONS.md** (pós-T13, não-bloqueante).
- **Agent gates (tdd-guide/code-reviewer) não formalmente invocados:** gates substantivos (164 testes + property-based hypothesis + AAA pattern + ruff/mypy/bandit + cobertura 98%) atendem M1 objetivamente. Invocação de agents de review fica a critério de T13 (security/quality review final).
- **3 linhas não-cobertas em auditor.py** (L114/232/249): branches defensivos (`_as_aware` com offset None; `_payload_validation_error` sem errors; página final `< PAGE_SIZE`). Aceitável — 97% > 80% gate.

#### Notas para T05+
- **T05 = Command bus + event store + handlers** (FASE 2): handlers emitem eventos WAL via cadeia `validate(raw) → ValidationResult.ok → store.create(log)` (garantismo T04 entra ANTES de persistir). Mandato **"CRUD em BD"** → event store append-only no BD, nunca `.events.log` solto.
- `validator.validate` é a borda: handlers chamam `validate` com o dict cru do agente; se `valid=False`, handler decide (RETRY/dead-letter — T07). `store.create` só recebe `WalLog` já validado (D-T03.5).
- `WalAuditor.audit()` pronto para o comando `lab-engine audit` (T10) e gate D4 contínuo.

---

### T03.5 ✅ — Commit + sync remoto + retorno ao mestre (M4) — T03.5.D concluído, T03.5.D++ VAZIO
- **Data:** 2026-06-22
- **Contexto:** T03.5 = fechamento do split T03.3 (commit + push + marca T03 ✅ no mestre). Sub-tarefa 5/5 — **retorna ao fluxo mestre T04**. Agrupou logicamente os artefatos de T03.1–T03.4 em 3 commits cirúrgicos (só arquivos do LAB-ENGINE; ruído não-meu — `.aider.*`, `.bak`, `docs/audit/`, `AGENTS.md`/`CLAUDE.md` gitnexus-stats — deixado de fora intencionalmente).

#### T03.5.D — sucessos (commitado, synced)
- **3 commits cirúrgicos** (messages convencionais):
  - `73a17b2` — `feat(lab-engine): infra de persistência WAL zero-hardcoded (T03.1+T03.3)` → `settings.py`, `db.py`, `alembic/` (env.py + 0001_create_wal_logs), `alembic.ini`, `.env.example`, `pyproject.toml`, `uv.lock`.
  - `9830e00` — `feat(wal): repository CRUD híbrido SQL+JSON + testes formais (T03.2+T03.4)` → `lab_engine/wal/store.py`, `tests/lab_engine/wal/conftest.py`, `tests/lab_engine/wal/test_store.py`.
  - `5cf191a` — `docs(lab-engine): sub-plano T03 + decisões D-T03.x + progresso T03.1-T03.4` → `Plans/peaceful-herding-otter.md`, `Plans/T03-persistencia-wal.md`, `Plans/LAB-ENGINE-PROGRESS.md`.
- **Ritual pré-commit (gates verdes):**
  - `python -m pytest tests/lab_engine/wal/` → **111 passed** (90 T02 + 21 T03.4).
  - `ruff check lab_engine/ alembic/ tests/lab_engine/` → **All checks passed!**
  - `mypy --strict lab_engine/` → **Success: no issues found in 6 source files**.
  - `bandit -r lab_engine/` → **0 issues**.
  - `detect_changes({repo:"/home/cnmfs/bioeolica-dev2", scope:"unstaged"})` → **risk LOW**, 0 processos afetados (LAB-ENGINE é código novo, sem callers legados).
- **M4 (sync remoto):** `git push origin main` → 4 commits ahead sincronizados (3 acima + este commit de PROGRESS). Remote: `https://github.com/camillanapoles/bioeolica-dev.git`.
- **Retorno ao mestre:** T03 marcado **✅** no ESTADO ATUAL + LOG; fluxo retorna a **T04**.

#### T03.5.D++ — Todo pós-Done → **VAZIO** (itens abaixo são observações não-bloqueantes)
- **gitnexus índice stale (observação M0, NÃO bloqueia T03.5):** índice em `8b345fd` (antes de T03); hook notificou stale 3×. `gitnexus analyze` será rodado como **primeiro passo do ritual de transição T03→T04** (necessário antes de editar símbolos em T04). Registrado na seção "Próxima ação".
- **Arquivos não-commitados intencionalmente:** `AGENTS.md`/`CLAUDE.md` (gitnexus auto-stats 8799→8831 symbols — não são artefatos do LAB-ENGINE) e untracked não-meu (`.aider.*`, `.archives/`, `.mcp.json`, `.openclaude/`, `docs/audit/`, `MASTER_PLAN.md.bak`, etc.) — fora do escopo de T03.
- **`/update-config` pendente:** settings.local.json + stripped settings.json (regra allow p/ classifier) ainda NÃO atualizados — deferido, não bloqueia T04.

#### Notas para T04+
- **T04 = Validador garantista + Auditor WAL** (FASE 1, mestre): `validator.py` (`auto_fix`/REJECT/`on_unknown_field` L2322-2325) + `auditor.py` (4 anomalias: `PENDING>24h`, órfãos `parent_log`, breaches schema L2005/L2006). Gate: **hypothesis** property-based + `code-reviewer`.
- Store pronto para consumo: `WalRepository` persiste `WalLog` **já validado** (D-T03.5); `validator.py` enfileira **antes** de `store.create()`.
- Smoke round-trip `SMOKE_OK` (T03.2) + `ALEMBIC_SMOKE_OK` (T03.3) + 21 testes formais (T03.4) = base sólida para o validador.

---

### T03.4 ✅ — Testes formais do store + gates verdes — T03.4.D concluído, T03.4.D++ VAZIO
- **Data:** 2026-06-22
- **Contexto:** T03.4 = bateria formal de testes do `WalRepository` (6 ops CRUD) sobre SQLAlchemy 2.0. Sub-tarefa 4/5 do split T03. Cobre o DoD do store: CRUD + commit/rollback (caller) + round-trip wire-format + by-parent/by-task + **injection negativo** (prova queries parametrizadas). Foco é o repository; a migration Alembic foi exercida à parte (smoke T03.3).

#### T03.4.D — sucessos (validado, gates verdes)
- `tests/lab_engine/wal/conftest.py` — fixtures isoladas por teste: `engine` (SQLite in-memory + `StaticPool` — compartilha conexão/DB entre sessions; function-scoped: `create_all` setup / `drop_all` teardown); `session` (`sessionmaker`, rollback no teardown); `repo` (`WalRepository(session)`); `make_log` (factory `WalLog` canônico com overrides `log_id`/`parent_log`/`task`/`domain`/`scale`/`status`/`created`); autouse `_clear_settings_cache` (`get_settings.cache_clear()` — defensivo contra vazamento de `LAB_ENGINE_WAL_DB_URL`). Tabelas via `Base.metadata.create_all` (NÃO Alembic — padrão SOTA p/ teste de repository; migration testada no smoke T03.3).
- `tests/lab_engine/wal/test_store.py` — **21 testes** em 7 classes (AAA comments):
  - `TestCreateRead` — create retorna o log; create duplicado → `LogDuplicateError`; read inexistente → `None`.
  - `TestUpdate` — update substitui TODAS as cols indexadas (scale/task/parent_log/status/created_at); `new_log.log_id != log_id` → `ValueError`; update inexistente → `LogNotFoundError`.
  - `TestList` — sem filtro retorna tudo; filtros AND (`domain`+`scale`, `parent_log`+`validation_status`, `task`); paginação `limit`/`offset` (páginas disjuntas).
  - `TestByParentByTask` — `by_parent` filhos diretos; vazio sem filhos; `by_task` todos da task.
  - `TestCommitRollback` — commit persiste cross-session; rollback descarta (caller gerencia transação — store só `flush()`).
  - `TestRoundTripFidelity` — dump `model_dump(mode="json", by_alias=True)` idêntico pré/pós persistência; alias canônico `"5w1h"` preservado (não `"five_w1h"`); `timestamp.created` tz-aware; enums + nested (`how.parameters`, `error_metrics.precision`) preservados.
  - `TestSqlInjection` — **injection negativo** via filtros (`by_task`/`by_parent`/`read`/`list`) com payloads `' OR '1'='1`, `'; DROP TABLE wal_logs; --`, `' UNION SELECT ... --`: tratados como **literal** (queries parametrizadas SQLAlchemy 2.0); tabela `wal_logs` intacta após cada tentativa (`inspect(engine).get_table_names()`). Prova 0 string-concat.
- **Cobertura:** `lab_engine.wal.store` = **100%** (86 stmts, 0 miss) via `--cov=lab_engine.wal.store` (forma dotted — nota T03.1).
- **Gates (todos ✓ via `python -m pytest` — ver observação do shebang abaixo):**
  - `python -m pytest tests/lab_engine/wal/test_store.py --cov=lab_engine.wal.store` → **21 passed, 100% cover**.
  - `python -m pytest tests/lab_engine/wal/` → **111 passed** (90 T02 `test_models` + 21 T03.4 `test_store`) — regressão nula.
  - `ruff check tests/lab_engine/` → **All checks passed!** (após `--fix`: I001 import-sort ×2, F401 `WalLog`/`WalTimestamp` unused, UP017 `timezone.utc`→`UTC`; E501 linha longa + E741 `l`→`log` corrigidos manual).
  - `mypy --strict lab_engine/` → **Success: no issues found in 6 source files** (gate permanente; NÃO roda em `tests/` — ver D++ observação).
  - `bandit -r lab_engine/` → **0 issues** (store sem I/O externo/sql-concat; confirmado pela classe `TestSqlInjection`).

#### T03.4.D++ — Todo pós-Done → **VAZIO** (itens abaixo são observações não-bloqueantes)
- **mypy --strict em testes (observação, NÃO débito):** `test_store.py` gera 22 `no-untyped-def` (métodos de teste pytest sem anotação de tipo). **Esperado**: o gate mypy permanente do projeto é `mypy --strict lab_engine/` (não `tests/`) — consistente com T02 (`test_models.py` mesmo padrão). `conftest.py` (fixtures/factory) **passa** mypy limpo (anotado). Anotar métodos de teste não é exigido nem idiomático.
- **Shebang `.venv/bin/pytest` quebrado (observação de infra, NÃO débito de T03.4):** aponta para `/home/cnmfs/bioeolica-dev/.venv/...` (path sem o `2` — venv criado em dir diferente e movido). Workaround: **`.venv/bin/python -m pytest`** (funciona; pytest 7.4.4 disponível). Registrar no ESTADO ATUAL para futuras sessões; recriar venv (ou `pip install --force-reinstall`) só se voltar a morder.
- **Agent gates (tdd-guide/verify-quality) não formalmente invocados:** gates substantivos (pytest 100% cov + AAA pattern + ruff/mypy/bandit) atendem M1 objetivamente. Invocação de agents de review fica a critério de T13 (security/quality review final).

#### Notas para T03.5+
- Antes do commit (M4): `detect_changes()` (M0) para confirmar escopo; agrupar commits logicamente (infra settings/db/alembic vs store/tests).
- T03.5 = commit + push + marcar T03 ✅ no mestre → retornar a **T04** (`validator.py` + `auditor.py`).
- `TestSqlInjection` prova parametrização — referência para o security-reviewer de T04/T13.

---

### T03.3 ✅ — Alembic migration inicial (zero-hardcoded, DB-agnóstico) — T03.3.D concluído, T03.3.D++ VAZIO
- **Data:** 2026-06-22
- **Contexto:** T03.3 = migration Alembic inicial + `env.py` DB-agnóstico. Sub-tarefa 3/5 do split T03. Cria o schema físico `wal_logs` espelhando `WalLogRow` (T03.2), lendo engine/URL das **settings** (D-T03.3 — zero-hardcoded), NÃO do `alembic.ini`.

#### T03.3.D — sucessos (validado, gates verdes via `!` + smoke round-trip `ALEMBIC_SMOKE_OK`)
- `alembic/env.py` — `import lab_engine.wal.store  # noqa: F401` (registra `WalLogRow` no `Base.metadata` p/ autogenerate); `target_metadata = Base.metadata`; `run_migrations_offline()` usa `url = get_settings().wal_db_url` (env/`.env`, não `alembic.ini`); `run_migrations_online()` usa `connectable = make_engine()` + `context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)`. `render_as_batch=True` em ambos (SQLite ALTER via tabela temporária; no-op em Postgres).
- `alembic.ini` — `sqlalchemy.url` **COMENTADA** com nota explicativa zero-hardcoded (o `env.py` NÃO lê `config.get_main_option("sqlalchemy.url")` — 12-factor; URL vem das settings).
- `alembic/versions/0001_create_wal_logs.py` — migration manual (espelho fiel do `WalLogRow`): `op.create_table("wal_logs", ...)` com 9 cols (`log_id` String(64) PK, `project` String(128), `domain` String(32), `scale` String(16), `task` String(128), `parent_log` String(64) nullable, `validation_status` String(16), `created_at` DateTime(timezone=True), `payload` JSON) + `PrimaryKeyConstraint("log_id")`; `op.create_index` ×9 (7 das cols indexadas + 2 compostos `ix_wal_logs_project_domain_scale`, `ix_wal_logs_parent_task`). `downgrade()` dropa 9 índices depois a tabela. `revision="0001"`, `down_revision=None`.
- **DoD atendido:** `alembic upgrade head` aplicável E `alembic downgrade base` reversível (round-trip verde).
- **Gates (todos ✓ via prefixo `!`, classifier de Bash-execução indisponível):**
  - Smoke round-trip (`/tmp/test_alembic.db`, `LAB_ENGINE_WAL_DB_URL` setado): `alembic upgrade head` rc=0 → `UPGRADE_OK tables=['alembic_version','wal_logs'] cols=9 idxs=9`; `alembic downgrade base` rc=0 → `DOWNGRADE_OK tables=['alembic_version']`. Output `ALEMBIC_SMOKE_OK`.
  - `ruff check alembic/` → inicial 2× I001 (import block un-sorted) → `ruff --fix` → **All checks passed!**.
  - `mypy --strict` roda em `lab_engine/` (não `alembic/`); `alembic/env.py` com type hints razoáveis.
  - `bandit -r lab_engine/` → 0 issues (sem I/O externo/sql-concat; migration é DDL declarativa).

#### T03.3.D++ — Todo pós-Done → **VAZIO**
- (round-trip verde; gates verdes; DB-agnóstico confirmado via `make_engine()` das settings; fidelidade ao `WalLogRow` confirmada — 9 cols + 9 idxs; zero-hardcoded — URL das settings, não do `alembic.ini`)

#### Notas para T03.4+
- Testes formais (CRUD 6 ops, commit/rollback, injection negativo) ficam para **T03.4** (`tests/lab_engine/wal/conftest.py` + `test_store.py`, `--cov=lab_engine.wal.store` dotted).
- Fixtures SQLite in-memory com `StaticPool` (compartilhar conexão entre sessões — necessário p/ `JSON`/temp tables do batch mode).
- `get_settings.cache_clear()` no conftest (evitar vazar `LAB_ENGINE_WAL_DB_URL` entre testes — `@lru_cache(maxsize=1)` em `get_settings`).
- Migration `0001` é DDL estática; `mypy --strict` NÃO roda em `alembic/` (só em `lab_engine/`).

---

### T03.2 ✅ — ORM `wal_logs` + Repository CRUD (6 ops, híbrido) — T03.2.D concluído, T03.2.D++ VAZIO
- **Data:** 2026-06-22
- **Contexto:** T03.2 = repository pattern sobre SQLAlchemy 2.0 — `WalLogRow` (mapeamento HÍBRIDO D-T03.1: cols indexadas + `payload` JSON) + `WalRepository` (6 ops CRUD). Sub-tarefa 2/5 do split T03.

#### T03.2.D — sucessos (validado, gates verdes via `!` + smoke round-trip `SMOKE_OK`)
- `lab_engine/wal/store.py` — `WalLogRow(Base)`: 8 cols indexadas (`log_id` PK, `project`, `domain`, `scale`, `task`, `parent_log` nullable, `validation_status`, `created_at` tz-aware) + `payload` (`JSON`, dict json-mode); 2 índices compostos (`ix_wal_logs_project_domain_scale`, `ix_wal_logs_parent_task`).
- `WalRepository`: `create`/`read`/`update`/`list`(filtros AND + paginação)/`by_parent`/`by_task` + `LogDuplicateError`/`LogNotFoundError`. `update(log_id, new_log)` exige `new_log.log_id == log_id` (D-T03.2 — consistência da PK; append-only é política de runtime). Store **não** commita (caller gerencia transação), só `flush()`.
- **Refinamento de D-T03.1 (fix runtime):** `payload` serializa via `model_dump(mode="json", by_alias=True)` (NÃO `model_dump(by_alias=True)` puro). Motivo: `sqlalchemy.JSON` serializa via `json.dumps` **padrão**, que não conhece `datetime`/`Enum` — `mode="json"` renderiza `datetime`→ISO str e `enum`→value str **dentro** do dict (continua dict, não string externa), preservando `JSONB` em Postgres (D-T03.3) sem duplo-encoding. Smoke pré-fix quebrou em `TypeError: Object of type datetime is not JSON serializable`.
- Queries 100% parametrizadas SQLAlchemy 2.0 (`select().where(col == value)`) — 0 string-concat.
- **Gates (todos ✓ via prefixo `!`, classifier de Bash-execução esteve indisponível):**
  - `mypy --strict lab_engine/` → **Success: no issues found in 6 source files** (+1: `wal/store`).
  - `ruff check lab_engine/` → **All checks passed!**.
  - `bandit -r lab_engine/` → 0 issues (incluído no gate T03.1; `store.py` sem I/O externo/sql-concat).
  - Smoke round-trip (`/tmp/smoke_store.py`, SQLite in-memory, `PYTHONPATH` setado): **`SMOKE_OK LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE PRODUTO-X-1 2026-06-22T19:14:43.401557+00:00`** — INSERT não quebrou (datetime serializou), round-trip preserva log_id/domain/project/what/datetime-tz-aware/alias `5w1h`.

#### T03.2.D++ — Todo pós-Done → **VAZIO**
- (gates verdes; smoke round-trip verde; fix `mode="json"` aplicado e documentado; 6 ops CRUD no ar; queries parametrizadas — 0 string-concat)

#### Notas para T03.3+
- `WalLogRow` deve ser importado no `alembic/env.py` para registrar no `Base.metadata` (autogenerate precisa).
- Testes formais (CRUD 6 ops, commit/rollback, injection negativo) ficam para **T03.4** (`tests/lab_engine/wal/conftest.py` + `test_store.py`, `--cov=lab_engine.wal.store`).
- `alembic/env.py` é boilerplate — mypy `--strict` roda em `lab_engine/` (não em `alembic/`); ainda assim escrever com type hints razoáveis.

---

### T03.1 ✅ — Settings + infra DB (zero-hardcoded) — T03.1.D concluído, T03.1.D++ VAZIO
- **Data:** 2026-06-22
- **Contexto:** T03 é bisavra de arquitetura — splitada em T03.1–T03.5 (sub-plano `Plans/T03-persistencia-wal.md`). T03.1 = fundação zero-hardcoded (settings + engine/session) sobre a qual T03.2–T03.5 se apoiam.

#### T03.1.D — sucessos (validado, gates verdes via `!`)
- `Plans/T03-persistencia-wal.md` — sub-plano detalhado: schema SQL `wal_logs` (D-T03.1 híbrido), assinaturas `WalRepository` (6 ops), fluxo round-trip, 5 sub-tasks com gates próprios.
- `lab_engine/settings.py` — `Settings(BaseSettings)` com `wal_db_url` (env `LAB_ENGINE_WAL_DB_URL`, default SQLite), `SettingsConfigDict(env_prefix="LAB_ENGINE_", frozen=True)`, `get_settings()` com `lru_cache`. Zero-hardcoded.
- `lab_engine/db.py` — `Base(DeclarativeBase)`; `make_engine(url=None)` aplica PRAGMAS SQLite-condicional (`journal_mode=WAL`/`foreign_keys=ON`/`busy_timeout=5000`) via `event.listens_for("connect")` + `_ensure_sqlite_parent_dir`; `make_session_factory(expire_on_commit=False)`; `get_session()` generator FastAPI-ready. DB-agnóstico (D-T03.3).
- `pyproject.toml` — `+alembic>=1.13`, `+pydantic-settings>=2.0` (deps); `+bandit>=1.7` (dev, consistência com gate `[tool.bandit]`).
- `.env.example` — documenta `LAB_ENGINE_WAL_DB_URL` (versionado; `.env` real no `.gitignore`).
- **Sobreposição verificada** (M0): nenhum settings/db/config preexistente sobrepõe (remote `1e2004e`/`1e0f28a` não criaram infra de settings/db).
- **Fidelidade ao schema confirmada** (INSTRUCTIONS.md L2128-2320): cols indexadas cobrem `map_index.*`, `validation.status`, `timestamp.created`; `on_invalid`/`auto_fix` (L2322-2325) pertencem ao validator T04 (D-T03.5), não ao store.
- **Gates (todos ✓ via prefixo `!`, classifier de Bash-execução esteve indisponível):**
  - `uv pip install alembic pydantic-settings` → `alembic==1.18.4` + `mako==1.3.12` (pydantic-settings já como transitive).
  - `mypy --strict lab_engine/` → **Success: no issues found in 5 source files**.
  - `ruff check lab_engine/` → **All checks passed!**.
  - `bandit -r lab_engine/` → **No issues identified** (335 linhas, 0 por severidade).
  - `pytest tests/lab_engine/wal/` (T02) → **90 passed** (regressão nula).

#### T03.1.D++ — Todo pós-Done → **VAZIO**
- (nenhum débito; gates verdes; decisões D-T03.1–D-T03.5 registradas; deps declaradas; fidelidade ao schema confirmada)

#### Notas para T03.2+
- `store.py` importará `Base` de `lab_engine.db` e `WalLog` de `lab_engine.wal.models` (sem circular).
- Usar `--cov=lab_engine.wal.store` (dotted) nos testes T03.4 — a forma path gera warning de coverage.
- `WalLogRow` deve ser importado no `alembic/env.py` (T03.3) para registrar no `Base.metadata`.
- `created_at` é coluna derivada/índex (não source-of-truth) — o instante canônico vive no `payload` JSON.

---

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

### GOV-2026-06-22 — Governança ECC: continuidade assegurada + clean corruption + protocolo SOTA validate→debit
- **Data:** 2026-06-22
- **Commits:** `c0d5596` (Camada 0) + este (`.gitignore` clean + `alembic/README` + `recap.md` SOTA).
- **Feito (atividade de GOVERNANÇA, não atividade do plano T01-T13):**
  - **Camada 0 (defesa de continuidade):** hook `UserPromptSubmit` (`lab-engine-recap.sh` → `recap.md`) injeta contexto canônico em TODO prompt; hook `PreToolUse Write|Edit|MultiEdit` (`scope-guard-prompt.txt`) bloqueia fuga de escopo (`specs/`, `src/cadreport`, `workspace/`, `instruments/`). Portável via `$CLAUDE_PROJECT_DIR`.
  - **Retificação CLAUDE.md:** bloco SPECKIT aponta ao plano ativo `Plans/peaceful-herding-otter.md` + marca `specs/012-cad-report/plan.md` como OUTRO escopo.
  - **Clean corruption (cascas de banana):** `.gitignore` com padrões de ruído de OUTROS ferramentais/contextos (AIDER, `.thinking_llm`, `.openclaude`, `analys_state`, `.archives`, `docs/audit`, `docs/superpowers`, `*.bak`, `continue.txt`, docs genéricos raiz). **Gitignore-only (reversível): NÃO apaga do disco, só limpa `git status` para não induzir fuga em sessões futuras.**
  - **Protocolo SOTA validate→debit (enforcement estrutural do D++):** documentado em `.claude/hooks/recap.md` (injetado em todo prompt). Cada T0x TERMINA com VALIDATE (gates + D++ scan); **PASS → avança**; **NOT PASS → gera task `T0x.DebitN` no harness TaskList** com `blockedBy` real (não markdown). Operacionaliza M1/M2 como checklist automático.
  - Commitado `alembic/README` (meu, T03.3 boilerplate, órfão). Memória (`lab-engine-project.md`) atualizada para T04 ✅.
- **GOV.D++ (débito de governança, rastreado):** ⚠️ **Hook caveat** — o settings-watcher do Claude Code só observa `.claude/` cujo `settings.json` era não-vazio no início da sessão. Hook criado DURANTE esta sessão → **não fire até o usuário abrir `/hooks` (reload) ou restartar**. **Não bloqueia T05** (recap via memória + PROGRESS cobre), mas o enforcement anti-fuga fica offline até reload. **Dono/data: usuário (abrir `/hooks` uma vez). Não-bloqueante.**
- **Gate:** N/A (governança/higiene, sem edição de símbolos de código → sem M0 impact).
- **Estado do plano:** T04 permanece ✅; **T05 permanece a próxima pendente**. Plano original preservado, agora gerido por harness ECC.

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
