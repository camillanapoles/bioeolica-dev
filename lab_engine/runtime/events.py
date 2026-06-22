"""Event store + event bus — projeção do WAL (decisão D-T05.1).

O **event store NÃO é uma tabela separada**: eventos de domínio são ``WalLog``s
persistidos em ``wal_logs`` via ``WalRepository``. O ``EventStore`` é uma
abstração de leitura/escrita sobre o WAL que impõe a ordenação temporal
canônica (``timestamp.created``) necessária ao replay event-sourced. Fiel à
arquitetura §2 ("source of truth único = WAL em BD") e a D-T03.1 (mapeamento
híbrido cols indexadas + payload JSON).

- ``append(log)`` delega ao ``WalRepository.create`` (validação pré-persistência
  T04 fica a cargo do caller/bus — D-T03.5; aqui só persiste).
- ``stream(project)`` pagina o WAL por projeto e ordena por
  ``(timestamp.created, log_id)`` — ordenação determinística e idempotente,
  necessária porque ``WalRepository.list`` não impõe ``order_by`` (D-T03.2).
- ``EventBus`` pub/sub in-proc: handlers reagem ao ``map_index.task`` do log
  (event_type canônico, pattern ``^TASK-``); ``"*"`` é catch-all. Exceção de
  handler é capturada e logada — nunca quebra o ``publish`` (pré-figura a
  resiliência T07: um handler com bug não corrompe o append do evento).
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator

from lab_engine.wal.models import WalLog
from lab_engine.wal.store import WalRepository

_logger = logging.getLogger(__name__)

# Página interna do stream — robustez a volume crescente do WAL (mesma
# estratégia do auditor T04, D-T04.5). ``WalRepository.list`` é chamado em
# batches; o stream materializa + ordena globalmente antes de iterar.
_PAGE_SIZE = 500

# event_type catch-all — handler inscrito em "*" recebe todos os logs.
_WILDCARD = "*"

#: Handler de evento: recebe o ``WalLog`` publicado. Erros são capturados.
EventHandler = Callable[[WalLog], None]


class EventStore:
    """Event store = projeção ordenada do WAL sobre um ``WalRepository``."""

    def __init__(self, repo: WalRepository) -> None:
        self._repo = repo

    def append(self, log: WalLog) -> WalLog:
        """Persiste ``log`` como evento de domínio (delega ao repository).

        A validação garantista (T04) é responsabilidade do caller (command bus
        T05.2 / handlers T05.3) — D-T03.5: o store persiste ``WalLog`` já
        validado. Retorna o próprio log (o WAL é append-only; ``create`` lança
        ``LogDuplicateError`` se o ``log_id`` já existir).
        """
        return self._repo.create(log)

    def stream(self, project: str) -> Iterator[WalLog]:
        """Itera os eventos de ``project`` em ordem temporal canônica.

        Páginas internamente (``_PAGE_SIZE``), materializa e ordena por
        ``(timestamp.created, log_id)`` — determinístico e idempotente,
        pré-requisito do replay (T05.4). ``WalRepository.list`` não ordena
        (D-T03.2), por isso a ordenação vive aqui. ``timestamp.created`` é
        sempre timezone-aware (invariante de T02), então a comparação é segura.
        """
        collected: list[WalLog] = []
        offset = 0
        while True:
            batch = self._repo.list(project=project, limit=_PAGE_SIZE, offset=offset)
            if not batch:
                break
            collected.extend(batch)
            if len(batch) < _PAGE_SIZE:
                break
            offset += _PAGE_SIZE
        collected.sort(key=lambda log: (log.timestamp.created, log.log_id))
        yield from collected


class EventBus:
    """Pub/sub in-proc sobre o ``map_index.task`` (event_type canônico).

    O event_type é o valor de ``log.map_index.task`` (pattern ``^TASK-`` do
    schema — e.g. ``TASK-NEW-PROJECT`` em T05.3). ``"*"`` inscreve um handler
    catch-all. Handlers são síncronos (escopo SQLite local, sem servidor
    externo — arquitetura §10).
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Inscreve ``handler`` para ``event_type`` (ou ``"*"`` para todos)."""
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, log: WalLog) -> None:
        """Notifica handlers de ``log.map_index.task`` e do catch-all ``"*"``.

        Exceções de handler são capturadas e logadas — nunca propagam. Assim um
        handler com bug não corrompe o append do evento (pré-figura T07). A
        ordenação é: handlers do event_type específico, depois catch-all.
        """
        event_type = log.map_index.task
        handlers = [
            *self._handlers.get(event_type, []),
            *self._handlers.get(_WILDCARD, []),
        ]
        for handler in handlers:
            try:
                handler(log)
            except Exception:
                _logger.exception(
                    "EventBus handler falhou (event_type=%s, log_id=%s)",
                    event_type,
                    log.log_id,
                )


__all__ = ["EventBus", "EventHandler", "EventStore"]
