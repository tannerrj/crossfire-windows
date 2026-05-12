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

## Post-Install Verification Checklist

After every installer rebuild and fresh installation, always verify the following:

1. **Start Menu entry exists** — Click Start and type `Crossfire`. The server
   should appear in search results. Also check:
   Start Menu → All Apps → Crossfire Server → Start Server and Uninstall

2. **Start Menu shortcuts work** — Click `Start Server` from the Start Menu
   and confirm the server window opens and shows:
   - `plugins: loading cfanim.dll`
   - `plugins: loading cfpython.dll`
   - `CFPython: Initializing CFBank`
   - `CFPython: Initializing CFMail`
   - `CFPython: Initializing CFShop`
   - `Waiting for connections`

3. **Plugin DLLs are current** — Check the timestamp on:
   `C:\Program Files\Crossfire Server\lib\crossfire\plugins\cfanim.dll`
   `C:\Program Files\Crossfire Server\lib\crossfire\plugins\cfpython.dll`
   They should match the build date.

4. **crossfire.dll is current** — Check the timestamp on:
   `C:\Program Files\Crossfire Server\bin\crossfire.dll`
   It should match the build date.

5. **Player login works** — Connect a client, create a character, log out,
   reconnect and log back in with the same character.

If the Start Menu entry is missing after installation:
- Check `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Crossfire Server\`
- If shortcuts exist there but don't appear in search, the shortcuts were also
  created in the current user Start Menu folder as a fallback.
- Check `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Crossfire Server\`
- If neither location has shortcuts, rebuild the installer and reinstall.
