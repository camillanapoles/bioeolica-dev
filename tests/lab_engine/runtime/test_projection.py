"""Testes do replay/projection T05.4 — M3 (pytest equivalente).

Cobre ``replay(project, store) -> ProjectState``: reduz o WAL do projeto
(ordenado via ``EventStore.stream``, D-T05.1) a um agregado determinístico.
Idempotência verificada (2 replays → mesmo ``ProjectState``); ``last_log``
= evento mais recente por ``(created, log_id)``; contagens por task/status;
projeto vazio → estado-zero; isolamento por projeto; ``ProjectState`` frozen.

Padrão AAA. Cobertura alvo ≥80% (histórico: 100%) em ``projection``. Fixtures
``repo``/``make_log`` do conftest do runtime (SQLite in-memory isolado por teste).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import FrozenInstanceError

import pytest

from lab_engine.runtime.events import EventStore
from lab_engine.runtime.projection import ProjectState, replay
from lab_engine.wal.models import WalLog
from lab_engine.wal.store import WalRepository

_PROJECT = "PRODUTO-PMSG-100kW-001"


def _store_with(
    repo: WalRepository, logs: tuple[WalLog, ...]
) -> EventStore:
    """Cria EventStore sobre repo e persiste ``logs`` (na ordem dada)."""
    store = EventStore(repo)
    for log in logs:
        store.append(log)
    return store


# --------------------------------------------------------------------------- #
# replay — projeto vazio
# --------------------------------------------------------------------------- #


def test_replay_empty_project_returns_zero_state(repo: WalRepository) -> None:
    # Arrange — store sem logs
    store = EventStore(repo)
    # Act
    state = replay(_PROJECT, store)
    # Assert — estado-zero canônico
    assert state.project == _PROJECT
    assert state.total_logs == 0
    assert state.counts_by_task == {}
    assert state.counts_by_status == {}
    assert state.last_log is None


# --------------------------------------------------------------------------- #
# replay — log único
# --------------------------------------------------------------------------- #


def test_replay_single_log(repo: WalRepository, make_log: Callable[..., WalLog]) -> None:
    # Arrange
    log = make_log(task="TASK-NEW-PROJECT", status="PASS")
    store = _store_with(repo, (log,))
    # Act
    state = replay(_PROJECT, store)
    # Assert
    assert state.total_logs == 1
    assert state.counts_by_task == {"TASK-NEW-PROJECT": 1}
    assert state.counts_by_status == {"PASS": 1}
    assert state.last_log is not None
    assert state.last_log.log_id == log.log_id


# --------------------------------------------------------------------------- #
# replay — agregação por task/status
# --------------------------------------------------------------------------- #


def test_replay_counts_by_task_and_status(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange — 3 logs: 2 tasks distintas, 3 status distintos
    l1 = make_log(task="TASK-NEW-PROJECT", status="PASS")
    l2 = make_log(task="TASK-ALLOCATE-TASK", status="PENDING")
    l3 = make_log(task="TASK-NEW-PROJECT", status="FAIL")
    store = _store_with(repo, (l1, l2, l3))
    # Act
    state = replay(_PROJECT, store)
    # Assert — agregação correta
    assert state.total_logs == 3
    assert state.counts_by_task == {"TASK-NEW-PROJECT": 2, "TASK-ALLOCATE-TASK": 1}
    assert state.counts_by_status == {"PASS": 1, "PENDING": 1, "FAIL": 1}


# --------------------------------------------------------------------------- #
# replay — last_log é o mais recente (stream ordena, não o insert order)
# --------------------------------------------------------------------------- #


def test_replay_last_log_is_most_recent(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange — inserção NÃO-ordenada: newer primeiro, older depois.
    # stream ordena por (created, log_id) → last_log deve ser o newer.
    older = make_log(task="TASK-NEW-PROJECT", status="PASS", created="2026-06-20T10:00:00Z")
    newer = make_log(task="TASK-PUBLISH-CONTEXT", status="PASS", created="2026-06-22T10:00:00Z")
    store = _store_with(repo, (newer, older))
    # Act
    state = replay(_PROJECT, store)
    # Assert — last_log = maior created (newer), não o último inserido (older)
    assert state.last_log is not None
    assert state.last_log.log_id == newer.log_id


# --------------------------------------------------------------------------- #
# replay — idempotência (determinismo)
# --------------------------------------------------------------------------- #


def test_replay_idempotent(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange
    store = _store_with(
        repo,
        (
            make_log(task="TASK-NEW-PROJECT", status="PASS"),
            make_log(task="TASK-ALLOCATE-TASK", status="PENDING"),
        ),
    )
    # Act — dois replays do mesmo WAL
    state1 = replay(_PROJECT, store)
    state2 = replay(_PROJECT, store)
    # Assert — mesmo agregado (determinismo da ordenação D-T05.1)
    assert state1 == state2
    assert state1.total_logs == state2.total_logs == 2


# --------------------------------------------------------------------------- #
# replay — isolamento por projeto (lê do store, não inventa)
# --------------------------------------------------------------------------- #


def test_replay_isolates_by_project(
    repo: WalRepository, make_log: Callable[..., WalLog]
) -> None:
    # Arrange — log de OUTRO projeto + log do projeto consultado
    other = make_log(task="TASK-NEW-PROJECT", status="PASS", project="PRODUTO-OUTRO-001")
    mine = make_log(task="TASK-PUBLISH-CONTEXT", status="PASS")
    store = _store_with(repo, (other, mine))
    # Act
    state = replay(_PROJECT, store)
    # Assert — só o log do projeto consultado aparece no agregado
    assert state.total_logs == 1
    assert state.counts_by_task == {"TASK-PUBLISH-CONTEXT": 1}
    assert state.last_log is not None
    assert state.last_log.log_id == mine.log_id


# --------------------------------------------------------------------------- #
# ProjectState — frozen (imutável)
# --------------------------------------------------------------------------- #


def test_project_state_is_frozen(repo: WalRepository) -> None:
    # Arrange
    store = EventStore(repo)
    state = replay(_PROJECT, store)
    # Act/Assert — mutação de field frozen levanta FrozenInstanceError
    with pytest.raises(FrozenInstanceError):
        state.total_logs = 999


def test_project_state_defaults_on_empty() -> None:
    # Arrange/Act — construção direta confirma defaults do dataclass
    state = ProjectState(project=_PROJECT)
    # Assert
    assert state.total_logs == 0
    assert state.counts_by_task == {}
    assert state.counts_by_status == {}
    assert state.last_log is None
