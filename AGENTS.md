# AGENTS.md — Crossfire Server Windows Build Project

## Project Overview

This repository contains Windows compatibility patches, build tooling, and
an NSIS installer generator for the Crossfire RPG server. The Crossfire
server source lives on SourceForge; this repo contains only the
Windows-specific patches and build infrastructure.

## Repository Structure

```text
crossfire-windows/
├── AGENTS.md                   ← This file
├── README.md                   ← Project overview and quick start
├── build.sh                    ← Automated build script (MSYS2 UCRT64)
├── patches/                    ← Git diff patches for Windows compatibility
│   ├── object.cpp.diff         ← Adds ffs() for MinGW
│   ├── output_file.cpp.diff    ← Fixes atomic rename with MoveFileExA()
│   ├── cfpython.cpp.diff       ← Adds CF_PLUGIN export to initPlugin()
│   ├── plugins.cpp.diff        ← Win32 directory scan + absolute paths
│   ├── win32.cpp.diff          ← Fixes bRunning uninitialized variable
│   ├── init.cpp.diff           ← Fixes Winsock initialization/error reporting
│   └── loop.cpp.diff           ← Fixes select() error handling for Winsock
├── installer/
│   ├── write_nsi.py            ← Generates crossfire-installer.nsi
│   └── win32_stub.cpp          ← Stub for bRunning, service_register/unregister/handle
└── docs/
    ├── build-instructions.md   ← Step-by-step build guide
    └── gpl-compatibility.md    ← GPLv2 license compatibility analysis
```

## Build Environment

- **OS**: Windows 10/11 64-bit
- **Shell**: MSYS2 UCRT64
- **Compiler**: GCC (mingw-w64-ucrt-x86_64-gcc)
- **Python**: 3.14 (mingw-w64-ucrt-x86_64-python3)
- **Installer**: NSIS (makensis)
- **Source**: Crossfire server v1.75.0 from SourceForge

## Key Paths (MSYS2)

| Purpose | Path |
|---|---|
| This repo | \`/home/leaf/crossfire-windows/\` |
| Crossfire source | \`/home/leaf/crossfire/crossfire-server/\` |
| Build staging | \`/home/leaf/crossfire-staging/\` |
| MSYS2 UCRT64 root | \`C:\msys64\ucrt64\\\` |
| Install target | \`C:\Program Files\Crossfire Server\\\` |
| Player data | \`C:\ProgramData\Crossfire Server\\\` |

## Key Build Artifacts

| File | Location | Purpose |
|---|---|---|
| \`crossfire-server.exe\` | \`server/\` | Main server executable |
| \`crossfire.dll\` | \`crossfire-server/\` | Monolithic server DLL for plugin linkage |
| \`crossfire.dll.a\` | \`crossfire-server/\` | Import library for building plugins |
| \`cfanim.dll\` | \`plugins/cfanim/\` | Animation plugin |
| \`cfpython.dll\` | \`plugins/cfpython/\` | Python scripting plugin |
| \`CrossfireServer-*.exe\` | \`/home/leaf/\` | NSIS installer |

## Architecture Notes

### Why crossfire.dll exists
Windows DLLs cannot resolve symbols from an \`.exe\` file at load time.
On Linux, plugins load against the server binary via \`RTLD_GLOBAL\`. On
Windows this is impossible, so all server code is compiled into a
monolithic \`crossfire.dll\` that both \`crossfire-server.exe\` and the
plugin DLLs link against.

### crossfire.dll build process
1. Extract all objects from \`server/.libs/libserver.a\` excluding
   \`libserver_la-win32.o\` and \`libserver_la-server.o\`
2. Compile \`installer/win32_stub.cpp\` to provide \`bRunning\`,
   \`service_register()\`, \`service_unregister()\`, \`service_handle()\`
3. Link with \`--whole-archive\` against \`libcross.a\` and \`librandom_map.a\`
4. Link remaining server objects and the stub
5. Output: \`crossfire.dll\` + \`crossfire.dll.a\` (import library)

### Plugin loading
Plugins are loaded from an absolute path derived from
\`GetModuleFileNameA()\` — stripping the executable name and \`\bin\\\`
to get the install root, then appending \`\lib\crossfire\plugins\*.dll\`.
\`SetDllDirectoryA()\` points to \`bin\\\` so runtime DLLs are found.

### Python stdlib
\`PYTHONHOME\` and \`PYTHONPATH\` must point to the MSYS2 Python installation.
Currently set in \`start-server.bat\` at runtime. For a fully portable
installer these would need to be bundled.

## Patch Application Order

Apply patches in this order to avoid conflicts:

1. \`object.cpp.diff\`
2. \`win32.cpp.diff\`
3. \`init.cpp.diff\`
4. \`loop.cpp.diff\`
5. \`output_file.cpp.diff\`
6. \`plugins.cpp.diff\`
7. \`cfpython.cpp.diff\`

## Runtime Dependencies (bundled in installer)

| DLL | Source | Purpose |
|---|---|---|
| \`crossfire.dll\` | Built from source | Monolithic server DLL |
| \`libgcc_s_seh-1.dll\` | MSYS2 UCRT64 | GCC runtime |
| \`libstdc++-6.dll\` | MSYS2 UCRT64 | C++ runtime |
| \`libwinpthread-1.dll\` | MSYS2 UCRT64 | POSIX threads |
| \`libpython3.14.dll\` | MSYS2 UCRT64 | Python runtime |
| \`libsqlite3-0.dll\` | MSYS2 UCRT64 | SQLite (for CFBank/CFMail) |
| \`api-ms-win-crt-*.dll\` | Windows downlevel | Universal CRT forwarders |

## License

All patches and build tooling in this repository are released under
GPLv2, matching the Crossfire server license. See \`docs/gpl-compatibility.md\`
for a full analysis. The Crossfire server source is copyright the
Crossfire Development Team.

## Maintainer

Rick Tanner <leaf@real-time.com>
GitHub: https://github.com/tannerrj/crossfire-windows
