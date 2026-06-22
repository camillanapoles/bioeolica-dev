"""Command bus — despacho de comandos (CQRS-lite) — T05.2 (FASE 2).

Um ``Command`` é a **intenção** (request do usuário/runtime); o handler executa
e produz um ``CommandResult`` (+ eventos WAL via ``EventStore`` em T05.3). O
``CommandBus`` é o despachante puro: registra handlers por ``command_type`` e
despacha, **capturando exceções** (resiliência básica que pré-figura T07 — um
handler com bug retorna ``failure``, não quebra o caller do bus).

Decisões de contrato (D-T05.2):

- **D-T05.2.1** — ``Command`` é Pydantic v2 ``frozen``/``extra="forbid"``;
  ``command_type`` pattern ``^CMD-`` — **distinto** do ``event_type`` ``^TASK-``
  do WAL (command = intenção/input; evento = fato persistido). Reusa
  ``TZAwareDatetime`` de ``wal.models`` (garantismo tz-aware compartilhado).
- **D-T05.2.2** — ``command_id``/``timestamp`` auto-gerados (UUID4 hex /
  agora-UTC) mas **overrideable** — facilita correlação explícita (A2A T08) e
  testes determinísticos sem esconder a rastreabilidade.
- **D-T05.2.3** — ``CommandBus.register`` **levanta** ``CommandAlreadyRegisteredError``
  em duplicata. Registro ambíguo é bug de config — mais garantista que overwrite
  silencioso.
- **D-T05.2.4** — ``CommandBus.dispatch`` **não propaga** exceções de handler →
  ``CommandResult(success=False)`` + log. Handler ausente → failure (sem raise).
  Pré-figura T07 (resiliência): um handler com bug não derruba o caller.
- **D-T05.2.5** — ``CommandResult.events: list[WalLog]`` é retorno semântico
  (quais eventos o handler diz ter produzido). A **persistência** é do handler
  (via ``EventStore`` em T05.3); o bus é despachante puro (separation of concerns).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from lab_engine.wal.models import TZAwareDatetime, WalLog

_logger = logging.getLogger(__name__)

# command_type canônico — distinto do event_type ^TASK- do WAL. Commands são a
# intenção (input do runtime); eventos (^TASK-) são o fato persistido no WAL.
_COMMAND_TYPE_PATTERN = r"^CMD-"


class Command(BaseModel):
    """Comando imutável — a intenção (input do runtime).

    ``command_id`` e ``timestamp`` são auto-gerados por default (UUID4 hex /
    agora-UTC tz-aware) mas overrideable — facilita correlação explícita (A2A
    T08) e testes determinísticos. ``command_type`` segue ``^CMD-`` (distinto
    do ``^TASK-`` do WAL).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    command_id: str = Field(default_factory=lambda: uuid4().hex)
    command_type: str = Field(..., pattern=_COMMAND_TYPE_PATTERN)
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None
    timestamp: TZAwareDatetime = Field(default_factory=lambda: datetime.now(UTC))


class CommandAlreadyRegisteredError(Exception):
    """``command_type`` já tem handler registrado — registro ambíguo (bug config)."""


class CommandResult(BaseModel):
    """Resultado do despacho: ``success`` + eventos WAL emitidos pelo handler.

    ``events`` carrega os ``WalLog``s que o handler diz ter produzido (retorno
    semântico para o caller). A **persistência** é responsabilidade do handler
    (via ``EventStore``, T05.3) — o bus é despachante puro (D-T05.2.5).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    command_id: str
    success: bool = False
    events: list[WalLog] = Field(default_factory=list)
    error: str | None = None


#: Handler de comando: recebe o ``Command`` e devolve o ``CommandResult``.
CommandHandler = Callable[[Command], CommandResult]


class CommandBus:
    """Registry + despacho de ``CommandHandler`` por ``command_type``.

    Inspiração CQRS-lite: o bus não contém lógica de domínio — só despacha.
    Handlers são registrados uma vez por ``command_type`` (D-T05.2.3) e o
    despacho é resiliente (D-T05.2.4): exceções viram ``failure``, nunca
    propagam para o caller.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {}

    def register(self, command_type: str, handler: CommandHandler) -> None:
        """Inscreve ``handler`` para ``command_type``.

        Duplicata lança ``CommandAlreadyRegisteredError`` (D-T05.2.3) — dois
        handlers para o mesmo command_type tornaria o despacho ambíguo.
        """
        if command_type in self._handlers:
            raise CommandAlreadyRegisteredError(command_type)
        self._handlers[command_type] = handler

    def dispatch(self, command: Command) -> CommandResult:
        """Despacha ``command`` ao handler registrado.

        Handler ausente → ``CommandResult(success=False)``. Exceção do handler
        → capturada, logada e convertida em ``failure`` (D-T05.2.4) — nunca
        propaga para o caller (pré-figura T07).
        """
        handler = self._handlers.get(command.command_type)
        if handler is None:
            return CommandResult(
                command_id=command.command_id,
                error=(
                    f"nenhum handler registrado para "
                    f"command_type={command.command_type!r}"
                ),
            )
        try:
            return handler(command)
        except Exception:
            _logger.exception(
                "CommandBus handler falhou (command_type=%s, command_id=%s)",
                command.command_type,
                command.command_id,
            )
            return CommandResult(
                command_id=command.command_id,
                error=f"handler falhou para command_type={command.command_type!r}",
            )

    @property
    def registered_types(self) -> tuple[str, ...]:
        """``command_type``s com handler registrado (inspeção/teste)."""
        return tuple(self._handlers)


__all__ = [
    "Command",
    "CommandAlreadyRegisteredError",
    "CommandBus",
    "CommandHandler",
    "CommandResult",
]
