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
    autoconf automake libtool make git pkgconf flex
```

### 3. Clone this repository
```bash
cd ~
git clone https://github.com/tannerrj/crossfire-windows.git
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
- Sync all freshly built binaries to the staging directory
- Generate the NSIS installer script
- Compile the installer `.exe`
- Copy the installer to your Windows Desktop

## Manual Build Steps

### Step 1 - Clone and patch Crossfire source
```bash
git clone https://git.code.sf.net/p/crossfire/crossfire-server \
    ~/crossfire/crossfire-server
cd ~/crossfire/crossfire-server
git apply ~/crossfire-windows/patches/output_file.cpp.diff
git apply ~/crossfire-windows/patches/plugins.cpp.diff
git apply ~/crossfire-windows/patches/init.cpp.diff
git apply ~/crossfire-windows/patches/loop.cpp.diff
```

### Step 2 - Configure and compile
```bash
cd ~/crossfire/crossfire-server
autoreconf -i
./configure --prefix="/usr/local/crossfire" \
    --disable-shared --enable-static --without-gd \
    CXXFLAGS="-D_GNU_SOURCE" CFLAGS="-D_GNU_SOURCE"
make -j$(nproc) -C include
make -j$(nproc) -C common
make -j$(nproc) -C random_maps
make -j$(nproc) -C server
```

### Step 3 - Build crossfire.dll
```bash
mkdir -p /tmp/server_objs && cd /tmp/server_objs
ar x ~/crossfire/crossfire-server/server/.libs/libserver.a
ar x ~/crossfire/crossfire-server/server/.libs/libserver.a libserver_la-server.o
rm -f libserver_la-win32.o

g++ -c -D_GNU_SOURCE -I~/crossfire/crossfire-server/include \
    ~/crossfire-windows/installer/win32_stub.cpp -o /tmp/win32_stub.o

cd ~/crossfire/crossfire-server
g++ -shared -D_GNU_SOURCE \
    -Wl,--whole-archive common/.libs/libcross.a random_maps/.libs/librandom_map.a \
    -Wl,--no-whole-archive /tmp/server_objs/*.o server/main.o /tmp/win32_stub.o \
    -lsqlite3 -lws2_32 -lpython3.14 \
    -Wl,--enable-auto-image-base \
    -Wl,--allow-shlib-undefined \
    -Wl,--out-implib,crossfire.dll.a -o crossfire.dll
```

> **Note:** `server/main.o` must be linked explicitly — it is not included in
> `libserver.a` and is required so `ServiceMain` can call `main()` at runtime.

### Step 4 - Build plugin DLLs
```bash
cd ~/crossfire/crossfire-server/plugins/cfanim
g++ -shared -D_GNU_SOURCE -I../../include -I./include -I../common/include \
    cfanim.cpp ../common/plugin_common.cpp \
    ~/crossfire/crossfire-server/crossfire.dll.a \
    -lsqlite3 -lws2_32 -Wl,--enable-auto-image-base \
    -Wl,--out-implib,cfanim.dll.a -o cfanim.dll

cd ~/crossfire/crossfire-server/plugins/cfpython
g++ -shared -D_GNU_SOURCE -I../../include -I./include -I../common/include \
    -IC:/msys64/ucrt64/include/python3.14 \
    cfpython.cpp cfpython_archetype.cpp cfpython_map.cpp \
    cfpython_object.cpp cfpython_party.cpp cfpython_region.cpp \
    cjson.cpp ../common/plugin_common.cpp \
    ~/crossfire/crossfire-server/crossfire.dll.a \
    -lpython3.14 -lsqlite3 -lws2_32 -Wl,--enable-auto-image-base \
    -Wl,--out-implib,cfpython.dll.a -o cfpython.dll
```

### Step 5 - Sync staging directory
```bash
cd ~/crossfire/crossfire-server
cp server/crossfire-server.exe \
    ~/crossfire-staging/usr/local/crossfire/bin/crossfire-server.exe
cp crossfire.dll \
    ~/crossfire-staging/usr/local/crossfire/bin/crossfire.dll
cp plugins/cfanim/cfanim.dll \
    ~/crossfire-staging/usr/local/crossfire/lib/crossfire/plugins/cfanim.dll
cp plugins/cfpython/cfpython.dll \
    ~/crossfire-staging/usr/local/crossfire/lib/crossfire/plugins/cfpython.dll
```

