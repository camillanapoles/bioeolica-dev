"""Testes do schema WAL (T02) — espelham o JSON Schema do INSTRUCTIONS.md L2198-2320.

TDD: estes testes foram escritos ANTES da implementação (M3) e expandidos após
os gates (tdd-guide + python-reviewer) apontarem lacunas de fidelidade e de
cobertura comportamental.

Cobrem 100% dos casos do json_schema_validation:
  - campos required vs optional
  - patterns (log_id UUID, project ^PRODUTO-, task ^TASK-)
  - enums (domain x10, scale x3, validation.status x3, D3_rigor, security_classification)
  - minLength (what/why >= 10)
  - additionalProperties: false (extra forbid onde o schema declara) E
    additionalProperties permitido onde o schema NÃO declara forbid
    (error_metrics L2274-2281, patches L2304-2311)
  - tipos strict (number = int|float SEM bool; integer SEM bool)
  - timestamps timezone-aware (format: date-time = RFC 3339)
  - wire-format "5w1h" na entrada E saída (alias canônico)
  - imutabilidade (frozen=True — WAL append-only)
  - round-trip JSON
"""

from __future__ import annotations

import copy
from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from lab_engine.wal.models import (
    VALID_DOMAINS,
    Domain,
    ErrorMetrics,
    MapIndex,
    Patches,
    QualityMetrics,
    RigorStatus,
    Scale,
    SecurityClassification,
    ValidationStatus,
    Wal5W1H,
    WalLog,
    WalTimestamp,
    WalValidation,
)

# --------------------------------------------------------------------------- #
# Helpers / Fixtures
# --------------------------------------------------------------------------- #

def _uuid_hex() -> str:
    """UUID v4 em HEX maiúsculo (compatível com o pattern LOG-[A-F0-9]{8}-...)."""
    return uuid4().hex.upper()


def _valid_log_dict() -> dict:
    """Log WAL canônico válido — só campos required (mínimo que o schema aceita).

    log_id derivado de um ÚNICO uuid4 (segmentos canônicos do mesmo UUID, não
    5 UUIDs distintos) — preserva a semântica de UUID v4 além do pattern.
    """
    h = _uuid_hex()
    return {
        "log_id": f"LOG-{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}",
        "timestamp": {
            "created": "2026-06-22T12:00:00Z",
            "started": "2026-06-22T12:00:00Z",
            "finished": "2026-06-22T12:05:00Z",
        },
        "5w1h": {
            "what": "Análise estrutural da torre via FEM",
            "why": "Verificar integridade mecânica sob carga de vento",
            "who": "agent-mecanica",
            "when": "2026-06-22T12:00:00Z a 12:05:00Z",
            "where": {
                "file": "src/cad/tower.py",
                "line": 42,
                "version": "abc1234",
                "branch": "main",
            },
            "how": {
                "method": "FEM linear",
                "tool": "calculix",
                "tool_version": "2.21",
                "parameters": {"mesh_size": 0.01},
                "input_files": ["data/tower.step"],
                "output_files": ["out/stress.csv"],
            },
        },
        "map_index": {
            "project": "PRODUTO-PMSG-100kW-001",
            "domain": "mecanica",
            "scale": "macro",
            "task": "TASK-0001",
            "parent_log": None,
            "child_logs": [],
        },
        "validation": {
            "status": "PASS",
            "method": "comparação analítica",
            "reference": "ASME BPVC VIII",
            "error_metrics": {
                "precision": 1.5,
                "convergence": 99.0,
                "fidelity": 0.95,
            },
        },
    }


@pytest.fixture
def valid_log() -> dict:
    return _valid_log_dict()


# --------------------------------------------------------------------------- #
# Aceitação — logs válidos
# --------------------------------------------------------------------------- #

