from osgeo import gdal

from geopackage_validator.utils import (
    open_dataset,
    dataset_geometry_tables,
)


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geom_columnname.gpkg")
    checks = list(dataset_geometry_tables(dataset))
    assert len(checks) == 3
    assert checks[0][0] == "test_columnname"
    assert checks[0][1] == "geom"
    assert checks[1][0] == "test_columnname2"
    assert checks[1][1] == "geometry"
    assert checks[2][0] == "test_columnname3"
    assert checks[2][1] == "geometry"


def test_with_gdal_error():
    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        results.append("GDAL_ERROR")

    dataset = open_dataset("tests/data/test_gdal_error.gpkg", gdal_error_handler)

    # Since GDAL 3.7 the exceptions work more pythonic
    try:
        validations = dataset.ExecuteSQL('select rtreecheck("rtree_table_geom");')
        dataset.ReleaseResultSet(validations)
    except RuntimeError as e:
        results.append("GDAL_TRY_ERROR")

    assert results[0] == "GDAL_ERROR" or results[0] == "GDAL_TRY_ERROR"
    assert len(results) == 1


def test_without_gdal_error():
    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        results.append("GDAL_ERROR")

    dataset = open_dataset("tests/data/test_gdal_error.gpkg", gdal_error_handler)
    with dataset.silence_gdal():
        validations = dataset.ExecuteSQL(
            'select rtreecheck("rtree_cbs_arbeidsmarktregio_2014_gegeneraliseerd_geom_parent");'
        )
    dataset.ReleaseResultSet(validations)
    assert len(results) == 0


def do_something_with_error_gdal(dataset):
    gdal.Error(gdal.CE_Warning, 9999, "test warning message")


def do_something_silenced_gdal(dataset):
    with dataset.silence_gdal():
        gdal.Error(gdal.CE_Warning, 9999, "test warning message")


def test_silence_between_gdal_errors():
    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        print(results)
        results.append("GDAL_ERROR")

    dataset = open_dataset("tests/data/test_gdal_error.gpkg", gdal_error_handler)

    do_something_with_error_gdal(dataset)
    do_something_silenced_gdal(dataset)
    do_something_with_error_gdal(dataset)

    assert len(results) == 2
    assert results == ["GDAL_ERROR", "GDAL_ERROR"]
