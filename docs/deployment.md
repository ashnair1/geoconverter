# Deployment

This guide covers how to create and distribute standalone executable versions of geoconverter for end users.

## Overview

Geoconverter can be distributed as standalone executables that include:
- Python runtime and dependencies
- GDAL libraries
- Cesium Terrain Builder (CTB) tools
- PROJ data files

This allows users to run geoconverter without installing Python or GDAL separately.

## Prerequisites

Before creating deployable executables, ensure you have completed the [installation](installation.md) process:

1. ✅ Environment setup with GDAL ≥ 3.1
2. ✅ Repository cloned with submodules
3. ✅ Cesium Terrain Builder compiled
4. ✅ Python dependencies installed

## Creating Standalone Executables

### Using PyInstaller

The recommended approach uses PyInstaller to bundle the application with all dependencies.

#### Windows Deployment

Run from the **Developer Tools x64 cmd prompt** with the conda environment activated:

```bat
pyinstaller --clean --onedir geoconverter/app.py ^
--add-data "cesium-terrain-builder\build\tools\ctb-tile.exe;." ^
--add-binary "cesium-terrain-builder\build\src\ctb.dll;." ^
--add-data "%PROJ_LIB%;proj" ^
--name geoconverter-gui

pyinstaller --clean --onefile geoconverter/cli.py ^
--add-data "cesium-terrain-builder\build\tools\ctb-tile.exe;." ^
--add-binary "cesium-terrain-builder\build\src\ctb.dll;." ^
--add-data "%PROJ_LIB%;proj" ^
--name geoconverter-cli
```

#### Linux Deployment

```bash
pyinstaller --clean --onedir geoconverter/app.py \
--add-data "cesium-terrain-builder/build/tools/ctb-tile:." \
--add-binary "cesium-terrain-builder/build/src/libctb.so:." \
--add-data "$PROJ_LIB:proj" \
--name geoconverter-gui

pyinstaller --clean --onefile geoconverter/cli.py \
--add-data "cesium-terrain-builder/build/tools/ctb-tile:." \
--add-binary "cesium-terrain-builder/build/src/libctb.so:." \
--add-data "$PROJ_LIB:proj" \
--name geoconverter-cli
```

#### macOS Deployment

```bash
pyinstaller --clean --onedir geoconverter/app.py \
--add-data "cesium-terrain-builder/build/tools/ctb-tile:." \
--add-binary "cesium-terrain-builder/build/src/libctb.dylib:." \
--add-data "$PROJ_LIB:proj" \
--name geoconverter-gui

pyinstaller --clean --onefile geoconverter/cli.py \
--add-data "cesium-terrain-builder/build/tools/ctb-tile:." \
--add-binary "cesium-terrain-builder/build/src/libctb.dylib:." \
--add-data "$PROJ_LIB:proj" \
--name geoconverter-cli
```

### Build Output

After successful compilation, you'll find:

```
dist/
├── geoconverter-gui/     # GUI application directory
│   ├── geoconverter-gui.exe  (Windows)
│   ├── proj/             # PROJ data files
│   ├── ctb-tile.exe      # Cesium terrain builder
│   └── ... (other files)
└── geoconverter-cli.exe  # CLI executable (onefile)
```

## Distribution Packages

### Windows Distribution

Create a ZIP package for Windows users:

```bat
powershell Compress-Archive -Path "dist\geoconverter-gui" -DestinationPath "geoconverter-windows-x64.zip"
copy dist\geoconverter-cli.exe .\
```

Include a `README.txt`:
```
Geoconverter for Windows

GUI Application:
- Extract geoconverter-windows-x64.zip
- Run geoconverter-gui.exe

CLI Application:
- Run geoconverter-cli.exe from command prompt

Requirements:
- Windows 10 or later
- No additional software installation required

For help: geoconverter-cli.exe --help
```

### Linux Distribution

Create a tarball for Linux users:

```bash
tar -czf geoconverter-linux-x64.tar.gz -C dist geoconverter-gui
cp dist/geoconverter-cli ./
```

Include installation script `install.sh`:
```bash
#!/bin/bash
echo "Installing geoconverter..."
sudo cp geoconverter-cli /usr/local/bin/
sudo chmod +x /usr/local/bin/geoconverter-cli
echo "Installation complete. Run with: geoconverter-cli"
```

### macOS Distribution

Create a DMG or zip for macOS:

