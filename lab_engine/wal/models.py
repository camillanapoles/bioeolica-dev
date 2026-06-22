"""Modelos Pydantic v2 do WAL — espelham fielmente o JSON Schema (draft 2020-12)
do ``INSTRUCTIONS.md`` (L2198-2320).

Garantismo: todo sub-modelo reflete **exatamente** o contrato canônico —
``additionalProperties: false`` onde o schema declara (timestamp, 5w1h, where,
how, map_index, validation, quality_metrics e o nível top-level), e
``additionalProperties`` permitido onde o schema **não** declara forbid
(``error_metrics`` L2274-2281 e ``patches`` L2304-2311 aceitam campos extras,
pois é isso que o JSON Schema canônico determina).

Imutabilidade: todos os modelos são ``frozen=True`` — um log WAL é um record
append-only; mutação pós-criação é um anti-padrão que corromperia o rastro.
Use ``model_copy(update=...)`` para derivar variações.

O campo ``5w1h`` (começa por dígito) não é um identificador Python válido, por
isso é modelado como ``five_w1h`` com ``alias="5w1h"``. Para alinhar 100% ao
wire-format canônico, ``populate_by_name`` fica **desligado** (só ``"5w1h"``
é aceito na entrada) e ``serialize_by_alias=True`` fica **ligado** (a saída
sempre emite ``"5w1h"``). Assim entrada **e** saída são wire-format puro.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
)

# --------------------------------------------------------------------------- #
# Configurações compartilhadas
# --------------------------------------------------------------------------- #

# Sub-modelos cujo schema canônico declara `additionalProperties: false`.
# frozen=True garante imutabilidade (WAL append-only).
_FORBID_EXTRA = ConfigDict(extra="forbid", frozen=True)

# Sub-modelos cujo schema canônico NÃO declara `additionalProperties: false`
# (error_metrics L2274-2281, patches L2304-2311) — aceitam campos extras,
# espelhando fielmente o JSON Schema.
_ALLOW_EXTRA = ConfigDict(extra="allow", frozen=True)


def _ensure_tz_aware(dt: datetime) -> datetime:
    """JSON Schema ``format: "date-time"`` (RFC 3339) exige offset/Z.

    Rejeita datetimes *naive* — sem tzinfo eles quebram a ordenação do WAL
    replay e a comparabilidade entre logs.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError(
            "timestamp deve ser timezone-aware (ISO 8601 com offset ou Z)"
        )
    return dt


# datetime canônico do WAL: sempre timezone-aware.
TZAwareDatetime = Annotated[datetime, AfterValidator(_ensure_tz_aware)]

# JSON Schema "number" = int|float (NÃO bool). ``StrictInt``/``StrictFloat``
# rejeitam ``bool`` (que em Python é subtipo de ``int`` e seria aceito por
# coerção no modo lax). Combinado com "string" → int|float|str.
NumberOrStr = StrictInt | StrictFloat | str


# --------------------------------------------------------------------------- #
# Enums canônicos (do INSTRUCTIONS.md L2259-2261, L2271, L2291, L2314)
# --------------------------------------------------------------------------- #

class Domain(str, Enum):
    """Os 10 domínios de engenharia (conteúdo variável, estrutura invariante)."""

    MECANICA = "mecanica"
    FLUIDOS = "fluidos"
    TERMO = "termo"
    ENERGIA = "energia"
    ELETRICIDADE = "eletricidade"
    MATERIAIS = "materiais"
    CONSTRUCAO = "construcao"
    AMBIENTE = "ambiente"
    NORMATIVO = "normativo"
    ECONOMICO = "economico"


# Conjunto canônico dos 10 domínios (para iteração/parametrização em testes).
VALID_DOMAINS = frozenset(d.value for d in Domain)


class Scale(str, Enum):
    """Escala M³ (Macro-Meso-Micro) — INSTRUCTIONS.md L2261, L653."""

    MACRO = "macro"
    MESO = "meso"
    MICRO = "micro"


class ValidationStatus(str, Enum):
    """Status de validação do log — INSTRUCTIONS.md L2168, L2271."""

    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class RigorStatus(str, Enum):
    """D3_rigor (PASS/FAIL) — INSTRUCTIONS.md L2291."""

    PASS = "PASS"
    FAIL = "FAIL"


