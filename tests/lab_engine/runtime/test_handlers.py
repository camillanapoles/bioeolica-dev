"""Testes dos handlers T05.3 — M3 (pytest equivalente).

Cobre os 4 handlers (``new_project``, ``publish_context`` [4 gates],
``allocate_task``, ``derive_team``) via ``build_handlers(store)`` despachados
por um ``CommandBus`` real. Cada handler valida (validator T04) e persiste
``WalLog`` via ``EventStore`` (cadeia T04->T03->T02); o handler IMÕE o
``map_index.task`` canônico do command_type (D-T05.3.1 — não forjável).

``publish_context`` aplica 4 gates (D-T05.3.2): GATE 1 Schema (= validator),
GATE 2 Sanity (formato LOG-UUID do parent_log), GATE 3 Freshness (<24h),
GATE 4 Revisor Hostil (stub PASS). Falha em qualquer gate -> ``failure``
**sem persistir** (D-T05.3.3 — verificado negando a persistência).

Padrão AAA. Cobertura alvo ≥80% em ``handlers``. Fixtures ``repo``/``make_log``
vêm do ``conftest`` do runtime (SQLite in-memory isolado por teste).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from lab_engine.runtime.bus import Command, CommandBus, CommandResult
from lab_engine.runtime.events import EventStore
from lab_engine.runtime.handlers import build_handlers
from lab_engine.wal.models import WalLog
from lab_engine.wal.store import WalRepository

# now fixo alinhado ao ``created`` default do make_log (2026-06-22T12:00:00Z)
# -> GATE 3 freshness passa por default; testes de stale usam created anterior.
_NOW = datetime(2026, 6, 22, 12, 0, 0, tzinfo=UTC)
_PROJECT = "PRODUTO-PMSG-100kW-001"


@pytest.fixture
def bus_and_store(
    repo: WalRepository,
) -> tuple[CommandBus, EventStore]:
    """CommandBus com os 4 handlers registrados + EventStore (now fixo p/ GATE 3)."""
    store = EventStore(repo)
    bus = CommandBus()
    for command_type, handler in build_handlers(store, now=_NOW).items():
        bus.register(command_type, handler)
    return bus, store


def _wal_dict(make_log: Callable[..., WalLog], **overrides: object) -> dict[str, object]:
    """Wire-format dict (by_alias) de um WalLog canônico + overrides."""
    return make_log(**overrides).model_dump(by_alias=True)


def _dispatch(
    bus: CommandBus, command_type: str, wal_dict: dict[str, object]
) -> CommandResult:
    return bus.dispatch(
        Command(command_type=command_type, payload={"wal": wal_dict})
    )


# --------------------------------------------------------------------------- #
# build_handlers — registro dos 4 command_types
# --------------------------------------------------------------------------- #


def test_build_handlers_returns_four_command_types(repo: WalRepository) -> None:
    # Act
    handlers = build_handlers(EventStore(repo))
    # Assert — exatamente os 4 commands do contrato T05
    assert set(handlers) == {
        "CMD-NEW-PROJECT",
        "CMD-ALLOCATE-TASK",
        "CMD-DERIVE-TEAM",
        "CMD-PUBLISH-CONTEXT",
    }


# --------------------------------------------------------------------------- #
# Handlers simples — validam (task imposto) -> append. Sem gates 2-4.
# --------------------------------------------------------------------------- #


def test_new_project_success_persists_and_imposes_task(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange — payload tenta forjar task diferente; handler deve impor o canônico
    wal = _wal_dict(make_log, task="TASK-HACK")
    bus, store = bus_and_store
    # Act
    result = _dispatch(bus, "CMD-NEW-PROJECT", wal)
    # Assert — sucesso, 1 evento, task imposto, persistido no WAL
    assert result.success is True
    assert len(result.events) == 1
    [log] = list(store.stream(_PROJECT))
    assert log.map_index.task == "TASK-NEW-PROJECT"


def test_allocate_task_success(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    result = _dispatch(bus_and_store[0], "CMD-ALLOCATE-TASK", _wal_dict(make_log))
    assert result.success is True
    assert result.events[0].map_index.task == "TASK-ALLOCATE-TASK"


def test_derive_team_success(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    result = _dispatch(bus_and_store[0], "CMD-DERIVE-TEAM", _wal_dict(make_log))
    assert result.success is True
    assert result.events[0].map_index.task == "TASK-DERIVE-TEAM"


def test_new_project_missing_wal_returns_gate0_failure(
    bus_and_store: tuple[CommandBus, EventStore],
) -> None:
    # Act — payload sem "wal"
    result = bus_and_store[0].dispatch(
        Command(command_type="CMD-NEW-PROJECT", payload={})
    )
    # Assert
    assert result.success is False
    assert result.error is not None
    assert "GATE 0" in result.error


def test_new_project_schema_fail_rejects_without_persisting(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange — what com <10 chars (viola min_length do schema T02)
    wal = _wal_dict(make_log)
    wal["5w1h"]["what"] = "curto"  # type: ignore[index]
    bus, store = bus_and_store
    # Act
    result = _dispatch(bus, "CMD-NEW-PROJECT", wal)
    # Assert — GATE 1 falhou e NADA foi persistido
    assert result.success is False
    assert result.error is not None
    assert "GATE 1" in result.error
    assert list(store.stream(_PROJECT)) == []


# --------------------------------------------------------------------------- #
# publish_context — 4 gates
# --------------------------------------------------------------------------- #


def test_publish_context_success_passes_four_gates(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange — wal canônico (fresh, sem parent_log, schema válido) passa tudo
    wal = _wal_dict(make_log, task="TASK-HACK")
    bus, store = bus_and_store
    # Act
    result = _dispatch(bus, "CMD-PUBLISH-CONTEXT", wal)
    # Assert — sucesso, task imposto, persistido (GATE 4 stub aprovou)
    assert result.success is True
    assert result.events[0].map_index.task == "TASK-PUBLISH-CONTEXT"
    assert len(list(store.stream(_PROJECT))) == 1


def test_publish_gate1_schema_fail_rejects_without_persisting(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    wal = _wal_dict(make_log)
    wal["5w1h"]["what"] = "x"  # type: ignore[index]
    bus, store = bus_and_store
    # Act
    result = _dispatch(bus, "CMD-PUBLISH-CONTEXT", wal)
    # Assert
    assert result.success is False
    assert "GATE 1" in (result.error or "")
    assert list(store.stream(_PROJECT)) == []


def test_publish_gate2_sanity_fail_bad_parent_log(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange — parent_log presente mas fora do formato LOG-UUID
    wal = _wal_dict(make_log, parent_log="not-a-log-id")
    result = _dispatch(bus_and_store[0], "CMD-PUBLISH-CONTEXT", wal)
    # Assert
    assert result.success is False
    assert "GATE 2" in (result.error or "")


def test_publish_accepts_well_formed_parent_log(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange — parent_log no formato LOG-UUID canônico (existência é do auditor T04)
    parent = "LOG-12345678-1234-1234-1234-123456789ABC"
    wal = _wal_dict(make_log, parent_log=parent)
    result = _dispatch(bus_and_store[0], "CMD-PUBLISH-CONTEXT", wal)
    # Assert
    assert result.success is True
    assert result.events[0].map_index.parent_log == parent


def test_publish_gate3_freshness_fail_stale(
    bus_and_store: tuple[CommandBus, EventStore], make_log: Callable[..., WalLog]
) -> None:
    # Arrange — created 3 dias antes do now fixo (>> 24h) -> stale
    wal = _wal_dict(make_log, created="2026-06-19T12:00:00Z")
    result = _dispatch(bus_and_store[0], "CMD-PUBLISH-CONTEXT", wal)
    # Assert
    assert result.success is False
    assert "GATE 3" in (result.error or "")


def test_publish_missing_wal_returns_gate0_failure(
    bus_and_store: tuple[CommandBus, EventStore],
) -> None:
    result = bus_and_store[0].dispatch(
        Command(command_type="CMD-PUBLISH-CONTEXT", payload={})
    )
    assert result.success is False
    assert "GATE 0" in (result.error or "")


def test_publish_non_dict_wal_returns_gate0_failure(
    bus_and_store: tuple[CommandBus, EventStore],
) -> None:
    result = bus_and_store[0].dispatch(
        Command(
            command_type="CMD-PUBLISH-CONTEXT", payload={"wal": "nao-sou-dict"}
        )
    )
    assert result.success is False
    assert "GATE 0" in (result.error or "")
