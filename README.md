# gdal-converter

Application for converting between geospatial raster formats. 

## Requirements

- gdal >= 3.1
- Python >= 3.6

## Installation

If you want to use `cesium terrain builder` to convert DEM tiffs to Terrain files or quantized Meshes, run the following command
```
git clone --recurse-submodules https://github.com/ashnair1/geoconverter.git
```
else
```
git clone https://github.com/ashnair1/geoconverter.git
```

## Instructions

### Install dependencies

Use `conda` to install your dependencies
```console
$ conda install -n geo gdal>=3.4.1 pyinstaller
$ conda activate geo
```

### Windows

#### Create ctb executables

```console
$ mkdir cesium-terrain-builder\build
$ cmake -DCMAKE_BUILD_TYPE=Release -G "NMake Makefiles" -S cesium-terrain-builder -B cesium-terrain-builder\build && cmake --build cesium-terrain-builder\build
```

#### Create the application
Package the application with `ctb-tile.exe`, its associated dll `ctb.dll` and the proj directory. Either ensure your `PROJ_LIB` is set or pass the path to `proj` directory explicitly.

```console
$ pyinstaller --clean --onedir geoconverter/app.py --add-data "cesium-terrain-builder\build\tools\ctb-tile.exe;." --add-data "%PROJ_LIB%;proj" --add-binary "cesium-terrain-builder\build\src\ctb.dll;."
```

Note: While deploying, there are two things users need to be aware of
- Target system must not have `GDAL` installed as it will lead to conflicting DLLs.
- If target system python >= 3.8, you will need to set the environment variable `USE_PATH_FOR_GDAL_PYTHON=YES` before running the application.
