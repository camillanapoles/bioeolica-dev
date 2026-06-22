# Sub-plano T03 — Persistência + CRUD WAL (SQLAlchemy 2.0 + Alembic)

> **Sub-plano da atividade T03** do plano mestre `Plans/peaceful-herding-otter.md`.
> T03 é **bisavra de arquitetura** — a decisão de persistência aqui governa T03→T13.
> Por isso é splitada em **T03.1–T03.5**; a última (T03.5) **retorna ao mestre** (marca T03 ✅).
>
> Cada sub-task segue o **mandato T0x.D / T0x.D++** (anti-bola-de-neve) e o **ritual de
> transição** entre sub-tasks (revisa por test → confirma sucesso antecessor → prossegue).

---

## Decisões bisavras (espelham o mestre)

| ID | Decisão |
|----|---------|
| **D-T03.1** | Mapeamento **HÍBRIDO**: tabela `wal_logs` = colunas indexadas de navegação **+** `payload` JSON (wire-format `model_dump_json(by_alias=True)`). Round-trip via `WalLog.model_validate_json(row.payload)`. |
| **D-T03.2** | `update(log_id, new_log)` substitui a row ( exige `new_log.log_id == log_id`). **Append-only é política de runtime** (T05/T06), não do store. |
| **D-T03.3** | **DB-agnóstico** via SQLAlchemy: `wal_db_url` configurável (`LAB_ENGINE_WAL_DB_URL`), default SQLite. PRAGMAS SQLite-condicional. Coluna JSON genérica (`JSONB` em Postgres). |
| **D-T03.4** | Source-of-truth = **BD relacional durável** (SQLite/Postgres). **Redis é complementar** (T05/T07/T08), NÃO substituto. |
| **D-T03.5** | Store recebe `WalLog` **já validado** (Pydantic T02). `auto_fix`/REJECT ficam em T04 (`validator.py`). |

---

## Schema SQL — tabela `wal_logs` (D-T03.1 híbrido)

Colunas indexadas de navegação + `payload` JSON. Tipos SQLAlchemy 2.0 genéricos
(mapeiam corretamente SQLite e Postgres via dialect).

```python
# lab_engine/wal/store.py
from sqlalchemy import JSON, Index, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from lab_engine.db import Base

class WalLogRow(Base):
    """Row WAL — colunas indexadas (query) + payload JSON (fidelidade total)."""

    __tablename__ = "wal_logs"

    log_id:             Mapped[str]      = mapped_column(String(64),  primary_key=True)  # LOG-uuid-v4
    project:            Mapped[str]      = mapped_column(String(128), index=True)        # PRODUTO-...
    domain:             Mapped[str]      = mapped_column(String(32),  index=True)        # 10 domínios (enum)
    scale:              Mapped[str]      = mapped_column(String(16),  index=True)        # macro/meso/micro
    task:               Mapped[str]      = mapped_column(String(128), index=True)        # TASK-...
    parent_log:         Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    validation_status:  Mapped[str]      = mapped_column(String(16),  index=True)        # PASS/FAIL/PENDING
    created_at:         Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), index=True)  # de timestamp.created
    payload:            Mapped[str]      = mapped_column(JSON, nullable=False)          # wire-format completo

    __table_args__ = (
        Index("ix_wal_logs_project_domain_scale", "project", "domain", "scale"),
        Index("ix_wal_logs_parent_task", "parent_log", "task"),
    )
```

**Observações de fidelidade:**
- `created_at` é **derivado** de `payload["timestamp"]["created"]` — duplicação intencional para query eficiente por janela temporal (auditor T04 detecta PENDING>24h).
- `parent_log` é **FK lógica**, não FK rígida — permite criar child antes do parent (ordem de ingestão) e órfãos são detectados pelo auditor (T04), não pelo DB.
- `payload` com `JSON` (genérico): `TEXT` em SQLite, `JSONB` em Postgres. Contém o wire-format Pydantic completo — **zero drift**.

---

## Assinaturas — `WalRepository` (6 ops CRUD, D-T03.2)

