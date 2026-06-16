"""Tests for KDI Dashboard app."""

import ast, os

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "app.py")


def test_syntax():
    with open(APP_PATH) as f:
        tree = ast.parse(f.read())
    assert isinstance(tree, ast.Module)


def test_has_tabs():
    with open(APP_PATH) as f:
        content = f.read()
    for tab in ["Config", "Macro", "Meso", "Micro", "Report"]:
        assert tab in content


def test_imports():
    errs = []
    for mod in ["modules.kdi_forwarder"]:
        try:
            __import__(mod)
        except ImportError as e:
            errs.append(str(e))
    assert not errs, f"Import errors: {errs}"
