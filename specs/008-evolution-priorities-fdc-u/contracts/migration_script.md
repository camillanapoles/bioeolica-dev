# Contract: `scripts/migrate_unify_db.py`

> CLI script to consolidate all SQLite databases into `data/bioeolica.db`.

## Interface

```
usage: scripts/migrate_unify_db.py [-h] [--dry-run] [--backup-dir DIR] [--force]

Consolidate all databases into data/bioeolica.db.

positional arguments:
  (none — targets auto-detected from repo)

options:
  -h, --help            show this help message and exit
  --dry-run             Report what would be migrated without writing (default: False)
  --backup-dir DIR      Backup directory for pre-migration snapshots (default: data/backup/)
  --force               Skip confirmation prompt (default: False)
```

## Behavior

1. Auto-detect DBs: glob `./bioeolica.db`, `data/database.db`
2. Verify `data/bioeolica.db` is the canonical (has data, 16 tables)
3. Dry-run mode: print table-by-table diff between source and target
4. Real mode: backup → attach source → INSERT OR IGNORE → DETACH → verify
5. Symlink source paths to canonical for backward compat (optional)
6. Exit codes: 0 = OK, 1 = conflict, 2 = error

## Conflict Resolution

- Rows with same PK in both DBs: keep row with latest `updated_at` timestamp
- Log conflicts to stdout in dry-run mode
- In real mode: `INSERT OR REPLACE` with timestamp-based tiebreaker

## Post-Migration Verification

- Row count consistency: target_rows ≥ source_rows (no data loss)
- Table count: target has union of all source tables
- SHA-256 checksum before/after hash matches expected
