#!/bin/bash
# Script to build geoconverter with bundled ctb-tile binary

set -e

echo "Building cesium-terrain-builder..."
cd cesium-terrain-builder

# Clean and create build directory
rm -rf build
mkdir -p build
cd build

# Get GDAL paths from conda environment
GDAL_ROOT=$(dirname $(dirname $(which gdal-config)))
echo "Using GDAL from: $GDAL_ROOT"

# Set environment for CMake tests
export CMAKE_LIBRARY_PATH="$GDAL_ROOT/lib"
export CMAKE_INCLUDE_PATH="$GDAL_ROOT/include"

# Configure with conda environment prefix path and explicit library linking
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=$GDAL_ROOT \
    -DCMAKE_POLICY_DEFAULT_CMP0074=NEW \
    -DCMAKE_EXE_LINKER_FLAGS="-L$GDAL_ROOT/lib -Wl,-rpath,$GDAL_ROOT/lib" \
    -DCMAKE_SHARED_LINKER_FLAGS="-L$GDAL_ROOT/lib -Wl,-rpath,$GDAL_ROOT/lib" \
    -DHAVE_UNIFIED_GDAL=1


cmake --build . --config Release

cd ../..

echo "Setting up binary directories..."
mkdir -p geoconverter/bin
mkdir -p geoconverter/lib

echo "Copying binaries..."
cp cesium-terrain-builder/build/tools/ctb-tile geoconverter/bin/
cp cesium-terrain-builder/build/tools/ctb-export geoconverter/bin/
cp cesium-terrain-builder/build/tools/ctb-extents geoconverter/bin/
cp cesium-terrain-builder/build/tools/ctb-info geoconverter/bin/
cp cesium-terrain-builder/build/src/libctb.so geoconverter/lib/
chmod +x geoconverter/bin/*

echo "Building Python wheel..."
python -m build --wheel

echo "Build complete! Wheel is in dist/"
ls -la dist/

echo ""
echo "To test the wheel:"
echo "1. pip install dist/geoconverter-*.whl"
echo "2. geoconverter-gui"