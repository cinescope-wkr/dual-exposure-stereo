---
hide:
  - toc
---

<section class="des-hero" markdown="1">

<div class="des-kicker">CVPR 2025</div>

# Dual Exposure Stereo for Extended Dynamic Range 3D Imaging

<p class="des-hero-lead">
This site is the main paper-to-code guide for the repository: how the dual-exposure
stereo method is organized, where the paper logic appears in the implementation,
what is already reproducible from the checked-in code, and what public assets are
still being reorganized.
</p>

[Get Started](getting-started.md){ .md-button .md-button--primary }
[Read the Method](method.md){ .md-button }
[Check Reproducibility](reproducibility.md){ .md-button }

</section>

<div class="des-mini-note" markdown="1">
The **full dataset release**, **pretrained checkpoints**, and related **dataset-generation code**
are currently being reorganized. For now, this repository is best read as a documented research
code release with validators, code-to-paper mapping, and reproducibility notes first.

Maintainer: **Jinwoo Lee (`cinescope@kaist.ac.kr`)**
</div>

## What You Will Find Here

This documentation is designed to be the fast path through the repository: paper context,
method structure, equation-to-code mapping, reproducibility status, and the expected data/checkpoint layout.

<div class="grid cards" markdown="1">

- [**Project page**](https://light.princeton.edu/publication/dual-exposure-stereo/)

  ---

  Start from the public project overview, videos, bibtex, and external links.

- [**Paper**](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf)

  ---

  Read the official CVPR 2025 paper through CVF OpenAccess.

- [**Method overview**](method.md)

  ---

  See the strongest paper-to-code bridge, including equation and logic mapping.

- [**Reproducibility**](reproducibility.md)

  ---

  Check what can be validated today and what still depends on future asset updates.

</div>

## Find What You Need

If you are here for something specific, start from one of these pages:

<div class="grid cards" markdown="1">

- [**I want to run something quickly**](getting-started.md)

  ---

  Start with installation, validation commands, local docs preview, and first entry points.

- [**I want the paper-to-code map**](method.md)

  ---

  Follow the implementation through ADEC, image formation, warping, fusion, and stereo matching.

- [**I want the repository structure**](repository.md)

  ---

  See how `core/`, `tools/`, `test/`, `paper/`, and the MkDocs site fit together.

- [**I want the data and checkpoint status**](data-and-checkpoints.md)

  ---

  See the expected layout, current packaging status, and what is still being reorganized.

- [**I want the validation story**](reproducibility.md)

  ---

  Start from the shipped validators, unit tests, and current reproduction boundaries.

- [**I want the citation information**](citation.md)

  ---

  Use the BibTeX entry, project page, and paper links from one place.

</div>

## Method in One View

The method combines three main ideas:

1. `ADEC` adapts a pair of stereo exposures instead of relying on a single-exposure controller.
2. Alternating frames capture complementary bright and dark scene regions under different exposures.
3. Motion-aware dual-exposure fusion aligns and combines information across frames before stereo disparity estimation.

This allows the system to preserve more useful depth cues in scenes where a single exposure would either clip highlights or bury shadows.

## Recommended Reading Path

1. Start with [Getting Started](getting-started.md) for installation, docs preview, and validators.
2. Move to [Paper and Project](paper.md) for the public paper context.
3. Read [Method Overview](method.md) for the equation-to-code mapping.
4. Continue with [Repository Guide](repository.md) and [Data and Checkpoints](data-and-checkpoints.md).
5. Finish with [Reproducibility](reproducibility.md) if you are trying to reproduce or audit the current public release.

## Audience

This repository is intended for researchers and developers working on stereo vision,
computational imaging, HDR capture, robotic perception, and related areas that need a
clear link between a published method and its codebase.