class TestValidLogs:
    def test_minimal_required_log_accepted(self, valid_log):
        log = WalLog.model_validate(valid_log)
        assert log.log_id.startswith("LOG-")
        assert log.map_index.domain == Domain.MECANICA

    def test_full_log_with_all_optionals_accepted(self, valid_log):
        # Arrange — preencher TODOS os opcionais do schema.
        valid_log["quality_metrics"] = {
            "D1_completude": 95,
            "D2_profundidade": 90,
            "D3_rigor": "PASS",
            "D4_rastreabilidade": 100,
            "D5_conhecimento": 8,
            "D6_integracao": 80,
            "D7_qualidade_numerica": 97,
            "D8_impacto": 50000,
            "D9_vies": 0,
            "D10_ensino": 70,
        }
        valid_log["next_steps"] = ["refinar malha", "validar com dados de campo"]
        valid_log["rag_sources"] = ["ASME BPVC VIII 2023"]
        valid_log["patches"] = {
            "added": ["src/cad/tower.py:10"],
            "removed": [],
            "modified": ["src/cad/tower.py:5"],
        }
        valid_log["security_classification"] = "internal"
        # Act — validar o payload completo (todos os opcionais).
        log = WalLog.model_validate(valid_log)
        # Assert — opcionais parseados nos tipos canônicos esperados.
        assert log.quality_metrics.D3_rigor == RigorStatus.PASS
        assert log.security_classification == SecurityClassification.INTERNAL

    @pytest.mark.parametrize("domain", list(VALID_DOMAINS))
    def test_all_10_domains_accepted(self, valid_log, domain):
        valid_log["map_index"]["domain"] = domain
        log = WalLog.model_validate(valid_log)
        assert log.map_index.domain.value == domain

    @pytest.mark.parametrize("scale", [s.value for s in Scale])
    def test_all_3_scales_accepted(self, valid_log, scale):
        valid_log["map_index"]["scale"] = scale
        log = WalLog.model_validate(valid_log)
        assert log.map_index.scale.value == scale

    @pytest.mark.parametrize("status", [s.value for s in ValidationStatus])
    def test_all_validation_statuses_accepted(self, valid_log, status):
        valid_log["validation"]["status"] = status
        log = WalLog.model_validate(valid_log)
        assert log.validation.status.value == status

    @pytest.mark.parametrize("rigor", [s.value for s in RigorStatus])
    def test_all_d3_rigor_values_accepted(self, valid_log, rigor):
        valid_log["quality_metrics"] = {"D3_rigor": rigor}
        log = WalLog.model_validate(valid_log)
        assert log.quality_metrics.D3_rigor.value == rigor

    @pytest.mark.parametrize("sec", [s.value for s in SecurityClassification])
    def test_all_security_classifications_accepted(self, valid_log, sec):
        valid_log["security_classification"] = sec
        log = WalLog.model_validate(valid_log)
        assert log.security_classification.value == sec

    def test_parent_log_optional_none(self, valid_log):
        log = WalLog.model_validate(valid_log)
        assert log.map_index.parent_log is None


# --------------------------------------------------------------------------- #
# Rejeição — patterns
# --------------------------------------------------------------------------- #

class TestPatternRejection:
    def test_log_id_not_uuid_rejected(self, valid_log):
        valid_log["log_id"] = "LOG-not-a-uuid"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_log_id_lowercase_hex_rejected(self, valid_log):
        # pattern exige [A-F0-9] maiúsculo
        h = uuid4().hex  # minúsculo
        valid_log["log_id"] = f"LOG-{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_log_id_missing_LOG_prefix_rejected(self, valid_log):
        h = _uuid_hex()
        valid_log["log_id"] = f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_project_missing_PREFIX_rejected(self, valid_log):
        valid_log["map_index"]["project"] = "PMSG-100kW-001"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_task_missing_PREFIX_rejected(self, valid_log):
        valid_log["map_index"]["task"] = "0001"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)


