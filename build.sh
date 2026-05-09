#!/bin/bash
# Crossfire Server Windows Build Script
# Requires: MSYS2 UCRT64, git, makensis, python3
# Run from MSYS2 UCRT64 shell

set -e

SRCDIR="$HOME/crossfire/crossfire-server"
PATCHDIR="$(dirname "$0")/patches"
INSTALLERDIR="$(dirname "$0")/installer"
BUILDDIR="$HOME"

echo "=== Crossfire Windows Build Script ==="
echo ""

# Step 1: Clone source if not present
if [ ! -d "$SRCDIR" ]; then
    echo "[1/8] Cloning Crossfire server source..."
    mkdir -p "$HOME/crossfire"
    git clone https://git.code.sf.net/p/crossfire/crossfire-server \
        "$SRCDIR"
else
    echo "[1/8] Source already present at $SRCDIR, skipping clone."
fi

# Step 2: Apply patches
echo "[2/8] Applying patches..."
cd "$SRCDIR"
for patch in "$PATCHDIR"/*.diff; do
    name=$(basename "$patch")
    echo "  Applying $name..."
    git apply --check "$patch" 2>/dev/null && git apply "$patch" \
        || echo "  WARNING: $name already applied or failed, skipping."
done

# Step 3: Configure
echo "[3/8] Running configure..."
./autogen.sh 2>/dev/null || true
./configure --prefix="/usr/local/crossfire" \
    --disable-shared --enable-static \
    CXXFLAGS="-D_GNU_SOURCE" CFLAGS="-D_GNU_SOURCE"

# Step 4: Build server
echo "[4/8] Building server..."
make -j$(nproc)

# Step 5: Build crossfire.dll
echo "[5/8] Building crossfire.dll..."
mkdir -p /tmp/server_objs
cd /tmp/server_objs
ar x "$SRCDIR/server/.libs/libserver.a"
rm -f libserver_la-win32.o libserver_la-server.o
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
    server/.libs/libserver_la-server.o \
    /tmp/win32_stub.o \
    -lsqlite3 -lws2_32 -lpython3.14 \
    -Wl,--enable-auto-image-base \
    -Wl,--allow-shlib-undefined \
    -Wl,--out-implib,crossfire.dll.a \
    -o crossfire.dll

echo "  crossfire.dll built: $(ls -lh crossfire.dll | awk '{print $5}')"

# Step 6: Build plugin DLLs
echo "[6/8] Building plugin DLLs..."
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

# Step 7: Generate NSIS installer script
echo "[7/8] Generating NSIS installer script..."
cd "$BUILDDIR"
GITVER="git-$(git -C "$SRCDIR" log --format='%h' -1 | cut -c1-7)"
echo "  Version: $GITVER"
python3 "$INSTALLERDIR/write_nsi.py" "$GITVER" \
    "$(cygpath -m "$BUILDDIR/crossfire-installer.nsi")"

# Step 8: Build installer
echo "[8/8] Building installer..."
makensis crossfire-installer.nsi
cp "CrossfireServer-${GITVER}-Setup.exe" /c/Users/leaf/Desktop/
echo ""
echo "=== Build complete ==="
echo "Installer: CrossfireServer-${GITVER}-Setup.exe"
echo "Copied to Desktop."
