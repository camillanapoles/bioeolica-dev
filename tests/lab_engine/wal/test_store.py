"""Testes formais do WAL store (T03.4) — repository CRUD sobre SQLAlchemy 2.0.

DoD T03.4: CRUD 6 ops (create/read/update/list/by_parent/by_task) + commit/rollback
(caller gerencia transação) + round-trip WalLog (fidelidade wire-format ``5w1h``) +
by-parent/by-task + **injection negativo** (prova queries parametrizadas — 0
string-concat). Cobertura ≥80% em ``lab_engine.wal.store``.

Cobertura (M3): cada operação do ``WalRepository`` + helpers internos
(``_to_row``, ``_get_row``, ``_rows_to_logs``) + branchs de erro
(``LogDuplicateError``, ``LogNotFoundError``, ``ValueError`` de update).

Segurança: a classe ``TestSqlInjection`` prova que input malicioso em filtros
(``list``/``by_parent``/``by_task``/``read``) é tratado como **literal** (queries
parametrizadas SQLAlchemy 2.0) — nenhuma execução de SQL, tabela intacta.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session, sessionmaker

from lab_engine.wal.models import Scale, ValidationStatus, WalValidation
from lab_engine.wal.store import (
    LogDuplicateError,
    LogNotFoundError,
    WalRepository,
)

# --------------------------------------------------------------------------- #
# create + read
# --------------------------------------------------------------------------- #


class TestCreateRead:
    def test_create_returns_log_and_read_recovers_it(self, repo, session, make_log):
        # Arrange
        log = make_log()
        # Act
        returned = repo.create(log)
        session.commit()
        recovered = repo.read(log.log_id)
        # Assert — create retorna o próprio log; read desserializa do payload
        assert returned is log
        assert recovered is not None
        assert recovered.log_id == log.log_id

    def test_create_duplicate_raises(self, repo, make_log):
        # Arrange
        log = make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")
        repo.create(log)
        # Act / Assert — mesmo log_id de novo → LogDuplicateError
        with pytest.raises(LogDuplicateError):
            repo.create(log)

    def test_read_unknown_returns_none(self, repo):
        # Act / Assert
        assert repo.read("LOG-00000000-0000-0000-0000-000000000000") is None


# --------------------------------------------------------------------------- #
# update (substituição de row + consistência de PK)
# --------------------------------------------------------------------------- #


class TestUpdate:
    def test_update_replaces_all_indexed_columns(self, repo, session, make_log):
        # Arrange — log original (macro, TASK-0001, PASS, sem parent)
        original = make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")
        repo.create(original)
        # new_log: muda scale, task, parent_log, status, created_at — mesma PK
        new_ts = original.timestamp.model_copy(
            update={"created": datetime(2026, 6, 23, 10, 0, tzinfo=UTC)}
        )
        new_map = original.map_index.model_copy(
            update={
                "scale": Scale.MICRO,
                "task": "TASK-9999",
                "parent_log": "LOG-PARENT-0000-0000-0000-000000000000",
            }
        )
        new_log = original.model_copy(
            update={
                "map_index": new_map,
                "validation": WalValidation(
                    status=ValidationStatus.FAIL, method="método revisado"
                ),
                "timestamp": new_ts,
            }
        )
        # Act
        repo.update(original.log_id, new_log)
        session.commit()
        # Assert — read reflete TODAS as colunas indexadas substituídas
        recovered = repo.read(original.log_id)
        assert recovered is not None
        assert recovered.map_index.scale is Scale.MICRO
        assert recovered.map_index.task == "TASK-9999"
        assert recovered.map_index.parent_log == "LOG-PARENT-0000-0000-0000-000000000000"
        assert recovered.validation.status is ValidationStatus.FAIL
        assert recovered.timestamp.created == datetime(
            2026, 6, 23, 10, 0, tzinfo=UTC
        )

    def test_update_with_mismatched_log_id_raises_value_error(self, repo, make_log):
        # Arrange
        log = make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")
        repo.create(log)
        other = make_log()  # log_id aleatório ≠ do persistido
        # Act / Assert — consistência da PK violada → ValueError
        with pytest.raises(ValueError):
            repo.update(log.log_id, other)

    def test_update_unknown_raises_not_found(self, repo, make_log):
        # Arrange
        log = make_log(log_id="LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")
        # Act / Assert — log_id inexistente → LogNotFoundError
        with pytest.raises(LogNotFoundError):
            repo.update(log.log_id, log)


# --------------------------------------------------------------------------- #
# list (filtros AND + paginação)
# --------------------------------------------------------------------------- #


class TestList:
    def test_list_returns_all_when_no_filter(self, repo, session, make_log):
        # Arrange
        for _ in range(3):
            repo.create(make_log())
        session.commit()
        # Act / Assert
        assert len(repo.list()) == 3

    def test_list_filters_by_domain_and_scale(self, repo, session, make_log):
        # Arrange
        repo.create(make_log(domain="mecanica", scale="macro"))
        repo.create(make_log(domain="mecanica", scale="micro"))
        repo.create(make_log(domain="fluidos", scale="macro"))
        session.commit()
        # Act / Assert — filtro AND
        mecanica_macro = repo.list(domain="mecanica", scale="macro")
        assert len(mecanica_macro) == 1
        all_mecanica = repo.list(domain="mecanica")
        assert len(all_mecanica) == 2

    def test_list_paginates_with_limit_offset(self, repo, session, make_log):
        # Arrange
        for _ in range(5):
            repo.create(make_log())
        session.commit()
        # Act / Assert — página 1 (limit=2) + página 2 (offset=2)
        page1 = repo.list(limit=2, offset=0)
        page2 = repo.list(limit=2, offset=2)
        assert len(page1) == 2
        assert len(page2) == 2
        # sem overlap de log_ids
        ids1 = {log.log_id for log in page1}
        ids2 = {log.log_id for log in page2}
        assert ids1.isdisjoint(ids2)

    def test_list_filters_by_parent_log_and_status(self, repo, session, make_log):
        # Arrange
        repo.create(make_log(parent_log="LOG-PARENT-0000-0000-0000-000000000000"))
        repo.create(make_log(status="PENDING"))
        session.commit()
        # Act / Assert
        children = repo.list(parent_log="LOG-PARENT-0000-0000-0000-000000000000")
        assert len(children) == 1
        pending = repo.list(validation_status="PENDING")
        assert len(pending) == 1

    def test_list_filters_by_task(self, repo, session, make_log):
        # Arrange
        repo.create(make_log(task="TASK-0001"))
        repo.create(make_log(task="TASK-0002"))
        session.commit()
        # Act / Assert — filtro task (cobre o branch de filtro por task do list)
        assert len(repo.list(task="TASK-0001")) == 1


# --------------------------------------------------------------------------- #
# by_parent / by_task
# --------------------------------------------------------------------------- #


class TestByParentByTask:
    def test_by_parent_returns_direct_children(self, repo, session, make_log):
        # Arrange
        parent_id = "LOG-AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
        repo.create(make_log(log_id=parent_id))
        repo.create(make_log(parent_log=parent_id))
        repo.create(make_log(parent_log=parent_id))
        repo.create(make_log())  # órfão (sem parent)
        session.commit()
        # Act / Assert
        children = repo.by_parent(parent_id)
        assert len(children) == 2
        assert all(c.map_index.parent_log == parent_id for c in children)

    def test_by_parent_empty_when_no_children(self, repo, session, make_log):
        # Arrange
        repo.create(make_log())  # sem filhos
        session.commit()
        # Act / Assert
        assert repo.by_parent("LOG-00000000-0000-0000-0000-000000000000") == []

    def test_by_task_returns_all_logs_of_task(self, repo, session, make_log):
        # Arrange
        for _ in range(3):
            repo.create(make_log(task="TASK-0077"))
        repo.create(make_log(task="TASK-0088"))
        session.commit()
        # Act / Assert
        logs = repo.by_task("TASK-0077")
        assert len(logs) == 3
        assert all(log.map_index.task == "TASK-0077" for log in logs)


# --------------------------------------------------------------------------- #
# commit / rollback (transação é do caller)
# --------------------------------------------------------------------------- #


class TestCommitRollback:
    def test_commit_persists_across_sessions(self, engine, make_log):
        # Arrange — session 1 (escreve + commit)
        factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
        sess1: Session = factory()
        log = make_log()
        # Act
        WalRepository(sess1).create(log)
        sess1.commit()
        sess1.close()
        # Assert — session 2 (nova) enxerga o log persistido
        sess2: Session = factory()
        recovered = WalRepository(sess2).read(log.log_id)
        sess2.close()
        assert recovered is not None
        assert recovered.log_id == log.log_id

    def test_rollback_discards_uncommitted(self, engine, make_log):
        # Arrange — session 1 (escreve SEM commit)
        factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
        sess1: Session = factory()
        log = make_log()
        # Act
        WalRepository(sess1).create(log)
        sess1.rollback()  # descarta
        sess1.close()
        # Assert — session 2 não vê o log (rollback descartou)
        sess2: Session = factory()
        assert WalRepository(sess2).read(log.log_id) is None
        sess2.close()


# --------------------------------------------------------------------------- #
# Round-trip — fidelidade do wire-format (alias "5w1h", tz-aware, enums, nested)
# --------------------------------------------------------------------------- #


class TestRoundTripFidelity:
    def test_roundtrip_preserves_canonical_wire_format(
        self, repo, session, make_log
    ):
        # Arrange
        original = make_log()
        original_dump = original.model_dump(mode="json", by_alias=True)
        # Act
        repo.create(original)
        session.commit()
        recovered = repo.read(original.log_id)
        # Assert
        assert recovered is not None
        recovered_dump = recovered.model_dump(mode="json", by_alias=True)
        # dump idêntico (fidelidade total do wire-format)
        assert recovered_dump == original_dump
        # alias canônico "5w1h" preservado (não "five_w1h")
        assert "5w1h" in recovered_dump
        # datetime tz-aware preservado (AfterValidator de T02 no round-trip)
        assert recovered.timestamp.created.tzinfo is not None
        # enum preservado
        assert recovered.map_index.domain.value == original.map_index.domain.value
        # nested preservado (parameters do how; error_metrics)
        assert recovered.five_w1h.how.parameters == {"mesh_size": 0.01}
        assert recovered.validation.error_metrics is not None
        assert recovered.validation.error_metrics.precision == 1.5


# --------------------------------------------------------------------------- #
# Injection negativo — queries parametrizadas (0 string-concat)
# --------------------------------------------------------------------------- #


class TestSqlInjection:
    """Prova que filtros/recebem strings crus são tratados como LITERAL.

    O vetor de injection relevante no store são os **filtros** (``list``,
    ``by_parent``, ``by_task``, ``read``) — eles recebem ``str`` sem validação
    Pydantic. Queries SQLAlchemy 2.0 (``col == :value``) parametrizam: o input
    jamais é concatenado ao SQL. Cada teste confirma (a) 0 execução de SQL
    malicioso e (b) tabela ``wal_logs`` intacta.
    """

    @staticmethod
    def _table_intact(engine) -> bool:
        return "wal_logs" in inspect(engine).get_table_names()

    def test_by_task_with_injection_is_literal(self, repo, engine, make_log):
        # Arrange — log válido persistido
        repo.create(make_log(task="TASK-0001"))
        # Act — tentativa de injection via filtro (str cru, não validado)
        malicious = "TASK-0001'; DROP TABLE wal_logs; --"
        results = repo.by_task(malicious)
        # Assert — tratado como literal: 0 resultados; tabela intacta
        assert results == []
        assert self._table_intact(engine)

    def test_by_parent_with_injection_is_literal(self, repo, engine, make_log):
        # Arrange
        repo.create(make_log())
        # Act
        malicious = "LOG-x' OR '1'='1"
        assert repo.by_parent(malicious) == []
        # Assert — tabela intacta (não houve execução de SQL arbitrário)
        assert self._table_intact(engine)

    def test_read_with_injection_is_literal(self, repo, engine):
        # Act — log_id malicioso tratado como literal (retorna None, não executa)
        assert repo.read("' UNION SELECT * FROM wal_logs --") is None
        # Assert
        assert self._table_intact(engine)

    def test_list_project_with_injection_is_literal(self, repo, engine, make_log):
        # Arrange
        repo.create(make_log())
        # Act
        malicious = "PRODUTO-X' OR '1'='1"
        assert repo.list(project=malicious) == []
        # Assert
        assert self._table_intact(engine)
