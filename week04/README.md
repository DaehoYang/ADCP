# Week 04: Boundary Modeling and Inverse Problems

## Overview

This folder now follows the same practice philosophy as `week03/`.

Students are given:

- one baseline implementation file: `solver_2d.py`
- two broken-first diagnosis files:
	- `broken_boundary_starter.py`
	- `broken_objective_starter.py`
- one lightweight configuration file: `config.yaml`

The main coding practices are **not** pre-written as starter files.
Students should ask an AI agent to extend `solver_2d.py` or generate small
experiment scripts, then review that output against the checklists in
`week04.md`.

---

## Quick Start

```bash
cd week04

# Broken-first diagnosis 1
python broken_boundary_starter.py

# Broken-first diagnosis 2
python broken_objective_starter.py
```

---

## Files

| File | Purpose |
|:---|:---|
| `solver_2d.py` | Week 04 baseline solver to extend via AI prompting |
| `config.yaml` | Shared parameters for grid, boundary diagnostics, and inversion |
| `broken_boundary_starter.py` | Broken-first example 1: absorbing boundary bug hunt |
| `broken_objective_starter.py` | Broken-first example 2: inverse objective leakage |
| `logs/`, `outputs/` | Optional artifact directories |

---

## Requirements

```bash
pip install numpy scipy scikit-optimize
```

---

## Recommended Workflow

1. Read `solver_2d.py` to understand the baseline Dirichlet solver.
2. Diagnose the two broken examples without editing them first.
3. Ask the AI a simple Week 04 task such as:
	 - "Extend my solver to compare Dirichlet, Neumann, and absorbing boundaries."
	 - "Build a small sensitivity test for recovering wave speed from sensor data."
4. Review the AI output against the validation checklist in `week04.md`.
5. Re-prompt only after identifying exactly what is numerically or physically wrong.

---

## What Is Intentionally Missing

- There is no pre-written `boundary_starter.py`.
- There is no pre-written `optimizer_starter.py`.
- There are no canned test files that answer the Week 04 questions automatically.

This is deliberate. The Week 04 coding practices should be produced by the AI
on demand and then reviewed by the student, exactly as in the Week 03 practice
structure.
