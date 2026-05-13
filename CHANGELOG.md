# Changelog

All notable changes to the Crossfire Server Windows build are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

[v1.75.0-git-a28489b]: https://github.com/tannerrj/crossfire-windows/releases/tag/v1.75.0-git-a28489b