```python
# lab_engine/wal/store.py
from collections.abc import Sequence
from sqlalchemy.orm import Session
from lab_engine.wal.models import WalLog

class WalRepository:
    """CRUD do WAL — persiste objetos WalLog já validados (D-T03.5).

    Queries 100% parametrizadas (SQLAlchemy 2.0 select().where(col == value)).
    Zero string-concat em SQL — gate security-reviewer.
    """

    def __init__(self, session: Session) -> None: ...

    def create(self, log: WalLog) -> WalLog:
        """Insere novo log. LogDuplicateError se log_id já existe."""

    def read(self, log_id: str) -> WalLog | None:
        """Retorna o WalLog ou None (desserializa do payload JSON)."""

    def update(self, log_id: str, new_log: WalLog) -> WalLog:
        """Substitui a row `log_id` pelos valores de `new_log`.
        Pré-condição: new_log.log_id == log_id (ValueError caso contrário).
        LogNotFoundError se `log_id` não existe. Política append-only é do runtime (D-T03.2)."""

    def list(
        self,
        *,
        project: str | None = None,
        domain: str | None = None,
        scale: str | None = None,
        task: str | None = None,
        validation_status: str | None = None,
        parent_log: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[WalLog]:
        """Lista com filtros opcionais + paginação (limit/offset)."""

    def by_parent(self, parent_log: str) -> Sequence[WalLog]:
        """Filhos diretos de parent_log (child_logs da árvore WAL)."""

    def by_task(self, task: str) -> Sequence[WalLog]:
        """Todos os logs de uma task (pattern TASK-)."""
```

**Round-trip (create/read):**
```
create: WalLog → _to_row(log): extrai cols indexadas + log.model_dump_json(by_alias=True) → payload
read:   row → WalLog.model_validate_json(row.payload) → WalLog nativo (fidelidade total)
```

**Helper interno `_to_row(log: WalLog) -> WalLogRow`:** deriva colunas indexadas
(`log.map_index.project`, `.domain.value`, `.scale.value`, `.task`, `.parent_log`,
`log.validation.status.value`, `log.timestamp.created`) + serializa payload.

---

## Estrutura de arquivos (T03 global)

```
lab_engine/
├── __init__.py
├── settings.py              # T03.1 — BaseSettings (wal_db_url, zero-hardcoded)
├── db.py                    # T03.1 — Base(DeclarativeBase), make_engine(), get_session()
└── wal/
    ├── __init__.py
    ├── models.py            # (T02 ✅ — consumir, NÃO editar)
    └── store.py             # T03.2 — WalLogRow + WalRepository (6 ops)
alembic/
├── env.py                   # T03.3 — engine das settings + target_metadata
├── script.py.mako
└── versions/
    └── 0001_create_wal_logs.py   # T03.3 — migration inicial
tests/lab_engine/wal/
├── conftest.py              # T03.4 — fixtures engine/session (in-memory StaticPool)
└── test_store.py            # T03.4 — CRUD 6 ops + commit/rollback + round-trip + injection
```

---

## Sub-tasks (cada uma com gate próprio + ritual T0x.D/T0x.D++)

### T03.1 — Settings + infra DB (zero-hardcoded)
- **Faixa:**
  - Criar este sub-plano (`Plans/T03-persistencia-wal.md`) ✅ (este arquivo).
  - `lab_engine/settings.py`: `Settings(BaseSettings)` com `wal_db_url: str` (env `LAB_ENGINE_WAL_DB_URL`, default `sqlite:///data/lab_engine.db`), `SettingsConfigDict(env_prefix="LAB_ENGINE_")`, cache via `get_settings()`.
  - `lab_engine/db.py`: `Base(DeclarativeBase)`; `make_engine(url=None)` aplica PRAGMAS SQLite-condicional (`journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`) via `event.listens_for(engine, "connect")`; cria dir-parent de DB file-based SQLite (higiene, não hardcoded); `sessionmaker(bind=engine)`; `get_session()` generator (FastAPI-ready).
  - `pyproject.toml`: adicionar deps `alembic`, `pydantic-settings` (declarados em `[project] dependencies`).
  - Instalar deps no `.venv` via `uv pip install --python .venv/bin/python alembic pydantic-settings`.
