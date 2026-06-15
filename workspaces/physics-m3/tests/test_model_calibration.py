"""Tests for ModelCalibration module."""

import numpy as np
import pytest

from modules.model_calibration import ModelCalibration


def linear_model(params, x):
    return params[0] * x + params[1]


def test_init():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    assert mc.param_names == ["a", "b"]
    assert len(mc.initial_guess) == 2


def test_set_experimental_data():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    x = np.array([0, 1, 2, 3])
    y = 2.0 * x + 1.0
    mc.set_experimental_data(x, y)
    assert mc.ydata is not None


def test_calibrate_perfect():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    x = np.array([0, 1, 2, 3, 4])
    y = 2.0 * x + 1.0
    mc.set_experimental_data(x, y)
    result = mc.calibrate(method="least_squares")
    assert "params" in result
    assert np.isclose(result["params"][0], 2.0, rtol=0.01)
    assert np.isclose(result["params"][1], 1.0, rtol=0.01)


def test_calibrate_noisy():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    x = np.array([0, 1, 2, 3, 4, 5])
    y_true = 3.0 * x + 0.5
    y = y_true + np.random.normal(0, 0.2, len(x))
    mc.set_experimental_data(x, y)
    result = mc.calibrate(method="least_squares")
    assert np.isclose(result["params"][0], 3.0, rtol=0.1)
    assert np.isclose(result["params"][1], 0.5, rtol=0.3)


def test_predict():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    x = np.array([0, 1, 2])
    y = 2.0 * x + 1.0
    mc.set_experimental_data(x, y)
    mc.calibrate(method="least_squares")
    x_new = np.array([5, 6])
    y_pred = mc.predict(x_new)
    assert len(y_pred) == 2
    assert np.isclose(y_pred[0], 11.0, rtol=0.05)


def test_validate():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    x = np.array([0, 1, 2, 3, 4])
    y = 2.0 * x + 1.0
    mc.set_experimental_data(x[:3], y[:3])
    mc.calibrate(method="least_squares")
    rmse = mc.validate(x[3:], y[3:])
    assert rmse >= 0


def test_no_data_raises():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    with pytest.raises(ValueError):
        mc.calibrate(method="least_squares")


def test_recalibrate_updates():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    x = np.array([0, 1, 2])
    y = 2.0 * x + 1.0
    mc.set_experimental_data(x, y)
    r1 = mc.calibrate(method="least_squares")
    y2 = 5.0 * x + 2.0
    mc.set_experimental_data(x, y2)
    r2 = mc.calibrate(method="least_squares")
    assert not np.allclose(r1["params"], r2["params"])


def test_results_no_calibrate():
    mc = ModelCalibration(linear_model, ["a", "b"], [1.0, 0.0])
    with pytest.raises(RuntimeError):
        mc.results()
