# Crossfire Server — Windows Build

This repository contains the patches, installer script, and build tooling
to compile and package the [Crossfire RPG server](https://sourceforge.net/projects/crossfire/)
for Windows 10/11 (64-bit) using MSYS2 UCRT64.

## What This Repo Contains

- `patches/` — Git diff patches for Windows compatibility fixes
- `installer/` — NSIS installer generator script and Win32 stub
- `docs/` — Build instructions and license notes
- `build.sh` — Automated build script

## Quick Start

1. Install [MSYS2](https://www.msys2.org/) and open the UCRT64 shell
2. Install dependencies (see `docs/build-instructions.md`)
3. Clone this repo into your MSYS2 home directory
4. Run `bash build.sh`
5. The installer `.exe` will appear on your Desktop

## Requirements

- Windows 10/11 64-bit
- MSYS2 UCRT64
- NSIS (Nullsoft Scriptable Install System)
- Python 3.14 (via MSYS2)
- Git

## What the Patches Fix

| Patch | Description |
|---|---|
| `output_file.cpp.diff` | Fixes atomic file rename using `MoveFileExA()` |
| `plugins.cpp.diff` | Replaces POSIX dir scan with Win32 `FindFirstFileA()` |
| `init.cpp.diff` | Fixes Winsock socket initialization and error reporting |
| `loop.cpp.diff` | Fixes `select()` error handling for Winsock |

## License

The patches in this repository apply to the Crossfire server source code,
which is licensed under [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
All changes in this repository are likewise released under GPLv2.
See `docs/gpl-compatibility.md` for a full compatibility analysis.
