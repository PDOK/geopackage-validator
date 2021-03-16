from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geom_column_check import (
    GeomColumnNameValidator,
    GeomColumnNameEqualValidator,
)


def test_geom_name_success():
    assert (
        len(
            GeomColumnNameValidator.geom_columnname_check(
                columns=[
                    ("table1", "geom", "POINT"),
                    ("table2", "geom", "POINT"),
                    ("table3", "geom", "POINT"),
                    ("table4", "geom", "POINT"),
                ]
            )
        )
        == 0
    )


def test_geom_name_failure():
    result = GeomColumnNameValidator.geom_columnname_check(
        columns=[
            ("table1", "geom", "POINT"),
            ("table2", "geom2", "POINT"),
            ("table3", "geom", "POINT"),
            ("table4", "geom3", "POINT"),
        ]
    )

    assert len(result) == 2


def test_equal_name_success():
    assert (
        len(
            GeomColumnNameEqualValidator.geom_equal_columnname_check(
                columns=[
                    ("table1", "geometry", "POINT"),
                    ("table2", "geometry", "POINT"),
                    ("table3", "geometry", "POINT"),
                    ("table4", "geometry", "POINT"),
                ]
            )
        )
        == 0
    )


def test_equal_name_failure():
    assert (
        len(
            GeomColumnNameEqualValidator.geom_equal_columnname_check(
                columns=[
                    ("table1", "geometry", "POINT"),
                    ("table2", "geom", "POINT"),
                    ("table3", "geometry", "POINT"),
                    ("table4", "geometry", "POINT"),
                ]
            )
        )
        > 0
    )
