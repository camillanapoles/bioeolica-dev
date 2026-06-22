"""create wal_logs

Revision ID: 0001
Revises:
Create Date: 2026-06-22 00:00:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria ``wal_logs`` — tabela WAL source-of-truth (D-T03.1 híbrido).

    Colunas indexadas de navegação + ``payload`` JSON (wire-format Pydantic
    completo). Espelha fielmente ``WalLogRow`` em ``lab_engine/wal/store.py``.
    """
    op.create_table(
        "wal_logs",
        sa.Column("log_id", sa.String(length=64), nullable=False),
        sa.Column("project", sa.String(length=128), nullable=False),
        sa.Column("domain", sa.String(length=32), nullable=False),
        sa.Column("scale", sa.String(length=16), nullable=False),
        sa.Column("task", sa.String(length=128), nullable=False),
        sa.Column("parent_log", sa.String(length=64), nullable=True),
        sa.Column("validation_status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("log_id"),
    )
    op.create_index("ix_wal_logs_project", "wal_logs", ["project"])
    op.create_index("ix_wal_logs_domain", "wal_logs", ["domain"])
    op.create_index("ix_wal_logs_scale", "wal_logs", ["scale"])
    op.create_index("ix_wal_logs_task", "wal_logs", ["task"])
    op.create_index("ix_wal_logs_parent_log", "wal_logs", ["parent_log"])
    op.create_index("ix_wal_logs_validation_status", "wal_logs", ["validation_status"])
    op.create_index("ix_wal_logs_created_at", "wal_logs", ["created_at"])
    op.create_index(
        "ix_wal_logs_project_domain_scale", "wal_logs", ["project", "domain", "scale"]
    )
    op.create_index("ix_wal_logs_parent_task", "wal_logs", ["parent_log", "task"])


def downgrade() -> None:
    """Remove ``wal_logs`` (índices primeiro, depois a tabela)."""
    op.drop_index("ix_wal_logs_parent_task", table_name="wal_logs")
    op.drop_index("ix_wal_logs_project_domain_scale", table_name="wal_logs")
    op.drop_index("ix_wal_logs_created_at", table_name="wal_logs")
    op.drop_index("ix_wal_logs_validation_status", table_name="wal_logs")
    op.drop_index("ix_wal_logs_parent_log", table_name="wal_logs")
    op.drop_index("ix_wal_logs_task", table_name="wal_logs")
    op.drop_index("ix_wal_logs_scale", table_name="wal_logs")
    op.drop_index("ix_wal_logs_domain", table_name="wal_logs")
    op.drop_index("ix_wal_logs_project", table_name="wal_logs")
    op.drop_table("wal_logs")
