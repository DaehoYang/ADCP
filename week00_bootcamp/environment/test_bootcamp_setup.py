"""Week 00 setup check script (dependency-focused)."""

from __future__ import annotations

import importlib
from importlib import metadata


REQUIRED_PACKAGES = [
    "numpy",
    "scipy",
    "matplotlib",
    "pandas",
    "sympy",
    "openai",
    "tiktoken",
    "pydantic",
    "jupyterlab",
]


def check_imports() -> int:
    print("Checking environment setup...\n")
    missing: list[str] = []

    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            print(f"[OK] {package}")
        except ImportError:
            # jupyterlab can be installed but not always importable as a module.
            if package == "jupyterlab":
                try:
                    metadata.version("jupyterlab")
                    print(f"[OK] {package}")
                    continue
                except metadata.PackageNotFoundError:
                    pass
            missing.append(package)
            print(f"[MISSING] {package}")

    print("\n" + "-" * 30)
    if missing:
        print("Missing packages: " + ", ".join(missing))
        return 1

    print("All required dependencies are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(check_imports())
