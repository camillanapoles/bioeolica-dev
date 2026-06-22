"""Auditor WAL — detecta anomalias de rastreabilidade no log persistido (T04).

Implementa o gate D4 (Rastreabilidade) do ``INSTRUCTIONS.md`` (L2001-2006): o
auditor automático que garante "zero logs com status PENDING > 24h" e "nenhum
log ORPHAN ou ABANDONADO não resolvido" (L2002/L2004). Emite um ``AuditReport``
classificando cada anomalia por tipo.

Quatro anomalias cobertas (D-T04.4 — definições operacionais):

- ``PENDING_STALE`` (L2002/L2004, **explícito**) — ``status == PENDING`` E
  ``created_at`` anterior a ``now - pending_stale_after`` (default 24h).
- ``ORPHAN`` (L2002, **explícito**) — ``parent_log`` não-None E inexistente no
  store (cadeia quebrada — child aponta para parent ausente).
- ``ABANDONED`` (L2002, **explícito**) — ``PENDING`` que é **folha** (sem logs
  filhos): análise iniciada, nunca retomada. O contrato cita ORPHAN e ABANDONED
  como distintos sem definir ABANDONED operacionalmente; esta é a definição
  adotada (D-T04.4). Se o contrato precisar formalizar, vira emenda pós-T13.
- ``SCHEMA_BREACH`` (L2001, **implícito**) — payload que falha re-validação
  Pydantic (drift pós-emenda do schema, corrupção, ingestão externa mal-feita).

Decisões de design (fidelidade + separação de concerns):

- **D-T04.6 — auditor query ``WalLogRow`` direto (Session), NÃO ``WalRepository.list``.**
  ``list()`` desserializa via ``_rows_to_logs`` que **levanta** ``ValidationError``
  em payload inválido — quebraria o auditor ao encontrar um breach. O auditor é
  camada de **inspeção/diagnóstico** sobre o modelo físico; query as rows e
  re-valida defensivamente (captura o erro → classifica como SCHEMA_BREACH).

- **D-T04.5 — paginação via ``select().limit().offset()`` (não infla o store).**
  O store (D-T03.5) é CRUD puro; o auditor pagina internamente para ser robusto
  a volume. ``WalLogRow`` é importado do store (mesmo modelo físico).

- **D-T04.7 — normaliza ``created_at`` para tz-aware (assume UTC se naive).**
  SQLite pode descartar ``tzinfo`` no round-trip; sem normalização,
  ``naive < aware`` levanta ``TypeError``. O instante canônico vive no payload
  JSON (D-T03.1); ``created_at`` é só índice de filtro.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from lab_engine.wal.models import WalLog
from lab_engine.wal.store import WalLogRow

# Janela canônica PENDING_STALE (INSTRUCTIONS.md L2002/L2004: "> 24h").
DEFAULT_PENDING_STALE_AFTER = timedelta(hours=24)

# Tamanho de página para iteração do auditor (robusto a volume).
_PAGE_SIZE = 500


class AnomalyType(StrEnum):
    """Tipos de anomalia detectados pelo auditor (D4 — Rastreabilidade)."""

    PENDING_STALE = "PENDING_STALE"
    ORPHAN = "ORPHAN"
    ABANDONED = "ABANDONED"
    SCHEMA_BREACH = "SCHEMA_BREACH"


@dataclass(frozen=True)
class Anomaly:
    """Uma anomalia detectada sobre um log — imutável (rastreabilidade do WAL).

    ``detail`` é humano (para relatório); ``log_id`` liga ao log problemático;
    ``type`` classifica a ação corretiva esperada.
    """

    log_id: str
    type: AnomalyType
    detail: str


@dataclass(frozen=True)
class AuditReport:
    """Relatório imutável de uma auditoria — anomalidades classificadas.

    ``anomalies`` é tuple (imutável); ``counts`` agrega por tipo (todas as 4
    chaves sempre presentes, valor 0 se nenhuma daquele tipo).
    """

    generated_at: datetime
    total_logs: int
    anomalies: tuple[Anomaly, ...] = ()
    pending_stale_after: timedelta = field(default=DEFAULT_PENDING_STALE_AFTER)

    @property
    def counts(self) -> dict[AnomalyType, int]:
        """Contagem por tipo — todas as 4 chaves sempre presentes."""
        tally: dict[AnomalyType, int] = {t: 0 for t in AnomalyType}
        for anomaly in self.anomalies:
            tally[anomaly.type] += 1
        return tally


def _as_aware(dt: datetime) -> datetime:
    """Normaliza um datetime para tz-aware (assume UTC se naive).

    SQLite pode descartar ``tzinfo`` no round-trip; sem isto, ``naive < aware``
    levanta ``TypeError``. O instante canônico vive no payload (D-T03.1);
    ``created_at`` é índice de filtro — normalizar preserva a semântica.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=UTC)
    return dt


