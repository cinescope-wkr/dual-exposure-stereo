# Getting Started

## Environment

Install the main runtime dependencies:

```bash
pip install -r requirements.txt
```

If you also want to build the documentation locally:

```bash
pip install -r requirements-docs.txt
```

## Core Entry Points

The repository currently exposes three main runnable paths:

- `train_disp_recon_dual.py` for synthetic training
- `test_sequence_carla.py` for synthetic sequence evaluation
- `test_sequence_real.py` for real sequence evaluation with projected LiDAR

## Validation First

Before attempting paper-style evaluation, start with the shipped validation tools:

```bash
python tools/validate_paper_repro.py
python tools/validate_dual_exposure_logic.py
python -m unittest discover -s test -p 'test_dual_exposure_logic.py' -v
```

These do not require the full paper-scale assets and help verify that the key repository logic is wired correctly.

## Build the Docs Locally

To preview the MkDocs site:

```bash
mkdocs serve
```

or:

```bash
make docs-serve
```

To build the static site:

```bash
mkdocs build
```

or:

```bash
make docs-build
```

The repository also includes a GitHub Pages workflow at `.github/workflows/docs.yml`
so the same MkDocs site can be deployed automatically from `main`.

Planned documentation URL:

- <https://cinescope-wkr.github.io/dual-exposure-stereo/>

## Current Availability Note

!!! note
    The repository is public now, but the **full dataset release** and **pretrained checkpoints** are still being reorganized. If you are looking for the complete paper-scale assets, please treat the current repository as a code-and-documentation release first. Asset packaging, related dataset-generation code, and dataset sanity and volume preparation work are still in progress.

## Primary References

- [Project page](https://light.princeton.edu/publication/dual-exposure-stereo/)
- [CVPR 2025 OpenAccess paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf)
