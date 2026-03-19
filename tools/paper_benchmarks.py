#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_METHODS = ("average", "gradient", "nae", "adec")
DEFAULT_DATASETS = ("synthetic", "real")


def add_shared_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--valid_iters", type=int, default=32)
    parser.add_argument("--mixed_precision", action="store_true")
    parser.add_argument("--max_samples", type=int, default=None)

    parser.add_argument("--corr_implementation", choices=["reg", "alt", "reg_cuda", "alt_cuda"], default="reg")
    parser.add_argument("--shared_backbone", action="store_true")
    parser.add_argument("--corr_levels", type=int, default=4)
    parser.add_argument("--corr_radius", type=int, default=4)
    parser.add_argument("--n_downsample", type=int, default=2)
    parser.add_argument("--context_norm", type=str, default="batch", choices=["group", "batch", "instance", "none"])
    parser.add_argument("--slow_fast_gru", action="store_true")
    parser.add_argument("--n_gru_layers", type=int, default=3)
    parser.add_argument("--hidden_dims", nargs="+", type=int, default=[128] * 3)

    parser.add_argument("--disable_adec", action="store_true")
    parser.add_argument("--disable_motion_compensation", action="store_true")
    parser.add_argument("--disable_weighted_fusion", action="store_true")

    parser.add_argument("--adec_ckpt", type=str, default=None)
    parser.add_argument("--average_ckpt", type=str, default=None)
    parser.add_argument("--gradient_ckpt", type=str, default=None)
    parser.add_argument("--nae_ckpt", type=str, default=None)


def build_repo_args(cli_args: argparse.Namespace, dataset: str) -> SimpleNamespace:
    train_datasets = ["test_carla"] if dataset == "synthetic" else ["test_real"]
    return SimpleNamespace(
        name="paper_benchmark",
        restore_ckpt=None,
        mixed_precision=cli_args.mixed_precision,
        train_datasets=train_datasets,
        batch_size=cli_args.batch_size,
        valid_iters=cli_args.valid_iters,
        device=cli_args.device,
        corr_implementation=cli_args.corr_implementation,
        shared_backbone=cli_args.shared_backbone,
        corr_levels=cli_args.corr_levels,
        corr_radius=cli_args.corr_radius,
        n_downsample=cli_args.n_downsample,
        context_norm=cli_args.context_norm,
        slow_fast_gru=cli_args.slow_fast_gru,
        n_gru_layers=cli_args.n_gru_layers,
        hidden_dims=cli_args.hidden_dims,
        disable_adec=cli_args.disable_adec,
        disable_motion_compensation=cli_args.disable_motion_compensation,
        disable_weighted_fusion=cli_args.disable_weighted_fusion,
    )


def checkpoint_for_method(cli_args: argparse.Namespace, method: str) -> str | None:
    return {
        "adec": cli_args.adec_ckpt,
        "average": cli_args.average_ckpt,
        "gradient": cli_args.gradient_ckpt,
        "nae": cli_args.nae_ckpt,
    }[method]


def strip_prefixes(state_dict: dict[str, Any], prefixes: tuple[str, ...]) -> dict[str, Any]:
    normalized = {}
    for key, value in state_dict.items():
        new_key = key
        changed = True
        while changed:
            changed = False
            for prefix in prefixes:
                if new_key.startswith(prefix):
                    new_key = new_key[len(prefix) :]
                    changed = True
        normalized[new_key] = value
    return normalized


def add_prefix(state_dict: dict[str, Any], prefix: str) -> dict[str, Any]:
    return {prefix + key: value for key, value in state_dict.items()}


def load_raw_checkpoint(path: str, device: torch.device) -> dict[str, Any]:
    checkpoint = torch.load(path, map_location=device)
    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        checkpoint = checkpoint["state_dict"]
    if not isinstance(checkpoint, dict):
        raise ValueError(f"Checkpoint at {path} is not a state dict.")
    return checkpoint


def count_matching_keys(target_state: dict[str, Any], candidate: dict[str, Any]) -> int:
    matched = 0
    for key, value in candidate.items():
        if key in target_state and hasattr(target_state[key], "shape") and hasattr(value, "shape"):
            if target_state[key].shape == value.shape:
                matched += 1
    return matched


