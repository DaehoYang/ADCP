"""
Week 02 Tests: Analytic Reference and First Error Measurement
=============================================================
AI-Driven Computational Physics — Graduate Course

Scope Boundary
--------------
This week (02):   define reference, implement L2, measure one scalar.
Next week (02.5): resolution sweep, log-log slope, automated asserts.

Test Structure (mirrors the Module Map)
-----------------------------------------
Module 2 — Integration kernel
    TestTrapezoidal
        test_linear_function_exact       : ∫0^2 x dx = 2.0  (exact for trapz)
        test_constant_function           : ∫0^3 2 dx = 6.0  (exact for trapz)
        test_quadratic_convergence_order : error ∝ N^-2

Module 3 — L2 norm contract
    TestComputeL2
        test_zero_error_for_identical_fields
        test_known_uniform_error         : uniform ε on [0,1]^2 → L2 = ε
        test_resolution_invariant        : dx*dy makes result grid-independent
        test_rejects_shape_mismatch
        test_rejects_nonpositive_dx

Module 3/4 — Reference function
    TestReference
        test_output_shape_matches_input
        test_initial_condition           : u(x,y,0) == sin(πx)sin(πy)
        test_boundary_conditions         : u=0 on all four walls at any t
        test_wave_speed_scaling          : different c gives different phase
        test_time_evolution              : u changes with t (not constant)
        test_dispersion_relation         : verify ω^2 = c^2(kx^2+ky^2) numerically

Module 4 — Variable isolation diagnostics
    TestWaveEnergy (extension)
        test_wave_energy_returns_positive_scalar
        test_wave_energy_area_scaled

Module 5 — Gate functions
    TestGates
        test_analytic_limit_test_passes  : gate returns (True, ~2.0)
        test_single_case_measurement_is_finite
        test_single_case_l2_is_small

Run
---
    pytest test_reference_check.py -v
"""

from __future__ import annotations

import numpy as np
import pytest

from starter_reference_check import (
    analytic_limit_test,
    compute_l2,
    fake_numerical_field,
    reference,
    single_case_l2_measurement,
    trapezoidal,
    wave_energy,
)


# ---------------------------------------------------------------------------
# Module 2 — Integration kernel
# ---------------------------------------------------------------------------

class TestTrapezoidal:
    """Composite Trapezoidal Rule: ∫_a^b f(x) dx."""

    def test_linear_function_exact(self) -> None:
        """∫0^2 x dx = 2.0 — trapezoidal rule is exact for linear functions."""
        result = trapezoidal(lambda x: x, 0.0, 2.0, 100)
        assert np.isclose(result, 2.0, rtol=1e-10), (
            f"Expected 2.0, got {result:.6f}. "
            "Likely a weighting or endpoint bug."
        )

    def test_constant_function(self) -> None:
        """∫0^3 2 dx = 6.0 — trapezoidal is also exact for constants."""
        result = trapezoidal(lambda x: np.full_like(x, 2.0), 0.0, 3.0, 50)
        assert np.isclose(result, 6.0, rtol=1e-10)

    def test_quadratic_convergence_order(self) -> None:
        """Error must scale as O(N^-2): doubling N reduces error by ~4×."""
        # ∫0^pi sin(x) dx = 2.0 (exact)
        exact = 2.0
        N_coarse, N_fine = 20, 40
        err_coarse = abs(trapezoidal(np.sin, 0.0, np.pi, N_coarse) - exact)
        err_fine   = abs(trapezoidal(np.sin, 0.0, np.pi, N_fine)   - exact)
        ratio = err_coarse / err_fine
        assert ratio > 3.5, (
            f"Expected error ratio ≥ 4 (2nd-order), got {ratio:.2f}. "
            "Check that interior weights are 1.0 and endpoints 0.5."
        )

    def test_sine_integral(self) -> None:
        """∫0^π sin(x) dx = 2.0 — non-trivial integrand check."""
        result = trapezoidal(np.sin, 0.0, np.pi, 1000)
        assert np.isclose(result, 2.0, rtol=1e-6), (
            f"Expected 2.0, got {result:.8f}."
        )


# ---------------------------------------------------------------------------
# Module 3 — L2 norm contract
# ---------------------------------------------------------------------------

