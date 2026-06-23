"""Projection + replay (T05.4) — FASE 2 (Runtime event-driven).

O replay event-sourced reconstroi um agregado ``ProjectState`` a partir do
WAL do projeto — consumindo ``EventStore.stream`` (projeção ordenada do WAL
em BD, D-T05.1). É a metade de leitura do pattern event-sourcing: escreve-se
via handlers (T05.3), lê-se o agregado via replay (T06/T10 consomem).

``ProjectState`` é **determinístico e idempotente**: como ``stream`` ordena
por ``(timestamp.created, log_id)`` (D-T05.1), dois replays do mesmo WAL
produzem o mesmo agregado. Mandato **"CRUD em BD"** → lê do ``EventStore``
(projeção do ``wal_logs`` em BD), **nunca** de arquivos soltos.

Decisões (D-T05.4):
- **D-T05.4.1** — ``ProjectState`` é ``dataclass(frozen=True)`` (imutável,
  consistente com toda a camada de modelos WAL). Agregados derivados:
  ``total_logs``, ``counts_by_task``, ``counts_by_status``, ``last_log``.
- **D-T05.4.2** — ``replay(project, store)`` reduz o ``store.stream(project)``
  a um agregado. Nenhum estado em memória além do retornado (stateless).
- **D-T05.4.3** — ``last_log`` é o último yielded pelo stream (maior
  ``(timestamp.created, log_id)``); ``None`` se o projeto não tem logs.
- **D-T05.4.4** — status convertido a ``str`` (``ValidationStatus`` é
  ``StrEnum`` <: ``str``) → ``counts_by_status: dict[str, int]`` limpo.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from lab_engine.runtime.events import EventStore
from lab_engine.wal.models import WalLog


@dataclass(frozen=True)
class ProjectState:
    """Agregado de projeto reduzido do seu WAL (event-sourced projection).

    Determinístico: dois replays do mesmo WAL produzem o mesmo ``ProjectState``
    (ordenação canônica do ``EventStore.stream``, D-T05.1). ``last_log`` é o
    evento mais recente por ``(timestamp.created, log_id)``; ``None`` se o
    projeto não tem logs. Imutável (``frozen=True``) — mutação levanta
    ``FrozenInstanceError``.
    """

    project: str
    total_logs: int = 0
    counts_by_task: dict[str, int] = field(default_factory=dict)
    counts_by_status: dict[str, int] = field(default_factory=dict)
    last_log: WalLog | None = None


def replay(project: str, store: EventStore) -> ProjectState:
    """Reduz o WAL de ``project`` (via ``store.stream``) a um ``ProjectState``.

    Idempotente: a ordenação determinística do ``EventStore.stream``
    (``(timestamp.created, log_id)``, D-T05.1) garante que replay reconstroi
    exatamente o mesmo agregado a cada chamada. Lê do WAL em BD (projeção do
    ``wal_logs`` via ``WalRepository``) — nunca de arquivos soltos. Stateless:
    não mantém cache nem estado entre chamadas.
    """
    tasks: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    total = 0
    last_log: WalLog | None = None
    for log in store.stream(project):
        total += 1
        tasks[log.map_index.task] += 1
        statuses[str(log.validation.status)] += 1
        last_log = log  # stream é ascendente (created, log_id) → último = recente
    return ProjectState(
        project=project,
        total_logs=total,
        counts_by_task=dict(tasks),
        counts_by_status=dict(statuses),
        last_log=last_log,
    )


__all__ = ["ProjectState", "replay"]
