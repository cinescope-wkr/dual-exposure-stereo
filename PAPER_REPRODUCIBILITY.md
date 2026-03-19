# Paper Reproducibility Audit

This document explains how the current repository maps to the CVPR 2025 paper
`Dual Exposure Stereo for Extended Dynamic Range 3D Imaging`, what can already
be validated from the checked-in code, and what still blocks full paper-scale
reproduction.

Primary references:

- [Project page](https://light.princeton.edu/publication/dual-exposure-stereo/)
- [CVPR 2025 OpenAccess paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf)

> [!NOTE]
> The repository is public, but the **full dataset release** and **pretrained checkpoints**
> are currently being reorganized. At the moment, this repository should be understood as
> a documented research code release with validators, paper-to-code mapping, and runnable
> entry points first. Public asset packaging, related dataset-generation code, and ongoing
> dataset sanity and volume preparation work are being cleaned up and will be updated again.
>
> Maintainer: **Jinwoo Lee (cinescope@kaist.ac.kr)**

## At a Glance

### What is already here

- the main dual-exposure stereo method code
- synthetic and real-data loader scaffolding
- paper-facing benchmark entry points
- repository validation and mock-scene logic validation
- local paper asset bundling

### What is not fully packaged yet

- full paper-scale synthetic and real datasets
- the expected released checkpoints
- some asset-dependent benchmark paths and unsupported ablation rows

## Paper-to-Code Mapping

The core method components described in the paper are reflected in the repository as follows:

- ADEC rule-based exposure control: [core/adec.py](/root/ADEC/core/adec.py)
- Image formation and capture simulation: [core/utils/simulate.py](/root/ADEC/core/utils/simulate.py)
- Motion-aware dual-exposure fusion and disparity estimation:
  [core/disp_recon_model_dual.py](/root/ADEC/core/disp_recon_model_dual.py)
- Finetuning variant:
  [core/disp_recon_model_dual_finetune.py](/root/ADEC/core/disp_recon_model_dual_finetune.py)
- End-to-end pipeline wrapper:
  [core/combine_model_dual.py](/root/ADEC/core/combine_model_dual.py)
- Synthetic CARLA loader:
  [core/stereo_datasets.py](/root/ADEC/core/stereo_datasets.py)
- Real stereo-plus-LiDAR loader:
  [core/real_datasets_lidar.py](/root/ADEC/core/real_datasets_lidar.py)

## Experimental Scope Reflected in the Repository

The checked-in code clearly reflects the paper's intended experimental structure:

- synthetic training is present
- synthetic sequence evaluation is present
- real sequence evaluation with projected LiDAR is present
- several exposure-control baselines are partially represented through `AverageAE`, `GradientAE`, and `NeuralAE`

## What Was Validated Locally

### Static and Structural Validation

The following were validated directly from the repository:

- checked-in Python files compile successfully with `py_compile`
- the bundled paper PDF is present
- the repository contains the main files required to trace the method end to end
- paper-facing benchmark runners exist in [tools/reproduce_table1.py](/root/ADEC/tools/reproduce_table1.py) and [tools/reproduce_table2.py](/root/ADEC/tools/reproduce_table2.py)

### Functional Validation Added in This Repo State

The repository now also contains a lightweight mock-scene validator and unit tests:

- [tools/validate_dual_exposure_logic.py](/root/ADEC/tools/validate_dual_exposure_logic.py)
- [core/mock_validation.py](/root/ADEC/core/mock_validation.py)
- [test/test_dual_exposure_logic.py](/root/ADEC/test/test_dual_exposure_logic.py)

These checks validate core method behavior without requiring the full paper assets:

- complementary valid coverage across dual exposures
- ADEC exposure-gap expansion on a synthetic HDR scene
- disparity gain from dual-exposure fusion
- temporal alignment gain from motion compensation

### Implementation Fixes Applied During This Audit

Several issues were corrected because they materially affect whether the code path matches the method described in the paper:

- Added the missing `random` import required by the training exposure sampler in [train_disp_recon_dual.py](/root/ADEC/train_disp_recon_dual.py)
- Fixed a frame-routing bug where `image1_next` was overwritten with `image2_next` in
  [core/disp_recon_model_dual.py](/root/ADEC/core/disp_recon_model_dual.py) and
  [core/disp_recon_model_dual_finetune.py](/root/ADEC/core/disp_recon_model_dual_finetune.py)
- Removed hard-coded CUDA device usage so execution follows the active model/input device in
  [core/combine_model_dual.py](/root/ADEC/core/combine_model_dual.py) and
  [core/disp_recon_model_dual_finetune.py](/root/ADEC/core/disp_recon_model_dual_finetune.py)

## Current Gaps vs. Full Paper Reproduction

### Environment Gaps

The local validation environment still differs from a fully prepared reproduction environment:

- Python 3.13 with `pip` 25.3 is newer than the repository's pinned ML stack and may trigger compatibility issues
- `ptlflow` was not available in the validation environment
- `opt_einsum` was not available in the validation environment
- `torchvision` was not available in the validation environment, though it is now optional for the main ADEC path

Without the missing runtime pieces, full benchmark execution cannot be confirmed end to end.

### Repository and Asset Gaps

The main repository-side blockers are straightforward:

- the paper-scale CARLA and real datasets are not bundled
- `datasets/camera_params/post.npz` is not bundled
- the checkpoints referenced by the scripts and README are not bundled
- some Table 2 rows still depend on variants that are not packaged as explicit code paths

### Paper Claims That Cannot Be Fully Verified from This Repo Alone

The following paper-level claims still require the missing assets or full benchmarking environment:

- the reported synthetic dataset scale of 1,000 training videos and 200 testing videos
- the complete real-world capture setup and dataset statistics
- the quantitative numbers in Table 1
- the complete Table 2 ablation matrix
- FPS numbers reported for the baselines and ADEC

## Recommended Reproduction Workflow

If your goal is to work from the current repository state as safely as possible, this is the recommended order:

1. Install the runtime dependencies with `pip install -r requirements.txt`
2. Run `python tools/validate_paper_repro.py`
3. Run `python tools/validate_dual_exposure_logic.py`
4. Run `python -m unittest discover -s test -p 'test_dual_exposure_logic.py' -v`
5. Populate the expected datasets once the reorganized public assets are available
6. Populate the expected checkpoints once they are republished
7. Run `python tools/reproduce_table1.py --output_json results/table1.json`
8. Run `python tools/reproduce_table2.py --output_json results/table2_supported.json`

If unsupported Table 2 rows are required, the missing fusion or backbone variants will need to be added explicitly.

## Recommended Next Steps

The most useful next improvements for full reproducibility are:

- package dataset download or preparation scripts
- package checkpoint download scripts using the filenames expected by the evaluation scripts
- add the remaining unsupported Table 2 variants as explicit code paths
- keep a small CI smoke test around the validators and unit tests

## Bottom Line

This repository is now in a much better state for **method inspection**, **paper-to-code tracing**, and **lightweight functional validation** than a bare code dump.

It is not yet a fully self-contained paper reproduction package, mainly because the
public dataset and checkpoint packaging is still being reorganized.
