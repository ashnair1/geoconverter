# Installation

This guide covers installation options for geoconverter, from simple package installation to full development setup.

## Quick Installation

### Option 1: PyPI Installation (Recommended for Users)

Install geoconverter directly from PyPI:

```bash
pip install geoconverter
```

This provides both command-line and GUI interfaces:
- `geoconverter` - Command line interface
- `geoconverter-gui` - Graphical user interface

**Requirements:** Python ≥ 3.8, GDAL ≥ 3.1.0

!!! note "GDAL Installation"
    GDAL must be installed separately. We recommend using conda:
    ```bash
    conda install -c conda-forge gdal>=3.1.0
    pip install geoconverter
    ```

### Option 2: Standalone Executables

Download pre-built executables from the [releases page](https://github.com/ashnair1/geoconverter/releases) - no Python or GDAL installation required.

## Development Installation

### Prerequisites

For development work, you'll need:

- **Python ≥ 3.8**
- **GDAL ≥ 3.1.0**
- **CMake ≥ 3.8** (for cesium-terrain-builder)
- **C++ compiler** with C++11 support (C++17 for GDAL ≥ 3.9)

### Environment Setup

We recommend using conda for managing dependencies:

```bash
# Create conda environment
conda create -n geoconverter python=3.11
conda activate geoconverter

# Install GDAL and build dependencies
conda install -c conda-forge gdal>=3.1.0 cmake ninja
```

### Clone Repository

Clone with submodules to get cesium-terrain-builder:

```bash
git clone --recurse-submodules https://github.com/ashnair1/geoconverter.git
cd geoconverter
```

### GDAL Version Compatibility

For GDAL ≥ 3.4, switch cesium-terrain-builder to the compatible branch:

```bash
# For GDAL 3.4+
git config --file=.gitmodules submodule.cesium-terrain-builder.branch gdal3.4
git submodule update --remote
```

!!! info "GDAL Compatibility"
    See the [GDAL Compatibility](gdal-compatibility.md) guide for detailed version support information.

## Building Cesium Terrain Builder

Cesium Terrain Builder (CTB) provides terrain tile generation capabilities.

### Windows Build

**Prerequisites:**
- Visual Studio Build Tools or Visual Studio Community
- Developer Command Prompt (recommended)

```bat
cd geoconverter
mkdir cesium-terrain-builder\build
cd cesium-terrain-builder\build

cmake -G "Visual Studio 17 2022" -A x64 ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DGDAL_LIBRARY_DIR=%CONDA_PREFIX%\Library\lib ^
    -DGDAL_LIBRARY=%CONDA_PREFIX%\Library\lib\gdal.lib ^
    -DGDAL_INCLUDE_DIR=%CONDA_PREFIX%\Library\include ^
    ..

cmake --build . --config Release
```

### Linux Build

```bash
cd geoconverter
mkdir -p cesium-terrain-builder/build
cd cesium-terrain-builder/build

cmake -DCMAKE_BUILD_TYPE=Release \
    -DGDAL_LIBRARY_DIR=$CONDA_PREFIX/lib \
    -DGDAL_LIBRARY=$CONDA_PREFIX/lib/libgdal.so \
    -DGDAL_INCLUDE_DIR=$CONDA_PREFIX/include \
    ..

make -j$(nproc)
```

### macOS Build

```bash
cd geoconverter
mkdir -p cesium-terrain-builder/build
cd cesium-terrain-builder/build

cmake -DCMAKE_BUILD_TYPE=Release \
    -DGDAL_LIBRARY_DIR=$CONDA_PREFIX/lib \
    -DGDAL_LIBRARY=$CONDA_PREFIX/lib/libgdal.dylib \
    -DGDAL_INCLUDE_DIR=$CONDA_PREFIX/include \
    ..

make -j$(sysctl -n hw.ncpu)
```

### Verify CTB Build

Test that cesium-terrain-builder compiled successfully:

```bash
# Windows
cesium-terrain-builder\build\tools\ctb-tile.exe --version

# Linux/macOS
cesium-terrain-builder/build/tools/ctb-tile --version
```

Expected output: `ctb-tile version X.X.X`

## Install Python Package

### Development Installation

Install in editable mode for development:

```bash
# From geoconverter root directory
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

### Test Installation

Verify the installation works:

```bash
# Test CLI
geoconverter --help

# Test Python import
python -c "from geoconverter import gdal_convert; print('✅ Import successful')"

# Test GUI (if display available)
geoconverter-gui
```

## Docker Installation

For containerized development or testing:

```bash
# Clone repository
git clone --recurse-submodules https://github.com/ashnair1/geoconverter.git
cd geoconverter

# Build development container
docker build -f docker/Dockerfile.gdal-test -t geoconverter-dev .

# Run container
docker run -it --rm -v $(pwd):/workspace geoconverter-dev bash
```

## Platform-Specific Notes

### Windows

**Visual Studio Requirements:**
- Visual Studio Build Tools 2019 or later
- C++ CMake tools component
- MSVC v143 compiler toolset

**Environment Variables:**
```bat
# May be needed for Python ≥ 3.8
set USE_PATH_FOR_GDAL_PYTHON=YES
```

**conda-forge GDAL:**
Using conda-forge GDAL is recommended on Windows as it provides consistent builds.

### Linux

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake ninja-build libgdal-dev python3-dev
```

**CentOS/RHEL:**
```bash
sudo yum groupinstall "Development Tools"
sudo yum install cmake ninja-build gdal-devel python3-devel
```

**Environment:**
```bash
# Add to ~/.bashrc if needed
export USE_PATH_FOR_GDAL_PYTHON=YES
```

### macOS

**Homebrew:**
```bash
brew install cmake ninja gdal
```

**Xcode:**
Ensure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

## Troubleshooting

### Common Issues

#### GDAL Not Found
```
CMake Error: Could not find GDAL
```

**Solutions:**
1. Install GDAL via conda: `conda install -c conda-forge gdal`
2. Specify GDAL paths manually in CMake command
3. Set `GDAL_DATA` environment variable

#### C++ Compiler Issues
```
error: This file requires compiler C++17 support
```

**Solutions:**
1. Update to GDAL < 3.9 or use C++17 compiler
2. Install newer compiler (GCC 8+ or MSVC 2017+)
3. Check [GDAL compatibility guide](gdal-compatibility.md)

#### Python Import Errors
```
ImportError: cannot import name 'gdal' from 'osgeo'
```

**Solutions:**
1. Reinstall GDAL Python bindings: `pip install gdal==$(gdal-config --version)`
2. Check conda environment activation
3. Set `USE_PATH_FOR_GDAL_PYTHON=YES`

#### CTB Build Failures
```
fatal error: 'gdal.h' file not found
```

**Solutions:**
1. Install GDAL development headers
2. Specify correct GDAL include directory in cmake
3. Ensure GDAL version compatibility

### Getting Help

1. **Check Documentation**: Review this guide and [GDAL compatibility](gdal-compatibility.md)
2. **GitHub Issues**: Search existing [issues](https://github.com/ashnair1/geoconverter/issues)
3. **System Information**: When reporting issues, include:
   - Operating system and version
   - Python version (`python --version`)
   - GDAL version (`gdal-config --version`)
   - CMake version (`cmake --version`)
   - Compiler version

### Build Verification

Use this script to verify your installation:

```bash
#!/bin/bash
echo "=== Geoconverter Installation Verification ==="

echo "Python version:"
python --version

echo "GDAL version:"
gdal-config --version 2>/dev/null || echo "gdal-config not found"

echo "CMake version:"
cmake --version | head -n1

echo "CTB tools:"
if [ -f "cesium-terrain-builder/build/tools/ctb-tile" ]; then
    ./cesium-terrain-builder/build/tools/ctb-tile --version
else
    echo "ctb-tile not found - build cesium-terrain-builder first"
fi

echo "Python import test:"
python -c "from geoconverter import gdal_convert; print('✅ Import successful')" 2>/dev/null || echo "❌ Import failed"

echo "CLI test:"
geoconverter --help >/dev/null 2>&1 && echo "✅ CLI working" || echo "❌ CLI not working"

echo "=== Verification Complete ==="
```

## Next Steps

After successful installation:

1. **Try the Examples**: See [Usage](usage.md) for GUI and CLI examples
2. **Read GDAL Compatibility**: Review [GDAL compatibility](gdal-compatibility.md) for version-specific information
3. **Build Executables**: Follow [Deployment](deployment.md) to create standalone executables
4. **Development**: Explore the codebase and contribute improvements

For questions or issues, please visit the [GitHub repository](https://github.com/ashnair1/geoconverter).
