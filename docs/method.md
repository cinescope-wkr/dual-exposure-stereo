# Method Overview

This page is meant to be the main **paper-to-code bridge** for the repository.
It does not just summarize the pipeline. It also explains where the paper's key
equations and logic appear in the code, and where the implementation makes
practical engineering choices beyond the compact mathematical presentation.

## Pipeline at a Glance

The repository implements the method as the following connected stages:

1. auto dual exposure control (`ADEC`)
2. image formation from HDR scene radiance to captured LDR images
3. motion estimation between alternating frames
4. temporal warping and dual-exposure feature fusion
5. stereo correlation-volume construction and disparity estimation

## Reading Order

If you want to study the implementation with the paper open next to it, this is a good order:

1. `core/adec.py`
2. `core/utils/simulate.py`
3. `core/utils/mask.py`
4. `core/disp_recon_model_dual.py`
5. `core/combine_model_dual.py`

## Equation-by-Equation Mapping

| Paper item | Paper role | Main repository location | What to look for |
| --- | --- | --- | --- |
| Eq. (1) | image formation | `core/utils/simulate.py` | `ImageFormation.__init__`, `noise_modeling()` |
| Algorithm 1 | ADEC | `core/adec.py` | histogram, skewness, clamping ratio, exposure-gap update |
| Eq. (6) | optical flow model between alternating frames | `core/disp_recon_model_dual.py` | `compute_optical_flow_batch()` |
| Eq. (7) | warping from frame 2 to frame 1 | `core/disp_recon_model_dual.py` | `warp_feature_map()` |
| Eq. (8) | feature extraction | `core/disp_recon_model_dual.py` | `self.fnet(...)` |
| Eq. (9) | warped second-frame feature | `core/disp_recon_model_dual.py` | `warped_fmap_left`, `warped_fmap_right` |
| Eq. (10) | weighted dual-exposure fusion | `core/disp_recon_model_dual.py` | `mask_based_feature_fusion()` |
| Eq. (11) | trapezoidal exposure weights | `core/utils/mask.py` | `soft_binary_threshold_batch()` |
| Eq. (12) | correlation volume for disparity | `core/disp_recon_model_dual.py` | `corr_block(...)`, `corr_fn(coords1)` |

## 1. Image Formation: Equation (1)

The paper's image-formation model appears most directly in `core/utils/simulate.py`.

### Paper logic

Equation (1) models captured intensity as a sequence of:

- exposure-dependent photon collection
- pre-gain and post-gain noise
- clipping by camera dynamic range
- quantization

The paper also defines:

- shutter time `t_i = e_i / g_i`
- gain `g_i = max(1, e_i / t_max)`

### Code mapping

In the repository:

- `ImageFormation.__init__` computes the exposure-dependent gain and shutter time
- `ImageFormation.noise_modeling()` applies noise, clipping, and normalization
- `QuantizeSTE` is used to simulate quantization before the stereo network consumes the image

### Important implementation note

The code follows the paper's structure closely, but not symbol-for-symbol.
In particular, the repository uses a practical normalized image simulation path
around the clipped intensity range before quantization. So the implementation is
best understood as a paper-aligned simulation module rather than a literal one-line transcription of Equation (1).

## 2. ADEC: Algorithm 1

The paper's automatic dual exposure control is implemented in `core/adec.py`.

### Paper logic

Algorithm 1 describes the controller in two phases:

1. compute histogram-derived metrics for each exposure
2. decide whether to diverge or converge the exposure pair

The paper uses:

- histograms
- skewness
- low/high extreme-pixel ratios
- the exposure-gap threshold

### Code mapping

The main repository pieces are:

- `calculate_histogram_global()` for the global histogram
- `calculate_batch_skewness()` for skewness-driven balancing
- `clamping_ratio()` and `clamping_ratio_flag()` for HDR / clipping detection
- `adjust_exposure_gap()` for increasing the exposure separation
- `stereo_exposure_control()` for the full controller update

### How the logic reads in code

`stereo_exposure_control()` is the best single function to inspect. It follows the same two-branch logic as the paper:

- if the scene appears wider than the camera's dynamic range, widen the dual-exposure gap
- otherwise, move the exposures toward a more balanced state using skewness-related adjustment

This is the code location that most directly corresponds to the paper's control pseudocode.

## 3. Motion Between Alternating Frames: Equations (6) and (7)

The paper treats the two exposures as arriving in alternating frames, which means temporal motion must be compensated before fusion.

### Paper logic

- Eq. (6) defines optical flow between corresponding pixels in alternating frames
- Eq. (7) defines warping from frame 2 into frame 1 coordinates

### Code mapping

In `core/disp_recon_model_dual.py`:

- `compute_optical_flow_batch()` estimates the left and right flow fields
- `warp_feature_map()` applies the warp operation
- `resize_flow()` handles resolution conversion when the flow is applied at feature-map scale

### Practical implementation detail

