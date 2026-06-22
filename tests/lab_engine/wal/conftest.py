"""Fixtures de teste para o WAL store (T03.4).

Estratégia de isolamento: SQLite **in-memory** com ``StaticPool`` — assim todas
as sessions de um mesmo teste compartilham a **mesma** conexão (e portanto o
mesmo DB in-memory), o que é essencial para (a) o modo batch do Alembic/SQLite
e (b) testes cross-session (commit numa session, leitura em outra).

O engine é **function-scoped**: cada teste recebe um DB zerado
(``create_all`` no setup, ``drop_all`` no teardown) — isolamento total,
0 vazio residual entre testes. SQLite in-memory torna esse custo negligenciável.

As tabelas são criadas via ``Base.metadata.create_all`` (NÃO via migration
Alembic) — o foco de T03.4 é o repository CRUD; a migration é exercida à parte
(smoke round-trip de T03.3). Esse desacoplamento é o padrão SOTA para testes de
repository.

``get_settings.cache_clear`` (autouse): ``Settings`` usa ``@lru_cache``; limpar
o cache por teste previne que um ``LAB_ENGINE_WAL_DB_URL`` setado por
``monkeypatch`` vaze para testes seguintes. Defensivo — os testes atuais não
setam env nem usam ``make_engine``, mas o contrato do fixture deve ser
"dado limpo por teste".
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from lab_engine.db import Base
from lab_engine.settings import get_settings
from lab_engine.wal.models import WalLog
from lab_engine.wal.store import WalRepository

# --------------------------------------------------------------------------- #
# Engine + Session (SQLite in-memory, StaticPool, isolado por teste)
# --------------------------------------------------------------------------- #


@pytest.fixture
def engine():  # type: ignore[no-untyped-def]
    """Engine SQLite in-memory compartilhado (StaticPool) + schema WAL criado."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def session(engine):  # type: ignore[no-untyped-def]
    """Session fresca; rollback no teardown limpa qualquer pendência."""
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    sess: Session = factory()
    yield sess
    sess.rollback()
    sess.close()


@pytest.fixture
def repo(session: Session) -> WalRepository:
    """Repository ligado à session do teste."""
    return WalRepository(session)


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Limpa o cache de ``get_settings`` antes de cada teste (defensivo).

    ``Settings`` é ``@lru_cache`` — garante que nenhum env setado por
    ``monkeypatch`` vaze entre testes.
    """
    get_settings.cache_clear()


# --------------------------------------------------------------------------- #
# Factory de WalLog canônico (override de campos aninhados)
# --------------------------------------------------------------------------- #

# Log canônico válido (espelha o builder de T02 — schema INSTRUCTIONS.md L2198-2320).
# Mantido aqui (e não importado de test_models) para desacoplar test_store de
# test_models: o builder é estável (espelha o schema canônico) e duplicá-lo
# evita acoplamento frágil entre módulos de teste.
_CANONICAL_LOG: dict[str, Any] = {
    "log_id": "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE",
    "timestamp": {
        "created": "2026-06-22T12:00:00Z",
        "started": "2026-06-22T12:00:00Z",
        "finished": "2026-06-22T12:05:00Z",
    },
    "5w1h": {
        "what": "Análise estrutural da torre via FEM",
        "why": "Verificar integridade mecânica sob carga de vento",
        "who": "agent-mecanica",
        "when": "2026-06-22T12:00:00Z a 12:05:00Z",
        "where": {
            "file": "src/cad/tower.py",
            "line": 42,
            "version": "abc1234",
            "branch": "main",
        },
        "how": {
            "method": "FEM linear",
            "tool": "calculix",
            "tool_version": "2.21",
            "parameters": {"mesh_size": 0.01},
            "input_files": ["data/tower.step"],
            "output_files": ["out/stress.csv"],
        },
    },
    "map_index": {
        "project": "PRODUTO-PMSG-100kW-001",
        "domain": "mecanica",
        "scale": "macro",
        "task": "TASK-0001",
        "parent_log": None,
        "child_logs": [],
    },
    "validation": {
        "status": "PASS",
        "method": "comparação analítica",
        "reference": "ASME BPVC VIII",
        "error_metrics": {
            "precision": 1.5,
            "convergence": 99.0,
            "fidelity": 0.95,
        },
    },
}


def _fresh_log_id() -> str:
    """log_id canônico único a cada chamada (uuid4 em HEX maiúsculo).

    Necessário para criar múltiplos logs num teste sem colisão de PK; sempre
    casa o pattern ``LOG-[A-F0-9]{8}-[A-F0-9]{4}-...``.
    """
    from uuid import uuid4

    h = uuid4().hex.upper()
    return f"LOG-{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


@pytest.fixture
def canonical_log() -> dict[str, Any]:
    """Dict cru (wire-format) do log canônico — cópia profunda mutável por teste.

    Para os testes do **validador** (T04), que precisam mutar o input (remover
    campos, quebrar patterns) antes de chamar ``validate``. Cada teste obtém sua
    própria cópia — mutações não vazam entre testes. Espelha o ``_CANONICAL_LOG``
    abaixo (mesma estrutura do builder ``make_log``).
    """
    return copy.deepcopy(_CANONICAL_LOG)


@pytest.fixture
def make_log() -> Callable[..., WalLog]:
    """Factory: retorna um ``WalLog`` canônico válido com overrides opcionais.

    Overrides suportados (todos opcionais, aplicados ao dict antes de validar):
        log_id, parent_log, task, project, domain, scale, status, created

    ``log_id`` default é único por chamada (uuid4 HEX) — permite criar vários
    logs sem colisão de PK. Override explícito de ``log_id`` para cenários que
    exigem log_id previsível (e.g. read/update por ID).
    """

    def _factory(  # noqa: PLR0913 — overrides explícitos é mais legível que **kwargs
        *,
        log_id: str | None = None,
        parent_log: str | None = None,
        task: str = "TASK-0001",
        project: str = "PRODUTO-PMSG-100kW-001",
        domain: str = "mecanica",
        scale: str = "macro",
        status: str = "PASS",
        created: str = "2026-06-22T12:00:00Z",
    ) -> WalLog:
        d = copy.deepcopy(_CANONICAL_LOG)
        d["log_id"] = log_id if log_id is not None else _fresh_log_id()
        d["timestamp"]["created"] = created
        d["map_index"]["project"] = project
        d["map_index"]["domain"] = domain
        d["map_index"]["scale"] = scale
        d["map_index"]["task"] = task
        d["map_index"]["parent_log"] = parent_log
        d["validation"]["status"] = status
        return WalLog.model_validate(d)

    return _factory
