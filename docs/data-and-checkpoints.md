# Data and Checkpoints

## Availability Status

!!! important
    The **full dataset release** and **pretrained checkpoints** are currently being reorganized. This repository therefore documents the expected structure and supported code paths clearly, but it does **not** yet serve as a full paper-scale asset drop. Public asset packaging, related dataset-generation code, and dataset sanity and volume preparation work are all still in progress, and we intend to update the public release again soon.

## Synthetic CARLA Layout

Expected path:

```text
datasets/
└── CARLA/
    ├── training/
    │   └── Experiment*/
    │       ├── ground_truth_depth_left/
    │       ├── ground_truth_depth_right/
    │       ├── ground_truth_disparity_left/
    │       ├── ground_truth_disparity_right/
    │       ├── hdr_left/
    │       ├── hdr_right/
    │       ├── calibration_file_extrinsic_left.npy
    │       ├── calibration_file_extrinsic_right.npy
    │       └── calibration_file_intrinsic.npy
    └── test/
        └── Experiment*/
```

The paper reports a much larger synthetic setup than what is bundled here. The checked-in repository documents the expected loader layout, but not the full paper-scale asset release.

## Real Stereo + LiDAR Layout

Expected path:

```text
datasets/
├── Real/
│   └── <date>/<time>/
│       ├── left.npy
│       ├── right.npy
│       └── points.npy
└── camera_params/
    └── post.npz
```

The real-data loader assumes synchronized stereo data, projected LiDAR supervision, and calibrated camera parameters.

## Expected Checkpoint Paths

The repository currently references example checkpoint paths such as:

- `models/raftstereo-eth3d.pth`
- `checkpoints/10000_disp_gru_eth3d_blur_gmflow_iter20.pth`
- `checkpoints/5000_disp_fusion_mask_finetuned_gru.pth`

These paths are documented because the training and evaluation scripts expect them, but the checkpoint files themselves are not currently bundled.

## Practical Interpretation

At the moment, this repository is best understood as providing:

- the paper-linked implementation
- the dataset/checkpoint interface contracts
- validator and reproducibility helpers
- a clearer documentation layer for future public asset updates

If you need the complete public asset release, please watch for the next documentation update.
