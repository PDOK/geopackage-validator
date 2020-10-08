from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.columnname_check import (
    columnname_check,
    columnname_check_query,
)


def test_lowercasecolumnname_success():
    assert (
        len(
            columnname_check(
                columnname_list=[
                    ("table", "column"),
                    ("table", "lower_case"),
                    ("table", "is"),
                    ("table", "good"),
                ]
            )
        )
        == 0
    )


def test_lowercasecolumnname_start_number():
    results = columnname_check(columnname_list=[("table", "1column")])
    assert len(results) == 1
    assert results[0]["validation_code"] == "RQ6"
    assert results[0]["locations"][0] == "Error found in table: table, column: 1column"


def test_lowercasecolumnname_with_capitals():
    assert (
        len(
            columnname_check(
                columnname_list=[
                    ("table", "columnR"),
                    ("table", "column"),
                    ("table", "column"),
                ]
            )
        )
        == 1
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_columnname.gpkg")
    checks = list(columnname_check_query(dataset))
    assert len(checks) == 2
    assert checks[0][0] == "test_columnname"
    assert checks[0][1] == "fid"
    assert checks[1][0] == "test_columnname"
    assert checks[1][1] == "GEOmetry"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(columnname_check_query(dataset))
    assert len(checks) == 2
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == "fid"
    assert checks[1][0] == "test_allcorrect"
    assert checks[1][1] == "geometry"
