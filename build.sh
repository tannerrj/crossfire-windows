#!/bin/bash
# Crossfire Server Windows Build Script
# Requires: MSYS2 UCRT64, git, makensis, python3
# Run from MSYS2 UCRT64 shell

set -e

SRCDIR="$HOME/crossfire/crossfire-server"
ARCHDIR="$HOME/crossfire/crossfire-arch"
MAPSDIR="$HOME/crossfire/crossfire-maps"
STAGINGDIR="$HOME/crossfire-staging/usr/local/crossfire"
PATCHDIR="$(dirname "$0")/patches"
INSTALLERDIR="$(dirname "$0")/installer"
BUILDDIR="$HOME"

echo "=== Crossfire Windows Build Script ==="
echo ""

# Step 0: Ensure required packages are installed
echo "[0/9] Checking dependencies..."
pacman -S --needed --noconfirm \
    mingw-w64-ucrt-x86_64-gcc \
    mingw-w64-ucrt-x86_64-python3 \
    mingw-w64-ucrt-x86_64-sqlite3 \
    mingw-w64-ucrt-x86_64-nsis \
    autoconf automake libtool make git pkgconf flex

# Step 1: Clone source if not present or empty
if [ ! -f "$SRCDIR/configure.ac" ]; then
    echo "[1/9] Cloning Crossfire server source..."
    mkdir -p "$HOME/crossfire"
    git clone https://git.code.sf.net/p/crossfire/crossfire-server \
        "$SRCDIR"
else
    echo "[1/9] Source already present at $SRCDIR, skipping clone."
fi

# Step 1b: Clone arch and maps if not present (needed for make install / installer)
if [ ! -f "$ARCHDIR/crossfire.arc" ]; then
    echo "[1b/9] Cloning Crossfire archetypes (~20MB)..."
    rm -rf "$ARCHDIR"
    mkdir -p "$HOME/crossfire"
    git clone https://git.code.sf.net/p/crossfire/crossfire-arch "$ARCHDIR"
else
    echo "[1b/9] Archetypes already present, skipping clone."
fi

if [ ! -d "$MAPSDIR/scorn" ]; then
    echo "[1c/9] Cloning Crossfire maps (~800MB, this will take a while)..."
    rm -rf "$MAPSDIR"
    mkdir -p "$HOME/crossfire"
    git clone https://git.code.sf.net/p/crossfire/crossfire-maps "$MAPSDIR"
else
    echo "[1c/9] Maps already present, skipping clone."
fi

# Symlink arch and maps into the source tree so make install works
rm -rf "$SRCDIR/lib/arch" "$SRCDIR/lib/maps"
ln -s "$ARCHDIR" "$SRCDIR/lib/arch"
ln -s "$MAPSDIR" "$SRCDIR/lib/maps"

