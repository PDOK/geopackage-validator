import sys
from typing import Callable

from osgeo import ogr
from osgeo.ogr import DataSource


def open_dataset(filename: str) -> DataSource:
    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(filename, 0)
    return dataset


def init_gdal(gdal_error_handler: Callable[[str, str, str], None]):
    """Initializes GDAL and registers Error handler function"""
    try:
        from osgeo import ogr, osr, gdal

        assert ogr  # silence pyflakes
        assert osr  # silence pyflakes
        assert gdal  # silence pyflakes
    except:
        sys.exit("ERROR: cannot find GDAL/OGR modules")

    # Enable GDAL/OGR exceptions
    gdal.UseExceptions()

    gdal.PushErrorHandler(gdal_error_handler)


def check_gdal_version():
    """This method checks if GDAL has the right version and exits with an error otherwise."""
    import sys
    from osgeo import gdal

    version_num = int(gdal.VersionInfo("VERSION_NUM"))
    if version_num < 1100000:
        sys.exit("ERROR: Python bindings of GDAL 1.10 or later required")


def check_gdal_installed():
    """This method checks if GDAL is properly installed and exits with an error otherwise."""
    try:
        from osgeo import ogr, osr, gdal

        assert ogr  # silence pyflakes
        assert osr  # silence pyflakes
        assert gdal  # silence pyflakes
    except ModuleNotFoundError:
        sys.exit(
            "ERROR: cannot find GDAL/OGR modules, follow the instructions in the README to install these."
        )