def choose_and_load(target: torch.nn.Module, candidates: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    target_state = target.state_dict()
    scored = []
    for name, candidate in candidates:
        scored.append((count_matching_keys(target_state, candidate), name, candidate))

    best_match_count, best_name, best_candidate = max(scored, key=lambda item: item[0])
    if best_match_count == 0:
        raise ValueError("No checkpoint keys matched the target module.")

    missing_keys, unexpected_keys = target.load_state_dict(best_candidate, strict=False)
    return {
        "strategy": best_name,
        "matched_keys": best_match_count,
        "missing_keys": len(missing_keys),
        "unexpected_keys": len(unexpected_keys),
    }


def load_model_checkpoint(model: torch.nn.Module, method: str, ckpt_path: str | None, device: torch.device) -> dict[str, Any] | None:
    if ckpt_path is None:
        return None

    raw_state = load_raw_checkpoint(ckpt_path, device)
    stripped = strip_prefixes(raw_state, ("module.", "model."))

    if method == "adec":
        disp_state = strip_prefixes(raw_state, ("module.", "model.", "disp_recon_net."))
        return choose_and_load(
            model.disp_recon_net,
            [
                ("disp_recon/stripped", disp_state),
                ("disp_recon/raw", raw_state),
                ("disp_recon/fully_stripped", strip_prefixes(raw_state, ("module.", "model.", "disp_recon_net.", "raft_stereo."))),
            ],
        )

    full_candidates = [
        ("model/stripped", stripped),
        ("model/raw", raw_state),
        ("model/raft_prefixed", add_prefix(strip_prefixes(raw_state, ("module.", "model.", "raft_stereo.")), "raft_stereo.")),
    ]

    best_full = max(count_matching_keys(model.state_dict(), candidate) for _, candidate in full_candidates)
    if hasattr(model, "raft_stereo"):
        raft_candidates = [
            ("raft/stripped", strip_prefixes(raw_state, ("module.", "model.", "raft_stereo."))),
            ("raft/raw", raw_state),
        ]
        best_raft = max(count_matching_keys(model.raft_stereo.state_dict(), candidate) for _, candidate in raft_candidates)
        if best_raft > best_full:
            return choose_and_load(model.raft_stereo, raft_candidates)

    return choose_and_load(model, full_candidates)


def make_model(method: str, args: SimpleNamespace, ckpt_path: str | None) -> tuple[torch.nn.Module, dict[str, Any] | None]:
    device = torch.device(args.device)

    if method == "adec":
        from core.combine_model_dual import CombineModel

        model = CombineModel(args).to(device)
    elif method == "average":
        from core.combine_model_average import CombineModel_w_averageAE

        model = CombineModel_w_averageAE(args).to(device)
    elif method == "gradient":
        from core.combine_model_gradient import CombineModel_w_gradientAE

        model = CombineModel_w_gradientAE(args).to(device)
    elif method == "nae":
        from core.combine_model_nae import CombineModel_w_nae

        model = CombineModel_w_nae(args).to(device)
    else:
        raise ValueError(f"Unknown method: {method}")

    load_info = load_model_checkpoint(model, method, ckpt_path, device)
    model.eval()

    for module in model.modules():
        if isinstance(module, (torch.nn.BatchNorm2d, torch.nn.InstanceNorm2d)):
            module.eval()

    return model, load_info


def masked_mae(prediction: torch.Tensor, target: torch.Tensor, valid_mask: torch.Tensor) -> float:
    absolute_error = torch.abs(prediction - target)
    valid = valid_mask.bool()
    while valid.dim() < absolute_error.dim():
        valid = valid.unsqueeze(1)
    return absolute_error[valid].mean().item()


def lidar_depth_metrics(disparity: torch.Tensor, points: torch.Tensor, focal_length: torch.Tensor, baseline: torch.Tensor, threshold: float = 15000) -> tuple[float, float]:
    points = points.detach().cpu()
    focal_length = focal_length.detach().cpu()
    baseline = baseline.detach().cpu()
    disparity = disparity.detach().cpu()

    mask = points[..., 2] < threshold
    u = points[..., 0][mask].long()
    v = points[..., 1][mask].long()
    z = points[..., 2][mask]

    depth = -(baseline * focal_length / (disparity + 1e-6))[0, 0]

    valid = (u >= 0) & (u < depth.shape[1]) & (v >= 0) & (v < depth.shape[0])
    u = u[valid]
    v = v[valid]
    z = z[valid]

    if u.numel() == 0:
        return float("nan"), float("nan")

    sampled_depth = depth[v, u]
    mae = torch.mean(torch.abs(sampled_depth - z)).item() / 1000.0
    rmse = torch.sqrt(torch.mean((sampled_depth - z) ** 2)).item() / 1000.0
    return mae, rmse


def evaluate_method(cli_args: argparse.Namespace, method: str, dataset: str) -> dict[str, Any]:
    repo_args = build_repo_args(cli_args, dataset)
    ckpt_path = checkpoint_for_method(cli_args, method)
    model, load_info = make_model(method, repo_args, ckpt_path)
    device = torch.device(repo_args.device)

    if dataset == "synthetic":
        from core.stereo_datasets import fetch_dataloader

        loader = fetch_dataloader(repo_args)
        metric_values = []
        total_forward_time = 0.0
        samples = 0
        single_exp = torch.tensor([[2.0]], dtype=torch.float32, device=device)
        exp1 = torch.tensor([[2.0]], dtype=torch.float32, device=device)
        exp2 = torch.tensor([[2.0]], dtype=torch.float32, device=device)

        with torch.inference_mode():
            for batch in loader:
                _, left_hdr, right_hdr, left_next_hdr, right_next_hdr, disp, valid = batch
                left_hdr = left_hdr.to(device)
                right_hdr = right_hdr.to(device)
                left_next_hdr = left_next_hdr.to(device)
                right_next_hdr = right_next_hdr.to(device)
                disp = disp.to(device)
                valid = valid.to(device)

                start = time.perf_counter()
                if method == "adec":
                    disp_predictions, _, _, _, exp1, exp2, _, _, _, _ = model(
                        left_hdr,
                        right_hdr,
                        left_next_hdr,
                        right_next_hdr,
                        exp1,
                        exp2,
                    )
                    exp1 = exp1.detach()
                    exp2 = exp2.detach()
                else:
                    disp_predictions, single_exp, _, _, _ = model(left_hdr, right_hdr, single_exp)
                    single_exp = single_exp.detach()
                total_forward_time += time.perf_counter() - start

                metric_values.append(masked_mae(disp_predictions[-1], disp, valid))
                samples += 1
                if cli_args.max_samples is not None and samples >= cli_args.max_samples:
                    break

        return {
            "method": method,
            "dataset": dataset,
            "samples": samples,
            "disparity_mae_px": float(np.nanmean(metric_values)),
            "forward_fps": float(samples / total_forward_time) if total_forward_time > 0 else float("nan"),
            "checkpoint": ckpt_path,
            "load_info": load_info,
            "ablations": {
                "disable_adec": bool(repo_args.disable_adec),
                "disable_motion_compensation": bool(repo_args.disable_motion_compensation),
                "disable_weighted_fusion": bool(repo_args.disable_weighted_fusion),
            },
        }

    from core.real_datasets_lidar import fetch_real_dataloader

    loader = fetch_real_dataloader(repo_args)
    mae_values = []
    rmse_values = []
    total_forward_time = 0.0
    samples = 0
    single_exp = torch.tensor([[2.0]], dtype=torch.float32, device=device)
    exp1 = torch.tensor([[2.0]], dtype=torch.float32, device=device)
    exp2 = torch.tensor([[2.0]], dtype=torch.float32, device=device)
    fixed_range_middle = torch.tensor([0.5], dtype=torch.float32, device=device)

    with torch.inference_mode():
        for batch in loader:
            if batch is None:
                continue

            _, left_hdr, right_hdr, left_next_hdr, right_next_hdr, focal_length, baseline, points, _, _ = batch
            left_hdr = left_hdr.to(device)
            right_hdr = right_hdr.to(device)
            left_next_hdr = left_next_hdr.to(device)
            right_next_hdr = right_next_hdr.to(device)
            focal_length = focal_length.to(device)
            baseline = baseline.to(device)
            points = points.to(device)

            start = time.perf_counter()
            if method == "adec":
                disp_predictions, _, _, _, exp1, exp2, _, _, _, fixed_range_middle = model(
                    left_hdr,
                    right_hdr,
                    left_next_hdr,
                    right_next_hdr,
                    exp1,
                    exp2,
                    test_mode=True,
                    fixed_range_middle=fixed_range_middle,
                )
                exp1 = exp1.detach()
                exp2 = exp2.detach()
                fixed_range_middle = fixed_range_middle.detach()
            else:
                disp_predictions, single_exp, _, _, _ = model(left_hdr, right_hdr, single_exp)
                single_exp = single_exp.detach()
            total_forward_time += time.perf_counter() - start

            mae, rmse = lidar_depth_metrics(disp_predictions[-1], points, focal_length, baseline)
            mae_values.append(mae)
            rmse_values.append(rmse)
            samples += 1
            if cli_args.max_samples is not None and samples >= cli_args.max_samples:
                break

    return {
        "method": method,
        "dataset": dataset,
        "samples": samples,
        "depth_mae_m": float(np.nanmean(mae_values)),
        "depth_rmse_m": float(np.nanmean(rmse_values)),
        "forward_fps": float(samples / total_forward_time) if total_forward_time > 0 else float("nan"),
        "checkpoint": ckpt_path,
        "load_info": load_info,
        "ablations": {
            "disable_adec": bool(repo_args.disable_adec),
            "disable_motion_compensation": bool(repo_args.disable_motion_compensation),
            "disable_weighted_fusion": bool(repo_args.disable_weighted_fusion),
        },
    }


def print_results(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        if row["dataset"] == "synthetic":
            metric = f"disp_mae={row['disparity_mae_px']:.4f}px"
        else:
            metric = f"depth_mae={row['depth_mae_m']:.4f}m rmse={row['depth_rmse_m']:.4f}m"
        print(
            f"{row['dataset']:>9} | {row['method']:<8} | {metric} | "
            f"forward_fps={row['forward_fps']:.2f} | samples={row['samples']}"
        )


def save_results(rows: list[dict[str, Any]], output_path: str | None) -> None:
    if output_path is None:
        return
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(rows, indent=2))
