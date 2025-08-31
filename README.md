# Geoconverter

[![docs](https://github.com/ashnair1/geoconverter/actions/workflows/docs.yml/badge.svg)](https://github.com/ashnair1/geoconverter/actions/workflows/docs.yml)
[![PyPI version](https://badge.fury.io/py/geoconverter.svg)](https://badge.fury.io/py/geoconverter)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![GDAL](https://img.shields.io/badge/GDAL-3.1%2B-green.svg)](https://gdal.org/)

A powerful geospatial raster format conversion tool with GUI and CLI interfaces, featuring automatic data type handling, contrast enhancement, and Cesium terrain support.

## ✨ Key Features

- **🔄 Smart Conversion**: Automatically handles data type conversion with proper scaling
- **📊 Format Support**: Converts between major geospatial formats (GeoTIFF, COG, JPEG2000, IMG)
- **🌍 Terrain Generation**: Creates Cesium terrain and quantized mesh tiles from DEMs
- **🎛️ Dual Interface**: Both command-line and graphical user interfaces
- **📈 Contrast Enhancement**: Built-in percentile-based stretch capabilities
- **🎯 Band Selection**: Flexible band selection for multispectral imagery
- **⚡ Batch Processing**: Process entire directories efficiently

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install geoconverter

# Or install with conda for GDAL
conda install -c conda-forge gdal>=3.1.0
pip install geoconverter
```

### Basic Usage

**Command Line:**
```bash
# Simple format conversion
geoconverter -i input.tif -o output_cog.tif -of COG

# Multi-band with contrast enhancement
geoconverter -i landsat.tif -o enhanced.tif -b 5,4,3 stretch -s 2 98
```

**GUI Application:**
```bash
geoconverter-gui
```

## 📖 Documentation

| Section | Description |
|---------|-------------|
| [Installation](https://ashnair1.github.io/geoconverter/installation) | Setup guide for all platforms and use cases |
| [Usage](https://ashnair1.github.io/geoconverter/usage) | Complete CLI and GUI usage examples |
| [Deployment](https://ashnair1.github.io/geoconverter/deployment) | Creating standalone executables |
| [GDAL Compatibility](https://ashnair1.github.io/geoconverter/gdal-compatibility) | Version compatibility and testing |

## 🛠️ What Makes Geoconverter Special

Unlike basic GDAL utilities, geoconverter provides:

### Automatic Data Scaling
```bash
# Manual GDAL approach - you need to find min/max yourself
gdal_translate -scale 0 32767 0 255 input.tif output.tif

# Geoconverter - automatic scaling
geoconverter -i input.tif -o output.tif -ot Byte
```

### Built-in Contrast Enhancement
```bash
# Apply 2-98% percentile stretch automatically
geoconverter -i input.tif -o enhanced.tif stretch -s 2 98
```

### Cesium Terrain Support
```bash
# Create terrain tiles for web visualization
geoconverter -i dem.tif -o terrain_tiles/ -of Terrain
```

## 🎯 Use Cases

### Remote Sensing
- **Landsat/Sentinel Processing**: Band combinations and contrast enhancement
- **Multispectral Analysis**: Flexible band selection and data type conversion
- **Large Dataset Processing**: Batch conversion of satellite imagery

### Web Mapping
- **Cloud Optimized GeoTIFF**: Optimize rasters for web serving
- **Cesium Integration**: Generate terrain tiles for 3D visualization
- **Format Optimization**: Convert to web-friendly formats

### GIS Workflows
- **Data Preparation**: Standardize formats across datasets
- **Archive Conversion**: Batch convert legacy formats
- **Quality Enhancement**: Apply contrast stretching for visualization

## 📊 Supported Formats

### Input Formats
Any GDAL-readable format including:
- GeoTIFF (.tif, .tiff)
- Erdas Imagine (.img)
- JPEG2000 (.jp2)
- HDF, NetCDF, and more

### Output Formats
- **COG** - Cloud Optimized GeoTIFF
- **GTiff** - Standard GeoTIFF
- **JP2OpenJPEG** - JPEG2000
- **HFA** - Erdas Imagine
- **Terrain** - Cesium terrain tiles
- **Mesh** - Quantized mesh tiles

## 🔧 Requirements

- **Python**: ≥ 3.8
- **GDAL**: ≥ 3.1.0
- **Platform**: Windows, Linux, macOS
- **Dependencies**: NumPy (automatically installed)

## 🤝 Contributing

We welcome contributions! Areas where help is needed:

- **Format Support**: Adding new output formats
- **Performance**: Optimization for large datasets
- **GUI Enhancements**: Interface improvements
- **Documentation**: Examples and tutorials
- **Testing**: GDAL compatibility testing

Visit our [GitHub repository](https://github.com/ashnair1/geoconverter) to get started.

## 📄 License

MIT License - see the [LICENSE](https://github.com/ashnair1/geoconverter/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- **GDAL Team**: For the foundational geospatial library
- **@homme** & **@ahuarte47**: Cesium Terrain Builder contributors
- **Cesium**: For terrain visualization standards
- **Community**: All users and contributors

---

**Need Help?** Check our [documentation](https://ashnair1.github.io/geoconverter/) or [create an issue](https://github.com/ashnair1/geoconverter/issues) on GitHub.
