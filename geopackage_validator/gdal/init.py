import sys
from typing import Callable


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
