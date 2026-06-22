"""Testes formais do Auditor WAL (T04) — ``lab_engine.wal.auditor``.

DoD T04 (parte auditor): detecta 4 anomalias (INSTRUCTIONS.md L2001-2006, L2318).
D4 (Rastreabilidade) exige "zero logs com status PENDING > 24h" e "nenhum log
ORPHAN ou ABANDONADO não resolvido" (L2002/L2004). O auditor emite um
``AuditReport`` classificando cada anomalia por tipo:

- ``PENDING_STALE`` (L2002/L2004) — ``validation.status == PENDING`` E
  ``timestamp.created`` anterior a ``now - 24h``.
- ``ORPHAN`` (L2002) — ``map_index.parent_log`` não-None E inexistente no store.
- ``ABANDONED`` (L2002) — ``PENDING`` que é **folha** (sem logs filhos): análise
  iniciada, nunca retomada (definição operacional — D-T04.4).
- ``SCHEMA_BREACH`` (L2001) — payload que falha re-validação Pydantic (drift
  pós-emenda, corrupção).

Determinismo: ``now`` é injetável (testes não dependem de relógio real).
Property-based (hypothesis) prova invariantes estruturais.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from lab_engine.wal.auditor import (
    AnomalyType,
    WalAuditor,
)
from lab_engine.wal.store import WalLogRow

# Instante canônico dos testes — determinismo (não depende de relógio real).
NOW = datetime(2026, 6, 22, 12, 0, tzinfo=UTC)


def _iso(dt: datetime) -> str:
    """ISO 8601 string (formato aceito pelo ``make_log``)."""
    return dt.isoformat()


# --------------------------------------------------------------------------- #
# PENDING_STALE (L2002/L2004)
# --------------------------------------------------------------------------- #


class TestPendingStale:
    def test_pending_older_than_24h_is_stale(self, repo, session, make_log):
        # Arrange — PENDING criado há 25h
        repo.create(
            make_log(
                status="PENDING",
                created=_iso(NOW - timedelta(hours=25)),
            )
        )
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        stale = [a for a in report.anomalies if a.type is AnomalyType.PENDING_STALE]
        assert len(stale) == 1

    def test_pending_recent_is_not_stale(self, repo, session, make_log):
        # Arrange — PENDING criado há 1h (dentro da janela)
        repo.create(
            make_log(status="PENDING", created=_iso(NOW - timedelta(hours=1)))
        )
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — 0 PENDING_STALE (mas pode ser ABANDONED; isolamos o tipo)
        assert not any(a.type is AnomalyType.PENDING_STALE for a in report.anomalies)

    def test_pass_old_is_not_stale(self, repo, session, make_log):
        # Arrange — PASS criado há 30h (só PENDING é stale)
        repo.create(
            make_log(status="PASS", created=_iso(NOW - timedelta(hours=30)))
        )
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        assert report.anomalies == ()

    def test_custom_stale_threshold(self, repo, session, make_log):
        # Arrange — PENDING há 2h; threshold custom = 1h
        repo.create(
            make_log(status="PENDING", created=_iso(NOW - timedelta(hours=2)))
        )
        session.commit()
        # Act — threshold agressivo (1h)
        report = WalAuditor(
            session, now=NOW, pending_stale_after=timedelta(hours=1)
        ).audit()
        # Assert
        assert any(a.type is AnomalyType.PENDING_STALE for a in report.anomalies)


# --------------------------------------------------------------------------- #
# ORPHAN (L2002)
# --------------------------------------------------------------------------- #


class TestOrphan:
    def test_child_with_missing_parent_is_orphan(self, repo, session, make_log):
        # Arrange — child aponta para parent que NÃO existe no store
        missing_parent = "LOG-00000000-0000-0000-0000-000000000000"
        repo.create(make_log(parent_log=missing_parent))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        orphans = [a for a in report.anomalies if a.type is AnomalyType.ORPHAN]
        assert len(orphans) == 1

    def test_child_with_existing_parent_is_not_orphan(
        self, repo, session, make_log
    ):
        # Arrange — parent existe; child aponta para ele
        parent_id = "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEE0000"
        repo.create(make_log(log_id=parent_id))
        repo.create(make_log(parent_log=parent_id))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — 0 ORPHAN (cadeia intacta)
        assert not any(a.type is AnomalyType.ORPHAN for a in report.anomalies)

    def test_root_log_is_never_orphan(self, repo, session, make_log):
        # Arrange — root (parent_log=None)
        repo.create(make_log(parent_log=None))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — root não pode ser orphan (não tem parent a quebrar)
        assert not any(a.type is AnomalyType.ORPHAN for a in report.anomalies)


# --------------------------------------------------------------------------- #
# ABANDONED (L2002) — PENDING sem desdobramento (folha)
# --------------------------------------------------------------------------- #


class TestAbandoned:
    def test_pending_leaf_is_abandoned(self, repo, session, make_log):
        # Arrange — PENDING sem filhos (folha da árvore WAL)
        repo.create(make_log(status="PENDING"))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        abandoned = [a for a in report.anomalies if a.type is AnomalyType.ABANDONED]
        assert len(abandoned) == 1

    def test_pending_with_child_is_not_abandoned(
        self, repo, session, make_log
    ):
        # Arrange — PENDING que TEM filho (tem desdobramento)
        parent_id = "LOG-BBBBBBBB-BBBB-CCCC-DDDD-EEEEEEEE0000"
        repo.create(make_log(log_id=parent_id, status="PENDING"))
        repo.create(make_log(parent_log=parent_id))  # filho → parent não é folha
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — parent PENDING tem filho → não é abandoned
        parent_anoms = [
            a for a in report.anomalies
            if a.log_id == parent_id and a.type is AnomalyType.ABANDONED
        ]
        assert parent_anoms == []

    def test_pass_leaf_is_not_abandoned(self, repo, session, make_log):
        # Arrange — PASS folha (só PENDING abandoned)
        repo.create(make_log(status="PASS"))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        assert not any(a.type is AnomalyType.ABANDONED for a in report.anomalies)


# --------------------------------------------------------------------------- #
# SCHEMA_BREACH (L2001) — payload falha re-validação
# --------------------------------------------------------------------------- #


class TestSchemaBreach:
    def test_corrupt_payload_is_breach(self, session):
        # Arrange — row direta com payload inválido (bypass do store.create)
        bad = WalLogRow(
            log_id="LOG-DEADBEEF-DEAD-BEEF-DEAD-BEEFDEADBEEF",
            project="PRODUTO-X",
            domain="mecanica",
            scale="macro",
            task="TASK-X",
            parent_log=None,
            validation_status="PASS",
            created_at=NOW,
            payload={"garbage": "não é um WalLog válido"},
        )
        session.add(bad)
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        breaches = [a for a in report.anomalies if a.type is AnomalyType.SCHEMA_BREACH]
        assert len(breaches) == 1
        assert breaches[0].log_id == "LOG-DEADBEEF-DEAD-BEEF-DEAD-BEEFDEADBEEF"

    def test_valid_payload_is_not_breach(self, repo, session, make_log):
        # Arrange
        repo.create(make_log())
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — 0 SCHEMA_BREACH (pode haver ABANDONED; isolamos o tipo)
        assert not any(a.type is AnomalyType.SCHEMA_BREACH for a in report.anomalies)


# --------------------------------------------------------------------------- #
# AuditReport — agregação
# --------------------------------------------------------------------------- #


class TestAuditReport:
    def test_total_logs_counted(self, repo, session, make_log):
        # Arrange — 3 logs válidos
        for _ in range(3):
            repo.create(make_log(status="PASS"))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        assert report.total_logs == 3

    def test_report_metadata(self, repo, session, make_log):
        # Arrange
        repo.create(make_log(status="PASS"))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — metadados do relatório
        assert report.generated_at == NOW
        assert report.pending_stale_after == timedelta(hours=24)

    def test_counts_by_type(self, repo, session, make_log):
        # Arrange — 1 PENDING stale (também abandoned) + 1 orphan
        repo.create(
            make_log(
                status="PENDING",
                created=_iso(NOW - timedelta(hours=30)),
            )
        )
        repo.create(make_log(parent_log="LOG-00000000-0000-0000-0000-000000000000"))
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        counts = report.counts
        # Assert
        assert counts[AnomalyType.PENDING_STALE] >= 1
        assert counts[AnomalyType.ORPHAN] >= 1

    def test_log_with_multiple_anomalies(self, repo, session, make_log):
        # Arrange — 1 log que é PENDING stale E abandoned E orphan simultaneamente
        repo.create(
            make_log(
                status="PENDING",
                created=_iso(NOW - timedelta(hours=30)),
                parent_log="LOG-00000000-0000-0000-0000-000000000000",
            )
        )
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — 3 anomalias (tipos distintos) sobre o MESMO log
        types = {a.type for a in report.anomalies}
        assert AnomalyType.PENDING_STALE in types
        assert AnomalyType.ABANDONED in types
        assert AnomalyType.ORPHAN in types

    def test_empty_store_clean_report(self, session):
        # Act — store vazio
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        assert report.total_logs == 0
        assert report.anomalies == ()


# --------------------------------------------------------------------------- #
# Property-based (hypothesis) — invariantes estruturais do auditor
# --------------------------------------------------------------------------- #


class TestAuditorPropertyBased:
    @given(status=st.sampled_from(["PASS", "FAIL"]))
    @settings(
        max_examples=15,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_resolved_status_never_pending_anomaly(
        self, repo, session, make_log, status: str
    ):
        # Arrange — PASS/FAIL antigo (48h)
        repo.create(
            make_log(status=status, created=_iso(NOW - timedelta(hours=48)))
        )
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert — invariante: PASS/FAIL nunca são PENDING_STALE nem ABANDONED
        assert not any(a.type is AnomalyType.PENDING_STALE for a in report.anomalies)
        assert not any(a.type is AnomalyType.ABANDONED for a in report.anomalies)


# --------------------------------------------------------------------------- #
# Boundary do threshold PENDING_STALE (> 24h) — casos determinísticos
# --------------------------------------------------------------------------- #


class TestPendingStaleBoundary:
    @pytest.mark.parametrize(
        ("age_hours", "expected_stale"),
        [
            (0.0, False),  # agora
            (23.0, False),  # dentro da janela
            (24.0, False),  # exatamente no threshold (NÃO stale — comparação estrita <)
            (24.001, True),  # mal acima do threshold
            (25.0, True),  # claramente stale
            (168.0, True),  # 1 semana
        ],
    )
    def test_threshold_boundary(
        self, repo, session, make_log, age_hours: float, expected_stale: bool
    ):
        # Arrange — PENDING há exatamente age_hours
        repo.create(
            make_log(
                status="PENDING",
                created=_iso(NOW - timedelta(hours=age_hours)),
            )
        )
        session.commit()
        # Act
        report = WalAuditor(session, now=NOW).audit()
        # Assert
        is_stale = any(a.type is AnomalyType.PENDING_STALE for a in report.anomalies)
        assert is_stale is expected_stale
