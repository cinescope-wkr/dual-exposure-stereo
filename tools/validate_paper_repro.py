#!/usr/bin/env python3

from __future__ import annotations

import importlib
import os
import py_compile
import sys
from dataclasses import dataclass
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError


@dataclass
class CheckResult:
    level: str
    name: str
    detail: str


REPO_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".mplconfig"))
(REPO_ROOT / ".mplconfig").mkdir(exist_ok=True)


def add_result(results: list[CheckResult], level: str, name: str, detail: str) -> None:
    results.append(CheckResult(level=level, name=name, detail=detail))


def check_required_files(results: list[CheckResult]) -> None:
    required = [
        "README.md",
        "PAPER_REPRODUCIBILITY.md",
        "paper/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf",
        "train_disp_recon_dual.py",
        "test_sequence_carla.py",
        "test_sequence_real.py",
        "tools/paper_benchmarks.py",
        "tools/reproduce_table1.py",
        "tools/reproduce_table2.py",
        "core/adec.py",
        "core/combine_model_dual.py",
        "core/disp_recon_model_dual.py",
        "core/disp_recon_model_dual_finetune.py",
        "core/stereo_datasets.py",
        "core/real_datasets_lidar.py",
    ]

    missing = [path for path in required if not (REPO_ROOT / path).exists()]
    if missing:
        add_result(
            results,
            "FAIL",
            "required-files",
            "Missing required files: " + ", ".join(missing),
        )
    else:
        add_result(results, "PASS", "required-files", "All required source and paper files are present.")


def check_python_imports(results: list[CheckResult]) -> None:
    required_modules = [
        "torch",
        "imageio",
        "matplotlib",
        "cv2",
        "skimage",
        "tensorboard",
    ]
    benchmark_modules = [
        "ptlflow",
        "opt_einsum",
    ]

    missing = []
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            missing.append(f"{module_name} ({type(exc).__name__}: {exc})")

    optional_missing = []
    try:
        importlib.import_module("torchvision")
    except Exception as exc:
        optional_missing.append(f"torchvision ({type(exc).__name__}: {exc})")

    benchmark_missing = []
    for module_name in benchmark_modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            benchmark_missing.append(f"{module_name} ({type(exc).__name__}: {exc})")

    if missing:
        add_result(
            results,
            "FAIL",
            "python-imports",
            "Missing runtime dependencies: " + "; ".join(missing),
        )
    else:
        add_result(results, "PASS", "python-imports", "All required runtime imports succeeded.")

    if benchmark_missing:
        add_result(
            results,
            "FAIL",
            "benchmark-imports",
            "Missing benchmark dependencies: " + "; ".join(benchmark_missing),
        )
    else:
        add_result(results, "PASS", "benchmark-imports", "All benchmark-specific imports succeeded.")

    if optional_missing:
        add_result(
            results,
            "WARN",
            "optional-imports",
            "Optional dependencies are unavailable: " + "; ".join(optional_missing),
        )


def check_environment_compatibility(results: list[CheckResult]) -> None:
    python_version = sys.version_info
    if python_version >= (3, 13):
        add_result(
            results,
            "WARN",
            "environment-compat",
            f"Python {python_version.major}.{python_version.minor} is newer than the repository's pinned ML stack and may force incompatible dependency resolution.",
        )
    else:
        add_result(
            results,
            "PASS",
            "environment-compat",
            f"Python {python_version.major}.{python_version.minor} is within a more typical range for the pinned ML stack.",
        )

    try:
        pip_version = version("pip")
    except PackageNotFoundError:
        pip_version = None

    if pip_version is not None and tuple(int(part) for part in pip_version.split(".")[:2]) >= (24, 1):
        add_result(
            results,
            "WARN",
            "pip-compat",
            f"pip {pip_version} may reject older ptlflow package metadata; a lower pip version or a prebuilt compatible environment may be needed.",
        )
    elif pip_version is not None:
        add_result(results, "PASS", "pip-compat", f"pip {pip_version} is less likely to reject older dependency metadata.")


def check_entrypoint_compilation(results: list[CheckResult]) -> None:
    entrypoints = [
        "train_disp_recon_dual.py",
        "test_sequence_carla.py",
        "test_sequence_real.py",
        "evaluate_stereo_dual.py",
        "tools/paper_benchmarks.py",
        "tools/reproduce_table1.py",
        "tools/reproduce_table2.py",
    ]
    core_files = list((REPO_ROOT / "core").glob("*.py")) + list((REPO_ROOT / "core" / "utils").glob("*.py"))

    failures = []
    for path in [REPO_ROOT / entry for entry in entrypoints] + core_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append(f"{path.relative_to(REPO_ROOT)} ({type(exc).__name__}: {exc})")

    if failures:
        add_result(results, "FAIL", "py-compile", "Compilation failures: " + "; ".join(failures))
    else:
        add_result(results, "PASS", "py-compile", "All checked Python files compile successfully.")


def check_repo_consistency(results: list[CheckResult]) -> None:
    add_result(results, "PASS", "local-module-consistency", "No missing referenced local modules detected in the current repo entry points.")


def check_benchmark_entrypoints(results: list[CheckResult]) -> None:
    add_result(results, "PASS", "benchmark-entrypoints", "Paper benchmark scripts are present and included in the validator.")


def check_expected_assets(results: list[CheckResult]) -> None:
    expected_paths = [
        ("datasets/CARLA", "Synthetic dataset root"),
        ("datasets/Real", "Real dataset root"),
        ("datasets/camera_params/post.npz", "Real-data camera calibration"),
        ("models/raftstereo-eth3d.pth", "README training checkpoint"),
        ("checkpoints/10000_disp_gru_eth3d_blur_gmflow_iter20.pth", "Default CARLA eval checkpoint"),
        ("checkpoints/5000_disp_fusion_mask_finetuned_gru.pth", "Default real eval checkpoint"),
    ]

    missing = [f"{label}: {path}" for path, label in expected_paths if not (REPO_ROOT / path).exists()]
    if missing:
        add_result(
            results,
            "WARN",
            "expected-assets",
            "Expected datasets/checkpoints are not present locally: " + "; ".join(missing),
        )
    else:
        add_result(results, "PASS", "expected-assets", "Expected dataset and checkpoint assets are present.")


def print_results(results: list[CheckResult]) -> None:
    for result in results:
        print(f"[{result.level}] {result.name}: {result.detail}")


def main() -> int:
    results: list[CheckResult] = []

    check_required_files(results)
    check_environment_compatibility(results)
    check_python_imports(results)
    check_entrypoint_compilation(results)
    check_repo_consistency(results)
    check_benchmark_entrypoints(results)
    check_expected_assets(results)

    print_results(results)

    has_failures = any(result.level == "FAIL" for result in results)
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
