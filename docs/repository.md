# Repository Guide

## Top-Level Layout

```text
core/
  adec.py
  combine_model_dual.py
  disp_recon_model_dual.py
  disp_recon_model_dual_finetune.py
  stereo_datasets.py
  real_datasets_lidar.py
  utils/
paper/
tools/
test/
train_disp_recon_dual.py
test_sequence_carla.py
test_sequence_real.py
evaluate_stereo_dual.py
```

## Main Research Components

### `core/`

The main method implementation lives here:

- `adec.py` for exposure control
- `combine_model_dual.py` for end-to-end orchestration
- `disp_recon_model_dual.py` for dual-exposure stereo estimation
- `stereo_datasets.py` and `real_datasets_lidar.py` for dataset access

### `tools/`

This directory now serves paper-facing and validation-facing workflows:

- `validate_paper_repro.py`
- `validate_dual_exposure_logic.py`
- `reproduce_table1.py`
- `reproduce_table2.py`

### `test/`

This directory contains regression-style validation, including the mock-scene unit tests for key dual-exposure logic.

## Recommended Reading Order

If you are trying to understand the repository for the first time, this order works well:

1. `README.md`
2. `PAPER_REPRODUCIBILITY.md`
3. `core/adec.py`
4. `core/utils/simulate.py`
5. `core/disp_recon_model_dual.py`
6. `core/combine_model_dual.py`
7. `tools/validate_dual_exposure_logic.py`

## Entry Points

### Training

```bash
python train_disp_recon_dual.py --restore_ckpt models/raftstereo-eth3d.pth --num_steps 10000 --batch_size 4
```

### Synthetic Evaluation

```bash
python test_sequence_carla.py --restore_ckpt checkpoints/10000_disp_gru_eth3d_blur_gmflow_iter20.pth --batch_size 1
```

### Real Evaluation

```bash
python test_sequence_real.py --restore_ckpt checkpoints/5000_disp_fusion_mask_finetuned_gru.pth --batch_size 1
```

## Documentation Design Goal

This MkDocs site is intentionally organized around the paper and project narrative, not just file listings. The goal is to help readers move from:

- paper claim
- to repository component
- to current reproducibility status

with much less guesswork than a code-only release.