The repository uses a pretrained optical-flow model as an engineering realization of the paper's motion-compensation step. In other words, the paper expresses the transformation abstractly, while the code instantiates it with a concrete learned flow estimator and `grid_sample`-based warping.

## 4. Feature Extraction: Equation (8)

The paper defines feature extraction with a feature encoder applied to the dual-exposure images.

### Code mapping

In `core/disp_recon_model_dual.py`:

- `self.fnet(...)` extracts stereo features
- `self.cnet(...)` extracts context features used by the recurrent stereo update block

The most direct correspondence to Eq. (8) is:

- `fmap1`, `fmap2` for the current frame
- `fmap1_next`, `fmap2_next` for the second frame

These are the features that later get warped and fused.

## 5. Temporal Feature Alignment: Equation (9)

After optical flow is estimated, the second-frame features are warped into the first-frame coordinate system.

### Code mapping

Look for:

- `warped_fmap_left = self.warp_feature_map(fmap1_next, flow_left)`
- `warped_fmap_right = self.warp_feature_map(fmap2_next, flow_right)`

This is the practical code counterpart of Eq. (9).

The same pattern is reused for:

- exposure masks
- context-network feature maps at multiple scales

So the repository extends the paper's alignment idea consistently across the feature hierarchy, not just one tensor.

## 6. Weighted Dual-Exposure Fusion: Equations (10) and (11)

This is one of the most important paper-to-code mappings in the repository.

### Paper logic

- Eq. (10) defines the fused feature as a weighted combination of two aligned exposure features
- Eq. (11) defines the weight map with a trapezoidal intensity function so that well-exposed pixels receive higher weight

### Code mapping

The main code pieces are:

- `core/utils/mask.py`
  - `soft_binary_threshold_batch()`
- `core/disp_recon_model_dual.py`
  - `resize_soft_binary_mask()`
  - `mask_based_feature_fusion()`

### What the code is doing

`soft_binary_threshold_batch()` provides the paper-style trapezoidal weighting logic in tensor form.

Then `mask_based_feature_fusion()` implements the weighted fusion itself:

- current-frame feature weighted by its exposure-validity mask
- temporally warped second-frame feature weighted by its exposure-validity mask
- safe normalization to avoid division by zero
- fallback logic for near-empty or failed warp regions

### Important implementation note

The paper states the trapezoidal thresholds as `alpha = 0.02` and `beta = 0.98`.
The repository default in `soft_binary_threshold_batch()` uses `alpha = 0.01` and `beta = 0.99`.

That means the code is **paper-aligned in structure**, but not strictly identical in every numeric default. This is exactly the kind of detail that matters when interpreting paper-to-code fidelity.

## 7. Stereo Correlation Volume: Equation (12)

The paper defines the correlation volume from the fused left and right features.

### Code mapping

In `core/disp_recon_model_dual.py`:

- the code selects a correlation implementation such as `CorrBlock1D`
- `corr_fn = corr_block(fused_fmap1, fused_fmap2, ...)`
- `corr = corr_fn(coords1)` indexes the correlation volume during iterative disparity refinement

This is the RAFT-style implementation counterpart of Eq. (12).

### Practical interpretation

The paper writes the correlation volume explicitly as a dot product over disparity offsets.
The code realizes the same idea through the RAFT-Stereo correlation-block abstraction and an iterative update loop.

## 8. End-to-End Orchestration

The cleanest single end-to-end path is in `core/combine_model_dual.py`.

That wrapper:

1. simulates captured LDR images from HDR inputs using `ImageFormation`
2. runs ADEC through `stereo_exposure_control()`
3. resimulates the adjusted dual exposures
4. passes the captured stereo inputs into the dual-exposure disparity network

So if you want to see how the paper's pieces are wired together in actual inference order,
`CombineModel.forward()` is the best top-level function to read.

## Where the Docs Are Faithful vs. Approximate

The repository matches the paper clearly at the level of:

- major method stages
- control logic structure
- flow-warp-fuse-disparity pipeline design
- dataset split intent

The repository is less literal at the level of:

- exact numerical defaults in some helper functions
- implementation details introduced by the chosen stereo backbone
- engineering choices required for training and inference code organization

That is normal for research code. The important question is whether the implementation preserves the method logic, and here the answer is broadly yes.

## Validation Hooks for the Core Logic

To make the code-to-paper mapping more inspectable without full paper assets, the repository now includes:

- `tools/validate_dual_exposure_logic.py`
- `core/mock_validation.py`
- `test/test_dual_exposure_logic.py`

These validate the qualitative logic that the paper is built on:

- two exposures provide complementary valid regions
- ADEC widens the exposure gap when appropriate
- dual-exposure fusion improves disparity relative to single-exposure inputs
- motion compensation helps align alternating-frame information before fusion

## Bottom Line

If you want the shortest answer to "does the documentation explain the code-to-paper mapping in enough detail?", the answer is now:

- yes for the main method stages
- yes for the key equations and algorithmic blocks
- with explicit notes where the implementation is paper-aligned in spirit but not a literal line-by-line transcription