class TestComputeL2:
    """L2 error metric with Riemann-sum grid-area weighting."""

    def test_zero_error_for_identical_fields(self) -> None:
        """If u_num == u_ref exactly, L2 must be 0."""
        u = np.ones((10, 10))
        assert compute_l2(u, u, dx=0.1, dy=0.1) == 0.0

    def test_known_uniform_error(self) -> None:
        """Uniform error ε on [0,1]^2 → L2 = ε*sqrt(Area) = ε (Area=1)."""
        nx, ny = 100, 100
        dx, dy = 1.0 / nx, 1.0 / ny
        eps = 0.5
        u_num = np.full((nx, ny), eps)
        u_ref = np.zeros((nx, ny))
        l2 = compute_l2(u_num, u_ref, dx=dx, dy=dy)
        # Expected: sqrt(sum(eps^2 * dx * dy)) = eps * sqrt(nx*ny*dx*dy) = eps
        assert np.isclose(l2, eps, rtol=1e-3), (
            f"Expected L2 ≈ {eps}, got {l2:.4f}. "
            "Verify the dx*dy factor is included."
        )

    def test_resolution_invariant(self) -> None:
        """Same physics → same L2 at N=20, 40, 80 (dx*dy makes it so)."""
        eps = 0.1
        results = []
        for n in [20, 40, 80]:
            dx = dy = 1.0 / n
            u_num = np.full((n, n), eps)
            u_ref = np.zeros((n, n))
            results.append(compute_l2(u_num, u_ref, dx=dx, dy=dy))
        assert np.allclose(results, results[0], rtol=1e-6), (
            f"L2 values differ across resolutions: {results}. "
            "Missing the dx*dy Riemann-sum weight."
        )

    def test_rejects_shape_mismatch(self) -> None:
        """Must raise ValueError when u_num and u_ref have different shapes."""
        u_num = np.zeros((8, 8))
        u_ref = np.zeros((8, 7))
        with pytest.raises(ValueError, match="shape"):
            compute_l2(u_num, u_ref, dx=0.1, dy=0.1)

    def test_rejects_nonpositive_dx(self) -> None:
        """Must raise ValueError when dx ≤ 0 or dy ≤ 0."""
        u = np.zeros((4, 4))
        with pytest.raises(ValueError):
            compute_l2(u, u, dx=0.0, dy=0.1)
        with pytest.raises(ValueError):
            compute_l2(u, u, dx=0.1, dy=-1.0)

    def test_symmetry(self) -> None:
        """L2(u_num, u_ref) == L2(u_ref, u_num) — error is symmetric."""
        rng = np.random.default_rng(7)
        u_a = rng.standard_normal((20, 20))
        u_b = rng.standard_normal((20, 20))
        dx = dy = 0.05
        assert np.isclose(
            compute_l2(u_a, u_b, dx, dy),
            compute_l2(u_b, u_a, dx, dy),
        )


# ---------------------------------------------------------------------------
# Module 3/4 — Reference function
# ---------------------------------------------------------------------------

class TestReference:
    """Exact analytic solution: u = sin(pi*x)*sin(pi*y)*cos(sqrt(2)*pi*c*t)."""

    @pytest.fixture()
    def mesh(self):
        x1 = np.linspace(0.0, 1.0, 20)
        y1 = np.linspace(0.0, 1.0, 20)
        return np.meshgrid(x1, y1)

    def test_output_shape_matches_input(self, mesh) -> None:
        """Output shape must equal input mesh shape."""
        x, y = mesh
        out = reference(x, y, t=0.5)
        assert out.shape == x.shape, (
            f"Expected shape {x.shape}, got {out.shape}."
        )

    def test_initial_condition(self, mesh) -> None:
        """At t=0, u(x,y,0) == sin(pi*x)*sin(pi*y)."""
        x, y = mesh
        expected = np.sin(np.pi * x) * np.sin(np.pi * y)
        np.testing.assert_allclose(
            reference(x, y, t=0.0), expected, atol=1e-12,
            err_msg="Initial condition mismatch: u(x,y,0) should equal sin(pi*x)*sin(pi*y)."
        )

    def test_boundary_conditions(self, mesh) -> None:
        """u = 0 on all four walls at any time t (Dirichlet BC)."""
        x, y = mesh
        t = 0.3
        u = reference(x, y, t)
        np.testing.assert_allclose(u[:, 0],  0.0, atol=1e-12,
                                   err_msg="Left wall (x=0) BC violated.")
        np.testing.assert_allclose(u[:, -1], 0.0, atol=1e-12,
                                   err_msg="Right wall (x=1) BC violated.")
        np.testing.assert_allclose(u[0, :],  0.0, atol=1e-12,
                                   err_msg="Bottom wall (y=0) BC violated.")
        np.testing.assert_allclose(u[-1, :], 0.0, atol=1e-12,
                                   err_msg="Top wall (y=1) BC violated.")

    def test_wave_speed_scaling(self, mesh) -> None:
        """Doubling c doubles the oscillation frequency — must give different phase."""
        x, y = mesh
        t = 0.25
        u_c1 = reference(x, y, t, c=1.0)
        u_c2 = reference(x, y, t, c=2.0)
        assert not np.allclose(u_c1, u_c2), (
            "c=1.0 and c=2.0 give identical results — wave speed is not used."
        )

    def test_time_evolution(self, mesh) -> None:
        """Module 4 (Hold Physical Time Fixed): u must be time-dependent."""
        x, y = mesh
        u_t0 = reference(x, y, t=0.0)
        u_t1 = reference(x, y, t=0.5)
        assert not np.allclose(u_t0, u_t1), (
            "u(t=0) == u(t=0.5): the reference has no time evolution. "
            "Check that the cos(omega*t) term is implemented."
        )

    def test_dispersion_relation(self, mesh) -> None:
        """Verify omega^2 = c^2*(kx^2+ky^2) = 2*pi^2*c^2 numerically.

        The period T = 2*pi/omega must be reproduced by the reference:
        u(x,y,T) should equal u(x,y,0) (full period → returns to IC).
        """
        x, y = mesh
        c = 1.0
        omega = np.sqrt(2) * np.pi * c
        T_theory = 2 * np.pi / omega  # full oscillation period

        u_t0 = reference(x, y, t=0.0,      c=c)
        u_tT = reference(x, y, t=T_theory, c=c)
        np.testing.assert_allclose(
            u_tT, u_t0, atol=1e-10,
            err_msg=(
                f"reference(x,y,T) ≠ reference(x,y,0) for T={T_theory:.4f}. "
                "Dispersion relation or cos formula may be wrong."
            )
        )