# Step 2: Apply patches
echo "[2/9] Applying patches..."
cd "$SRCDIR"
for patch in "$PATCHDIR"/*.diff; do
    name=$(basename "$patch")
    echo "  Applying $name..."
    git apply --check "$patch" 2>/dev/null && git apply "$patch" \
        || echo "  WARNING: $name already applied or failed, skipping."
done

# Step 3: Configure
echo "[3/9] Running configure..."
autoreconf -i
./configure --prefix="/usr/local/crossfire" \
    --disable-shared --enable-static \
    --without-gd \
    CXXFLAGS="-D_GNU_SOURCE" CFLAGS="-D_GNU_SOURCE"

# Step 4: Build server
echo "[4/9] Building server..."
make -j$(nproc) -C include
make -j$(nproc) -C common
make -j$(nproc) -C random_maps
make -j$(nproc) -C server

# Step 5: Build crossfire.dll
echo "[5/9] Building crossfire.dll..."
rm -rf /tmp/server_objs && mkdir -p /tmp/server_objs
cd /tmp/server_objs
ar x "$SRCDIR/server/.libs/libserver.a"
rm -f libserver_la-win32.o
cd "$SRCDIR"

g++ -c -D_GNU_SOURCE -I./include \
    "$INSTALLERDIR/win32_stub.cpp" -o /tmp/win32_stub.o

g++ -shared \
    -D_GNU_SOURCE \
    -Wl,--whole-archive \
    common/.libs/libcross.a \
    random_maps/.libs/librandom_map.a \
    -Wl,--no-whole-archive \
    /tmp/server_objs/*.o \
    server/main.o \
    /tmp/win32_stub.o \
    -lsqlite3 -lws2_32 -lpython3.14 \
    -Wl,--enable-auto-image-base \
    -Wl,--allow-shlib-undefined \
    -Wl,--out-implib,crossfire.dll.a \
    -o crossfire.dll

echo "  crossfire.dll built: $(ls -lh crossfire.dll | awk '{print $5}')"

# Step 6: Build plugin DLLs
echo "[6/9] Building plugin DLLs..."
cd "$SRCDIR/plugins/cfanim"
g++ -shared \
    -D_GNU_SOURCE \
    -I../../include -I./include -I../common/include \
    cfanim.cpp ../common/plugin_common.cpp \
    "$SRCDIR/crossfire.dll.a" \
    -lsqlite3 -lws2_32 \
    -Wl,--enable-auto-image-base \
    -Wl,--out-implib,cfanim.dll.a \
    -o cfanim.dll
echo "  cfanim.dll built."

cd "$SRCDIR/plugins/cfpython"
g++ -shared \
    -D_GNU_SOURCE \
    -I../../include -I./include -I../common/include \
    -IC:/msys64/ucrt64/include/python3.14 \
    cfpython.cpp cfpython_archetype.cpp cfpython_map.cpp \
    cfpython_object.cpp cfpython_party.cpp cfpython_region.cpp \
    cjson.cpp ../common/plugin_common.cpp \
    "$SRCDIR/crossfire.dll.a" \
    -lpython3.14 -lsqlite3 -lws2_32 \
    -Wl,--enable-auto-image-base \
    -Wl,--out-implib,cfpython.dll.a \
    -o cfpython.dll
echo "  cfpython.dll built."

# Step 7: Install server to staging directory, then sync freshly built binaries
echo "[7/9] Syncing staging directory..."
cd "$SRCDIR"
make install DESTDIR="$HOME/crossfire-staging"
cp -v "$SRCDIR/server/crossfire-server.exe" \
    "$STAGINGDIR/bin/crossfire-server.exe"
cp -v "$SRCDIR/crossfire.dll" \
    "$STAGINGDIR/bin/crossfire.dll" 2>/dev/null || true
cp -v "$SRCDIR/plugins/cfanim/cfanim.dll" \
    "$STAGINGDIR/lib/crossfire/plugins/cfanim.dll" 2>/dev/null || true
cp -v "$SRCDIR/plugins/cfpython/cfpython.dll" \
    "$STAGINGDIR/lib/crossfire/plugins/cfpython.dll" 2>/dev/null || true
echo "  Staging directory synced."

# Step 7b: Copy maps and arch into staging
echo "[7b/9] Copying maps and arch to staging..."
mkdir -p "$STAGINGDIR/share/crossfire/maps"
cp -r "$MAPSDIR/." "$STAGINGDIR/share/crossfire/maps/"
cp -r "$ARCHDIR/." "$STAGINGDIR/share/crossfire/"
echo "  Maps and arch copied."

# Step 7d: Bundle Python standard library into staging
echo "[7b/9] Bundling Python stdlib..."
PYLIB=/c/msys64/ucrt64/lib/python3.14
PYSTAGING="$STAGINGDIR/lib/python3.14"
mkdir -p "$PYSTAGING/encodings" "$PYSTAGING/importlib" \
    "$PYSTAGING/collections" "$PYSTAGING/sqlite3" \
    "$PYSTAGING/dbm" "$PYSTAGING/lib-dynload"
cp "$PYLIB/"*.py "$PYSTAGING/"
cp -r "$PYLIB/encodings/." "$PYSTAGING/encodings/"
cp -r "$PYLIB/importlib/." "$PYSTAGING/importlib/"
cp -r "$PYLIB/collections/." "$PYSTAGING/collections/"
cp -r "$PYLIB/sqlite3/." "$PYSTAGING/sqlite3/"
cp -r "$PYLIB/dbm/." "$PYSTAGING/dbm/"
cp "$PYLIB/lib-dynload/"*.pyd "$PYSTAGING/lib-dynload/"
echo "  Python stdlib bundled."

# Step 8: Generate NSIS installer script
echo "[8/9] Generating NSIS installer script..."
cd "$BUILDDIR"
GITVER="git-$(git -C "$(dirname "$0")" log --format='%h' -1 | cut -c1-7)"
echo "  Version: $GITVER"
python3 "$INSTALLERDIR/write_nsi.py" "$GITVER" \
    "$(cygpath -m "$BUILDDIR/crossfire-installer.nsi")"

# Step 9: Build installer
echo "[9/9] Building installer..."
makensis crossfire-installer.nsi
DESKTOP="$(cygpath "$USERPROFILE")/Desktop"
cp "CrossfireServer-${GITVER}-Setup.exe" "$DESKTOP/"
echo ""
echo "=== Build complete ==="
echo "Installer: CrossfireServer-${GITVER}-Setup.exe"
echo "Copied to Desktop."
