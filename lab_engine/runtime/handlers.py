"""Handlers dos 4 commands (T05.3) — FASE 2 (Runtime event-driven).

Cada handler é um ``CommandHandler`` que valida e persiste ``WalLog``(s) via
``validator.validate`` -> ``EventStore.append`` (cadeia T04->T03->T02). O
handler **impõe** o ``map_index.task`` canônico do seu command_type (D-T05.3.1
— garante que ``CMD-NEW-PROJECT`` sempre produz ``TASK-NEW-PROJECT``; não
forjável pelo ``payload``).

``publish_context`` aplica 4 quality gates fiéis ao ``propagation-proto.sh``
emergido (D-T05.3.2): GATE 1 Schema (= ``validator`` T04) · GATE 2 Sanity
(formato ``LOG-UUID`` do ``parent_log`` — consistência referencial não coberta
pelo schema) · GATE 3 Freshness (``created`` < 24h, mesmo critério do auditor
T04 ``PENDING_STALE``) · GATE 4 Revisor Hostil (**stub PASS** — real em T08
com agentes). Falha em qualquer gate -> ``failure`` **sem persistir**
(D-T05.3.3 — não polui o WAL).

Handlers são construídos por ``build_handlers(store)`` com ``EventStore``
injetado (D-T05.3.4 — separation: handler sabe runtime, caller sabe domínio).
"""

from __future__ import annotations

import copy
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from lab_engine.runtime.bus import Command, CommandHandler, CommandResult
from lab_engine.runtime.events import EventStore
from lab_engine.wal.models import WalLog
from lab_engine.wal.validator import validate

# GATE 3 — contexto publicado não pode ser stale (24h, mesmo critério do
# auditor T04 PENDING_STALE — D-T04.4).
_FRESHNESS_STALE_AFTER = timedelta(hours=24)

# GATE 2 — parent_log (str|None sem pattern no schema) deve, se presente,
# casar LOG-UUID (consistência referencial de FORMATO; a existência é do
# auditor T04 ORPHAN). Mesmo pattern canônico de log_id (INSTRUCTIONS L2206).
_PARENT_LOG_PATTERN = re.compile(
    r"^LOG-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$"
)

#: command_type -> task canônico imposto pelo handler (D-T05.3.1).
_COMMAND_TASK_MAP: dict[str, str] = {
    "CMD-NEW-PROJECT": "TASK-NEW-PROJECT",
    "CMD-PUBLISH-CONTEXT": "TASK-PUBLISH-CONTEXT",
    "CMD-ALLOCATE-TASK": "TASK-ALLOCATE-TASK",
    "CMD-DERIVE-TEAM": "TASK-DERIVE-TEAM",
}


class GateError(Exception):
    """Um quality gate falhou — ``gate`` indica qual, ``reason`` o motivo."""

    def __init__(self, gate: str, reason: str) -> None:
        self.gate = gate
        self.reason = reason
        super().__init__(f"{gate}: {reason}")


def _coerce_wal(command: Command, command_type: str) -> dict[str, Any]:
    """Extrai ``payload['wal']``, impõe task canônico, deepcopy (não muta payload).

    D-T05.3.1 — o task é SEMPRE o canônico do command_type, qualquer que seja o
    valor trazido pelo payload (não forjável).
    """
    wal = command.payload.get("wal")
    if not isinstance(wal, dict):
        raise GateError("GATE 0", "payload.wal ausente ou não é um dict")
    wal = copy.deepcopy(wal)
    wal.setdefault("map_index", {})["task"] = _COMMAND_TASK_MAP[command_type]
    return wal


def _gate_sanity(log: WalLog) -> None:
    """GATE 2 — consistência estrutural além do schema (formato do parent_log)."""
    parent = log.map_index.parent_log
    if parent is not None and not _PARENT_LOG_PATTERN.match(parent):
        raise GateError("GATE 2", f"parent_log fora do formato LOG-UUID: {parent!r}")


