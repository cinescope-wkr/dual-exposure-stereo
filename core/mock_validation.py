from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".mplconfig"))
(REPO_ROOT / ".mplconfig").mkdir(exist_ok=True)

import torch

from core.adec import calculate_histogram_global, stereo_exposure_control
from core.utils.mask import soft_binary_threshold_batch
from core.utils.simulate import ImageFormation, QuantizeSTE


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    metrics: dict[str, float]


def make_mock_hdr_stereo(
    height: int = 48,
    width: int = 96,
    disparity: int = 6,
) -> tuple[torch.Tensor, torch.Tensor]:
    x = torch.linspace(0, 1, width).view(1, 1, 1, width)
    y = torch.linspace(0, 1, height).view(1, 1, height, 1)

    texture = (
        0.5
        + 0.25 * torch.sin(10 * torch.pi * x)
        + 0.2 * torch.cos(8 * torch.pi * y)
        + 0.1 * torch.sin(7 * torch.pi * (x + y))
    ).clamp(0.05, 0.95)
    texture = texture.repeat(1, 3, 1, 1)

    radiance_scale = torch.ones(1, 1, height, width)
    radiance_scale[:, :, :, : width // 3] = 0.005
    radiance_scale[:, :, :, width // 3 : 2 * width // 3] = 0.5
    radiance_scale[:, :, :, 2 * width // 3 :] = 6.0

    left_hdr = (texture * radiance_scale).clamp_min(1e-4)
    right_hdr = torch.zeros_like(left_hdr)
    right_hdr[:, :, :, :-disparity] = left_hdr[:, :, :, disparity:]
    right_hdr[:, :, :, -disparity:] = left_hdr[:, :, :, -1:].expand(-1, -1, -1, disparity)

    return left_hdr, right_hdr


def shift_horizontal(image: torch.Tensor, shift: int) -> torch.Tensor:
    shifted = torch.zeros_like(image)

    if shift > 0:
        shifted[:, :, :, shift:] = image[:, :, :, :-shift]
        shifted[:, :, :, :shift] = image[:, :, :, :1].expand(-1, -1, -1, shift)
    elif shift < 0:
        shift = -shift
        shifted[:, :, :, :-shift] = image[:, :, :, shift:]
        shifted[:, :, :, -shift:] = image[:, :, :, -1:].expand(-1, -1, -1, shift)
    else:
        shifted = image.clone()

    return shifted


def make_mock_hdr_temporal_sequence(
    height: int = 48,
    width: int = 96,
    motion: int = 5,
) -> tuple[torch.Tensor, torch.Tensor]:
    left_t, _ = make_mock_hdr_stereo(height=height, width=width)
    left_t1 = shift_horizontal(left_t, motion)
    return left_t, left_t1


def mock_capture_linear(hdr: torch.Tensor, exposure: float | torch.Tensor) -> torch.Tensor:
    exposure_tensor = torch.as_tensor(exposure, dtype=hdr.dtype, device=hdr.device).view(-1, 1, 1, 1)
    ldr = torch.clamp(hdr * exposure_tensor, 0.0, 1.0)
    return torch.round(ldr * 255.0) / 255.0


def repo_capture_with_noise(
    hdr: torch.Tensor,
    exposure: torch.Tensor,
    fixed_range_middle: torch.Tensor,
) -> torch.Tensor:
    formation = ImageFormation(
        hdr,
        exposure,
        device="cpu",
        fixed_range_middle=fixed_range_middle,
    )
    return QuantizeSTE.apply(formation.noise_modeling(), 8)


def fuse_dual_exposure(current: torch.Tensor, companion: torch.Tensor) -> torch.Tensor:
    mask_current = soft_binary_threshold_batch(current)
    mask_companion = soft_binary_threshold_batch(companion)

    epsilon = 1e-6
    denom = torch.where(
        mask_current + mask_companion == 0,
        torch.full_like(mask_current, epsilon),
        mask_current + mask_companion,
    )
    fused = (mask_current * current + mask_companion * companion) / denom

    near_zero_mask = fused.abs() < 1e-2
    warping_failure_mask = (mask_current == 0) & (mask_companion > 0)
    update_mask = (~warping_failure_mask) & near_zero_mask
    fused = fused + update_mask.float() * companion

    return fused


def estimate_disparity_sad(
    left: torch.Tensor,
    right: torch.Tensor,
    max_disparity: int = 12,
    window: int = 7,
) -> torch.Tensor:
    left_gray = left.mean(dim=1, keepdim=True)
    right_gray = right.mean(dim=1, keepdim=True)

    cost_volume = []
    for disp in range(max_disparity + 1):
        shifted = torch.zeros_like(right_gray)
        if disp > 0:
            shifted[:, :, :, disp:] = right_gray[:, :, :, :-disp]
        else:
            shifted = right_gray

        cost = (left_gray - shifted).abs()
        cost = torch.nn.functional.avg_pool2d(cost, window, stride=1, padding=window // 2)
        cost_volume.append(cost)

    return torch.cat(cost_volume, dim=1).argmin(dim=1, keepdim=True).float()


def disparity_mae(prediction: torch.Tensor, target: torch.Tensor, valid: torch.Tensor) -> float:
    return (prediction[valid] - target[valid]).abs().mean().item()


def check_repo_image_formation_complementarity() -> CheckResult:
    torch.manual_seed(0)
    left_hdr, _ = make_mock_hdr_stereo()

    exp_high = torch.tensor([[2.8]])
    exp_low = torch.tensor([[0.45]])
    fixed_range_middle = ImageFormation(left_hdr, exp_high, device="cpu").range_middle.view(-1)

    high_ldr = repo_capture_with_noise(left_hdr, exp_high, fixed_range_middle)
    low_ldr = repo_capture_with_noise(left_hdr, exp_low, fixed_range_middle)

    high_valid = soft_binary_threshold_batch(high_ldr) > 0.5
    low_valid = soft_binary_threshold_batch(low_ldr) > 0.5
    union_valid = high_valid | low_valid

    high_coverage = high_valid.float().mean().item()
    low_coverage = low_valid.float().mean().item()
    union_coverage = union_valid.float().mean().item()

    passed = union_coverage > max(high_coverage, low_coverage) + 0.10
    detail = (
        "Repository image formation produced complementary valid regions across the two exposures."
        if passed
        else "Dual exposures did not expand valid-region coverage enough on the mock HDR scene."
    )

    return CheckResult(
        name="repo-image-formation-complementarity",
        passed=passed,
        detail=detail,
        metrics={
            "high_coverage": high_coverage,
            "low_coverage": low_coverage,
            "union_coverage": union_coverage,
        },
    )


def check_adec_expands_exposure_gap() -> CheckResult:
    left_hdr, _ = make_mock_hdr_stereo()

    initial_high = torch.tensor([1.3])
    initial_low = torch.tensor([1.1])
    high_ldr = mock_capture_linear(left_hdr, initial_high)
    low_ldr = mock_capture_linear(left_hdr, initial_low)

    hist_high = calculate_histogram_global(high_ldr)
    hist_low = calculate_histogram_global(low_ldr)
    alpha = torch.tensor([0.1])

    adjusted_high, adjusted_low = stereo_exposure_control(
        initial_high,
        initial_low,
        hist_high,
        hist_low,
        alpha1=alpha,
        alpha2=alpha,
        exp_gap_threshold=2.0,
    )

    initial_gap = torch.abs(initial_high - initial_low).item()
    adjusted_gap = torch.abs(adjusted_high - adjusted_low).item()

    passed = adjusted_gap > initial_gap + 0.04
    detail = (
        "ADEC widened the exposure gap on the mock HDR scene."
        if passed
        else "ADEC did not widen the exposure gap enough on the mock HDR scene."
    )

    return CheckResult(
        name="adec-gap-expansion",
        passed=passed,
        detail=detail,
        metrics={
            "initial_high": initial_high.item(),
            "initial_low": initial_low.item(),
            "adjusted_high": adjusted_high.item(),
            "adjusted_low": adjusted_low.item(),
            "initial_gap": initial_gap,
            "adjusted_gap": adjusted_gap,
        },
    )


def check_dual_exposure_stereo_gain() -> CheckResult:
    disparity = 6
    left_hdr, right_hdr = make_mock_hdr_stereo(disparity=disparity)

    exp_high = 12.0
    exp_low = 0.05

    left_high = mock_capture_linear(left_hdr, exp_high)
    right_high = mock_capture_linear(right_hdr, exp_high)
    left_low = mock_capture_linear(left_hdr, exp_low)
    right_low = mock_capture_linear(right_hdr, exp_low)

    left_fused = fuse_dual_exposure(left_high, left_low)
    right_fused = fuse_dual_exposure(right_high, right_low)
    left_average = 0.5 * (left_high + left_low)
    right_average = 0.5 * (right_high + right_low)

    height, width = left_hdr.shape[-2:]
    valid = torch.zeros((1, 1, height, width), dtype=torch.bool)
    valid[:, :, :, disparity : width - disparity] = True
    gt = torch.full((1, 1, height, width), float(disparity))

    high_mae = disparity_mae(estimate_disparity_sad(left_high, right_high), gt, valid)
    low_mae = disparity_mae(estimate_disparity_sad(left_low, right_low), gt, valid)
    fused_mae = disparity_mae(estimate_disparity_sad(left_fused, right_fused), gt, valid)
    average_mae = disparity_mae(estimate_disparity_sad(left_average, right_average), gt, valid)

    passed = fused_mae < min(high_mae, low_mae) * 0.2
    detail = (
        "Mask-based dual-exposure fusion substantially reduced disparity error on the mock stereo pair."
        if passed
        else "Dual-exposure fusion did not improve disparity enough on the mock stereo pair."
    )

    return CheckResult(
        name="dual-exposure-stereo-gain",
        passed=passed,
        detail=detail,
        metrics={
            "high_only_mae": high_mae,
            "low_only_mae": low_mae,
            "naive_average_mae": average_mae,
            "fused_mae": fused_mae,
        },
    )


def check_motion_compensated_fusion_alignment() -> CheckResult:
    motion = 5
    left_t, left_t1 = make_mock_hdr_temporal_sequence(motion=motion)

    high_t = mock_capture_linear(left_t, 12.0)
    low_t = mock_capture_linear(left_t, 0.05)
    low_t1 = mock_capture_linear(left_t1, 0.05)

    oracle_fusion = fuse_dual_exposure(high_t, low_t)
    unwarped_fusion = fuse_dual_exposure(high_t, low_t1)
    warped_fusion = fuse_dual_exposure(high_t, shift_horizontal(low_t1, -motion))

    unwarped_error = (unwarped_fusion - oracle_fusion).abs().mean().item()
    warped_error = (warped_fusion - oracle_fusion).abs().mean().item()

    passed = warped_error < unwarped_error * 0.2
    detail = (
        "Motion compensation aligned the complementary exposure before fusion on the mock temporal sequence."
        if passed
        else "Motion compensation did not improve alignment enough on the mock temporal sequence."
    )

    return CheckResult(
        name="motion-compensated-fusion-alignment",
        passed=passed,
        detail=detail,
        metrics={
            "unwarped_error": unwarped_error,
            "warped_error": warped_error,
        },
    )


def run_checks() -> list[CheckResult]:
    return [
        check_repo_image_formation_complementarity(),
        check_adec_expands_exposure_gap(),
        check_dual_exposure_stereo_gain(),
        check_motion_compensated_fusion_alignment(),
    ]


def print_results(results: list[CheckResult]) -> None:
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")
        for key, value in result.metrics.items():
            print(f"    - {key}: {value:.6f}")
