# Apple Silicon Mac setup (Phase 1)

This guide prepares a **read-only diagnostic**. It checks your Python installation and whether a small portion of your screen can be captured. It does not move the mouse, press keys, communicate with Roblox, save a screenshot, or contact Hugging Face. The existing `run.command` still launches the original automation program; do not use it for this diagnostic.

These steps are intended for an Apple M4 Mac. They have not yet been executed on macOS; the Mac checks below are for you to perform locally. Python 3.10 or newer is required. Python 3.12 is a reasonable initial choice, subject to the Mac installation test.

## Install

1. Install a native Apple Silicon Python 3.12 from [python.org](https://www.python.org/downloads/macos/) or a trusted package manager. Open a fresh Terminal window.
2. In Terminal, change into the project directory and check the interpreter:

   ```sh
   cd /path/to/fischingmacro
   python3 --version
   python3 -c 'import platform; print(platform.machine())'
   ```

   On an M4, the second command should print `arm64`. If it prints `x86_64`, Terminal or Python may be running through Rosetta. Install/select an arm64 interpreter before creating the virtual environment.

3. Create an isolated environment and install only the read-only diagnostic dependencies:

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements-diagnostic.txt
   .venv/bin/python -m pip check
   ```

   Repeating the `pip install` command is safe. If `.venv` was made with an Intel Python, create a new virtual environment with the arm64 Python; existing Intel wheels do not become arm64 automatically. Keep the original environment until you are sure it contains nothing you need.

## Run the diagnostic

First check dependencies without requesting screen access:

```sh
.venv/bin/python src/diagnose.py --no-capture
```

Then check a small in-memory screen capture:

```sh
.venv/bin/python src/diagnose.py
```

The default monitor number comes from `config.json` (usually `1`). To select another physical monitor, run `.venv/bin/python src/diagnose.py --monitor 2`. If the program reports an unavailable monitor, use a number in the range it prints.

macOS may ask for **Screen Recording** permission for Terminal. If capture fails, open **System Settings > Privacy & Security > Screen Recording**, allow your Terminal app, then quit and reopen Terminal before retrying. The diagnostic does not require Accessibility permission because it sends no input. A successful 32-by-32 pixel capture confirms only basic access; it does not prove that game elements are recognized or that a packaged app has permission. A black sample may simply reflect black content at the sampled corner.

## Tests and troubleshooting

Run the automated tests without screen access:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

If dependencies are missing, confirm you invoked `.venv/bin/python`, then repeat installation. If `arm64` is not shown, check which `python3` you selected and whether Terminal runs under Rosetta. If Screen Recording is allowed but capture still fails, restart Terminal and rerun the diagnostic; record the displayed error, macOS version, Python version, and whether an external display is connected. Do not share screenshots or tokens while troubleshooting.

The original automation launcher and PyInstaller build are outside this Phase 1 diagnostic verification. They require separate Mac testing and, for input, Accessibility permission. Do not infer their behavior from these tests.
