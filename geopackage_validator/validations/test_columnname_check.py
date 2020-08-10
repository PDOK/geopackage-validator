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
    errors = columnname_check(columnname_list=[("table", "1column")])
    assert len(errors) == 1
    assert (
        errors[0]["R6"]["errors"][0] == "Error found in table: table, column: 1column"
    )


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
    assert len(checks) == 1
    assert checks[0][0] == "test_columnname"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(columnname_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
