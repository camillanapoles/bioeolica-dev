"""Validador garantista do WAL — rejeita logs inválidos **antes** de persistir.

Implementa o ``validation_behavior`` canônico do ``INSTRUCTIONS.md`` (L2321-2326):

- ``on_invalid`` (L2322) → **REJECT**: log não é persistido; erros estruturados
  (campos faltantes, tipos incorretos, padrões não-casados) retornados para
  correção antes da retentativa.
- ``on_missing_optional`` (L2323) → **ACCEPT**: opcionais ausentes
  (``quality_metrics``, ``next_steps``, ``rag_sources``, ``patches``,
  ``security_classification``) viram ``null``; log é persistido.
- ``on_unknown_field`` (L2324) → **REJECT**: campos fora do schema são
  rejeitados (evita poluição/inconsistência).
- ``auto_fix`` (L2325) → gera ``log_id`` se fora do padrão ``LOG-UUID``;
  preenche ``timestamp.created`` se vazio.

Decisões de design (fidelidade ao contrato — D-T04.x no plano mestre):

- **D-T04.1 — opera sobre input cru (dict/JSON), NÃO sobre ``WalLog`` instanciado.**
  ``auto_fix`` precisa rodar **antes** de ``WalLog.model_validate``. Se o
  validador recebesse um ``WalLog`` já instanciado, a validação Pydantic teria
  rejeitado antes do ``auto_fix`` poder agir. O validador é a borda do sistema:
  recebe o wire-format cru que vem do agente/runtime.

- **D-T04.2 — retorna ``ValidationResult`` (NÃO levanta).**
  ``on_invalid`` diz "retornar erros para correção". O caller (T05 runtime)
  decide o que fazer (RETRY com correção, dead-letter, etc.). Levantar
  forçaria ``try/except`` em todo callsite — pior para o caller.

- **D-T03.5 — o store persiste ``WalLog`` já validado; o validador enfileira
  ANTES de ``store.create()``.** Separação de concerns: store = CRUD puro;
  validador = garantismo pré-persistência.

``on_invalid``/``on_unknown_field`` são cobertos pelo próprio ``WalLog`` (T02 faz
``extra="forbid"`` + tipos/mínimos/padrões). O validador orquestra auto_fix →
``model_validate`` → captura ``ValidationError`` estruturado.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import ValidationError as PydanticValidationError

from lab_engine.wal.models import WalLog

# Pattern canônico de log_id (INSTRUCTIONS.md L2206) — espelha o do WalLog.
_LOG_ID_PATTERN = re.compile(
    r"^LOG-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$"
)


# --------------------------------------------------------------------------- #
# Resultado estruturado (frozen — imutabilidade do WAL)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ValidationErrorItem:
    """Um erro de validação — estrutura para o caller corrigir e retentar.

    Espelha o formato do ``ValidationError.errors()`` do Pydantic v2:
    ``loc`` (caminho do campo), ``msg`` (mensagem humana), ``type`` (classe do
    erro, e.g. ``string_too_short``, ``extra_forbidden``).
    """

    loc: tuple[str, ...]
    msg: str
    type: str


@dataclass(frozen=True)
class ValidationResult:
    """Resultado imutável de ``validate``.

    ``valid=True`` → ``log`` é o ``WalLog`` instanciado (pronto para o store).
    ``valid=False`` → ``log`` é ``None`` e ``errors`` lista os problemas.
    ``auto_fixes`` documenta correções aplicadas (rastreabilidade do auto_fix).
    """

    valid: bool
    log: WalLog | None = None
    errors: tuple[ValidationErrorItem, ...] = ()
    auto_fixes: tuple[str, ...] = ()

    @classmethod
    def ok(cls, log: WalLog, auto_fixes: tuple[str, ...] = ()) -> ValidationResult:
        """Resultado válido — ``log`` pronto para persistir."""
        return cls(valid=True, log=log, auto_fixes=auto_fixes)

    @classmethod
    def reject(
        cls, errors: list[ValidationErrorItem], auto_fixes: tuple[str, ...] = ()
    ) -> ValidationResult:
        """Resultado rejeitado — ``errors`` para o caller corrigir."""
        return cls(valid=False, errors=tuple(errors), auto_fixes=auto_fixes)


# --------------------------------------------------------------------------- #
# auto_fix (INSTRUCTIONS.md L2325)
# --------------------------------------------------------------------------- #


def _generate_log_id() -> str:
    """Gera um ``log_id`` canônico (UUID v4 em HEX maiúsculo no padrão LOG-...)."""
    h = uuid4().hex.upper()
    return f"LOG-{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _auto_fix(data: dict[str, Any], *, now: datetime) -> list[str]:
    """Aplica auto_fix conservador no dict cru (L2325) — muta ``data`` in-place.

    Conservador (D-T03.5/D-T04.3): só **preenche ausentes**, nunca sobrescreve
    presentes. ``timestamp`` tz-aware é invariante de T02 — NÃO é auto-fixable
    (naive datetime presente é deixado para a validação rejeitar).

    Returns:
        Lista de descrições humanas das correções (rastreabilidade).
    """
    fixes: list[str] = []

    # log_id: se ausente ou fora do padrão → gera (L2325).
    log_id = data.get("log_id")
    if not isinstance(log_id, str) or not _LOG_ID_PATTERN.match(log_id):
        new_id = _generate_log_id()
        data["log_id"] = new_id
        fixes.append(f"log_id gerado automaticamente: {new_id}")

    # timestamp.created: se ausente/vazio → preenche (L2325). ``timestamp`` é
    # required; se o sub-objeto inteiro falta, NÃO inventamos — deixamos a
    # validação rejeitar (auto_fix só age dentro do contrato).
    ts = data.get("timestamp")
    if isinstance(ts, dict) and not ts.get("created"):
        iso = now.isoformat()
        ts["created"] = iso
        fixes.append(f"timestamp.created preenchido com momento da validação: {iso}")

    return fixes


# --------------------------------------------------------------------------- #
# Borda pública — validate
# --------------------------------------------------------------------------- #


def _parse_input(raw: Any) -> tuple[dict[str, Any] | None, ValidationErrorItem | None]:
    """Normaliza o input em dict cru. Retorna ``(data, None)`` ou ``(None, erro)``."""
    if isinstance(raw, (str, bytes, bytearray)):
        try:
            data = json.loads(raw)
        except (ValueError, TypeError) as exc:  # JSONDecodeError é subclasses de ValueError
            return None, ValidationErrorItem(
                loc=("",), msg=f"JSON inválido: {exc}", type="json_parse_error"
            )
    elif isinstance(raw, dict):
        # deepcopy: NÃO muta o input do caller (imutabilidade — coding-style).
        data = copy.deepcopy(raw)
    else:
        return None, ValidationErrorItem(
            loc=("",),
            msg=f"input deve ser dict/str/bytes, não {type(raw).__name__}",
            type="input_type_error",
        )

    if not isinstance(data, dict):
        return None, ValidationErrorItem(
            loc=("",),
            msg=f"JSON deve ser um objeto (dict), não {type(data).__name__}",
            type="input_type_error",
        )
    return data, None


def validate(
    raw: dict[str, Any] | str | bytes,
    *,
    now: datetime | None = None,
) -> ValidationResult:
    """Valida um log WAL cru — o gate garantista pré-persistência (D-T04.1).

    Fluxo: (1) parse (dict/str/bytes → dict); (2) ``auto_fix`` no dict;
    (3) ``WalLog.model_validate``; (4) sucesso → ``ValidationResult.ok`` ou
    falha → ``ValidationResult.reject`` com erros estruturados.

    Args:
        raw: log no wire-format (dict, str-JSON ou bytes-JSON).
        now: instante para ``auto_fix`` de ``timestamp.created`` (injetável para
            testes determinísticos; default ``datetime.now(UTC)``).

    Returns:
        ``ValidationResult`` — ``valid`` + ``log`` (se ok) + ``errors`` (se
        rejeitado) + ``auto_fixes`` (correções aplicadas). Nunca levanta.
    """
    moment = now if now is not None else datetime.now(UTC)

    # (1) parse
    data, parse_error = _parse_input(raw)
    if parse_error is not None:
        return ValidationResult.reject([parse_error])
    # ``_parse_input`` retorna ``(data, None)`` ou ``(None, erro)`` — o return
    # acima garante que aqui ``data`` não é None; o assert documenta isso para
    # o mypy (narrowing), já que o tuple não permite inferência automática.
    assert data is not None  # nosec B101

    # (2) auto_fix (L2325) — antes da validação Pydantic.
    fixes = tuple(_auto_fix(data, now=moment))

    # (3) validação — WalLog.model_validate cobre on_invalid + on_unknown_field.
    try:
        log = WalLog.model_validate(data)
    except PydanticValidationError as exc:
        errors = [
            ValidationErrorItem(
                loc=tuple(str(part) for part in err["loc"]),
                msg=err["msg"],
                type=err["type"],
            )
            for err in exc.errors()
        ]
        return ValidationResult.reject(errors, auto_fixes=fixes)

    # (4) sucesso — on_missing_optional já tratado pelo Pydantic (opcionais None).
    return ValidationResult.ok(log, auto_fixes=fixes)


__all__ = [
    "ValidationErrorItem",
    "ValidationResult",
    "validate",
]
