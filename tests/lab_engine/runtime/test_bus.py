"""Testes do command bus (T05.2) — M3 (pytest equivalente).

Cobre o contrato do ``CommandBus`` (CQRS-lite):
- ``Command`` Pydantic frozen, ``command_type`` pattern ``^CMD-``, ``timestamp``
  tz-aware (reusa ``TZAwareDatetime`` de ``wal.models``), id/timestamp
  auto-gerados mas overrideable (correlação A2A + testes determinísticos);
- ``CommandResult`` frozen com ``events: list[WalLog]`` (retorno semântico);
- ``CommandBus.register`` levanta em duplicata (registro ambíguo = bug config);
- ``CommandBus.dispatch`` captura exceções de handler → ``failure`` (não
  propaga — pré-figura a resiliência T07) e handler ausente → ``failure``.

Padrão AAA. Cobertura alvo ≥80% no módulo ``bus``. Handlers são lambdas/mocks
— o bus é despachante puro, sem acoplamento a BD (eventos reais são T05.3).
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from lab_engine.runtime.bus import (
    Command,
    CommandAlreadyRegisteredError,
    CommandBus,
    CommandResult,
)


def _cmd(**overrides: object) -> Command:
    """Command canônico ``CMD-TEST`` com overrides opcionais."""
    base: dict[str, object] = {"command_type": "CMD-TEST"}
    base.update(overrides)
    return Command(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Command — construção, defaults, validação, imutabilidade
# --------------------------------------------------------------------------- #


def test_command_auto_generates_id_and_timestamp() -> None:
    # Act
    c = Command(command_type="CMD-TEST")
    # Assert — defaults preenchidos (UUID hex não-vazio; tz-aware)
    assert c.command_id
    assert c.timestamp.tzinfo is not None


def test_command_accepts_explicit_id_and_timestamp() -> None:
    # Arrange
    ts = datetime.now(UTC)
    # Act
    c = Command(command_type="CMD-TEST", command_id="abc-123", timestamp=ts)
    # Assert
    assert c.command_id == "abc-123"
    assert c.timestamp == ts


def test_command_default_payload_is_empty_dict() -> None:
    c = _cmd()
    assert c.payload == {}


def test_command_payload_is_preserved() -> None:
    c = _cmd(payload={"a": 1, "b": [2, 3]})
    assert c.payload == {"a": 1, "b": [2, 3]}


def test_command_correlation_id_optional() -> None:
    assert _cmd().correlation_id is None
    assert _cmd(correlation_id="corr-1").correlation_id == "corr-1"


def test_command_rejects_type_without_cmd_prefix() -> None:
    # Arrange — ^TASK- (event_type do WAL) NÃO é command_type válido
    # Act / Assert
    with pytest.raises(ValidationError):
        Command(command_type="TASK-X")


def test_command_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Command(command_type="CMD-TEST", surprise=1)  # type: ignore[call-arg]


def test_command_is_frozen() -> None:
    c = _cmd()
    with pytest.raises(ValidationError):
        c.command_type = "CMD-OTHER"  # type: ignore[misc]


def test_command_rejects_naive_timestamp() -> None:
    # Arrange — naive (sem tzinfo) é rejeitado pelo TZAwareDatetime
    naive = datetime(2026, 1, 1, 12, 0, 0)
    # Act / Assert
    with pytest.raises(ValidationError):
        Command(command_type="CMD-TEST", timestamp=naive)


# --------------------------------------------------------------------------- #
# CommandResult
# --------------------------------------------------------------------------- #


def test_result_defaults_success_false_events_empty_error_none() -> None:
    r = CommandResult(command_id="x")
    assert r.success is False
    assert r.events == []
    assert r.error is None


def test_result_is_frozen() -> None:
    r = CommandResult(command_id="x", success=True)
    with pytest.raises(ValidationError):
        r.success = False  # type: ignore[misc]


def test_result_rejects_non_wallog_event() -> None:
    # Arrange — events é list[WalLog]; um dict cru deve ser rejeitado
    # Act / Assert
    with pytest.raises(ValidationError):
        CommandResult(command_id="x", events=[{"not": "a walog"}])  # type: ignore[list-item]


# --------------------------------------------------------------------------- #
# CommandBus — register / dispatch / registered_types
# --------------------------------------------------------------------------- #


def _ok(cmd: Command) -> CommandResult:
    return CommandResult(command_id=cmd.command_id, success=True)


def test_bus_dispatch_calls_handler_and_returns_its_result() -> None:
    # Arrange
    bus = CommandBus()
    bus.register("CMD-A", _ok)
    # Act
    result = bus.dispatch(_cmd(command_type="CMD-A"))
    # Assert
    assert result.success is True
    assert result.command_id  # propagado do command


def test_bus_dispatch_unknown_type_returns_failure() -> None:
    # Arrange — nenhum handler para CMD-NOPE
    bus = CommandBus()
    # Act
    result = bus.dispatch(_cmd(command_type="CMD-NOPE"))
    # Assert
    assert result.success is False
    assert result.error is not None
    assert "CMD-NOPE" in result.error


def test_bus_register_duplicate_raises() -> None:
    # Arrange
    bus = CommandBus()
    bus.register("CMD-A", _ok)
    # Act / Assert — re-registrar o mesmo command_type é ambíguo (bug config)
    with pytest.raises(CommandAlreadyRegisteredError):
        bus.register("CMD-A", _ok)


def test_bus_handler_exception_returns_failure_and_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange — handler com bug
    def boom(_cmd: Command) -> CommandResult:
        raise RuntimeError("handler com bug")

    bus = CommandBus()
    bus.register("CMD-A", boom)
    # Act
    with caplog.at_level(logging.ERROR, logger="lab_engine.runtime.bus"):
        result = bus.dispatch(_cmd(command_type="CMD-A"))
    # Assert — exceção capturada, não propagada; failure + log
    assert result.success is False
    assert result.error is not None
    assert "CMD-A" in result.error
    assert any("CommandBus handler falhou" in r.message for r in caplog.records)


def test_bus_handler_receives_the_command() -> None:
    # Arrange
    seen: list[Command] = []
    bus = CommandBus()
    bus.register("CMD-A", lambda cmd: (seen.append(cmd), _ok(cmd))[1])
    command = _cmd(command_type="CMD-A", payload={"k": 1})
    # Act
    bus.dispatch(command)
    # Assert
    assert seen == [command]
    assert seen[0].payload == {"k": 1}


def test_bus_registered_types_lists_all_registered() -> None:
    # Arrange
    bus = CommandBus()
    bus.register("CMD-A", _ok)
    bus.register("CMD-B", _ok)
    # Act / Assert
    assert set(bus.registered_types) == {"CMD-A", "CMD-B"}


def test_bus_registered_types_empty_by_default() -> None:
    assert CommandBus().registered_types == ()
