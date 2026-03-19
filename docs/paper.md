# Paper and Project

## Primary Links

- [Project page](https://light.princeton.edu/publication/dual-exposure-stereo/)
- [CVPR 2025 OpenAccess paper](https://openaccess.thecvf.com/content/CVPR2025/papers/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf)

The project page is a good companion to the paper because it collects the overview, videos, bibtex, and external paper/code/data links in one place.

## Paper Summary

The paper introduces **dual-exposure stereo** for extended-dynamic-range 3D imaging. Instead of relying on a single exposure for stereo capture, the method alternates between two exposure settings and adapts them to the scene. It then estimates disparity by compensating for motion between consecutive frames and fusing information from both exposures.

At a high level, the paper argues that:

- conventional stereo can fail badly when highlights saturate or shadows collapse
- classical auto exposure alone does not increase the camera's native dynamic range
- dual exposures can cover complementary radiance regions if they are controlled and fused carefully

## Main Contributions

The paper presents three main contributions:

- an automatic dual-exposure control strategy that combines auto exposure ideas with exposure bracketing
- a motion-aware dual-exposure stereo estimation method for disparity reconstruction
- validation on both synthetic data and a real robot-mounted stereo-plus-LiDAR capture setup

## Project Page Content That Informs This Repo

The project page highlights several components that are directly reflected in the repository:

- **Synthetic Dataset**
  The project page describes a synthetic HDR stereo dataset rendered with CARLA.
- **Real Dataset**
  The project page describes a real stereo-LiDAR dataset captured with a calibrated mobile platform.
- **Auto Dual Exposure Control**
  The project page summarizes the ADEC controller as adapting the exposure gap when the scene dynamic range exceeds the camera's range, and otherwise steering exposures toward a balanced state.
- **Dual-exposure Stereo Estimation**
  The project page explains that temporal alignment is used before fusing the two exposures for disparity estimation.

## Local Repository Assets

This repository bundles:

- `paper/Choi_Dual_Exposure_Stereo_for_Extended_Dynamic_Range_3D_Imaging_CVPR_2025_paper.pdf`
- `paper/teaser.pdf`

These local assets are useful for archival and presentation workflows even when the site itself links primarily to the official project and OpenAccess paper pages.
