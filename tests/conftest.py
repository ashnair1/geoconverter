"""Pytest configuration and fixtures for geoconverter tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_tif(temp_dir: Path) -> Path:
    """Create a sample TIFF file for testing."""
    # Import here to avoid GDAL import issues in test discovery
    try:
        from tests.data import create_test_tif

        tif_path = temp_dir / "sample.tif"
        create_test_tif(str(tif_path))
        return tif_path
    except ImportError:
        pytest.skip("GDAL not available for creating test data")


@pytest.fixture
def gdal_available() -> bool:
    """Check if GDAL is available for testing."""
    try:
        from osgeo import gdal

        return True
    except ImportError:
        return False


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "gui: mark test as requiring GUI components")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their location or imports."""
    for item in items:
        # Mark GUI tests
        if "gui" in str(item.fspath) or "app" in str(item.fspath):
            item.add_marker(pytest.mark.gui)

        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Skip GUI tests in CI if no display available
        if "gui" in [mark.name for mark in item.iter_markers()]:
            if not os.environ.get("DISPLAY") and os.environ.get("CI"):
                item.add_marker(pytest.mark.skip(reason="No display available in CI"))


def pytest_sessionstart(session):
    """Session startup - check GDAL availability."""
    try:
        from osgeo import gdal

        gdal_version = gdal.VersionInfo("RELEASE_NAME")
        print(f"GDAL {gdal_version} available for testing")
    except ImportError:
        print("Warning: GDAL not available - some tests will be skipped")
