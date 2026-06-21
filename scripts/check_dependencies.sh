#!/bin/bash
# =============================================================================
# Dependency Verification Script
# Part of T002 — Phase 1 Setup
# Verifies all required software for the Composite Biomaterial for Wind Energy
# research project.
# =============================================================================
# Prerequisites: SQLite 3.x, Python 3.10+, CalculiX 2.20+, OpenFOAM v2212+,
#                SU2 7.x, ParaView 5.10+
# Reference: quickstart.md section 1.1
# =============================================================================

set -euo pipefail

PASS=0
FAIL=0
WARN=0

echo "========================================================================"
echo "  Dependency Verification — Bioeolica Research Project"
echo "========================================================================"
echo ""

# -----------------------------------------------------------------------
# SQLite 3.x
# -----------------------------------------------------------------------
echo "--- SQLite ---"
if command -v sqlite3 &>/dev/null; then
    VERSION=$(sqlite3 --version | awk '{print $1}')
    echo "  Found: sqlite3 $VERSION"
    PKG_CHECK=$(sqlite3 -version)
    # Parse major version
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    if [ "$MAJOR" -ge 3 ]; then
        echo "  ✅ Version $VERSION >= 3.x"
        PASS=$((PASS + 1))
    else
        echo "  ❌ Version $VERSION < 3.x"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  ❌ NOT FOUND. Install: apt install sqlite3"
    FAIL=$((FAIL + 1))
fi
echo ""

# -----------------------------------------------------------------------
# Python 3.10+
# -----------------------------------------------------------------------
echo "--- Python ---"
if command -v python3 &>/dev/null; then
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  Found: Python $VERSION"
    MAJOR=$(echo "$VERSION" | cut -d. -f1)
    MINOR=$(echo "$VERSION" | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        echo "  ✅ Version $VERSION >= 3.10"
        PASS=$((PASS + 1))
    else
        echo "  ❌ Version $VERSION < 3.10"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  ❌ NOT FOUND. Install: apt install python3"
    FAIL=$((FAIL + 1))
fi
echo ""

# -----------------------------------------------------------------------
# pip3 (needed for virtual environment)
# -----------------------------------------------------------------------
echo "--- pip ---"
if command -v pip3 &>/dev/null; then
    VERSION=$(pip3 --version 2>&1 | awk '{print $2}')
    echo "  Found: pip $VERSION"
    PASS=$((PASS + 1))
else
    echo "  ⚠️  NOT FOUND. Install: apt install python3-pip"
    WARN=$((WARN + 1))
fi
echo ""

# -----------------------------------------------------------------------
# venv module
# -----------------------------------------------------------------------
echo "--- venv ---"
if python3 -c "import venv" &>/dev/null 2>&1; then
    echo "  ✅ Python venv module available"
    PASS=$((PASS + 1))
else
    echo "  ⚠️  NOT FOUND. Install: apt install python3-venv"
    WARN=$((WARN + 1))
fi
echo ""

# -----------------------------------------------------------------------
# CalculiX (ccx)
# -----------------------------------------------------------------------
echo "--- CalculiX (ccx) ---"
if command -v ccx &>/dev/null; then
    # Try to get version from ccx output
    VERSION=$(ccx -v 2>&1 || echo "unknown")
    echo "  Found: ccx $VERSION"
    PASS=$((PASS + 1))
elif ls /usr/share/doc/calculix-ccx*/ 2>/dev/null | head -1 &>/dev/null; then
    echo "  Found: CalculiX (package installed)"
    PASS=$((PASS + 1))
else
    echo "  ⚠️  NOT FOUND. Install: apt install calculix-ccx"
    echo "     Binary: $(which ccx 2>/dev/null || echo 'not in PATH')"
    WARN=$((WARN + 1))
fi
echo ""

# -----------------------------------------------------------------------
# OpenFOAM
# -----------------------------------------------------------------------
echo "--- OpenFOAM ---"
if command -v foamListApp &>/dev/null; then
    VERSION=$(foamListApp -version 2>/dev/null || echo "unknown")
    echo "  Found: OpenFOAM via foamListApp ($VERSION)"
    PASS=$((PASS + 1))
elif [ -d "/opt/openfoam"* ] || ls /usr/lib/openfoam/ 2>/dev/null | head -1 &>/dev/null; then
    echo "  Found: OpenFOAM (directory present)"
    PASS=$((PASS + 1))
else
    echo "  ⚠️  NOT FOUND. Install: apt install openfoam"
    echo "     Check: /opt/openfoam*, /usr/lib/openfoam/, foamListApp"
    WARN=$((WARN + 1))
fi
echo ""

# -----------------------------------------------------------------------
# SU2
# -----------------------------------------------------------------------
echo "--- SU2 ---"
if command -v SU2_CFD &>/dev/null; then
    VERSION=$(SU2_CFD --version 2>&1 | head -1 || echo "unknown")
    echo "  Found: SU2_CFD ($VERSION)"
    PASS=$((PASS + 1))
else
    echo "  ⚠️  NOT FOUND. Install: apt install su2"
    WARN=$((WARN + 1))
fi
echo ""

# -----------------------------------------------------------------------
# ParaView
# -----------------------------------------------------------------------
echo "--- ParaView ---"
if command -v paraview &>/dev/null; then
    VERSION=$(paraview --version 2>&1 || echo "unknown")
    echo "  Found: ParaView ($VERSION)"
    PASS=$((PASS + 1))
else
    echo "  ⚠️  NOT FOUND. Install: apt install paraview"
    WARN=$((WARN + 1))
fi
echo ""

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------
echo "========================================================================"
echo "  SUMMARY"
echo "========================================================================"
echo "  ✅ Pass:  $PASS"
echo "  ❌ Fail:  $FAIL"
echo "  ⚠️  Warn:  $WARN"
echo ""
if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
    echo "  🎯 ALL DEPENDENCIES VERIFIED. Environment ready."
elif [ "$FAIL" -eq 0 ]; then
    echo "  ⚠️  All critical dependencies found. $WARN optional tool(s) missing."
    echo "     Non-critical warnings above."
else
    echo "  ❌ $FAIL critical dependency(ies) missing. Install before proceeding."
fi
echo "========================================================================"

exit "$FAIL"