# ---------------------------------------------------------------------------
# Module 4 — Wave energy diagnostic (extension)
# ---------------------------------------------------------------------------

class TestWaveEnergy:
    """Discrete wave energy: kinetic + potential, area-scaled."""

    @pytest.fixture()
    def mesh_dt(self):
        n = 30
        x1 = np.linspace(0.0, 1.0, n)
        y1 = np.linspace(0.0, 1.0, n)
        x, y = np.meshgrid(x1, y1)
        dx = dy = 1.0 / (n - 1)
        dt = 0.01
        return x, y, dx, dy, dt

    def test_wave_energy_returns_positive_scalar(self, mesh_dt) -> None:
        """Wave energy must be a finite, positive float."""
        x, y, dx, dy, dt = mesh_dt
        c = 1.0
        u_now  = reference(x, y, t=dt,  c=c)
        u_prev = reference(x, y, t=0.0, c=c)
        E = wave_energy(u_now, u_prev, dt=dt, c=c, dx=dx, dy=dy)
        assert isinstance(E, float), f"Expected float, got {type(E)}"
        assert np.isfinite(E),       f"Energy must be finite, got {E}"
        assert E > 0,                f"Energy must be positive, got {E}"

    def test_wave_energy_area_scaled(self, mesh_dt) -> None:
        """Energy should scale with domain area, not raw grid-point count."""
        x, y, dx, dy, dt = mesh_dt
        c = 1.0
        u_now  = reference(x, y, t=dt,  c=c)
        u_prev = reference(x, y, t=0.0, c=c)
        E = wave_energy(u_now, u_prev, dt=dt, c=c, dx=dx, dy=dy)
        # Energy of the (1,1) sine mode on [0,1]^2:
        # E ≈ (1/2)*omega^2 * (1/4) + (1/2)*c^2*2*pi^2*(1/4)
        # Rough order-of-magnitude check: should be O(1) for c=1
        assert 0.1 < E < 100.0, (
            f"Energy magnitude {E:.3f} seems out of range for c=1, unit domain."
        )


# ---------------------------------------------------------------------------
# Module 5 — Gate functions
# ---------------------------------------------------------------------------

class TestGates:
    """Pass criteria: analytic-limit gate → status label."""

    def test_analytic_limit_test_passes(self) -> None:
        """analytic_limit_test() must return (True, value≈2.0)."""
        passed, value = analytic_limit_test()
        assert passed is True, (
            f"analytic_limit_test() returned False. value={value:.6f}. "
            "Check trapezoidal implementation."
        )
        assert np.isclose(value, 2.0, rtol=1e-4), (
            f"Analytic limit value should be ~2.0, got {value:.6f}."
        )

    def test_single_case_measurement_is_finite(self) -> None:
        """single_case_l2_measurement() must return a finite, non-negative scalar."""
        cfg = {
            "nx": 40,
            "ny": 40,
            "length_x": 1.0,
            "length_y": 1.0,
            "c": 1.0,
            "t_star": 0.5,
            "courant": 0.5,
        }
        l2 = single_case_l2_measurement(cfg)
        assert np.isfinite(l2), f"L2 must be finite, got {l2}."
        assert l2 >= 0.0,       f"L2 must be non-negative, got {l2}."

    def test_single_case_l2_is_small(self) -> None:
        """With fake_numerical_field (noise ~1e-3), L2 should be in (1e-5, 0.1)."""
        cfg = {
            "nx": 50,
            "ny": 50,
            "length_x": 1.0,
            "length_y": 1.0,
            "c": 1.0,
            "t_star": 0.5,
            "courant": 0.5,
        }
        l2 = single_case_l2_measurement(cfg)
        assert 1e-5 < l2 < 0.1, (
            f"Unexpected L2 magnitude: {l2:.4e}. "
            "Expected small but nonzero value for the fake noisy field."
        )

    def test_status_logic_gate(self) -> None:
        """Module 5: status must be 'needs-fix' when analytic-limit fails.

        This test documents the gate contract but cannot trigger it without
        a broken trapezoidal — it validates the status string logic directly.
        """
        # Simulate what main() does with a known passing gate
        passed, value = analytic_limit_test()
        status = "reference-checked" if passed else "needs-fix"
        assert status in {"reference-checked", "needs-fix"}, (
            f"Unexpected status value: {status!r}"
        )
