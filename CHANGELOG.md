# Changelog

All notable changes to the Crossfire Server Windows build are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **Windows Service support** — optional NSIS component installs and starts
  the server as a Windows service (`CrossfireServer`)
  - Service auto-starts at boot; survives user logout
  - Install path read from `HKLM\Software\Crossfire Server\InstallDir`
    (written by NSIS at install time); falls back to exe location
  - `PYTHONHOME`, `PYTHONPATH`, and `SetDllDirectoryA` configured from
    install path so cfpython.dll finds the bundled stdlib without MSYS2
  - `-regsrv` / `-unregsrv` / `-srv` flags added to `crossfire-server.exe`
    via `win32_stub.cpp`; installer registers/unregisters service automatically

### Changed
- **Installer version now derived from this repo** — `GITVER` is taken from
  the `crossfire-windows` git commit hash instead of the upstream server
  source. Installer filenames now track packaging changes (e.g.
  `CrossfireServer-git-4765bbb-Setup.exe`).
- `build.sh` rewritten end-to-end with full automation:
  - Step 0 `pacman -S --needed` ensures all build deps including `pkgconf`
    and `flex` are present
  - Clone steps for `crossfire-arch` and `crossfire-maps` with stale-dir
    detection; symlinks into source tree for `make install`
  - `autoreconf -i` replaces `./autogen.sh`
  - `--without-gd --disable-shared --enable-static` passed to `./configure`
  - Targeted `make -C include/common/random_maps/server` instead of full
    `make` to avoid failing in `lib/` before arch/maps are present
  - `server/main.o` explicitly linked into `crossfire.dll` (not in
    `libserver.a`) to resolve `main()` for `ServiceMain`
  - Python stdlib bundled from `/c/msys64/ucrt64/lib/python3.14`
- CI/CD updated to Node.js 24 native actions:
  - `actions/checkout@v4` → `@v5`
  - `actions/upload-artifact@v4` → `@v7`
  - Removed `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` workarounds
- CI installer job: all staging paths use `$GITHUB_WORKSPACE` (not `~`)
- CI Python lib path: `/ucrt64/lib/python3.14` (not `/c/msys64/ucrt64/...`)

### Fixed
- `libserver_la-win32.o` correctly excluded from `crossfire.dll` (contained
  the old empty stubs that conflicted with the full service implementation)
- `ServiceMain` signature corrected to `LPWSTR *argv` to match
  `SERVICE_TABLE_ENTRYW`
- NSIS `SectionDescription` removed from inside section bodies (invalid NSIS)
- `ln -s lib/arch lib/maps` now preceded by `rm -rf` to avoid
  "cannot overwrite non-directory" error on rebuild

---

## [v1.75.0-git-2f3c503-win2] - 2026-05-29

### Fixed
- **accounts.tmp Access Denied permanently fixed** — root cause was
  `start-server.bat` creating an `accounts` directory via `mkdir`, but
  the server expects `accounts` to be a plain file. `MoveFileExA` cannot
  replace a directory with a file, causing "Access is denied" on every
  first connect on a clean install.
  - Fix 1: Removed `mkdir accounts` from `start-server.bat`
  - Fix 2: Replaced `MoveFileExA` with `CopyFileA + DeleteFileA` in
    `output_file.cpp` to avoid inherited ACL issues in ProgramData

### Added
- **GitHub Actions CI** — automated build on every push to `main`
  - `compile` job: builds server + all DLLs using GitHub mirrors (~7 min)
  - `installer` job: full build with maps/arch, produces `.exe` installer,
    attaches to GitHub Release automatically on version tags
  - Uses `windows-2025` runner, Node.js 24
  - Sources: `crossfire-server-mirror`, `crossfire-arch-mirror`,
    `crossfire-maps-mirror`
- CI build status badge added to README

### Changed
- `output_file.cpp.diff`: replaced `MoveFileExA` retry loop with
  `CopyFileA + DeleteFileA` for more reliable file writes on Windows
- `write_nsi.py`: removed erroneous `mkdir accounts` from `start-server.bat`
- `write_nsi.py`: fixed duplicate `takeown` call
- `write_nsi.py`: moved `icacls` to run after all directories are created
- README, build-instructions.md, AGENTS.md updated for upstream base
  `2f3c503af`

### Patches Applied
| Patch | Description |
|---|---|
| `output_file.cpp.diff` | Atomic write via `CopyFileA + DeleteFileA` |
| `plugins.cpp.diff` | Win32 directory scan + absolute plugin paths |
| `init.cpp.diff` | WSAStartup error checking + WSAGetLastError |
| `loop.cpp.diff` | Enhanced Winsock `select()` error handling |

---

## [v1.75.0-git-2f3c503] - 2026-05-27

### Upstream Base
- Crossfire server commit `2f3c503af` (v1.75.0-1756)
- Upstream changes since previous base (`a28489bc1`):
  - `7411d10e4` Add code to handle Winsock quirks on WIN32
  - `0312bf5a3` Install lib/def_help with CMake
  - `705534ece` Add media tag for command help
  - `9e860b44f` Use caster level when curing disease
  - `ef30350ab` Improve cure disease result messages
  - `088e59465` Add GDB pretty-printing script
  - `1254bce3a` Make object_matches_string match tags
  - `adc2015e3` Fix compiler warning
  - `a067aa0b0` Fix deprecation warnings by updating to curl_mime
  - `bc4accaef` Fix non-deterministic map ordering in JSON output
  - `a1494e4a3` Fix C++14 compatibility
  - `2f3c503af` Skip new lines in accounts file

