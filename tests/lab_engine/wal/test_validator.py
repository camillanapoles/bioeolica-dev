"""Testes formais do validador garantista (T04) — ``lab_engine.wal.validator``.

DoD T04 (parte validador): nenhum log inválido entra no BD. ``validate`` aplica
``auto_fix`` (log_id, ``timestamp.created`` — INSTRUCTIONS.md L2325) **antes** de
``WalLog.model_validate`` (D-T04.1), cobrindo o ``validation_behavior`` canônico:

- ``on_invalid`` (L2322) → **REJECT** + erros estruturados (campos faltantes,
  tipos incorretos, padrões não-casados).
- ``on_unknown_field`` (L2324) → **REJECT** (campos fora do schema).
- ``on_missing_optional`` (L2323) → **ACCEPT** (opcionais ausentes viram null).
- ``auto_fix`` (L2325) → gera log_id se fora do padrão; preenche
  ``timestamp.created`` se vazio.

Segurança: ``validate`` **não muta** o input do caller (deepcopy); ``auto_fix``
é conservador (só preenche ausentes — timestamp tz-aware permanece invariante
de T02, não é auto-fixable). Property-based (hypothesis) prova invariantes.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from lab_engine.wal.models import WalLog
from lab_engine.wal.validator import (
    ValidationErrorItem,
    ValidationResult,
    validate,
)

# --------------------------------------------------------------------------- #
# validate — caminho feliz (log válido → ACCEPT)
# --------------------------------------------------------------------------- #


class TestValidateValid:
    def test_valid_log_returns_ok_with_instance(self, canonical_log: dict[str, Any]):
        # Act
        result = validate(canonical_log)
        # Assert — valid=True, log instanciado, sem erros, sem auto_fixes
        assert result.valid is True
        assert isinstance(result.log, WalLog)
        assert result.errors == ()
        assert result.auto_fixes == ()

    def test_valid_log_preserves_log_id(self, canonical_log: dict[str, Any]):
        # Arrange
        canonical_log["log_id"] = "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
        # Act
        result = validate(canonical_log)
        # Assert — log_id presente e válido NÃO é sobrescrito pelo auto_fix
        assert result.valid is True
        assert result.log is not None
        assert result.log.log_id == "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"

    def test_input_dict_not_mutated(self, canonical_log: dict[str, Any]):
        # Arrange — snapshot do input antes da validação
        before = {k: v for k, v in canonical_log.items()}
        # Act
        validate(canonical_log)
        # Assert — validate NÃO muta o dict do caller (imutabilidade)
        assert canonical_log == before


# --------------------------------------------------------------------------- #
# auto_fix — log_id + timestamp.created (INSTRUCTIONS.md L2325)
# --------------------------------------------------------------------------- #


class TestAutoFix:
    def test_generates_log_id_when_missing(self, canonical_log: dict[str, Any]):
        # Arrange — log sem log_id
        canonical_log.pop("log_id")
        # Act
        result = validate(canonical_log)
        # Assert — log_id gerado, válido, auto_fix documentado
        assert result.valid is True
        assert result.log is not None
        assert result.log.log_id.startswith("LOG-")
        assert len(result.log.log_id) == 40  # LOG- + 8-4-4-4-12 hex + 4 hífens
        assert any("log_id" in fix for fix in result.auto_fixes)

    def test_generates_log_id_when_pattern_invalid(self, canonical_log: dict[str, Any]):
        # Arrange — log_id fora do padrão LOG-UUID
        canonical_log["log_id"] = "log-invalido-sem-padrao"
        # Act
        result = validate(canonical_log)
        # Assert — regenerado para padrão canônico
        assert result.valid is True
        assert result.log is not None
        assert result.log.log_id != "log-invalido-sem-padrao"
        assert result.log.log_id.startswith("LOG-")
        assert any("log_id" in fix for fix in result.auto_fixes)

    def test_fills_timestamp_created_when_missing(self, canonical_log: dict[str, Any]):
        # Arrange — timestamp.created ausente (started/finished presentes)
        canonical_log["timestamp"].pop("created")
        # Act
        result = validate(canonical_log, now=datetime(2026, 6, 22, 12, 0, tzinfo=UTC))
        # Assert — preenchido com momento da validação, tz-aware
        assert result.valid is True
        assert result.log is not None
        assert result.log.timestamp.created == datetime(2026, 6, 22, 12, 0, tzinfo=UTC)
        assert any("created" in fix for fix in result.auto_fixes)

    def test_preserves_valid_timestamp_created(self, canonical_log: dict[str, Any]):
        # Arrange — created presente e válido
        canonical_log["timestamp"]["created"] = "2026-06-20T08:00:00Z"
        # Act
        result = validate(canonical_log, now=datetime(2026, 6, 22, 12, 0, tzinfo=UTC))
        # Assert — auto_fix NÃO sobrescreve valor presente
        assert result.valid is True
        assert result.log is not None
        assert result.log.timestamp.created == datetime(2026, 6, 20, 8, 0, tzinfo=UTC)
        assert not any("created" in fix for fix in result.auto_fixes)

    def test_auto_fixes_empty_when_nothing_to_fix(self, canonical_log: dict[str, Any]):
        # Arrange — log canônico completo (log_id + created presentes)
        # Act
        result = validate(canonical_log)
        # Assert — nenhum auto_fix aplicado
        assert result.auto_fixes == ()

    def test_does_not_auto_fix_naive_timestamp(self, canonical_log: dict[str, Any]):
        # Arrange — created presente mas inválido (naive datetime → invariante T02)
        canonical_log["timestamp"]["created"] = "2026-06-20T08:00:00"  # sem offset
        # Act
        result = validate(canonical_log, now=datetime(2026, 6, 22, 12, 0, tzinfo=UTC))
        # Assert — auto_fix NÃO mascara o erro; validação rejeita (timestamp tz-aware é invariante)
        assert result.valid is False
        assert any("timezone" in e.msg.lower() or "tz" in e.msg.lower() for e in result.errors)


# --------------------------------------------------------------------------- #
# on_invalid (L2322) — REJECT com erros estruturados
# --------------------------------------------------------------------------- #


class TestOnInvalidReject:
    def test_rejects_short_what(self, canonical_log: dict[str, Any]):
        # Arrange — what < 10 caracteres (minLength do schema L2223)
        canonical_log["5w1h"]["what"] = "curto"
        # Act
        result = validate(canonical_log)
        # Assert
        assert result.valid is False
        assert result.log is None
        assert len(result.errors) >= 1
        assert any("what" in e.loc for e in result.errors)

    def test_rejects_invalid_domain_enum(self, canonical_log: dict[str, Any]):
        # Arrange — domain fora do enum dos 10 domínios (L2259)
        canonical_log["map_index"]["domain"] = "quimica"  # não-canônico
        # Act
        result = validate(canonical_log)
        # Assert
        assert result.valid is False
        assert any("domain" in e.loc for e in result.errors)

    def test_rejects_missing_required_field(self, canonical_log: dict[str, Any]):
        # Arrange — remove campo required (validation.status)
        canonical_log["validation"].pop("status")
        # Act
        result = validate(canonical_log)
        # Assert
        assert result.valid is False
        assert any("status" in e.loc for e in result.errors)

    def test_rejects_bad_project_pattern(self, canonical_log: dict[str, Any]):
        # Arrange — project não casa ^PRODUTO- (L2258)
        canonical_log["map_index"]["project"] = "OUTRO-FORMATO-001"
        # Act
        result = validate(canonical_log)
        # Assert
        assert result.valid is False
        assert any("project" in e.loc for e in result.errors)

    def test_errors_are_structured(self, canonical_log: dict[str, Any]):
        # Arrange — múltiplas violações (what curto + why curto)
        canonical_log["5w1h"]["what"] = "x"
        canonical_log["5w1h"]["why"] = "y"
        # Act
        result = validate(canonical_log)
        # Assert — ValidationErrorItem com loc/msg/type (estrutura para correção)
        assert result.valid is False
        assert all(isinstance(e, ValidationErrorItem) for e in result.errors)
        assert all(e.loc and e.msg and e.type for e in result.errors)
        locs = {"".join(e.loc) for e in result.errors}
        assert "what" in "".join(locs) or any("what" in e.loc for e in result.errors)


# --------------------------------------------------------------------------- #
# on_unknown_field (L2324) — REJECT campos fora do schema
# --------------------------------------------------------------------------- #


class TestOnUnknownFieldReject:
    def test_rejects_extra_top_level_field(self, canonical_log: dict[str, Any]):
        # Arrange — campo desconhecido no top-level (additionalProperties: false L2318)
        canonical_log["campo_surpresa"] = "malicioso"
        # Act
        result = validate(canonical_log)
        # Assert
        assert result.valid is False
        assert any("campo_surpresa" in e.loc for e in result.errors)

    def test_rejects_extra_nested_field(self, canonical_log: dict[str, Any]):
        # Arrange — campo extra em where (additionalProperties: false L2236)
        canonical_log["5w1h"]["where"]["blob_inesperado"] = 123
        # Act
        result = validate(canonical_log)
        # Assert
        assert result.valid is False


# --------------------------------------------------------------------------- #
# on_missing_optional (L2323) — ACCEPT (opcionais → null)
# --------------------------------------------------------------------------- #


class TestOnMissingOptionalAccept:
    def test_accepts_log_without_quality_metrics(self, canonical_log: dict[str, Any]):
        # Arrange — quality_metrics ausente (opcional L2287)
        canonical_log.pop("quality_metrics", None)
        # Act / Assert
        assert validate(canonical_log).valid is True

    def test_accepts_log_without_optional_blocks(self, canonical_log: dict[str, Any]):
        # Arrange — remove TODOS os opcionais (quality_metrics, patches, etc.)
        optional_blocks = (
            "quality_metrics",
            "next_steps",
            "rag_sources",
            "patches",
            "security_classification",
        )
        for opt in optional_blocks:
            canonical_log.pop(opt, None)
        # Act / Assert — aceito (on_missing_optional = ACCEPT L2323)
        result = validate(canonical_log)
        assert result.valid is True


# --------------------------------------------------------------------------- #
# parse — dict / str-JSON / bytes-JSON
# --------------------------------------------------------------------------- #


class TestParseInputForms:
    def test_parses_json_string(self, canonical_log: dict[str, Any]):
        # Arrange
        import json

        raw = json.dumps(canonical_log)
        # Act / Assert
        result = validate(raw)
        assert result.valid is True

    def test_parses_json_bytes(self, canonical_log: dict[str, Any]):
        # Arrange
        import json

        raw = json.dumps(canonical_log).encode("utf-8")
        # Act / Assert
        result = validate(raw)
        assert result.valid is True

    def test_rejects_malformed_json(self):
        # Act
        result = validate("{not valid json")
        # Assert — erro de parse estruturado (não exceção quebrando o caller)
        assert result.valid is False
        assert result.log is None
        assert len(result.errors) == 1

    def test_rejects_non_object_json(self):
        # Act — JSON válido mas array (não objeto)
        result = validate("[1, 2, 3]")
        # Assert
        assert result.valid is False

    def test_rejects_unsupported_input_type(self):
        # Act — int não é dict/str/bytes
        result = validate(42)  # type: ignore[arg-type]
        # Assert
        assert result.valid is False


# --------------------------------------------------------------------------- #
# Property-based (hypothesis) — invariantes do validador
# --------------------------------------------------------------------------- #


class TestValidatorPropertyBased:
    @given(valid_domain=st.sampled_from(["mecanica", "fluidos", "termo"]))
    @settings(
        max_examples=25,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_canonical_log_always_valid_across_domains(
        self, canonical_log: dict[str, Any], valid_domain: str
    ):
        # Arrange — varia apenas o domínio (um dos 10 canônicos)
        canonical_log["map_index"]["domain"] = valid_domain
        # Act / Assert — invariante: log canônico é sempre válido
        result = validate(canonical_log)
        assert result.valid is True

    @given(
        bad_log_id=st.text(min_size=1, max_size=20).filter(
            lambda s: not s.startswith("LOG-")
        )
    )
    @settings(
        max_examples=25,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_bad_log_id_always_auto_fixed(
        self, canonical_log: dict[str, Any], bad_log_id: str
    ):
        # Arrange — log_id fora do padrão (qualquer string sem LOG-)
        canonical_log["log_id"] = bad_log_id
        # Act
        result = validate(canonical_log)
        # Assert — invariante: auto_fix sempre regenera para padrão canônico
        assert result.valid is True
        assert result.log is not None
        assert result.log.log_id.startswith("LOG-")
        assert any("log_id" in fix for fix in result.auto_fixes)

    @given(valid_scale=st.sampled_from(["macro", "meso", "micro"]))
    @settings(
        max_examples=15,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_valid_scale_never_rejected(
        self, canonical_log: dict[str, Any], valid_scale: str
    ):
        # Arrange
        canonical_log["map_index"]["scale"] = valid_scale
        # Act / Assert — invariante: escalas canônicas sempre aceitas
        assert validate(canonical_log).valid is True


# --------------------------------------------------------------------------- #
# ValidationResult — API do dataclass (factory methods)
# --------------------------------------------------------------------------- #


class TestValidationResultApi:
    def test_ok_factory(self, canonical_log: dict[str, Any]):
        # Act
        log = WalLog.model_validate(canonical_log)
        result = ValidationResult.ok(log)
        # Assert
        assert result.valid is True
        assert result.log is log
        assert result.errors == ()

    def test_reject_factory(self):
        # Act
        err = ValidationErrorItem(loc=("x",), msg="bad", type="value_error")
        result = ValidationResult.reject([err])
        # Assert
        assert result.valid is False
        assert result.log is None
        assert result.errors == (err,)

    def test_result_is_frozen(self, canonical_log: dict[str, Any]):
        # Act
        result = validate(canonical_log)
        # Assert — frozen dataclass (imutabilidade do WAL)
        with pytest.raises((AttributeError, Exception)):
            result.valid = False  # type: ignore[misc]
