from geopackage_validator.gdal_utils import open_dataset
from geopackage_validator.validations.geometry_valid_check import (
    ValidGeometryValidator,
    geometry_valid_check_query,
)


def test_aggregate_valid_geometries():
    assert len(ValidGeometryValidator.aggregate([])) == 0


def test_aggregate_invalid_geometry():
    results = ValidGeometryValidator.aggregate(
        [
            ("error1", "table_a", "column", 1),
            ("error1", "table_a", "column", 2),
            ("error1", "table_b", "column", 1),
            ("error2", "table_b", "column", 2),
        ]
    )

    assert len(results) == 3

    keys = list(results.keys())

    assert results[keys[0]]["table"] == "table_a"
    assert results[keys[0]]["column"] == "column"
    assert results[keys[0]]["reason"] == "error1"
    assert len(results[keys[0]]["rowid_list"]) == 2

    assert results[keys[1]]["table"] == "table_b"
    assert results[keys[1]]["column"] == "column"
    assert results[keys[1]]["reason"] == "error1"
    assert len(results[keys[1]]["rowid_list"]) == 1

    assert results[keys[2]]["table"] == "table_b"
    assert results[keys[2]]["column"] == "column"
    assert results[keys[2]]["reason"] == "error2"
    assert len(results[keys[2]]["rowid_list"]) == 1


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    checks = list(geometry_valid_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "Self-intersection[1.00524682835986 -0.175021628271762]"
    assert checks[0][1] == "test_geometry_valid"
    assert checks[0][2] == "geometry"
    assert checks[0][3] == 1


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(geometry_valid_check_query(dataset))
    assert len(checks) == 0


def test_rq5_with_gpkg_valid():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    result = list(ValidGeometryValidator(dataset).check())
    assert len(result) == 0


def test_rq5_with_gpkg_invalid():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    result = list(ValidGeometryValidator(dataset).check())
    assert len(result) == 1
    assert (
        result[0]
        == "Found invalid geometry in table: test_geometry_valid, column geometry, reason: Self-intersection, 1 time, example record id: [1]"
    )
