from geopackage_validator.utils import Dataset
from geopackage_validator.validations.columnname_check import (
    ColumnNameValidator,
    query_columnames,
)


def test_lowercasecolumnname_success():
    assert (
        len(
            ColumnNameValidator.check_columns(
                column_names=[
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
    results = ColumnNameValidator.check_columns(column_names=[("table", "1column")])
    assert len(results) == 1
    assert results[0] == "Error found in table: table, column: 1column"


def test_lowercasecolumnname_with_capitals():
    assert (
        len(
            ColumnNameValidator.check_columns(
                column_names=[
                    ("table", "columnR"),
                    ("table", "column"),
                    ("table", "column"),
                ]
            )
        )
        == 1
    )


def test_with_gpkg():
    dataset = Dataset("tests/data/test_columnname.gpkg")
    checks = list(query_columnames(dataset))
    assert len(checks) == 2
    assert checks[0][0] == "test_columnname"
    assert checks[0][1] == "fid"
    assert checks[1][0] == "test_columnname"
    assert checks[1][1] == "GEOmetry"


def test_with_gpkg_allcorrect():
    dataset = Dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_columnames(dataset))
    assert len(checks) == 2
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == "fid"
    assert checks[1][0] == "test_allcorrect"
    assert checks[1][1] == "geom"
