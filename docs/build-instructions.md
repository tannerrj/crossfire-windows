# Build Instructions

## Prerequisites

### 1. Install MSYS2
Download and install from https://www.msys2.org/
Open the **UCRT64** shell for all commands.

### 2. Install dependencies
```bash
pacman -S --needed \
    mingw-w64-ucrt-x86_64-gcc \
    mingw-w64-ucrt-x86_64-python3 \
    mingw-w64-ucrt-x86_64-sqlite3 \
    mingw-w64-ucrt-x86_64-nsis \
    autoconf automake libtool make git
```

### 3. Clone this repository
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/crossfire-windows.git
```

### 4. Run the build script
```bash
bash ~/crossfire-windows/build.sh
```

The script will:
- Clone the Crossfire server source from SourceForge
- Apply all Windows compatibility patches
- Configure and compile the server
- Build `crossfire.dll` (monolithic server DLL for plugin linkage)
- Build `cfanim.dll` and `cfpython.dll` plugins
- Generate the NSIS installer script
- Compile the installer `.exe`
- Copy the installer to your Windows Desktop

## Manual Build

If you prefer to build step by step, see the commands inside `build.sh`.
Each step is clearly commented and numbered.

## Installed Files

The installer places files in:
- `C:\Program Files\Crossfire Server\bin\` — server executable and DLLs
- `C:\Program Files\Crossfire Server\lib\crossfire\plugins\` — plugin DLLs
- `C:\Program Files\Crossfire Server\share\crossfire\` — game data
- `C:\Program Files\Crossfire Server\etc\crossfire\` — configuration
- `C:\ProgramData\Crossfire Server\` — player data (preserved on uninstall)

## Starting the Server

Run `start-server.bat` from the install directory, or use the
Start Menu shortcut. The server listens on TCP port 13327.
