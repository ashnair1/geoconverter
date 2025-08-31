#!/bin/bash
# GDAL Compatibility Testing Script for geoconverter
# 
# This script tests cesium-terrain-builder and geoconverter against different GDAL versions
# Usage: ./scripts/test_gdal_compatibility.sh [gdal_version]
#   e.g: ./scripts/test_gdal_compatibility.sh 3.11

set -e

GDAL_VERSIONS=${1:-"3.8 3.9 3.10 3.11"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== GDAL Compatibility Test Suite ==="
echo "Testing GDAL versions: $GDAL_VERSIONS"
echo "Project root: $PROJECT_ROOT"
echo

# Function to test a specific GDAL version
test_gdal_version() {
    local version=$1
    echo "=== Testing GDAL $version ==="
    
    # Create conda environment for this version
    local env_name="ctb-gdal-$version"
    echo "Creating conda environment: $env_name"
    
    # Remove existing environment if it exists
    conda env remove -n "$env_name" -y 2>/dev/null || true
    
    # Create new environment
    conda create -n "$env_name" python=3.10 -y
    conda activate "$env_name"
    
    # Install GDAL and dependencies
    echo "Installing GDAL $version and dependencies..."
    conda install -c conda-forge "gdal=$version" cmake ninja zlib numpy -y
    
    # Display environment info
    echo "Environment info:"
    echo "  GDAL version: $(gdal-config --version)"
    echo "  Python version: $(python --version)"
    echo "  Conda prefix: $CONDA_PREFIX"
    echo
    
    # Test cesium-terrain-builder
    echo "Testing cesium-terrain-builder..."
    cd "$PROJECT_ROOT/cesium-terrain-builder"
    
    # Clean previous build
    rm -rf build-test
    mkdir build-test
    cd build-test
    
    # Configure with explicit paths
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DGDAL_LIBRARY_DIR="$CONDA_PREFIX/lib" \
        -DGDAL_LIBRARY="$CONDA_PREFIX/lib/libgdal.so" \
        -DGDAL_INCLUDE_DIR="$CONDA_PREFIX/include" \
        -DZLIB_LIBRARY="$CONDA_PREFIX/lib/libz.so" \
        -DZLIB_INCLUDE_DIR="$CONDA_PREFIX/include"
    
    # Build
    echo "Building cesium-terrain-builder..."
    cmake --build . --config Release -j$(nproc)
    
    # Test tools
    echo "Testing cesium-terrain-builder tools..."
    ./tools/ctb-tile --version
    ./tools/ctb-info --version
    ./tools/ctb-extents --help > /dev/null
    
    # Test geoconverter
    cd "$PROJECT_ROOT"
    echo "Testing geoconverter..."
    
    # Test import
    python -c "from geoconverter import gdal_convert; print('Import successful')"
    
    # Test CLI help
    python geoconverter/gdal_convert.py --help > /dev/null
    
    # Create test data if it doesn't exist
    if [ ! -f "tests/dummy.tif" ]; then
        echo "Creating test data..."
        python tests/data.py
    fi
    
    # Test basic conversion
    echo "Testing basic conversion..."
    python geoconverter/gdal_convert.py -i tests/dummy.tif -o "test_output_gdal_$version.tif" -of GTiff
    
    # Verify output
    if [ -f "test_output_gdal_$version.tif" ]; then
        echo "✅ GDAL $version: All tests passed!"
        rm "test_output_gdal_$version.tif"
    else
        echo "❌ GDAL $version: Conversion test failed!"
        return 1
    fi
    
    conda deactivate
    echo
}

# Function to cleanup environments
cleanup_environments() {
    echo "Cleaning up test environments..."
    for version in $GDAL_VERSIONS; do
        local env_name="ctb-gdal-$version"
        conda env remove -n "$env_name" -y 2>/dev/null || true
    done
}

# Trap to cleanup on exit
trap cleanup_environments EXIT

# Main test loop
failed_versions=""
passed_versions=""

for version in $GDAL_VERSIONS; do
    if test_gdal_version "$version"; then
        passed_versions="$passed_versions $version"
    else
        failed_versions="$failed_versions $version"
        echo "❌ GDAL $version failed"
    fi
done

# Summary
echo "=== GDAL Compatibility Test Summary ==="
if [ -n "$passed_versions" ]; then
    echo "✅ Passed versions:$passed_versions"
fi
if [ -n "$failed_versions" ]; then
    echo "❌ Failed versions:$failed_versions"
    exit 1
else
    echo "🎉 All GDAL versions passed compatibility tests!"
fi