<h1> Deployment </h1>

Following the [installation guide](./installation.md), you should now have a directory under `geoconverter/dist` which contains the executable and its required libraries. Some considerations:

- If you used python>=3.8 while creating the application you might need to set the environment variable `USE_PATH_FOR_GDAL_PYTHON=YES` before running the application. 
- If the target system is Windows, ensure the gdal library is not installed as it can lead to DLLs conflicting.

<!-- === "Windows"

    ```bat
    @echo off
    setlocal 
    set USE_PATH_FOR_GDAL_PYTHON=YES && path/to/app.exe
    endlocal
    ```

=== "Linux"

    ```bash
    export USE_PATH_FOR_GDAL_PYTHON=YES; path/to/app
    ``` -->
