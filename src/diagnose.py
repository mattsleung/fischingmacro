"""Read-only installation and screen-capture checks. No game input or uploads."""

from __future__ import annotations

import argparse
import ctypes
import importlib
import json
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEPENDENCIES = {"numpy": "numpy", "opencv-python": "cv2", "mss": "mss"}


def check_dependencies(import_module=importlib.import_module):
    results = []
    for package, module in DEPENDENCIES.items():
        try:
            import_module(module)
        except (ImportError, OSError) as exc:
            results.append((False, f"{package}: unavailable ({exc}). Run the setup commands in docs/MAC_SETUP.md."))
        else:
            results.append((True, f"{package}: available"))
    return results


def screen_permission(system=None, library=None):
    """Return True/False on macOS when CoreGraphics exposes its preflight API."""
    if (system or platform.system()) != "Darwin":
        return None
    try:
        core_graphics = library or ctypes.CDLL(
            "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
        )
        check = core_graphics.CGPreflightScreenCaptureAccess
        check.restype = ctypes.c_bool
        return bool(check())
    except (AttributeError, OSError):
        return None


def capture_check(monitor, mss_factory=None):
    """Capture a small in-memory sample; never persist or transmit its pixels."""
    if mss_factory is None:
        from mss import MSS

        mss_factory = MSS
    try:
        with mss_factory() as capture:
            monitors = capture.monitors
            if monitor < 1 or monitor >= len(monitors):
                return False, f"Monitor {monitor} is unavailable; choose 1 through {len(monitors) - 1}."
            selected = monitors[monitor]
            if selected["width"] < 1 or selected["height"] < 1:
                return False, f"Monitor {monitor} has invalid dimensions."
            box = {
                "left": selected["left"],
                "top": selected["top"],
                "width": min(32, selected["width"]),
                "height": min(32, selected["height"]),
            }
            frame = capture.grab(box)
            if frame.width < 1 or frame.height < 1:
                return False, "Screen capture returned an empty frame. Check Screen Recording permission."
            return True, f"Monitor {monitor}: captured {frame.width}x{frame.height} pixels in memory. A successful capture does not prove game detection works."
    except Exception as exc:
        hint = (
            "Check Screen Recording permission in System Settings > Privacy & Security and restart Terminal."
            if platform.system() == "Darwin"
            else "Check that a graphical display is available."
        )
        return False, f"Screen capture failed ({type(exc).__name__}: {exc}). {hint}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monitor", type=int, default=None, help="Physical monitor number (default: config.json monitor)")
    parser.add_argument("--no-capture", action="store_true", help="Check installation without accessing the screen")
    args = parser.parse_args(argv)
    print(f"Python {platform.python_version()} | {platform.system()} | {platform.machine()}")
    if sys.version_info < (3, 10):
        print("FAIL: Python 3.10 or newer is required.")
        return 1
    if platform.system() == "Darwin" and platform.machine() != "arm64":
        print("WARNING: This Python is not native arm64. Install an Apple Silicon Python and recreate .venv.")

    results = check_dependencies()
    for _, message in results:
        print(message)
    if not all(ok for ok, _ in results):
        return 1
    try:
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        monitor = args.monitor if args.monitor is not None else int(config["monitor"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: Cannot read monitor setting in config.json ({exc}).")
        return 1
    if args.no_capture:
        print("Screen capture skipped by request; no permissions checked.")
        return 0
    permission = screen_permission()
    if permission is False:
        print("FAIL: Screen Recording permission is off. Enable it for Terminal in System Settings > Privacy & Security > Screen Recording, then restart Terminal.")
        return 1
    if permission is None:
        if platform.system() == "Darwin":
            print("Screen Recording permission could not be determined; trying an in-memory capture.")
        else:
            print("macOS Screen Recording permission check is not applicable here; trying an in-memory capture.")
    else:
        print("Screen Recording permission preflight passed.")
    ok, message = capture_check(monitor)
    print(("OK: " if ok else "FAIL: ") + message)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
