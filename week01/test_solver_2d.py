"""Week 01 test suite.

Run with:   pytest test_solver_2d.py -v
Quiet mode: pytest test_solver_2d.py -q
Filter:     pytest -q -k laplacian
            pytest -q -k drift

Each function is one verifiable physical claim (slides: M1–M4 pytest slides).
"""

import numpy as np
import pytest

from solver_2d import (
    compute_l2,
    enforce_dirichlet,
    laplacian_2d,
    reference,
    relative_energy_drift,
)


# ---------------------------------------------------------------------------
# enforce_dirichlet
# ---------------------------------------------------------------------------

def test_enforce_dirichlet_sets_all_boundaries_to_zero() -> None:
    u = np.ones((5, 6))
    enforce_dirichlet(u)

    assert np.allclose(u[0, :], 0.0)
    assert np.allclose(u[-1, :], 0.0)
    assert np.allclose(u[:, 0], 0.0)
    assert np.allclose(u[:, -1], 0.0)


def test_enforce_dirichlet_preserves_interior() -> None:
    u = np.ones((5, 5))
    enforce_dirichlet(u)

    assert np.all(u[1:-1, 1:-1] == 1.0), "Interior values must not change"


# ---------------------------------------------------------------------------
# laplacian_2d — shape and sanity checks (M2 slides)
# ---------------------------------------------------------------------------

def test_laplacian_shape_matches_input() -> None:
    """laplacian_2d output must have the same shape as the input."""
    u = np.random.rand(10, 10)
    lap = laplacian_2d(u, dx=0.1, dy=0.1)
    assert lap.shape == u.shape, f"shape mismatch: {lap.shape} != {u.shape}"


def test_laplacian_constant_field_is_zero() -> None:
    """∇²(constant) = 0 everywhere on interior."""
    nx, ny = 12, 14
    u = np.ones((nx, ny))
    lap = laplacian_2d(u, dx=0.05, dy=0.05)
    assert np.allclose(lap[1:-1, 1:-1], 0.0), \
        "Constant field must yield zero Laplacian"


def test_laplacian_linear_field_is_zero() -> None:
    """∇²(ax + by) = 0 everywhere on interior."""
    nx, ny = 12, 14
    x = np.linspace(0.0, 1.0, nx)
    y = np.linspace(0.0, 1.0, ny)
    X, Y = np.meshgrid(x, y, indexing="ij")
    u = 3.0 * X + 2.0 * Y
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    lap = laplacian_2d(u, dx=dx, dy=dy)
    assert np.allclose(lap[1:-1, 1:-1], 0.0, atol=1e-10), \
        "Linear field must yield zero Laplacian"


def test_laplacian_boundary_rows_are_zero() -> None:
    """Boundary rows/cols of laplacian_2d output must be zero."""
    u = np.random.rand(8, 9)
    lap = laplacian_2d(u, dx=0.1, dy=0.1)
    assert np.allclose(lap[0, :], 0.0)
    assert np.allclose(lap[-1, :], 0.0)
    assert np.allclose(lap[:, 0], 0.0)
    assert np.allclose(lap[:, -1], 0.0)


# ---------------------------------------------------------------------------
# relative_energy_drift (M4 slides)
# ---------------------------------------------------------------------------

def test_relative_energy_drift_identical_fields_is_zero() -> None:
    """Drift between identical fields must be zero."""
    u = np.random.rand(10, 10)
    drift = relative_energy_drift(u, u)
    assert drift == pytest.approx(0.0, abs=1e-12), \
        f"Drift between identical fields must be 0, got {drift}"


def test_relative_energy_drift_is_non_negative() -> None:
    u0 = np.random.rand(8, 8)
    u1 = np.random.rand(8, 8)
    drift = relative_energy_drift(u0, u1)
    assert drift >= 0.0, f"Drift must be non-negative, got {drift}"


def test_relative_energy_drift_zero_initial_energy() -> None:
    """Epsilon guard prevents division by zero when E0 ≈ 0."""
    u0 = np.zeros((6, 6))
    u1 = np.ones((6, 6))
    drift = relative_energy_drift(u0, u1)
    assert np.isfinite(drift), "Drift must be finite when E0=0 (eps guard)"


# ---------------------------------------------------------------------------
# compute_l2 (Week 02 interface stub)
# ---------------------------------------------------------------------------

def test_compute_l2_happy_path_returns_float() -> None:
    u_num = np.array([[1.0, 2.0], [3.0, 4.0]])
    u_ref = np.array([[1.0, 1.0], [1.0, 1.0]])

    result = compute_l2(u_num, u_ref, dx=0.5, dy=0.5)

    assert isinstance(result, float)
    assert result > 0.0


def test_compute_l2_raises_on_shape_mismatch() -> None:
    u_num = np.zeros((2, 2))
    u_ref = np.zeros((3, 2))

    with pytest.raises(ValueError, match="Shape mismatch"):
        compute_l2(u_num, u_ref, dx=1.0, dy=1.0)


def test_compute_l2_identical_fields_is_zero() -> None:
    u = np.random.rand(5, 5)
    result = compute_l2(u, u, dx=0.1, dy=0.1)
    assert result == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# reference interface (Week 02 stub)
# ---------------------------------------------------------------------------

def test_reference_interface_returns_matching_shape() -> None:
    x = np.zeros((3, 4))
    y = np.zeros((3, 4))

    u_ref = reference(x, y, t=0.0)

    assert u_ref.shape == x.shape