# --------------------------------------------------------------------------- #
# Rejeição — minLength (what/why >= 10)
# --------------------------------------------------------------------------- #

class TestMinLength:
    def test_what_too_short_rejected(self, valid_log):
        valid_log["5w1h"]["what"] = "curta"  # 5 chars
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_why_too_short_rejected(self, valid_log):
        valid_log["5w1h"]["why"] = "pq sim"  # 6 chars
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_what_exactly_10_accepted(self, valid_log):
        valid_log["5w1h"]["what"] = "0123456789"  # exatamente 10
        WalLog.model_validate(valid_log)  # não levanta


# --------------------------------------------------------------------------- #
# Rejeição — enums
# --------------------------------------------------------------------------- #

class TestEnumRejection:
    def test_domain_invalid_rejected(self, valid_log):
        valid_log["map_index"]["domain"] = "quantica"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_scale_invalid_rejected(self, valid_log):
        valid_log["map_index"]["scale"] = "nano"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_validation_status_invalid_rejected(self, valid_log):
        valid_log["validation"]["status"] = "MAYBE"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_security_classification_invalid_rejected(self, valid_log):
        valid_log["security_classification"] = "topsecret"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_d3_rigor_invalid_rejected(self, valid_log):
        valid_log["quality_metrics"] = {"D3_rigor": "INDETERMINADO"}
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)


# --------------------------------------------------------------------------- #
# Rejeição — additionalProperties: false (extra forbid onde o schema declara)
# --------------------------------------------------------------------------- #

class TestExtraForbidden:
    def test_unknown_top_level_field_rejected(self, valid_log):
        valid_log["foo"] = "bar"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_5w1h_field_rejected(self, valid_log):
        valid_log["5w1h"]["extra"] = "x"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_where_field_rejected(self, valid_log):
        valid_log["5w1h"]["where"]["extra"] = "x"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_how_field_rejected(self, valid_log):
        valid_log["5w1h"]["how"]["extra"] = "x"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_map_index_field_rejected(self, valid_log):
        valid_log["map_index"]["extra"] = "x"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_timestamp_field_rejected(self, valid_log):
        # WalTimestamp declara additionalProperties: false (schema L2217).
        valid_log["timestamp"]["extra"] = "x"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_quality_metrics_field_rejected(self, valid_log):
        valid_log["quality_metrics"] = {"D11_inexistente": 10}
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_unknown_validation_field_rejected(self, valid_log):
        # WalValidation declara additionalProperties: false (schema L2283).
        valid_log["validation"]["extra"] = "x"
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)


# --------------------------------------------------------------------------- #
# Aceitação — additionalProperties permitido onde o schema NÃO declara forbid
# (error_metrics L2274-2281 e patches L2304-2311)
# --------------------------------------------------------------------------- #

class TestExtraAllowed:
    def test_error_metrics_accepts_extra_field(self, valid_log):
        # O schema canônico NÃO declara additionalProperties: false em
        # error_metrics — campos extras são aceitos (fidelidade ao contrato).
        valid_log["validation"]["error_metrics"] = {
            "precision": 1.5,
            "custom_metric": "sob medida",
        }
        log = WalLog.model_validate(valid_log)
        assert log.validation.error_metrics.precision == 1.5

    def test_patches_accepts_extra_field(self, valid_log):
        valid_log["patches"] = {
            "added": ["a.py:1"],
            "reviewer_note": "merge trivial",
        }
        log = WalLog.model_validate(valid_log)
        assert log.patches.added == ["a.py:1"]


# --------------------------------------------------------------------------- #
# Rejeição — tipos strict (number/integer SEM bool)
# --------------------------------------------------------------------------- #

