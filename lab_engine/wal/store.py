"""Persistência do WAL — repository pattern sobre SQLAlchemy 2.0 (D-T03.1).

Mapeamento HÍBRIDO: cada log WAL = uma row em ``wal_logs`` com

1. **colunas indexadas de navegação** (``project``, ``domain``, ``scale``,
   ``task``, ``parent_log``, ``validation_status``, ``created_at``) — para
   query eficiente (by-parent, by-task, filtros, janela temporal do auditor);
2. **coluna ``payload``** (``JSON``) — wire-format Pydantic **completo**
   (``model_dump(by_alias=True)``), zero drift Pydantic↔ORM.

Round-trip: ``create`` serializa o ``WalLog`` para ``payload`` (dict JSON,
via ``model_dump(mode="json", by_alias=True)``); ``read`` desserializa via
``WalLog.model_validate(row.payload)`` → retorna o ``WalLog`` nativo com
fidelidade total (incl. alias ``"5w1h"``; Pydantic coerge ISO strings →
``datetime`` tz-aware via ``AfterValidator`` de T02).

``payload`` usa ``sqlalchemy.JSON`` (genérico) — mapeia ``JSONB`` em Postgres
e ``TEXT``-com-serialização em SQLite (D-T03.3 DB-agnóstico). Por isso o
valor persistido é o **dict** nativo em **modo JSON**
(``model_dump(mode="json", by_alias=True)``): o ``sqlalchemy.JSON``
serializa via ``json.dumps`` **padrão**, que NÃO conhece ``datetime``/``Enum``
— sem ``mode="json"`` o dict conteria objetos ``datetime`` e o ``INSERT``
quebraria (``TypeError: Object of type datetime is not JSON serializable``).
``mode="json"`` renderiza ``datetime``→ISO ``str`` e ``enum``→value ``str``
**dentro** do dict (continua sendo um dict, não uma string externa),
preservando ``JSONB`` em Postgres sem duplo-encoding (refinamento de
D-T03.1: a intenção "wire-format JSON completo + JSONB em Postgres" exige
``JSON`` type + dict em json-mode, não ``Text`` + string).

O store persiste objetos ``WalLog`` **já validados** pela camada Pydantic
(T02 faz ``extra="forbid"``). O garantismo pré-persistência (``auto_fix`` /
``REJECT`` / ``on_unknown_field``) vive em T04 (``validator.py``) — D-T03.5.
O store é CRUD puro: não revalida schema.

Queries 100% parametrizadas (``select().where(col == value)``) — zero
string-concat em SQL, auditável pelo security-reviewer. O store **não
commita**: o caller gerencia a transação (commit/rollback); ``flush()``
materializa mudanças para queries subsequentes na mesma session.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Index, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from lab_engine.db import Base
from lab_engine.wal.models import WalLog


class LogDuplicateError(Exception):
    """``log_id`` já existe no store (operação ``create``)."""


class LogNotFoundError(Exception):
    """``log_id`` não existe no store (operação ``read``/``update``)."""


class WalLogRow(Base):
    """Row WAL — colunas indexadas (query) + payload JSON (fidelidade total).

    ``parent_log`` é **FK lógica**, não FK rígida: permite ingestão
    fora-de-ordem (child antes do parent); órfãos são detectados pelo auditor
    (T04), não pelo DB. ``created_at`` é **derivado** de
    ``timestamp.created`` — só para filtro/janela temporal; o instante
    canônico vive no ``payload`` JSON (D-T03.1).
    """

    __tablename__ = "wal_logs"

    log_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project: Mapped[str] = mapped_column(String(128), index=True)
    domain: Mapped[str] = mapped_column(String(32), index=True)
    scale: Mapped[str] = mapped_column(String(16), index=True)
    task: Mapped[str] = mapped_column(String(128), index=True)
    parent_log: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(16), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_wal_logs_project_domain_scale", "project", "domain", "scale"),
        Index("ix_wal_logs_parent_task", "parent_log", "task"),
    )


def _to_row(log: WalLog) -> WalLogRow:
    """Deriva uma ``WalLogRow`` de um ``WalLog``: cols indexadas + payload (dict)."""
    return WalLogRow(
        log_id=log.log_id,
        project=log.map_index.project,
        domain=log.map_index.domain.value,
        scale=log.map_index.scale.value,
        task=log.map_index.task,
        parent_log=log.map_index.parent_log,
        validation_status=log.validation.status.value,
        created_at=log.timestamp.created,
        payload=log.model_dump(mode="json", by_alias=True),
    )


class WalRepository:
    """CRUD do WAL sobre uma ``Session`` SQLAlchemy (D-T03.1 híbrido, D-T03.2).

    Transação é do caller: o repository faz ``flush()`` (materializa) mas não
    ``commit()``. Use ``session.commit()`` / ``session.rollback()`` no caller.

    Política append-only (``mudar = criar novo log com parent_log``) é
    enforcement do runtime (T05/T06), **não** do store. O store oferece
    ``update`` para correções administrativas (D-T03.2).
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ----- helpers internos -----

    def _get_row(self, log_id: str) -> WalLogRow | None:
        stmt = select(WalLogRow).where(WalLogRow.log_id == log_id)
        return self._session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def _rows_to_logs(rows: Sequence[WalLogRow]) -> Sequence[WalLog]:
        """Desserializa rows em ``WalLog`` nativos (round-trip do payload JSON)."""
        return [WalLog.model_validate(row.payload) for row in rows]

    # ----- CRUD (6 ops) -----

    def create(self, log: WalLog) -> WalLog:
        """Insere novo log. ``LogDuplicateError`` se ``log_id`` já existe."""
        if self._get_row(log.log_id) is not None:
            raise LogDuplicateError(f"log_id já existe: {log.log_id}")
        self._session.add(_to_row(log))
        self._session.flush()
        return log

    def read(self, log_id: str) -> WalLog | None:
        """Retorna o ``WalLog`` (desserializado do payload) ou ``None``."""
        row = self._get_row(log_id)
        if row is None:
            return None
        return WalLog.model_validate(row.payload)

    def update(self, log_id: str, new_log: WalLog) -> WalLog:
        """Substitui a row ``log_id`` pelos valores de ``new_log``.

        Pré-condição: ``new_log.log_id == log_id`` (``ValueError`` caso
        contrário) — consistência da PK. ``LogNotFoundError`` se ``log_id``
        não existe. Append-only é política de runtime (D-T03.2).
        """
        if new_log.log_id != log_id:
            raise ValueError(
                f"new_log.log_id ({new_log.log_id}) deve igualar log_id ({log_id})"
            )
        row = self._get_row(log_id)
        if row is None:
            raise LogNotFoundError(f"log_id não encontrado: {log_id}")
        row.project = new_log.map_index.project
        row.domain = new_log.map_index.domain.value
        row.scale = new_log.map_index.scale.value
        row.task = new_log.map_index.task
        row.parent_log = new_log.map_index.parent_log
        row.validation_status = new_log.validation.status.value
        row.created_at = new_log.timestamp.created
        row.payload = new_log.model_dump(mode="json", by_alias=True)
        self._session.flush()
        return new_log

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
        """Lista logs com filtros opcionais (todos AND) + paginação."""
        stmt = select(WalLogRow)
        if project is not None:
            stmt = stmt.where(WalLogRow.project == project)
        if domain is not None:
            stmt = stmt.where(WalLogRow.domain == domain)
        if scale is not None:
            stmt = stmt.where(WalLogRow.scale == scale)
        if task is not None:
            stmt = stmt.where(WalLogRow.task == task)
        if validation_status is not None:
            stmt = stmt.where(WalLogRow.validation_status == validation_status)
        if parent_log is not None:
            stmt = stmt.where(WalLogRow.parent_log == parent_log)
        stmt = stmt.limit(limit).offset(offset)
        rows = self._session.execute(stmt).scalars().all()
        return self._rows_to_logs(rows)

    def by_parent(self, parent_log: str) -> Sequence[WalLog]:
        """Filhos diretos de ``parent_log`` (child_logs da árvore WAL)."""
        stmt = select(WalLogRow).where(WalLogRow.parent_log == parent_log)
        rows = self._session.execute(stmt).scalars().all()
        return self._rows_to_logs(rows)

    def by_task(self, task: str) -> Sequence[WalLog]:
        """Todos os logs de uma task (pattern ``TASK-``)."""
        stmt = select(WalLogRow).where(WalLogRow.task == task)
        rows = self._session.execute(stmt).scalars().all()
        return self._rows_to_logs(rows)


__all__ = [
    "LogDuplicateError",
    "LogNotFoundError",
    "WalLogRow",
    "WalRepository",
]
