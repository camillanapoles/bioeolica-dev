"""Testes do event store + event bus (T05.1) — M3 (pytest equivalente).

Cobre o contrato D-T05.1:
- eventos de domínio = ``WalLog``s persistidos (``append`` → repository);
- ``stream(project)`` ordena por ``(timestamp.created, log_id)`` e pagina;
- ``EventBus`` pub/sub sobre ``map_index.task`` (event_type canônico ``^TASK-``),
  com catch-all ``"*"`` e resiliência a handler com falha (captura + log).

Padrão AAA (Arrange-Act-Assert). Cobertura alvo ≥80% no módulo ``events``.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator

import pytest

from lab_engine.runtime.events import EventBus, EventStore
from lab_engine.wal.models import WalLog
from lab_engine.wal.store import LogDuplicateError, WalRepository

# Quantidade de logs que excede o _PAGE_SIZE interno (500) — exercita a
# paginação do stream mesmo se o tamanho da página for ajustado no futuro.
_MANY = 503


def _boom(_log: WalLog) -> None:
    """Handler que sempre falha — para validar captura do EventBus."""
    raise RuntimeError("handler com bug")


# --------------------------------------------------------------------------- #
# EventStore.append
# --------------------------------------------------------------------------- #


def test_append_persists_log_visible_to_read(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    log = make_log()
    # Act
    store.append(log)
    # Assert — read na mesma session vê o row via flush (sem commit)
    assert repo.read(log.log_id) == log


def test_append_returns_the_persisted_log(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    log = make_log()
    # Act
    returned = store.append(log)
    # Assert
    assert returned is log


def test_append_duplicate_log_id_raises(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    log = make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")
    store.append(log)
    dup = make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")
    # Act / Assert
    with pytest.raises(LogDuplicateError):
        store.append(dup)


# --------------------------------------------------------------------------- #
# EventStore.stream — ordenação e isolamento
# --------------------------------------------------------------------------- #


def test_stream_empty_project_returns_nothing(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    # Act
    events = list(store.stream("PRODUTO-VAZIO-000"))
    # Assert
    assert events == []


def test_stream_orders_by_created_timestamp(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange — insere fora de ordem temporal
    store = EventStore(repo)
    t3 = make_log(created="2026-06-22T12:03:00Z")
    t1 = make_log(created="2026-06-22T12:01:00Z")
    t2 = make_log(created="2026-06-22T12:02:00Z")
    store.append(t3)
    store.append(t1)
    store.append(t2)
    # Act
    events = list(store.stream("PRODUTO-PMSG-100kW-001"))
    # Assert — ordem canônica ascendente por timestamp.created
    assert [e.timestamp.created for e in events] == [
        t1.timestamp.created,
        t2.timestamp.created,
        t3.timestamp.created,
    ]


def test_stream_isolates_by_project(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    store.append(make_log(project="PRODUTO-A-001"))
    store.append(make_log(project="PRODUTO-A-001"))
    store.append(make_log(project="PRODUTO-B-001"))
    # Act
    events_a = list(store.stream("PRODUTO-A-001"))
    events_b = list(store.stream("PRODUTO-B-001"))
    # Assert
    assert len(events_a) == 2
    assert len(events_b) == 1
    assert all(e.map_index.project == "PRODUTO-A-001" for e in events_a)


def test_stream_tiebreak_by_log_id_when_same_created(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange — mesmo created; log_ids distintos e previsíveis
    store = EventStore(repo)
    same_created = "2026-06-22T12:00:00Z"
    store.append(
        make_log(log_id="LOG-BBBBBBBB-BBBB-CCCC-DDDD-EEEEEEEEEEEE", created=same_created)
    )
    store.append(
        make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE", created=same_created)
    )
    # Act
    events = list(store.stream("PRODUTO-PMSG-100kW-001"))
    # Assert — tiebreak determinístico por log_id ascendente
    assert [e.log_id for e in events] == [
        "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE",
        "LOG-BBBBBBBB-BBBB-CCCC-DDDD-EEEEEEEEEEEE",
    ]


def test_stream_is_idempotent_across_calls(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    store.append(make_log(created="2026-06-22T12:02:00Z"))
    store.append(make_log(created="2026-06-22T12:01:00Z"))
    # Act
    first = [e.log_id for e in store.stream("PRODUTO-PMSG-100kW-001")]
    second = [e.log_id for e in store.stream("PRODUTO-PMSG-100kW-001")]
    # Assert — mesma sequência determinística
    assert first == second


def test_stream_paginates_when_more_than_page_size(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange — mais logs que _PAGE_SIZE (500)
    store = EventStore(repo)
    for _ in range(_MANY):
        store.append(make_log())
    # Act
    events = list(store.stream("PRODUTO-PMSG-100kW-001"))
    # Assert — paginação interna retorna todos, sem truncar
    assert len(events) == _MANY


def test_stream_is_a_generator(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = EventStore(repo)
    store.append(make_log())
    # Act
    result = store.stream("PRODUTO-PMSG-100kW-001")
    # Assert — lazy iterator (consumo sob controle do caller)
    assert isinstance(result, Iterator)
    assert len(list(result)) == 1


# --------------------------------------------------------------------------- #
# EventBus — pub/sub
# --------------------------------------------------------------------------- #


def test_bus_publish_calls_matching_handler(
    make_log: Callable[..., WalLog],
) -> None:
    # Arrange
    bus = EventBus()
    received: list[WalLog] = []
    bus.subscribe("TASK-0001", received.append)
    log = make_log(task="TASK-0001")
    # Act
    bus.publish(log)
    # Assert
    assert received == [log]


def test_bus_publish_without_handlers_is_noop(
    make_log: Callable[..., WalLog],
) -> None:
    # Arrange
    bus = EventBus()
    log = make_log(task="TASK-0001")
    # Act / Assert — nenhum handler inscrito, nada quebra
    bus.publish(log)


def test_bus_only_matching_event_type_handler_called(
    make_log: Callable[..., WalLog],
) -> None:
    # Arrange
    bus = EventBus()
    a: list[WalLog] = []
    b: list[WalLog] = []
    bus.subscribe("TASK-A", a.append)
    bus.subscribe("TASK-B", b.append)
    # Act
    bus.publish(make_log(task="TASK-A"))
    # Assert
    assert len(a) == 1
    assert b == []


def test_bus_wildcard_handler_receives_all(
    make_log: Callable[..., WalLog],
) -> None:
    # Arrange
    bus = EventBus()
    catch_all: list[WalLog] = []
    bus.subscribe("*", catch_all.append)
    # Act
    bus.publish(make_log(task="TASK-A"))
    bus.publish(make_log(task="TASK-B"))
    # Assert
    assert len(catch_all) == 2


def test_bus_handler_exception_does_not_break_publish(
    make_log: Callable[..., WalLog], caplog: pytest.LogCaptureFixture
) -> None:
    # Arrange
    bus = EventBus()
    bus.subscribe("TASK-0001", _boom)
    log = make_log(task="TASK-0001")
    # Act / Assert — publish não propaga a exceção do handler
    with caplog.at_level(logging.ERROR, logger="lab_engine.runtime.events"):
        bus.publish(log)
    assert any("EventBus handler falhou" in r.message for r in caplog.records)


def test_bus_handler_exception_still_runs_subsequent_handlers(
    make_log: Callable[..., WalLog],
) -> None:
    # Arrange — primeiro handler falha, segundo deve mesmo assim rodar
    bus = EventBus()
    called: list[str] = []
    bus.subscribe("TASK-0001", _boom)
    bus.subscribe("TASK-0001", lambda log: called.append("second"))
    # Act
    bus.publish(make_log(task="TASK-0001"))
    # Assert
    assert called == ["second"]


def test_bus_wildcard_runs_after_specific_handlers(
    make_log: Callable[..., WalLog],
) -> None:
    # Arrange — ordenação: específico antes do catch-all
    bus = EventBus()
    order: list[str] = []
    bus.subscribe("TASK-0001", lambda log: order.append("specific"))
    bus.subscribe("*", lambda log: order.append("wildcard"))
    # Act
    bus.publish(make_log(task="TASK-0001"))
    # Assert
    assert order == ["specific", "wildcard"]