```bash
# Create application bundle structure
mkdir -p "Geoconverter.app/Contents/MacOS"
cp -r dist/geoconverter-gui/* "Geoconverter.app/Contents/MacOS/"
cp dist/geoconverter-cli ./

# Create zip
zip -r geoconverter-macos.zip Geoconverter.app geoconverter-cli
```

## Environment Variables

### GDAL Python Bindings (Python ≥ 3.8)

For systems with Python ≥ 3.8, the executable may need environment configuration:

**Windows:**
```bat
@echo off
set USE_PATH_FOR_GDAL_PYTHON=YES
start geoconverter-gui.exe
```

**Linux/macOS:**
```bash
#!/bin/bash
export USE_PATH_FOR_GDAL_PYTHON=YES
./geoconverter-gui
```

Include wrapper scripts in your distribution packages.

## Testing Deployments

### Validation Checklist

Before distributing, test on clean systems:

- [ ] GUI launches without Python installed
- [ ] CLI shows help message: `geoconverter-cli --help`
- [ ] Can process sample raster files
- [ ] Cesium terrain generation works
- [ ] No missing DLL/library errors
- [ ] PROJ coordinate transformations work

### Test Script

Create `test_deployment.bat` (Windows) or `test_deployment.sh` (Linux):

```bash
#!/bin/bash
set -e

echo "Testing geoconverter deployment..."

# Test CLI help
./geoconverter-cli --help > /dev/null
echo "✅ CLI help working"

# Test GUI version check (if available)
if command -v xvfb-run > /dev/null; then
    timeout 10s xvfb-run ./geoconverter-gui || echo "✅ GUI launches"
fi

# Test with sample data (if available)
if [ -f "test_data.tif" ]; then
    ./geoconverter-cli -i test_data.tif -o test_output.tif -of GTiff
    echo "✅ Conversion test passed"
fi

echo "🎉 Deployment test completed"
```

## Automated Building

### GitHub Actions

Create `.github/workflows/build_exe.yml` for automated builds:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: 'recursive'

    - name: Setup conda environment
      uses: conda-incubator/setup-miniconda@v3
      with:
        activate-environment: geo
        environment-file: environment.yml

    - name: Build cesium-terrain-builder
      shell: cmd
      run: |
        call conda activate geo
        cd cesium-terrain-builder
        mkdir build
        cmake -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=Release -S . -B build
        cmake --build build

    - name: Build executables
      shell: cmd
      run: |
        call conda activate geo
        pyinstaller build_scripts/geoconverter-gui.spec
        pyinstaller build_scripts/geoconverter-cli.spec

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: geoconverter-windows
        path: dist/
```

## Distribution Considerations

### File Sizes

Typical executable sizes:
- **CLI only**: ~50-100 MB
- **GUI with dependencies**: ~200-400 MB
- **Full distribution package**: ~300-600 MB

### Compatibility

- **Windows**: Requires Windows 10 or later
- **Linux**: Compatible with most modern distributions
- **macOS**: Requires macOS 10.14 or later

### Security

For public distribution:
- Sign executables on Windows (Authenticode)
- Notarize applications on macOS
- Provide checksums for verification
- Test with antivirus scanners

### License Compliance

Ensure compliance with bundled libraries:
- GDAL (MIT/X11)
- PROJ (MIT)
- Python (PSF License)
- NumPy (BSD)

Include a `LICENSES` folder with all relevant license files.

## Troubleshooting

### Common Build Issues

**Missing CTB tools:**
```
FileNotFoundError: cesium-terrain-builder/build/tools/ctb-tile not found
```
Solution: Ensure cesium-terrain-builder is compiled first.

**PROJ data not found:**
```
PROJ: proj_create_from_database: Cannot find proj.db
```
Solution: Verify `PROJ_LIB` environment variable points to PROJ data directory.

**DLL conflicts on Windows:**
```
ImportError: DLL load failed
```
Solution: Ensure no conflicting GDAL installations in system PATH.

### Runtime Issues

**"Application failed to start":**
- Check for missing Visual C++ redistributables (Windows)
- Verify executable permissions (Linux/macOS)
- Try running from command line to see error messages

**Performance issues:**
- Large file sizes may indicate unnecessary dependencies
- Use `--exclude-module` in PyInstaller to remove unused modules
- Consider `--onefile` vs `--onedir` trade-offs

For additional help, see the [troubleshooting](installation.md#troubleshooting) section in the installation guide.