class SecurityClassification(str, Enum):
    """Classificação de segurança — INSTRUCTIONS.md L2314.

    Determina encriptação e acesso (consumido em T03/T04 ao persistir).
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# --------------------------------------------------------------------------- #
# Sub-modelos
# --------------------------------------------------------------------------- #

class WalTimestamp(BaseModel):
    """Janela temporal do log (ISO 8601, timezone-aware). Required: created, started, finished."""

    model_config = _FORBID_EXTRA

    created: TZAwareDatetime
    started: TZAwareDatetime
    finished: TZAwareDatetime


class WalWhere(BaseModel):
    """Localização do log no código/config. Required: file, version."""

    model_config = _FORBID_EXTRA

    file: str
    # JSON Schema L2232: ["string","integer","null"] — integer NÃO inclui bool.
    line: str | StrictInt | None = None
    version: str
    branch: str | None = None


class WalHow(BaseModel):
    """Metodologia/ferramenta aplicada. Required: method, tool, tool_version."""

    model_config = _FORBID_EXTRA

    method: str
    tool: str
    tool_version: str
    # JSON Schema L2245: ["string","object","null"] — object = qualquer mapa JSON.
    parameters: str | dict[str, Any] | None = None
    input_files: list[str] = Field(default_factory=list)
    output_files: list[str] = Field(default_factory=list)


class Wal5W1H(BaseModel):
    """Estrutura 5W1H do log. what/why mínimo 10 caracteres."""

    model_config = _FORBID_EXTRA

    what: str = Field(min_length=10, description="Descrição exata da ação - mínimo 10 caracteres")
    why: str = Field(min_length=10, description="Justificativa técnica - mínimo 10 caracteres")
    who: str
    when: str
    where: WalWhere
    how: WalHow


class MapIndex(BaseModel):
    """Índice de navegação do log na árvore WAL. Required: project, domain, scale, task."""

    model_config = _FORBID_EXTRA

    project: str = Field(pattern=r"^PRODUTO-", description="Formato: PRODUTO-[NOME]-[VERSAO]")
    domain: Domain
    scale: Scale
    task: str = Field(pattern=r"^TASK-")
    parent_log: str | None = None
    child_logs: list[str] = Field(default_factory=list)


class ErrorMetrics(BaseModel):
    """Métricas de erro de validação (precision/convergence/fidelity).

    O schema canônico (L2274-2281) NÃO declara ``additionalProperties: false``
    para este sub-objeto — logo campos extras são aceitos, espelhando o
    contrato. Campos canônicos: precision/convergence/fidelity.
    """

    model_config = _ALLOW_EXTRA

    precision: NumberOrStr | None = None
    convergence: NumberOrStr | None = None
    fidelity: NumberOrStr | None = None


class WalValidation(BaseModel):
    """Resultado da validação. Required: status, method."""

    model_config = _FORBID_EXTRA

    status: ValidationStatus
    method: str
    reference: str | None = None
    error_metrics: ErrorMetrics | None = None


class QualityMetrics(BaseModel):
    """Métricas de qualidade D1-D10 (opcional no top-level).

    O schema canônico descreve alguns campos como ``"0-100%"`` (L2289-2298),
    porém apenas como *description* — não há ``minimum/maximum`` formais. O
    modelo NÃO inventa ranges, espelhando fielmente o contrato (futuramente
    uma emenda ao INSTRUCTIONS.md poderia elevar description a constraint).
    """

    model_config = _FORBID_EXTRA

    D1_completude: NumberOrStr | None = None
    D2_profundidade: NumberOrStr | None = None
    D3_rigor: RigorStatus | None = None
    D4_rastreabilidade: NumberOrStr | None = None
    D5_conhecimento: NumberOrStr | None = None
    D6_integracao: NumberOrStr | None = None
    D7_qualidade_numerica: NumberOrStr | None = None
    D8_impacto: NumberOrStr | None = None
    D9_vies: NumberOrStr | None = None
    D10_ensino: NumberOrStr | None = None


class Patches(BaseModel):
    """Diferencial de linhas adicionadas/removidas/modificadas.

    O schema canônico (L2304-2311) NÃO declara ``additionalProperties: false``
    para este sub-objeto — campos extras são aceitos, espelhando o contrato.
    """

    model_config = _ALLOW_EXTRA

    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    modified: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Modelo principal — WalLog
# --------------------------------------------------------------------------- #

class WalLog(BaseModel):
    """Log WAL canônico — source of truth garantista.

    Required: ``log_id``, ``timestamp``, ``5w1h``, ``map_index``, ``validation``.
    Opcionais: ``quality_metrics``, ``next_steps``, ``rag_sources``,
    ``patches``, ``security_classification``.

    Wire-format: o campo ``5w1h`` é o alias canônico. Com ``populate_by_name``
    desligado, **só** ``"5w1h"`` é aceito na entrada; com ``serialize_by_alias``
    ligado, **sempre** ``"5w1h"`` na saída. Entrada e saída são wire-format
    puro — ``model_dump_json()`` (sem args) já emite ``"5w1h"``.
    """

    # extra="forbid": additionalProperties: false (L2318). frozen: append-only.
    # serialize_by_alias: wire-format "5w1h" na saída por default.
    model_config = ConfigDict(extra="forbid", frozen=True, serialize_by_alias=True)

    log_id: str = Field(
        pattern=r"^LOG-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$",
        description="UUID v4 format (LOG-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)",
    )
    timestamp: WalTimestamp
    five_w1h: Wal5W1H = Field(alias="5w1h")
    map_index: MapIndex
    validation: WalValidation
    quality_metrics: QualityMetrics | None = None
    next_steps: list[str] | None = None
    rag_sources: list[str] | None = None
    patches: Patches | None = None
    security_classification: SecurityClassification | None = None


__all__ = [
    "VALID_DOMAINS",
    "Domain",
    "ErrorMetrics",
    "MapIndex",
    "NumberOrStr",
    "Patches",
    "QualityMetrics",
    "RigorStatus",
    "Scale",
    "SecurityClassification",
    "TZAwareDatetime",
    "ValidationStatus",
    "Wal5W1H",
    "WalHow",
    "WalLog",
    "WalTimestamp",
    "WalValidation",
    "WalWhere",
]