- **DoD:** `get_settings().wal_db_url` configurável via env; `make_engine()` aplica PRAGMAS em SQLite e é no-op em Postgres; `Base` importável; deps declaradas.
- **Gate:** verify-security (zero-hardcoded) + python-reviewer.
- **Métrica:** 0 paths/valores hardcoded (env-driven); mypy `--strict` verde nos 2 módulos.

### T03.2 — ORM `wal_logs` + Repository CRUD (6 ops, híbrido)
- **Faixa:** `lab_engine/wal/store.py` — `WalLogRow(Base)` (schema acima) + `WalRepository` (6 ops) + `_to_row()` helper + exceções `LogDuplicateError`/`LogNotFoundError`.
- **DoD:** 6 ops funcionais (create/read/update/list/by_parent/by_task); queries 100% parametrizadas; round-trip `WalLog ↔ row` sem perda.
- **Gate:** tdd-guide + security-reviewer (injection, 0 string-concat).
- **Métrica:** 0 string-concat em queries; round-trip preserva todos os campos (incl. alias `5w1h`).

### T03.3 — Alembic migration inicial
- **Faixa:** `alembic init alembic` (ou estrutura manual); `alembic.ini` + `alembic/env.py` (engine das settings, `target_metadata = Base.metadata`); migration `0001_create_wal_logs` (tabela + índices + ix compostos).
- **DoD:** `alembic upgrade head` cria a tabela; `alembic downgrade base` remove tudo. **Aplicável E reversível**.
- **Gate:** verify-change.
- **Métrica:** upgrade/downgrade testados em SQLite; schema da migration == `WalLogRow.__table__`.

### T03.4 — Testes + gates verdes
- **Faixa:** `tests/lab_engine/wal/conftest.py` (fixtures `engine`/`session` SQLite in-memory `StaticPool` + `repo`); `test_store.py` (CRUD 6 ops, commit/rollback explícitos, round-trip `WalLog`, by-parent/by-task, **injection negativo** com `log_id` malicioso contendo `'--`/`; DROP`/`' OR 1=1`).
- **DoD:** cobertura ≥80% em `store.py`; ruff/mypy/bandit/pytest verdes; injection não persiste/perturba queries.
- **Gate:** tdd-guide + verify-quality.
- **Métrica:** ≥80% cobertura `lab_engine/wal/store.py`; 0 gates vermelhos.

### T03.5 — Commit + sync + retorno ao mestre (M4)
- **Faixa:** commit + push `origin/main`; atualizar `Plans/LAB-ENGINE-PROGRESS.md` (T03.D/T03.D++); marcar **T03 ✅** no mestre → **retorna ao fluxo T04**.
- **DoD:** `git status` limpo; `main` sincronizado com remote; T03.D++ vazio (ou Emenda rastreada).
- **Gate:** M4 (commit + sync) + verify-security final.
- **Métrica:** push ✅; PROGRESS atualizado; TaskUpdate T03 → completed.

---

## Fluxo de dados (visão geral)

```
[Agente/Runtime T05+] 
   │ cria WalLog (Pydantic, já validado T02)
   ▼
[Validator T04] ── auto_fix / REJECT ──▶ (rejeita antes de persistir)
   │ WalLog válido
   ▼
[WalRepository.create] ──▶ _to_row ──▶ INSERT wal_logs (cols + payload JSON)
   │                                              │
   │   [read/by_parent/by_task/list]              ▼
   ◀────────────── SELECT ───── wal_logs ──── WalLog.model_validate_json(payload)
```

---

## Anti-padrões proibidos (específicos de T03)

- ❌ String-concat em SQL (`f"SELECT ... WHERE id = '{log_id}'"`) — usar `select().where(WalLogRow.log_id == log_id)`.
- ❌ Hardcoded DB URL (`sqlite:///foo.db` literal no código) — usar `get_settings().wal_db_url`.
- ❌ Revalidar schema no store (D-T03.5) — store é CRUD puro.
- ❌ FK rígida em `parent_log` — quebra ingestão fora-de-ordem; auditor (T04) cuida de órfãos.
- ❌ Marcar T03.x ✅ sem rodar o gate da sub-task + ritual de transição.
