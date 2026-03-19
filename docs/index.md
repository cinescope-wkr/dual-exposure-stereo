<div class="hero" markdown>
<div class="hero__eyebrow">CVPR 2025</div>

# Dual Exposure Stereo for Extended Dynamic Range 3D Imaging

Documentation and research code for dual-exposure stereo, linking the CVPR 2025 paper to the implementation of ADEC, image formation, motion-aware fusion, and stereo disparity estimation.

<div class="hero__actions" markdown>
[Get Started](getting-started.md){ .md-button .md-button--primary }
[Project Page](https://light.princeton.edu/publication/dual-exposure-stereo/){ .hero__link }
[Paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf){ .hero__link }
[Docs URL](https://cinescope-wkr.github.io/dual-exposure-stereo/){ .hero__link }
</div>
</div>

<div class="status-box" markdown>
**Repository status**

This repository is currently best understood as a documented research code release with validation utilities and paper-to-code mapping first.

<div class="status-grid" markdown>
<div class="status-chip">
<div class="status-chip__label">Assets</div>
<div class="status-chip__value">Dataset release and pretrained checkpoints are being reorganized.</div>
</div>
<div class="status-chip">
<div class="status-chip__label">Updates</div>
<div class="status-chip__value">Public assets and related dataset-generation code will be updated again.</div>
</div>
<div class="status-chip">
<div class="status-chip__label">Maintainer</div>
<div class="status-chip__value">Jinwoo Lee (`cinescope@kaist.ac.kr`)</div>
</div>
</div>
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

  Read the official CVPR 2025 paper through CVF OpenAccess.

  [OpenAccess PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf)

- **Project Page**

  Browse the project overview, videos, bibtex, and external links.

  [Project Page](https://light.princeton.edu/publication/dual-exposure-stereo/)

- **Documentation**

  Use the MkDocs site as the main paper-to-code reading path for the repository.

  [Documentation URL](https://cinescope-wkr.github.io/dual-exposure-stereo/)

- **Local Paper Assets**

  The repository also bundles the local paper PDF and teaser asset under `paper/`.

- **Validation**

  Run the lightweight validators and tests before full asset-based experiments.

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
