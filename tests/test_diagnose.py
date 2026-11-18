import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import diagnose


class FakeCapture:
    monitors = [
        {"left": -100, "top": 0, "width": 300, "height": 200},
        {"left": -100, "top": 0, "width": 300, "height": 200},
    ]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def grab(self, box):
        self.box = box
        return Mock(width=box["width"], height=box["height"])


class DiagnoseTests(unittest.TestCase):
    def test_missing_dependency_has_install_hint(self):
        def missing(_):
            raise ImportError("missing")

        results = diagnose.check_dependencies(missing)
        self.assertEqual(len(results), 3)
        self.assertTrue(all(not ok and "MAC_SETUP.md" in message for ok, message in results))

    def test_capture_uses_monitor_origin_and_small_sample(self):
        capture = FakeCapture()
        ok, _ = diagnose.capture_check(1, lambda: capture)
        self.assertTrue(ok)
        self.assertEqual(capture.box, {"left": -100, "top": 0, "width": 32, "height": 32})

    def test_invalid_monitor_does_not_capture(self):
        capture = FakeCapture()
        ok, message = diagnose.capture_check(2, lambda: capture)
        self.assertFalse(ok)
        self.assertIn("choose 1 through 1", message)
        self.assertFalse(hasattr(capture, "box"))

    def test_capture_failure_has_permission_hint(self):
        capture = FakeCapture()
        capture.grab = Mock(side_effect=RuntimeError("denied"))
        with patch.object(diagnose.platform, "system", return_value="Darwin"):
            ok, message = diagnose.capture_check(1, lambda: capture)
        self.assertFalse(ok)
        self.assertIn("Screen Recording", message)

    def test_permission_preflight(self):
        library = Mock()
        library.CGPreflightScreenCaptureAccess.return_value = False
        self.assertIs(diagnose.screen_permission("Darwin", library), False)
        self.assertIs(diagnose.screen_permission("Linux", library), None)


if __name__ == "__main__":
    unittest.main()
