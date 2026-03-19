from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".mplconfig"))
(REPO_ROOT / ".mplconfig").mkdir(exist_ok=True)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.mock_validation import (
    check_adec_expands_exposure_gap,
    check_dual_exposure_stereo_gain,
    check_motion_compensated_fusion_alignment,
    check_repo_image_formation_complementarity,
)


class DualExposureLogicTests(unittest.TestCase):
    def test_repo_image_formation_complementarity(self) -> None:
        result = check_repo_image_formation_complementarity()
        self.assertTrue(result.passed, result.detail)
        self.assertGreater(result.metrics["union_coverage"], result.metrics["high_coverage"] + 0.10)
        self.assertGreater(result.metrics["union_coverage"], result.metrics["low_coverage"] + 0.09)

    def test_adec_expands_exposure_gap(self) -> None:
        result = check_adec_expands_exposure_gap()
        self.assertTrue(result.passed, result.detail)
        self.assertGreater(result.metrics["adjusted_gap"], result.metrics["initial_gap"] + 0.04)

    def test_dual_exposure_stereo_gain(self) -> None:
        result = check_dual_exposure_stereo_gain()
        self.assertTrue(result.passed, result.detail)
        self.assertLess(result.metrics["fused_mae"], result.metrics["high_only_mae"] * 0.2)
        self.assertLess(result.metrics["fused_mae"], result.metrics["low_only_mae"] * 0.2)

    def test_motion_compensated_fusion_alignment(self) -> None:
        result = check_motion_compensated_fusion_alignment()
        self.assertTrue(result.passed, result.detail)
        self.assertLess(result.metrics["warped_error"], result.metrics["unwarped_error"] * 0.2)


if __name__ == "__main__":
    unittest.main()
