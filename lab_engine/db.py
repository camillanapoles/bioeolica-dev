"""Infra de banco da LAB-ENGINE — DB-agnóstico via SQLAlchemy 2.0 (D-T03.3).

Provê:
    - ``Base``: ``DeclarativeBase`` para o ORM (T03.2 define ``WalLogRow``).
    - ``make_engine(url=None)``: factory de ``Engine`` a partir das settings.
      Aplica PRAGMAS de durabilidade/integridade **condicionalmente** (só SQLite).
    - ``make_session_factory(engine)`` e ``get_session(engine)``: sessionmaker +
      generator FastAPI-ready.

DB-agnosticismo: o mesmo código de domínio roda em SQLite (dev/test) e Postgres
(prod). A coluna JSON do WAL (``payload``) usa ``sqlalchemy.JSON`` genérico, que
mapeia ``JSONB`` em Postgres automaticamente. PRAGMAS são no-op fora de SQLite.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from lab_engine.settings import get_settings


class Base(DeclarativeBase):
    """Base declarativa do ORM. ``WalLogRow`` (T03.2) herda desta."""


def make_engine(url: str | None = None) -> Engine:
    """Cria um ``Engine`` a partir das settings (ou URL explícita).

    Para SQLite, instala PRAGMAS (``journal_mode=WAL`` para durabilidade,
    ``foreign_keys=ON`` para integridade referencial, ``busy_timeout`` para
    contenção) e garante que o diretório-pai do arquivo exista. Para outros
    dialects (Postgres etc.), é no-op — fidelidade DB-agnóstica (D-T03.3).
    """
    db_url = url if url is not None else get_settings().wal_db_url
    engine = create_engine(db_url, future=True)

    if engine.dialect.name == "sqlite":
        _ensure_sqlite_parent_dir(db_url)
        _install_sqlite_pragmas(engine)

    return engine


def _install_sqlite_pragmas(engine: Engine) -> None:
    """Registra PRAGMAS de durabilidade/integridade em cada conexão SQLite.

    ``WAL`` (Write-Ahead Logging): durabilidade superior ao modo default;
    ``foreign_keys``: enforce de FK (defensivo, embora ``parent_log`` seja FK
    lógica, não rígida — D-T03.1); ``busy_timeout``: evita ``database is locked``.
    """

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
        finally:
            cursor.close()


def _ensure_sqlite_parent_dir(db_url: str) -> None:
    """Garante que o diretório-pai de um DB SQLite file-based exista.

    SQLite cria o arquivo mas não o diretório. No-op para ``:memory:`` / ``sqlite://``.
    """
    if db_url == "sqlite://" or ":memory:" in db_url:
        return
    path_part = db_url.replace("sqlite:///", "", 1)
    parent = Path(path_part).parent
    # Cria só se há um diretório-pai significativo (não cwd "." ou vazio).
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Cria uma ``sessionmaker`` ligada ao engine.

    ``expire_on_commit=False``: após commit, objetos permanecem acessíveis —
    essencial para o repository retornar ``WalLog`` desserializado do payload.
    """
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False, future=True)


def get_session(engine: Engine | None = None) -> Iterator[Session]:
    """Generator de Session (FastAPI ``Depends``-ready).

    Fecha a session ao finalizar o bloco. O engine default vem de ``make_engine()``.
    """
    eng = engine if engine is not None else make_engine()
    factory = make_session_factory(eng)
    session = factory()
    try:
        yield session
    finally:
        session.close()


__all__ = [
    "Base",
    "get_session",
    "make_engine",
    "make_session_factory",
]
