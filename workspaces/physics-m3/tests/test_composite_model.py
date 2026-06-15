"""Tests for composite_model module."""

import numpy as np
import pytest
from modules.composite_model import CompositeMaterial


def test_composite_init():
    c = CompositeMaterial(E_fiber=200, E_matrix=3, V_f=0.5)
    assert c.V_f == 0.5


def test_composite_e1():
    c = CompositeMaterial(E_fiber=200, E_matrix=3, V_f=0.5)
    e1 = c.E1
    expected = 200 * 0.5 + 3 * 0.5
    assert np.isclose(e1, expected)


def test_composite_e2_positive():
    c = CompositeMaterial(E_fiber=200, E_matrix=3, V_f=0.5)
    assert c.E2 > 0
