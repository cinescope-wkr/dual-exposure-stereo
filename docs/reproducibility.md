# Reproducibility

!!! important
    The **full dataset release** and **pretrained checkpoints** are currently being reorganized.
    The current repository is best read as a documented research code release with validation
    tools and paper-to-code mapping first, with public asset packaging, related dataset
    generation code, and dataset sanity and volume preparation work to be updated again.

## What Can Be Validated Today

The repository already supports several meaningful checks without the full paper-scale assets:

- static repository validation through `tools/validate_paper_repro.py`
- mock-scene functional validation through `tools/validate_dual_exposure_logic.py`
- regression-style unit tests in `test/test_dual_exposure_logic.py`

## Mock-Scene Validation

Run:

```bash
python tools/validate_dual_exposure_logic.py
```

This validator checks:

- repository image formation creates complementary valid regions across two exposures
- ADEC expands the exposure gap on a synthetic HDR scene
- dual-exposure fusion improves disparity estimation on a known-disparity mock stereo pair
- motion compensation improves temporal alignment before fusion

## Unit Tests

Run:

```bash
python -m unittest discover -s test -p 'test_dual_exposure_logic.py' -v
```

These tests provide a small regression harness for the core dual-exposure logic.

## Paper-Facing Reproduction Scripts

The repository also includes:

- `tools/reproduce_table1.py`
- `tools/reproduce_table2.py`

These are intended as paper-facing runners, but they still depend on datasets, checkpoints, and environment compatibility that are not fully packaged in the current release.

## Current Gaps

The main blockers for full paper-scale reproduction are:

- full datasets are not currently bundled
- checkpoints are not currently bundled
- some paper rows still depend on assets or variants not packaged here
- environment compatibility can matter because the ML stack is pinned to older versions than some modern Python setups

## Recommended Workflow

1. Install the runtime dependencies.
2. Run `python tools/validate_paper_repro.py`.
3. Run `python tools/validate_dual_exposure_logic.py`.
4. Run the unit tests.
5. Populate the expected datasets and checkpoints once the reorganized asset release is available.
6. Use the paper-facing benchmark scripts for larger-scale reproduction.

## Further Audit

For a repository-specific audit of alignment and gaps, see `PAPER_REPRODUCIBILITY.md` in the repository root.
