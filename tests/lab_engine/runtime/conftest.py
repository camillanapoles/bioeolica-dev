"""Fixtures de teste para o runtime (T05.1).

Reusa o ``_CANONICAL_LOG`` e ``_fresh_log_id`` do conftest do WAL via
``importlib`` (pytest não herda conftests entre diretórios irmãos sem
``__init__.py``; o repo usa rootdir mode). As fixtures de infra
(``engine``/``session``/``repo``) são redefinidas aqui — idênticas às do WAL
(SQLite in-memory, StaticPool, isolado por teste) — para garantir
independência do diretório de teste irmão e zero acoplamento frágil.
"""

from __future__ import annotations

import copy
import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from lab_engine.db import Base
from lab_engine.settings import get_settings
from lab_engine.wal.models import WalLog
from lab_engine.wal.store import WalRepository

# Carrega o conftest do WAL (dir irmão) como módulo para reusar o canonical log
# e o gerador de log_id — evita duplicar o dict canônico (DRY) sem introduzir
# dependência de sys.path/pacote (rootdir mode, sem __init__.py).
_wal_conftest_path = Path(__file__).resolve().parent.parent / "wal" / "conftest.py"
_spec = importlib.util.spec_from_file_location(
    "_runtime_reused_wal_conftest", _wal_conftest_path
)
assert _spec is not None and _spec.loader is not None
_wal_conftest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wal_conftest)
_CANONICAL_LOG: dict[str, Any] = _wal_conftest._CANONICAL_LOG
_fresh_log_id: Callable[[], str] = _wal_conftest._fresh_log_id


@pytest.fixture
def engine() -> Any:  # type: ignore[no-untyped-def]
    """Engine SQLite in-memory (StaticPool) + schema WAL — DB zerado por teste."""
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
def session(engine: Any) -> Session:  # type: ignore[no-untyped-def]
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
    """Limpa o cache de ``get_settings`` antes de cada teste (defensivo)."""
    get_settings.cache_clear()


@pytest.fixture
def make_log() -> Callable[..., WalLog]:
    """Factory: ``WalLog`` canônico válido com overrides opcionais.

    Mesmo contrato do ``make_log`` do WAL: ``log_id`` default é único por
    chamada (uuid4 HEX) — permite criar vários logs sem colisão de PK.
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
