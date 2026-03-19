<div class="hero" markdown>
<div class="hero__eyebrow">CVPR 2025</div>

# Dual Exposure Stereo for Extended Dynamic Range 3D Imaging

Research code and documentation for dual-exposure stereo: automatic dual exposure control, motion-aware cross-frame fusion, and extended-dynamic-range 3D imaging with stereo cameras.

[Project Page](https://light.princeton.edu/publication/dual-exposure-stereo/){ .md-button .md-button--primary }
[Paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf){ .md-button }
[Getting Started](getting-started.md){ .md-button }
</div>

<div class="status-box" markdown>
**Repository status**

The codebase is public, but the **full dataset release** and **pretrained checkpoints** are currently being reorganized. This repository is therefore positioned as a documented research code release with validation utilities and paper-to-code mapping first. We plan to update the public assets and related dataset-generation code again soon.

Maintainer: **Jinwoo Lee (cinescope@kaist.ac.kr)**
</div>

## What This Site Covers

This documentation is designed to connect the repository to the paper and project page more clearly:

- the paper and project context
- the method structure and code mapping
- the detailed equation-to-code relationship for the core method
- the current reproducibility status
- the expected data and checkpoint layout
- the lightweight validation tools already available in this repo

## Quick Links

<div class="grid cards" markdown>

- **Paper**

  The official CVPR 2025 paper is available through CVF OpenAccess.

  [OpenAccess PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf)

- **Project Page**

  The project page includes overview text, videos, bibtex, and external paper/code/data links.

  [Project Page](https://light.princeton.edu/publication/dual-exposure-stereo/)

- **Local Paper Assets**

  This repository also bundles a local paper PDF at `paper/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf` and a local teaser asset at `paper/teaser.pdf`.

- **Validation**

  The repository now includes a mock-scene logic validator and unit tests for key method behavior.

  [Reproducibility](reproducibility.md)

</div>

## Method in One View

The method combines three main ideas:

1. `ADEC` adjusts a pair of stereo exposures instead of relying on a single-exposure controller.
2. Alternating frames capture complementary bright and dark scene regions under different exposures.
3. Motion-aware dual-exposure fusion aligns and combines information across frames before stereo disparity estimation.

This allows the system to preserve more useful information for depth estimation in scenes where a single exposure would either clip highlights or bury shadows.

## Why the Repository Is Structured This Way

The paper evaluates both synthetic CARLA data and real stereo-plus-LiDAR capture. The repository therefore separates:

- exposure control logic in `core/adec.py`
- image formation and simulation utilities in `core/utils/simulate.py`
- dual-exposure stereo fusion in `core/disp_recon_model_dual.py`
- end-to-end orchestration in `core/combine_model_dual.py`
- dataset loading for synthetic and real settings

For a guided walkthrough, continue to [Method Overview](method.md) and [Repository Guide](repository.md).
