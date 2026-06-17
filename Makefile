# Bioeólica Dev — Makefile
# Usage: make setup test coverage clean

.PHONY: setup test lint coverage clean install-docs

# ─── Setup ──────────────────────────────────────────────────────────────
setup:
	pip install -e workspaces/physics-m3 -e workspaces/cad-cae-platform -e workspaces/kdi-m3-bridge
	pip install pytest pytest-cov ruff

# ─── Test ────────────────────────────────────────────────────────────────
test:
	cd workspaces/physics-m3 && python -m pytest tests/ -v --tb=short -p no:xdist

test-quick:
	cd workspaces/physics-m3 && python -m pytest tests/test_benchmarks/ tests/test_vvv_multiscale/ -v --tb=short

test-kdi:
	cd workspaces/kdi-m3-bridge && python -m pytest tests/ -v --tb=short

# ─── Coverage ─────────────────────────────────────────────────────────────
coverage:
	cd workspaces/physics-m3 && python -m pytest tests/ --cov=src/physics_m3 --cov=modules --cov-report=term-missing

# ─── Lint ─────────────────────────────────────────────────────────────────
lint:
	ruff check workspaces/physics-m3/src workspaces/physics-m3/modules workspaces/physics-m3/tests || true

# ─── Clean ────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .coverage coverage/ 2>/dev/null || true

# ─── Docs ─────────────────────────────────────────────────────────────────
install-docs:
	@echo "System dependencies:"
	@echo "  - CalculiX (ccx): apt-get install calculix-ccx"
	@echo "  - Gmsh: apt-get install gmsh"
	@echo "  - libGLU: apt-get install libglu1-mesa"
	@echo "See docs/INSTALL.md for details"
