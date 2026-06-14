# =============================================================================
# Database Connection Module — Composite Biomaterial for Wind Energy
# Part of T010 — Phase 2 Foundational
# Reference: contracts/schema-core.sql, contracts/schema-entities.sql
# =============================================================================
"""
SQLite database connection and schema management.

Database location: data/bioeolica.db (WAL mode, foreign_keys ON)

Usage:
    with database() as db:
        db.execute("SELECT * FROM objects")
"""
import os
import sqlite3
import hashlib
from typing import Optional

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "bioeolica.db",
)

SCHEMA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "specs",
    "001-composite-wind-energy",
    "contracts",
)

SCHEMA_FILES = [
    "schema-core.sql",
    "schema-entities.sql",
    "schema-validation.sql",
    "pqms-interface.sql",
]

REQUIRED_MIGRATIONS = {1, 2, 3, 4}  # Expected applied migration versions


class DatabaseError(Exception):
    """Raised on database-level failures (connection, schema mismatch, integrity)."""
    pass


def get_connection() -> sqlite3.Connection:
    """Create a configured connection to the project database.

    Returns:
        sqlite3.Connection with WAL mode, foreign_keys enforcement,
        and 5-second busy timeout applied.

    Raises:
        DatabaseError: if the database file does not exist.
    """
    if not os.path.exists(DB_PATH):
        raise DatabaseError(f"Database not found at {DB_PATH}. Run schema deployment first.")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.row_factory = sqlite3.Row
    return conn


class database:
    """Context manager for safe, auto-closing database access.

    Example:
        with database() as db:
            cursor = db.execute("SELECT * FROM objects")
    """

    def __enter__(self) -> sqlite3.Connection:
        self.conn = get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.close()


def check_schema_version() -> dict:
    """Verify all required migrations are applied.

    Returns:
        dict with keys:
            - applied: set of version ints found in schema_migrations
            - missing: set of versions in REQUIRED_MIGRATIONS not yet applied
            - expected: REQUIRED_MIGRATIONS (for reference)
            - ok: True if all required migrations are applied
    """
    try:
        with database() as db:
            rows = db.execute(
                "SELECT version FROM schema_migrations WHERE status = 'APPLIED'"
            ).fetchall()
        applied = {r["version"] for r in rows}
    except Exception:
        return {"applied": set(), "missing": REQUIRED_MIGRATIONS, "expected": REQUIRED_MIGRATIONS, "ok": False}

    missing = REQUIRED_MIGRATIONS - applied
    return {
        "applied": applied,
        "missing": missing,
        "expected": REQUIRED_MIGRATIONS,
        "ok": len(missing) == 0,
    }


def deploy_schema() -> dict:
    """Deploy all contract SQL files in dependency order.

    Deploys schema-core → schema-entities → schema-validation → pqms-interface.
    Each file's SHA-256 is recorded in schema_migrations.

    Returns:
        dict with keys:
            - deployed: list of file names deployed
            - errors: list of (file, error_message) tuples on failure
            - ok: True if all files deployed without error
    """
    deployed = []
    errors = []

    for sql_file in SCHEMA_FILES:
        filepath = os.path.join(SCHEMA_DIR, sql_file)
        if not os.path.exists(filepath):
            errors.append((sql_file, "File not found"))
            continue

        with open(filepath, "rb") as f:
            content = f.read()
        checksum = hashlib.sha256(content).hexdigest()

        try:
            conn = get_connection()
            conn.executescript(content.decode("utf-8"))
            conn.execute(
                """INSERT INTO schema_migrations (description, applied_at, checksum, status)
                   VALUES (?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), ?, 'APPLIED')""",
                (sql_file, checksum),
            )
            conn.commit()
            conn.close()
            deployed.append(sql_file)
        except Exception as e:
            errors.append((sql_file, str(e)))

    return {"deployed": deployed, "errors": errors, "ok": len(errors) == 0}