class TestStrictTypes:
    def test_bool_in_number_metric_rejected(self, valid_log):
        # JSON Schema "number" = int|float, NÃO bool. Em Python bool é subtipo
        # de int; StrictInt/StrictFloat rejeitam para espelhar o schema.
        valid_log["validation"]["error_metrics"] = {"precision": True}
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_bool_in_quality_metric_rejected(self, valid_log):
        valid_log["quality_metrics"] = {"D1_completude": True}
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_bool_in_line_rejected(self, valid_log):
        # JSON Schema L2232: ["string","integer","null"] — sem bool.
        valid_log["5w1h"]["where"]["line"] = True
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_int_and_float_and_str_in_number_metric_accepted(self, valid_log):
        valid_log["validation"]["error_metrics"] = {
            "precision": 1,        # int
            "convergence": 99.5,   # float
            "fidelity": "0.95",    # str
        }
        log = WalLog.model_validate(valid_log)
        assert log.validation.error_metrics.precision == 1
        assert log.validation.error_metrics.convergence == 99.5
        assert log.validation.error_metrics.fidelity == "0.95"

    def test_line_as_string_accepted(self, valid_log):
        # JSON Schema admite line como string.
        valid_log["5w1h"]["where"]["line"] = "42-50"
        log = WalLog.model_validate(valid_log)
        assert log.five_w1h.where.line == "42-50"

    def test_line_as_none_accepted(self, valid_log):
        valid_log["5w1h"]["where"]["line"] = None
        log = WalLog.model_validate(valid_log)
        assert log.five_w1h.where.line is None


# --------------------------------------------------------------------------- #
# Rejeição — timestamps devem ser timezone-aware (format: date-time, RFC 3339)
# --------------------------------------------------------------------------- #

class TestTimezoneAware:
    def test_naive_created_rejected(self, valid_log):
        valid_log["timestamp"]["created"] = "2026-06-22T12:00:00"  # sem offset
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_naive_finished_rejected(self, valid_log):
        valid_log["timestamp"]["finished"] = "2026-06-22T12:05:00"  # sem offset
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_zulu_offset_accepted(self, valid_log):
        log = WalLog.model_validate(valid_log)
        assert log.timestamp.created.tzinfo is not None

    def test_numeric_offset_accepted(self, valid_log):
        valid_log["timestamp"]["created"] = "2026-06-22T09:00:00-03:00"
        log = WalLog.model_validate(valid_log)
        # offset numérico aceito → datetime timezone-aware com utcoffset não-nulo
        assert log.timestamp.created.tzinfo is not None
        assert log.timestamp.created.utcoffset() is not None


# --------------------------------------------------------------------------- #
# Rejeição — required faltantes
# --------------------------------------------------------------------------- #