def _gate_freshness(log: WalLog, *, now: datetime) -> None:
    """GATE 3 — timestamp.created recente (now - created < 24h)."""
    age = now - log.timestamp.created
    if age > _FRESHNESS_STALE_AFTER:
        raise GateError("GATE 3", f"contexto stale (idade={age})")


def _gate_revisor_hostil(log: WalLog) -> None:
    """GATE 4 — revisor hostil (STUB PASS; revisão adversarial real em T08)."""
    # TODO(T08): revisão adversarial via agente. Por ora aprova — não bloqueia
    # o pipeline de publicação (o gate existe como ponto de extensão fiel ao
    # propagation-proto.sh emergido). D-T05.3.2.
    _ = log  # consome o arg (ponto de extensão futuro)


def _validate_and_append(
    store: EventStore, command: Command, wal: dict[str, Any]
) -> CommandResult:
    """GATE 1 (schema via validator T04) -> append. Usado pelos handlers simples."""
    result = validate(wal)
    if not result.valid:
        return CommandResult(
            command_id=command.command_id,
            error=f"GATE 1 schema: {result.errors}",
        )
    if result.log is None:  # pragma: no cover — invariante validator (valid -> log)
        return CommandResult(
            command_id=command.command_id, error="GATE 1: log ausente após validação"
        )
    log = store.append(result.log)
    return CommandResult(command_id=command.command_id, success=True, events=[log])


def _make_simple_handler(store: EventStore, command_type: str) -> CommandHandler:
    """Handler de command simples: valida (task imposto) -> append. Sem gates 2-4."""

    def handler(command: Command) -> CommandResult:
        try:
            wal = _coerce_wal(command, command_type)
        except GateError as e:
            return CommandResult(command_id=command.command_id, error=str(e))
        return _validate_and_append(store, command, wal)

    return handler


def _make_publish_handler(
    store: EventStore, *, now: datetime | None = None
) -> CommandHandler:
    """Handler de publish_context: 4 gates (schema/sanity/freshness/revisor) -> append."""
    now_utc = now if now is not None else datetime.now(UTC)

    def handler(command: Command) -> CommandResult:
        try:
            wal = _coerce_wal(command, "CMD-PUBLISH-CONTEXT")
        except GateError as e:
            return CommandResult(command_id=command.command_id, error=str(e))
        # GATE 1 — Schema (= validator T04).
        result = validate(wal)
        if not result.valid:
            return CommandResult(
                command_id=command.command_id,
                error=f"GATE 1 schema: {result.errors}",
            )
        log = result.log
        if log is None:  # pragma: no cover — invariante validator (valid -> log)
            return CommandResult(
                command_id=command.command_id, error="GATE 1: log ausente após validação"
            )
        # GATE 2/3/4 sobre o log validado.
        try:
            _gate_sanity(log)
            _gate_freshness(log, now=now_utc)
            _gate_revisor_hostil(log)
        except GateError as e:
            return CommandResult(command_id=command.command_id, error=str(e))
        persisted = store.append(log)
        return CommandResult(
            command_id=command.command_id, success=True, events=[persisted]
        )

    return handler


def build_handlers(
    store: EventStore, *, now: datetime | None = None
) -> dict[str, CommandHandler]:
    """Cria os 4 handlers com ``EventStore`` injetado -> mapa command_type->handler.

    ``now`` (opcional) fixa o instante do GATE 3 freshness — útil para testes
    determinísticos; default = agora-UTC.
    """
    return {
        "CMD-NEW-PROJECT": _make_simple_handler(store, "CMD-NEW-PROJECT"),
        "CMD-ALLOCATE-TASK": _make_simple_handler(store, "CMD-ALLOCATE-TASK"),
        "CMD-DERIVE-TEAM": _make_simple_handler(store, "CMD-DERIVE-TEAM"),
        "CMD-PUBLISH-CONTEXT": _make_publish_handler(store, now=now),
    }


__all__ = ["GateError", "build_handlers"]
