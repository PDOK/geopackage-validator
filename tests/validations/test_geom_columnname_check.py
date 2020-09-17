from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.geom_column_check import (
    geom_columnname_check_query,
    geom_columnname_check,
    geom_equal_columnname_check,
)


def test_geom_name_success():
    assert (
        len(
            geom_columnname_check(
                column_info_list=[
                    ("table1", "geom"),
                    ("table2", "geom"),
                    ("table3", "geom"),
                    ("table4", "geom"),
                ]
            )
        )
        == 0
    )


def test_geom_name_failure():
    result = geom_columnname_check(
        column_info_list=[
            ("table1", "geom"),
            ("table2", "geom2"),
            ("table3", "geom"),
            ("table4", "geom3"),
        ]
    )

    assert len(result) == 1
    assert len(result[0]["RC1"]["trace"]) == 2


def test_equal_name_success():
    assert (
        len(
            geom_equal_columnname_check(
                column_info_list=[
                    ("table1", "geometry"),
                    ("table2", "geometry"),
                    ("table3", "geometry"),
                    ("table4", "geometry"),
                ]
            )
        )
        == 0
    )


def test_equal_name_failure():
    assert (
        len(
            geom_equal_columnname_check(
                column_info_list=[
                    ("table1", "geometry"),
                    ("table2", "geom"),
                    ("table3", "geometry"),
                    ("table4", "geometry"),
                ]
            )
        )
        > 0
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geom_columnname.gpkg")
    checks = list(geom_columnname_check_query(dataset))
    assert len(checks) == 3
    assert checks[0][0] == "test_columnname"
    assert checks[0][1] == "geom"
    assert checks[1][0] == "test_columnname2"
    assert checks[1][1] == "geometry"
    assert checks[2][0] == "test_columnname3"
    assert checks[2][1] == "geometry"
