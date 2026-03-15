#!/usr/bin/env python3
"""
Cross-platform installation verification for EXIF Editor.

Run:
  python test_setup.py
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path


def status(ok: bool, message: str) -> bool:
    prefix = "[OK]" if ok else "[FAIL]"
    print(f"{prefix} {message}")
    return ok


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def check_python_version(min_major: int = 3, min_minor: int = 8) -> bool:
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (min_major, min_minor)
    return status(ok, f"Python {major}.{minor} detected (requires {min_major}.{min_minor}+)")


def check_venv_exists(project_root: Path) -> bool:
    venv_dir = project_root / "venv"
    return status(venv_dir.exists(), "Virtual environment directory exists (venv/)")


def check_running_in_venv() -> bool:
    in_venv = (getattr(sys, "base_prefix", sys.prefix) != sys.prefix) or bool(
        getattr(sys, "real_prefix", "")
    )
    if in_venv:
        return status(True, f"Running inside virtual environment: {sys.executable}")
    warn("Not running inside an active virtual environment (this can still work if using venv Python directly)")
    return True


def check_import(module_name: str, display_name: str | None = None) -> bool:
    label = display_name or module_name
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", None)
        msg = f"{label} import works"
        if version:
            msg += f" (version {version})"
        return status(True, msg)
    except Exception as exc:
        return status(False, f"{label} import failed: {exc}")


def check_camera_presets() -> bool:
    try:
        from camera_presets import CAMERA_PRESETS  # pylint: disable=import-outside-toplevel

        return status(True, f"Camera presets loaded ({len(CAMERA_PRESETS)} presets)")
    except Exception as exc:
        return status(False, f"Camera presets failed to load: {exc}")


def check_script_imports() -> bool:
    ok_editor = check_import("exif_editor", "exif_editor.py")
    ok_easy = check_import("easy_run", "easy_run.py")
    return ok_editor and ok_easy


def check_cli_help(project_root: Path) -> bool:
    cmd = [sys.executable, str(project_root / "exif_editor.py"), "--help"]
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except Exception as exc:
        return status(False, f"CLI help invocation failed: {exc}")

    if result.returncode == 0:
        return status(True, "Command line interface responds to --help")

    err = (result.stderr or result.stdout).strip().splitlines()
    detail = err[-1] if err else "unknown error"
    return status(False, f"CLI help failed (exit {result.returncode}): {detail}")


def check_sample_images(project_root: Path) -> bool:
    input_dir = project_root / "input_images"
    if not input_dir.exists():
        warn("input_images/ directory not found")
        return True

    patterns = ("*.jpg", "*.jpeg", "*.jpe", "*.jfif")
    images = []
    for pattern in patterns:
        images.extend(input_dir.glob(pattern))

    if images:
        return status(True, f"Sample JPEG images found in input_images/ ({len(images)} files)")

    warn("No sample JPEG images found in input_images/")
    return True


def main() -> int:
    project_root = Path(__file__).resolve().parent

    print("EXIF Editor setup verification")
    print("=" * 30)

    checks = [
        check_venv_exists(project_root),
        check_running_in_venv(),
        check_python_version(),
        check_import("PIL", "Pillow"),
        check_import("piexif"),
        check_camera_presets(),
        check_script_imports(),
        check_cli_help(project_root),
        check_sample_images(project_root),
    ]

    failed = sum(1 for c in checks if not c)
    print("\n" + "=" * 30)
    if failed == 0:
        print("All core checks passed.")
        print("Try: python easy_run.py")
        return 0

    print(f"{failed} check(s) failed.")
    print("Fix the failures above, then re-run: python test_setup.py")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