class WalAuditor:
    """Auditor do WAL sobre uma ``Session`` — detecta 4 anomalias (D-T04.4).

    ``now`` é injetável (testes determinísticos; default ``datetime.now(UTC)``).
    ``pending_stale_after`` configurável (default 24h — L2002/L2004).
    """

    def __init__(
        self,
        session: Session,
        *,
        now: datetime | None = None,
        pending_stale_after: timedelta = DEFAULT_PENDING_STALE_AFTER,
    ) -> None:
        self._session = session
        self._now = now if now is not None else datetime.now(UTC)
        self._pending_stale_after = pending_stale_after

    def audit(self) -> AuditReport:
        """Varre todos os logs e classifica anomalidades — retorna ``AuditReport``."""
        rows = self._all_rows()
        # Conjuntos de navegação (pré-computados — O(n) ao invés de O(n²)).
        all_log_ids: set[str] = {row.log_id for row in rows}
        # log_ids que SÃO referenciados como parent por algum log (têm filhos).
        parents_with_children: set[str] = {
            row.parent_log for row in rows if row.parent_log is not None
        }
        stale_cutoff = self._now - self._pending_stale_after

        anomalies: list[Anomaly] = []
        for row in rows:
            anomalies.extend(self._check_row(row, all_log_ids, parents_with_children, stale_cutoff))

        return AuditReport(
            generated_at=self._now,
            total_logs=len(rows),
            anomalies=tuple(anomalies),
            pending_stale_after=self._pending_stale_after,
        )

    # ----- checks por row -----

    def _check_row(
        self,
        row: WalLogRow,
        all_log_ids: set[str],
        parents_with_children: set[str],
        stale_cutoff: datetime,
    ) -> list[Anomaly]:
        """Classifica todas as anomalias de uma row — pode haver mais de uma."""
        found: list[Anomaly] = []

        # SCHEMA_BREACH — payload falha re-validação (L2001).
        payload_error = self._payload_validation_error(row)
        if payload_error is not None:
            found.append(
                Anomaly(
                    log_id=row.log_id,
                    type=AnomalyType.SCHEMA_BREACH,
                    detail=f"payload falha validação: {payload_error}",
                )
            )

        # PENDING_STALE — PENDING > 24h (L2002/L2004).
        if (
            row.validation_status == "PENDING"
            and _as_aware(row.created_at) < stale_cutoff
        ):
            age = self._now - _as_aware(row.created_at)
            age_h = age.total_seconds() / 3600
            threshold = self._pending_stale_after
            found.append(
                Anomaly(
                    log_id=row.log_id,
                    type=AnomalyType.PENDING_STALE,
                    detail=f"PENDING há {age_h:.1f}h (> {threshold})",
                )
            )

        # ORPHAN — parent_log inexistente (L2002).
        if row.parent_log is not None and row.parent_log not in all_log_ids:
            found.append(
                Anomaly(
                    log_id=row.log_id,
                    type=AnomalyType.ORPHAN,
                    detail=f"parent_log {row.parent_log} não existe no store",
                )
            )

        # ABANDONED — PENDING sem desdobramento (folha) (L2002, D-T04.4).
        if (
            row.validation_status == "PENDING"
            and row.log_id not in parents_with_children
        ):
            found.append(
                Anomaly(
                    log_id=row.log_id,
                    type=AnomalyType.ABANDONED,
                    detail="PENDING sem logs filhos (análise iniciada, sem desdobramento)",
                )
            )

        return found

    @staticmethod
    def _payload_validation_error(row: WalLogRow) -> str | None:
        """Re-valida o payload; retorna a primeira mensagem de erro ou ``None``."""
        try:
            WalLog.model_validate(row.payload)
        except PydanticValidationError as exc:
            errors: Sequence[Any] = exc.errors()
            if errors:
                first = errors[0]
                loc = ".".join(str(p) for p in first.get("loc", ()))
                return f"{loc}: {first.get('msg', 'inválido')}"
            return "payload inválido"
        return None

    # ----- iteração paginada (D-T04.5) -----

    def _all_rows(self) -> list[WalLogRow]:
        """Carrega todas as rows paginando (robusto a volume)."""
        out: list[WalLogRow] = []
        offset = 0
        while True:
            stmt = select(WalLogRow).limit(_PAGE_SIZE).offset(offset)
            batch = list(self._session.execute(stmt).scalars().all())
            if not batch:
                break
            out.extend(batch)
            if len(batch) < _PAGE_SIZE:
                break
            offset += _PAGE_SIZE
        return out


__all__ = [
    "Anomaly",
    "AnomalyType",
    "AuditReport",
    "DEFAULT_PENDING_STALE_AFTER",
    "WalAuditor",
]
