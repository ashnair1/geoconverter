# GDAL Compatibility Strategy

This document outlines the GDAL compatibility strategy for geoconverter and cesium-terrain-builder, ensuring compatibility with GDAL versions 3.10, 3.11, and future releases.

## Overview

The geoconverter project depends on:
- **GDAL** for geospatial raster processing
- **cesium-terrain-builder** (C++) for terrain tile generation
- **Python bindings** for the GUI and CLI interface

## Current Compatibility Status

### ✅ Tested and Supported
- **GDAL 3.8** - Stable, legacy support
- **GDAL 3.9** - Stable, C++17 required
- **GDAL 3.10** - Stable, fully compatible
- **GDAL 3.11** - Stable, fully compatible

### 🚨 Known Breaking Changes

#### GDAL 3.9+
- **C++17 Requirement**: GDAL 3.9+ requires C++17 compiler
- **Build System**: Automatic C++ standard detection implemented

#### GDAL 3.11
- **GDALGrid ABI Break**: ABI breakage in GDALGrid functions (API compatibility preserved)
- **Coordinate Transformation**: Behavior changes in transform methods
- **Forward Declarations**: New `gdal_fwd.h` header may cause issues

## Implementation

### 1. Build System Changes

#### CMakeLists.txt Enhancements
```cmake
# Automatic GDAL version detection
find_package(GDAL REQUIRED)
message(STATUS "Found GDAL version: ${GDAL_VERSION}")

# C++ standard selection based on GDAL version
if(GDAL_VERSION VERSION_GREATER_EQUAL "3.9.0")
  set(CMAKE_CXX_STANDARD 17)
else()
  set(CMAKE_CXX_STANDARD 11)
endif()

# Version compatibility checks
if(GDAL_VERSION VERSION_GREATER_EQUAL "3.9.0" AND CMAKE_CXX_STANDARD LESS 17)
  message(FATAL_ERROR "GDAL ${GDAL_VERSION} requires C++17")
endif()
```

### 2. Compatibility Header

#### gdal_compat.hpp
Provides version-specific compatibility macros:
```cpp
// Version detection
#define CTB_GDAL_VERSION_MAJOR GDAL_VERSION_MAJOR
#define CTB_GDAL_VERSION_MINOR GDAL_VERSION_MINOR

// GDAL 3.11+ specific features
#if GDAL_VERSION_NUM >= GDAL_COMPUTE_VERSION(3,11,0)
  #define CTB_GDAL_HAS_GRID_PREFIX 1
  #define CTB_GDAL_HAS_NEW_COORDINATE_TRANSFORM 1
#endif

// Smart pointer utilities (when gdal_priv.h is available)
namespace ctb::gdal_compat {
  using GDALDatasetPtr = std::unique_ptr<GDALDataset, decltype(&GDALClose)>;
  inline GDALDatasetPtr makeDatasetPtr(GDALDataset* dataset);
}
```

## Testing Strategy

### 1. Automated Testing

#### GitHub Actions Matrix
- **OS**: Ubuntu, Windows, macOS  
- **GDAL**: 3.8, 3.9, 3.10, 3.11
- **Python**: 3.9, 3.10, 3.11
- **Schedule**: Weekly runs to catch new releases

#### Local Testing
```bash
# Test all GDAL versions
./scripts/test_gdal_compatibility.sh

# Test specific version  
./scripts/test_gdal_compatibility.sh 3.11
```

#### Docker Testing
```bash
# Build test container for GDAL 3.11
docker build -f docker/Dockerfile.gdal-test --build-arg GDAL_VERSION=3.11 -t geoconverter:gdal-3.11 .

# Run compatibility tests
docker run --rm geoconverter:gdal-3.11
```

### 2. Release Monitoring

#### Automated Monitoring
```bash
# Check for new GDAL releases and compatibility status
python scripts/monitor_gdal.py
```

This script:
- Fetches latest GDAL releases from GitHub
- Identifies versions not in our test matrix
- Scans release notes for breaking changes
- Suggests GitHub Actions updates

## Maintenance Procedures

### When a New GDAL Version is Released

1. **Check Release Notes**
   ```bash
   python scripts/monitor_gdal.py
   ```

2. **Update Test Matrix**
   - Add new version to `.github/workflows/gdal-compatibility.yml`
   - Update `scripts/test_gdal_compatibility.sh`

3. **Test Locally**
   ```bash
   ./scripts/test_gdal_compatibility.sh 3.12  # New version
   ```

4. **Update Documentation**
   - Update this file with compatibility status
   - Document any breaking changes or required code changes

5. **Handle Breaking Changes**
   - Update `gdal_compat.hpp` with new version checks
   - Add conditional compilation if needed
   - Update CMakeLists.txt for build requirements

### Handling C++ Compilation Issues

If you encounter C++ compilation errors with newer GDAL versions:

1. **Check C++ Standard Requirements**
   - Verify GDAL's C++ standard requirement
   - Update CMakeLists.txt if needed

2. **Review API Changes**
   - Check GDAL's `MIGRATION_GUIDE.TXT`
   - Look for deprecated/removed functions
   - Check for new required headers

3. **Add Compatibility Code**
   ```cpp
   // In gdal_compat.hpp
   #if GDAL_VERSION_NUM >= GDAL_COMPUTE_VERSION(3,12,0)
     // New version compatibility code
   #endif
   ```

## Directory Structure

```
geoconverter/
├── .github/workflows/gdal-compatibility.yml    # CI/CD testing
├── cesium-terrain-builder/
│   ├── CMakeLists.txt                          # Enhanced with GDAL detection
│   └── src/gdal_compat.hpp                     # Compatibility header
├── docker/Dockerfile.gdal-test                 # Docker testing setup
├── scripts/
│   ├── test_gdal_compatibility.sh              # Local testing script
│   └── monitor_gdal.py                         # Release monitoring
└── docs/gdal-compatibility.md                  # This document
```

## Troubleshooting

### Common Issues

#### Build Fails with "GDAL not found"
```bash
# For conda environments
cmake .. \
  -DGDAL_LIBRARY_DIR=$CONDA_PREFIX/lib \
  -DGDAL_LIBRARY=$CONDA_PREFIX/lib/libgdal.so \
  -DGDAL_INCLUDE_DIR=$CONDA_PREFIX/include
```

#### C++17 Compilation Errors
- Ensure your compiler supports C++17
- Update CMake to 3.8+ for proper C++17 support
- On older systems, you may need to install a newer compiler

#### ABI Compatibility Issues
- Clean rebuild when switching GDAL versions
- Check for mixed library versions
- Use same compiler for all dependencies

### Getting Help

1. **Check GitHub Issues**: Search for GDAL-related issues
2. **GDAL Mailing List**: gdal-dev@lists.osgeo.org
3. **Stack Overflow**: Tag with `gdal` and `c++`
4. **Create Issue**: Document the GDAL version, error, and system details

## Future Considerations

### GDAL 4.x Preparation
- GDAL 4.x will likely have more significant breaking changes
- Monitor RFC discussions for advance warning
- Consider creating a separate compatibility layer

### Long-term Strategy
- Maintain compatibility with at least 2 major GDAL versions
- Automate more of the compatibility testing process
- Consider upstreaming compatibility improvements to cesium-terrain-builder

---

*Last updated: 2025-01-31*  
*Compatible with: GDAL 3.8 - 3.11*  
*Status: ✅ All tested versions working*