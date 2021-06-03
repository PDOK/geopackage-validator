from geopackage_validator.utils import open_dataset, init_gdal, silence_gdal
from geopackage_validator.validations.rtree_valid_check import (
    ValidRtreeValidator,
    rtree_valid_check_query,
)


def test_rtree_valid_all_tables():
    assert len(ValidRtreeValidator.check_rtree_is_valid(rtree_index_list=[])) == 0


def test_rtree_invalidvalid_one_tables():
    results = ValidRtreeValidator.check_rtree_is_valid(rtree_index_list=["tablename"])
    assert len(results) == 1
    assert results[0] == "Invalid rtree index found for table: tablename"


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_rtree_valid.gpkg")
    checks = list(rtree_valid_check_query(dataset))
    assert len(checks) == 1
    assert checks[0] == "Found (1 -> 2) in %_rowid table, expected (1 -> 1)"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(rtree_valid_check_query(dataset))
    assert len(checks) == 0


def test_with_gdal_error():
    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        results.append("GDAL_ERROR")

    init_gdal(gdal_error_handler)

    dataset = open_dataset("tests/data/test_gdal_error.gpkg")
    validations = dataset.ExecuteSQL('select rtreecheck("rtree_table_geom");')
    dataset.ReleaseResultSet(validations)
    assert results[0] == "GDAL_ERROR"
    assert len(results) == 1


def test_without_gdal_error():
    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        results.append("GDAL_ERROR")

    init_gdal(gdal_error_handler)

    dataset = open_dataset("tests/data/test_gdal_error.gpkg")
    with silence_gdal():
        validations = dataset.ExecuteSQL('select rtreecheck("rtree_table_geom");')
    dataset.ReleaseResultSet(validations)
    assert len(results) == 0


def do_something_with_error_gdal(dataset):
    validations = dataset.ExecuteSQL('select rtreecheck("rtree_table_geom");')
    dataset.ReleaseResultSet(validations)


def do_something_silenced_gdal(dataset):
    with silence_gdal():
        validations = dataset.ExecuteSQL('select rtreecheck("rtree_table_geom");')
    dataset.ReleaseResultSet(validations)


def test_silence_between_gdal_errors():
    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        results.append("GDAL_ERROR")

    init_gdal(gdal_error_handler)

    dataset = open_dataset("tests/data/test_gdal_error.gpkg")
    do_something_with_error_gdal(dataset)
    do_something_silenced_gdal(dataset)
    do_something_with_error_gdal(dataset)

    assert len(results) == 2
    assert results == ["GDAL_ERROR", "GDAL_ERROR"]
