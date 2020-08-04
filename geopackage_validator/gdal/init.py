import sys


def init_gdal():
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

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, err_msg):
        errtype = {
            gdal.CE_None: "None",
            gdal.CE_Debug: "Debug",
            gdal.CE_Warning: "Warning",
            gdal.CE_Failure: "Failure",
            gdal.CE_Fatal: "Fatal",
        }
        err_msg = err_msg.replace("\n", " ")
        err_class = errtype.get(err_class, "None")
        print("Error Number: %s" % err_num)
        print("Error Type: %s" % err_class)
        print("Error Message: %s" % err_msg)

    gdal.PushErrorHandler(gdal_error_handler)
