import sys


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


def check_gdal_version():
    """This method checks if GDAL has the right version and exits with an error otherwise."""
    import sys
    from osgeo import gdal

    version_num = int(gdal.VersionInfo("VERSION_NUM"))
    if version_num < 1100000:
        sys.exit("ERROR: Python bindings of GDAL 1.10 or later required")