### Changed
- Updated all four patches to apply cleanly against new upstream base
- `loop.cpp.diff` enhanced: upstream added empty fd_set check and basic
  Winsock error logging; our patch now adds specific handling for error
  codes 10004 (WSAEINTR), 10038 (WSAENOTSOCK), 10022 (WSAEINVAL)
- Fixed SyntaxWarning for invalid escape sequence in write_nsi.py

### Patches Applied
| Patch | Description |
|---|---|
| `output_file.cpp.diff` | Atomic rename via `DeleteFileA` + `MoveFileExA` |
| `plugins.cpp.diff` | Win32 directory scan + absolute plugin paths |
| `init.cpp.diff` | WSAStartup error checking + WSAGetLastError |
| `loop.cpp.diff` | Enhanced Winsock `select()` error handling |

---

## [v1.75.0-git-a28489b] - 2026-05-12

### First portable Windows release

**Upstream base:** Crossfire server commit `a28489bc1` (v1.75.0-1744)
**Installer:** `CrossfireServer-git-a28489b-Setup.exe`

### Added
- Fully self-contained installer — no MSYS2 required on target machine
- Bundled Python 3.14 standard library (154 .py modules + 71 extensions)
- Bundled Python packages: encodings, importlib, collections, sqlite3, dbm
- `crossfire.dll` — monolithic server DLL enabling plugin linkage on Windows
- `cfanim.dll` — animation plugin
- `cfpython.dll` — Python scripting plugin
- CFBank, CFMail, CFShop Python scripts fully operational
- All 14 guilds initialize correctly
- Windows Firewall rule added automatically on install (TCP port 13327)
- Start Menu entry under All Apps → Crossfire Server
- Uninstaller via Start Menu and Add/Remove Programs
- App Paths and DisplayIcon registry entries for Windows integration
- ProgramData directory permissions set at install time

### Fixed
- `ffs()` missing on MinGW — now handled upstream (commit `44c1e7f5a`)
- `CF_PLUGIN` missing from `initPlugin()` — now handled upstream (`a28489bc1`)
- `bRunning` uninitialized — now handled upstream (`7377b10f8`)
- `u_long` type for `ioctlsocket()` — now handled upstream
- `select()` error handling uses `WSAGetLastError()` instead of `errno`
- `WSAStartup()` now checks return value and exits on failure
- Plugin directory scan uses Win32 `FindFirstFileA()`/`FindNextFileA()`
- Plugin paths built from absolute executable location via `GetModuleFileNameA()`
- Atomic file rename uses `MoveFileExA()` + `DeleteFileA()` instead of `rename()`

### Known Issues
- Start Menu search may not find the server on some Windows installations
  (Windows indexing bug — server appears correctly under All Apps)
- `accounts.tmp` Access Denied error appears once on first client connect
  (cosmetic — does not affect gameplay or account saving)
- Python stdlib points to bundled location — not upgradeable without reinstall

### Patches Applied
| Patch | Description |
|---|---|
| `output_file.cpp.diff` | Atomic rename via `DeleteFileA()` + `MoveFileExA()` |
| `plugins.cpp.diff` | Win32 directory scan + absolute plugin paths |
| `init.cpp.diff` | WSAStartup error checking + WSAGetLastError reporting |
| `loop.cpp.diff` | Winsock `select()` error handling |

### Upstream Patches Accepted
The following patches from this project were accepted upstream:
| Patch | Upstream Commit |
|---|---|
| `ffs()` fix for MinGW | `44c1e7f5a` |
| `CF_PLUGIN` on `initPlugin()` | `a28489bc1` |
| `bRunning = 1` initialization | `7377b10f8` |
| `u_long` type for `ioctlsocket()` | upstream |

### Tested On
- Windows 10 (clean install, no MSYS2)
- Windows 11 (build machine with MSYS2)

---

## [v1.75.0-git-fe1fdb5] - 2026-05-08

### First Windows build (development/testing only)

**Upstream base:** Crossfire server commit `fe1fdb5c4` (v1.75.0-1735)
**Installer:** `CrossfireServer-git-fe1fdb5-Setup.exe`

### Added
- Initial Windows build using MSYS2 UCRT64
- `crossfire.dll` monolithic server DLL
- `cfanim.dll` and `cfpython.dll` plugins
- NSIS installer with Start Menu shortcuts and firewall rule

### Known Issues (resolved in next release)
- Required MSYS2 installed on target machine for Python stdlib
- `accounts.tmp` rename errors on fresh installs
- Start Menu search indexing unreliable

---

[Unreleased]: https://github.com/tannerrj/crossfire-windows/compare/v1.75.0-git-2f3c503-win2...HEAD
[v1.75.0-git-2f3c503-win2]: https://github.com/tannerrj/crossfire-windows/releases/tag/v1.75.0-git-2f3c503-win2
[v1.75.0-git-2f3c503]: https://github.com/tannerrj/crossfire-windows/releases/tag/v1.75.0-git-2f3c503
[v1.75.0-git-a28489b]: https://github.com/tannerrj/crossfire-windows/releases/tag/v1.75.0-git-a28489b
[v1.75.0-git-fe1fdb5]: https://github.com/tannerrj/crossfire-windows/releases/tag/v1.75.0-git-fe1fdb5