### Step 6 - Build installer
```bash
cd ~
GITVER="git-$(git -C ~/crossfire-windows log --format='%h' -1 | cut -c1-7)"
python3 ~/crossfire-windows/installer/write_nsi.py "$GITVER" \
    "$(cygpath -m ~/crossfire-installer.nsi)"
makensis crossfire-installer.nsi
cp ~/CrossfireServer-${GITVER}-Setup.exe /c/Users/$USERNAME/Desktop/
```

> **Note:** The version string is derived from the `crossfire-windows` repo
> commit hash (not the upstream server), so it reflects packaging changes.

## Windows Service

The installer offers an optional **Windows Service** component on the
Components page. When selected, the installer registers `CrossfireServer`
with the Windows Service Control Manager so the server starts at boot and
runs in the background without a logged-in user.

### Manual service management
```bat
REM Register the service (run as Administrator)
crossfire-server.exe -regsrv

REM Unregister the service
crossfire-server.exe -unregsrv

REM Start / stop via sc
sc start CrossfireServer
sc stop CrossfireServer
```

Or use `services.msc` to manage the service interactively.

### How it works
`ServiceMain` in `installer/win32_stub.cpp` reads the install path from
`HKLM\Software\Crossfire Server\InstallDir` (written by NSIS at install
time), sets `PYTHONHOME`, `PYTHONPATH`, and `SetDllDirectoryA`, then calls
`main()` with `-data`, `-conf`, `-local`, and `-p 13327`.

## Installed Files

| Path | Contents |
|---|---|
| `C:\Program Files\Crossfire Server\bin\` | Server executable, crossfire.dll, runtime DLLs |
| `C:\Program Files\Crossfire Server\lib\crossfire\plugins\` | cfanim.dll, cfpython.dll |
| `C:\Program Files\Crossfire Server\lib\python3.14\` | Bundled Python stdlib |
| `C:\Program Files\Crossfire Server\share\crossfire\` | Maps, archetypes, game data |
| `C:\Program Files\Crossfire Server\etc\crossfire\` | Server configuration |
| `C:\ProgramData\Crossfire Server\` | Player data (preserved on uninstall) |

## Starting the Server

Launch from **Start Menu -> All Apps -> Crossfire Server -> Start Server**,
or run `start-server.bat` from the install directory.
The server listens on TCP port **13327**.

## Post-Install Verification Checklist

After every installer rebuild and fresh installation, always verify:

1. **Start Menu entry exists** - Check All Apps -> C -> Crossfire Server.
   Note: Start Menu search may not index the app on some Windows 11 installs
   (see Known Issues below).

2. **Start Menu shortcuts work** - Click Start Server and confirm:
   - `plugins: loading cfanim.dll`
   - `plugins: loading cfpython.dll`
   - `CFPython: Initializing CFBank`
   - `CFPython: Initializing CFMail`
   - `CFPython: Initializing CFShop`
   - `Waiting for connections`

3. **Plugin DLLs are current** - Timestamps on these should match build date:
   - `C:\Program Files\Crossfire Server\lib\crossfire\plugins\cfanim.dll`
   - `C:\Program Files\Crossfire Server\lib\crossfire\plugins\cfpython.dll`

4. **crossfire.dll is current** - Timestamp on
   `C:\Program Files\Crossfire Server\bin\crossfire.dll` should match build date.

5. **Player login works** - Connect a client, create a character, log out,
   reconnect and log back in with the same character.

## Known Issues

### Start Menu Search
Crossfire Server may not appear in Windows Start Menu search results due to
a known Windows 10/11 indexing bug. This is not an installer defect.

Workaround: use **Start Menu -> All Apps -> scroll to "C" -> Crossfire Server**.

The application is correctly registered in the Windows registry and appears
correctly in All Apps and Add/Remove Programs.

### Unsigned Installer
The installer is not code-signed. Windows SmartScreen will show a warning.
Click **More info -> Run anyway** to proceed.
