[![Build](https://github.com/tannerrj/crossfire-windows/actions/workflows/build.yml/badge.svg)](https://github.com/tannerrj/crossfire-windows/actions/workflows/build.yml)

# Crossfire Server — Windows Build

This repository contains the patches, installer script, and build tooling
to compile and package the [Crossfire RPG server](https://sourceforge.net/projects/crossfire/)
for Windows 10/11 (64-bit) using MSYS2 UCRT64.

## Current Build

| Item | Value |
|---|---|
| Upstream base | `2f3c503af` (v1.75.0-1756) |
| Installer | `CrossfireServer-git-2f3c503-Setup.exe` |
| Tested on | Windows 10, Windows 11 (clean install, no MSYS2) |
| Python stdlib | Bundled (no MSYS2 required on target machine) |

## What This Repo Contains

- `patches/` — Git diff patches for Windows compatibility fixes
- `installer/` — NSIS installer generator script and Win32 stub
- `docs/` — Build instructions and license notes
- `build.sh` — Automated build script
- `CHANGELOG.md` — Build history and upstream changes

## Quick Start

1. Install [MSYS2](https://www.msys2.org/) and open the UCRT64 shell
2. Install dependencies (see `docs/build-instructions.md`)
3. Clone this repo into your MSYS2 home directory
4. Run `bash build.sh`
5. The installer `.exe` will appear on your Windows Desktop

## Requirements

- Windows 10/11 64-bit (build machine)
- MSYS2 UCRT64
- NSIS (Nullsoft Scriptable Install System)
- Python 3.14 (via MSYS2)
- Git

## What the Patches Fix

| Patch | Description |
|---|---|
| `output_file.cpp.diff` | Atomic file rename using `DeleteFileA` + `MoveFileExA` |
| `plugins.cpp.diff` | Replaces POSIX dir scan with Win32 `FindFirstFileA` |
| `init.cpp.diff` | WSAStartup error checking + `WSAGetLastError` reporting |
| `loop.cpp.diff` | Enhanced Winsock `select()` error handling with specific error codes |

These patches are maintained in this repository as the upstream Crossfire
project does not currently accept Windows-specific patches.

## Game Data

The installer bundles the complete Crossfire game data set:
- Full map set (~796MB, 35 top-level map regions)
- Archetypes (`crossfire.arc`, `crossfire.tar`)
- Python scripts for CFBank, CFMail, CFShop, Guilds
- All help files, i18n data, and configuration

Map content is updated to match upstream `2f3c503af`.

## Python Standard Library

The installer bundles a minimal Python 3.14 standard library so the
server runs on clean Windows installs without MSYS2:
- 154 stdlib `.py` files
- 71 C extension `.pyd` files
- Packages: `encodings`, `importlib`, `collections`, `sqlite3`, `dbm`

## Installing

1. Download the latest installer from the [Releases](https://github.com/tannerrj/crossfire-windows/releases) page
2. Right-click the `.exe` and select **Run as Administrator**
3. Follow the on-screen prompts
4. Launch from **Start Menu → All Apps → Crossfire Server → Start Server**

> **Note:** Windows SmartScreen may show a warning since the installer is
> unsigned. Click **More info → Run anyway** to proceed.

## Connecting

Use any Crossfire-compatible client pointed at your server's IP on port **13327**.
The recommended client is the [GTK client](https://crossfire.real-time.com/clients/).

## Known Issues

- **Start Menu search** — The server may not appear in Start Menu search on
  some Windows 11 installs. Use All Apps → C → Crossfire Server instead.
- **Unsigned installer** — SmartScreen will warn about the unsigned installer.
  Click More info → Run anyway.

## License

The patches in this repository apply to the Crossfire server source code,
which is licensed under [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
All changes in this repository are likewise released under GPLv2.
See `docs/gpl-compatibility.md` for a full compatibility analysis.

## Maintainer

Rick Tanner <leaf@real-time.com>
GitHub: https://github.com/tannerrj/crossfire-windows
