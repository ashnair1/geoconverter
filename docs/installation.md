<h1> Installation </h1>

## Setup environment

geoconverter has only two real requirements: `gdal > 3.1` and `Python >= 3.6`. Use conda to install these dependencies and setup your development environment.

```console
conda install -n geo gdal>=3.1.0 pyinstaller python=3.7
conda activate geo
```


## Clone repository

The source for geoconverter can be downloaded from the [Github repo](https://github.com/ashnair1/geoconverter).

```console
git clone https://github.com/ashnair1/geoconverter.git
git submodule update --init --recursive
```

??? note "Using gdal >= 3.4"
    To work with `gdal>=3.4`, you will need to switch to the `gdal3.4` branch of `cesium-terrain-builder`. Follow the instructions given below:
    ```console
    # Edit submodule branch
    $ git config --file=.gitmodules submodule.cesium-terrain-builder.branch gdal3.4

    # Sync and update the submodule
    $ git submodule sync
    $ git submodule update --init --recursive --remote
    ```

!!! important "Important"
    - For Windows users, it is highly recommended to use conda to install gdal. The Windows build of geoconverter was created using gdal from conda-forge channel. conda-forge builds on Windows use ==MSVC compiler== to maintain compatibility with Python so users will need to have it installed as well. The installation instructions below assume it is being run from the ==Developer Tools x64 cmd prompt==.

    - For Linux users, depending on your gdal installation you will need to specify additional directives to cmake so that it can find it correctly. These directives will be required if you used conda to install gdal. Refer to [ctb docs](https://github.com/geo-data/cesium-terrain-builder#installation) for more information. 


## Create the cesium terrain builder (ctb) executables ##

=== "Windows"

    ```bat
    cd geoconverter && mkdir cesium-terrain-builder\build
    cmake -DCMAKE_BUILD_TYPE=Release ^
    -G "NMake Makefiles" ^
    -S cesium-terrain-builder ^
    -B cesium-terrain-builder\build && cmake --build cesium-terrain-builder\build
    ```

=== "Linux"

    ```bash
    cd geoconverter && mkdir cesium-terrain-builder/build
    cmake -DCMAKE_BUILD_TYPE=Release \
    -DGDAL_LIBRARY_DIR=$CONDA_PREFIX/lib \
    -DGDAL_LIBRARY=$CONDA_PREFIX/lib/libgdal.so \
    -DGDAL_INCLUDE_DIR=$CONDA_PREFIX/include \
    -S cesium-terrain-builder \
    -B cesium-terrain-builder/build && cmake --build cesium-terrain-builder/build
    ```


## Create the application ##

Ensure `PROJ_LIB` environment variable is set. If you're working within a conda environment, this should already be set.


=== "Windows"

    ```bat
    pyinstaller --clean --onedir geoconverter/app.py ^
    --add-data "cesium-terrain-builder\build\tools\ctb-tile.exe;." ^
    --add-binary "cesium-terrain-builder\build\src\ctb.dll;." ^
    --add-data "%PROJ_LIB%;proj" 
    ```

=== "Linux"

    ```bash
    pyinstaller --clean --onedir geoconverter/app.py \
    --add-data "cesium-terrain-builder/build/tools/ctb-tile:." \
    --add-binary "cesium-terrain-builder/build/src/libctb.so:." \
    --add-data "$PROJ_LIB:proj"
    ```
      

