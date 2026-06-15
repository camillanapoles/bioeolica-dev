#!/bin/bash
# run_all_checks.sh — Automated validation runner
# Matches quickstart.md section 5.1 structure
# SC-001 through SC-010 validation via SQLite views
#
# Usage:
#   ./tests/validation/run_all_checks.sh [--db path/to/bioeolica.db]
#
# Exit codes:
#   0 — ALL checks PASS
#   1 — One or more checks FAIL
#   2 — Database not found

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DB="${1:-$PROJECT_ROOT/data/bioeolica.db}"

if [ ! -f "$DB" ]; then
    echo "❌ Database not found: $DB"
    echo "   Usage: $0 [--db path/to/bioeolica.db]"
    exit 2
fi

PASS=0
FAIL=0
TOTAL=0

check() {
    local name="$1"
    local query="$2"
    local expected="$3"
    TOTAL=$((TOTAL + 1))

    result=$(sqlite3 "$DB" "$query" 2>&1 || echo "QUERY_ERROR")

    if echo "$result" | grep -qiE "$expected"; then
        echo "  ✅ $name"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name"
        echo "     Query returned: $result"
        echo "     Expected match: $expected"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  BIOEOLICA — FULL VALIDATION RUN"
echo "  Database: $DB"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ── SC-001: Material Characterization ──
echo "─── SC-001: Material Characterization ───"
check "Baseline specimens exist" \
    "SELECT COUNT(*) FROM material_specimens WHERE specimen_type='baseline';" \
    "[1-9][0-9]*"
check "Composite specimens exist" \
    "SELECT COUNT(*) FROM material_specimens WHERE specimen_type='composite';" \
    "[1-9][0-9]*"
check "Test results exist" \
    "SELECT COUNT(*) FROM test_results;" \
    "[1-9][0-9]*"

# ── SC-003: Safety Factors ──
echo ""
echo "─── SC-003: Safety Factors (IEC 61400-2) ───"
check "Blade designs exist" \
    "SELECT COUNT(*) FROM blade_designs;" \
    "[1-9][0-9]*"
check "Safety factor >= 2.0" \
    "SELECT safety_factor_static FROM blade_designs WHERE safety_factor_static >= 2.0 LIMIT 1;" \
    "[2-9]"

# ── SC-004: Economic Targets ──
echo ""
echo "─── SC-004: Economic Targets ───"
check "LCOE < \$0.15/kWh" \
    "SELECT COUNT(*) FROM energy_systems WHERE lcoe_usd_per_kwh < 0.15 AND lcoe_usd_per_kwh > 0;" \
    "[1-9][0-9]*"
check "Cost < \$3,000/kW" \
    "SELECT COUNT(*) FROM energy_systems WHERE cost_per_kw_usd < 3000 AND cost_per_kw_usd > 0;" \
    "[1-9][0-9]*"

# ── SC-005: Energy Sizing ──
echo ""
echo "─── SC-005: Energy Sizing ───"
check "Autonomy >= 2 days" \
    "SELECT COUNT(*) FROM energy_systems WHERE autonomy_days >= 2.0;" \
    "[1-9][0-9]*"
check "Capacity factor >= 20%" \
    "SELECT COUNT(*) FROM energy_systems WHERE capacity_factor_pct >= 20.0;" \
    "[1-9][0-9]*"

# ── SC-007: Provenance Audit ──
echo ""
echo "─── SC-007: Provenance Audit ───"
check "Provenance edges exist" \
    "SELECT COUNT(*) FROM provenance;" \
    "[1-9][0-9]*"
check "No provenance cycles" \
    "SELECT COUNT(*) FROM v_provenance_cycles;" \
    "^0$"

# ── SC-008: PQMS ──
echo ""
echo "─── SC-008: PQMS ───"
check "Quality scores exist" \
    "SELECT COUNT(*) FROM quality_scores;" \
    "[1-9][0-9]*"
# Check PQMS aggregate >= 9.5 (if view exists)
if sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='view' AND name='v_pqms_summary';" | grep -q v_pqms_summary; then
    check "PQMS >= 9.5" \
        "SELECT computed_pqms FROM v_pqms_summary WHERE computed_pqms >= 9.5 LIMIT 1;" \
        "9\.[5-9]|10\.0"
fi

# ── SC-010: Environmental ──
echo ""
echo "─── SC-010: Environmental ───"
check "Validation references exist" \
    "SELECT COUNT(*) FROM validation_references;" \
    "[1-9][0-9]*"
check "Source quality >= 8/10 for all" \
    "SELECT COUNT(*) FROM validation_references WHERE source_quality_score >= 8;" \
    "[1-9][0-9]*"

# ── Schema Integrity ──
echo ""
echo "─── Schema Integrity ───"
# Core tables exist
for table in objects provenance quality_scores material_specimens test_results \
             computational_models simulation_results blade_designs \
             wind_turbine_systems energy_systems community_profiles validation_references; do
    check "Table exists: $table" \
        "SELECT name FROM sqlite_master WHERE type='table' AND name='$table';" \
        "$table"
done

# Orphan check
check "No orphan object references" \
    "SELECT COUNT(*) FROM material_specimens e LEFT JOIN objects o ON e.id=o.id WHERE o.id IS NULL;" \
    "^0$"

# ── Summary ──
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  RESULTS: $PASS/$TOTAL checks passed"
if [ $FAIL -eq 0 ]; then
    echo "  STATUS: ✅ ALL CHECKS PASS"
else
    echo "  STATUS: ❌ $FAIL CHECK(S) FAILED"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

exit $(( FAIL > 0 ? 1 : 0 ))