class TestMissingRequired:
    def test_missing_log_id_rejected(self, valid_log):
        del valid_log["log_id"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_timestamp_missing_finished_rejected(self, valid_log):
        del valid_log["timestamp"]["finished"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_where_missing_file_rejected(self, valid_log):
        del valid_log["5w1h"]["where"]["file"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_where_missing_version_rejected(self, valid_log):
        del valid_log["5w1h"]["where"]["version"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_how_missing_method_rejected(self, valid_log):
        del valid_log["5w1h"]["how"]["method"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_how_missing_tool_version_rejected(self, valid_log):
        del valid_log["5w1h"]["how"]["tool_version"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_validation_missing_method_rejected(self, valid_log):
        del valid_log["validation"]["method"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)

    def test_map_index_missing_scale_rejected(self, valid_log):
        del valid_log["map_index"]["scale"]
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)


# --------------------------------------------------------------------------- #
# Wire-format: o alias "5w1h" é canônico na entrada E na saída
# --------------------------------------------------------------------------- #

class TestWireFormat:
    def test_default_serialization_uses_5w1h_alias(self, valid_log):
        # serialize_by_alias=True: mesmo SEM by_alias, a saída emite "5w1h".
        log = WalLog.model_validate(valid_log)
        dumped = log.model_dump_json()
        assert '"5w1h"' in dumped
        assert "five_w1h" not in dumped

    def test_python_name_field_rejected_on_input(self, valid_log):
        # populate_by_name desligado: só "5w1h" é aceito na entrada.
        five = valid_log.pop("5w1h")
        valid_log["five_w1h"] = five
        with pytest.raises(ValidationError):
            WalLog.model_validate(valid_log)


# --------------------------------------------------------------------------- #
# Round-trip JSON (serialização estável)
# --------------------------------------------------------------------------- #

class TestRoundTrip:
    def test_json_round_trip_preserves_data(self, valid_log):
        # Arrange — log WAL canônico a partir do dict.
        log = WalLog.model_validate(valid_log)
        # Act — serializar (wire-format) e desserializar de volta.
        dumped = log.model_dump_json(by_alias=True)  # wire-format WAL usa "5w1h"
        restored = WalLog.model_validate_json(dumped)
        # Assert — round-trip sem perda; alias canônico preservado no JSON.
        assert '"5w1h"' in dumped  # alias canônico preservado
        assert restored.log_id == log.log_id
        assert restored.map_index.domain == log.map_index.domain
        assert restored.validation.status == log.validation.status

    def test_timestamp_parsed_as_datetime(self, valid_log):
        log = WalLog.model_validate(valid_log)
        assert isinstance(log.timestamp.created, datetime)
        # timezone-aware (Z = UTC)
        assert log.timestamp.created.tzinfo is not None

    def test_parent_log_round_trip(self, valid_log):
        valid_log["map_index"]["parent_log"] = "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
        log = WalLog.model_validate(valid_log)
        restored = WalLog.model_validate_json(log.model_dump_json(by_alias=True))
        assert restored.map_index.parent_log.startswith("LOG-")


# --------------------------------------------------------------------------- #
# Fidelidade JSON Schema: o schema GERADO pelo Pydantic deve refletir o
# canônico do INSTRUCTIONS.md L2198-2319 (DoD T02: "Round-trip JSON Schema
# <-> Pydantic"). Cada asserção espelha uma cláusula do contrato canônico.
# --------------------------------------------------------------------------- #

class TestSchemaFidelity:
    """DoD T02: o JSON Schema gerado pelos modelos é fiel ao canônico."""

    def test_wallog_required_top_level(self):
        s = WalLog.model_json_schema(by_alias=True)
        assert set(s["required"]) == {"log_id", "timestamp", "5w1h", "map_index", "validation"}

    def test_wallog_top_level_additional_properties_false(self):
        # INSTRUCTIONS.md L2318: additionalProperties: false no nível raiz.
        s = WalLog.model_json_schema(by_alias=True)
        assert s["additionalProperties"] is False

    def test_wallog_uses_alias_5w1h_in_schema(self):
        # O schema canônico usa "5w1h" (não "five_w1h").
        s = WalLog.model_json_schema(by_alias=True)
        assert "5w1h" in s["properties"]
        assert "five_w1h" not in s["properties"]

    def test_timestamp_required_and_forbid(self):
        # L2211: required created/started/finished; L2217: additionalProperties false.
        s = WalTimestamp.model_json_schema()
        assert set(s["required"]) == {"created", "started", "finished"}
        assert s["additionalProperties"] is False

    def test_where_required_and_forbid(self):
        # L2229: required file/version; L2236: forbid.
        s = Wal5W1H.model_json_schema()["properties"]["where"]
        # where é $ref — resolve via $defs
        defs = Wal5W1H.model_json_schema().get("$defs", {})
        where = defs.get("WalWhere", s)
        assert set(where["required"]) == {"file", "version"}
        assert where["additionalProperties"] is False

    def test_how_required_and_forbid(self):
        # L2240: required method/tool/tool_version; L2249: forbid.
        defs = Wal5W1H.model_json_schema()["$defs"]
        how = defs["WalHow"]
        assert set(how["required"]) == {"method", "tool", "tool_version"}
        assert how["additionalProperties"] is False

    def test_map_index_required_patterns_and_forbid(self):
        # L2256: required project/domain/scale/task; L2258/2261: patterns; L2265: forbid.
        s = MapIndex.model_json_schema()
        assert set(s["required"]) == {"project", "domain", "scale", "task"}
        assert s["properties"]["project"]["pattern"] == "^PRODUTO-"
        assert s["properties"]["task"]["pattern"] == "^TASK-"
        assert s["additionalProperties"] is False

    def test_validation_required_status_method_and_forbid(self):
        # L2269: required status/method; L2283: forbid.
        s = WalValidation.model_json_schema()
        assert set(s["required"]) == {"status", "method"}
        assert s["additionalProperties"] is False

    def test_quality_metrics_forbid(self):
        # L2300: forbid em quality_metrics.
        s = QualityMetrics.model_json_schema()
        assert s["additionalProperties"] is False

    def test_error_metrics_allows_extra(self):
        # L2274-2281: o schema canônico NÃO declara forbid em error_metrics.
        s = ErrorMetrics.model_json_schema()
        assert s.get("additionalProperties", True) is not False

    def test_patches_allows_extra(self):
        # L2304-2311: o schema canônico NÃO declara forbid em patches.
        s = Patches.model_json_schema()
        assert s.get("additionalProperties", True) is not False

    def test_log_id_pattern_canonical(self):
        s = WalLog.model_json_schema(by_alias=True)
        assert s["properties"]["log_id"]["pattern"] == (
            r"^LOG-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$"
        )

    def test_domain_enum_has_10_values(self):
        s = MapIndex.model_json_schema()
        # enums viram $ref para $defs/<EnumName>.
        assert set(s["$defs"]["Domain"]["enum"]) == VALID_DOMAINS
        assert len(s["$defs"]["Domain"]["enum"]) == 10

    def test_scale_enum_has_3_values(self):
        s = MapIndex.model_json_schema()
        assert set(s["$defs"]["Scale"]["enum"]) == {"macro", "meso", "micro"}

    def test_validation_status_enum(self):
        s = WalValidation.model_json_schema()
        assert s["$defs"]["ValidationStatus"]["enum"] == ["PASS", "FAIL", "PENDING"]

    def test_d3_rigor_enum(self):
        s = QualityMetrics.model_json_schema()
        assert s["$defs"]["RigorStatus"]["enum"] == ["PASS", "FAIL"]

    def test_security_classification_enum(self):
        s = WalLog.model_json_schema(by_alias=True)
        assert set(s["$defs"]["SecurityClassification"]["enum"]) == {
            "public", "internal", "confidential", "restricted",
        }

    def test_what_and_why_min_length_10(self):
        s = Wal5W1H.model_json_schema()
        assert s["properties"]["what"]["minLength"] == 10
        assert s["properties"]["why"]["minLength"] == 10


# --------------------------------------------------------------------------- #
# Imutabilidade: WAL é append-only (frozen=True) + fixture não vaza
# --------------------------------------------------------------------------- #

def test_model_is_frozen_and_fixture_independent(valid_log):
    # Arrange — snapshot do dict + log instanciado.
    snapshot = copy.deepcopy(valid_log)
    log = WalLog.model_validate(valid_log)
    # Act/Assert — WAL é append-only: mutação direta é proibida (frozen).
    with pytest.raises(ValidationError):
        log.map_index.domain = Domain.FLUIDOS
    # Act — derivar uma variação via model_copy NÃO muta a fixture original.
    derived = log.model_copy(
        update={"map_index": log.map_index.model_copy(update={"domain": Domain.FLUIDOS})}
    )
    # Assert — variação derivada tem o novo domínio e a fixture original (dict) não foi mutada.
    assert derived.map_index.domain == Domain.FLUIDOS
    assert valid_log["map_index"]["domain"] == snapshot["map_index"]["domain"]
