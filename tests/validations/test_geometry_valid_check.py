from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.geometry_valid_check import (
    geometry_valid_check,
    geometry_valid_check_query,
)


def test_valid_geometries():
    assert len(geometry_valid_check([])) == 0


def test_invalid_geometry():
    errors = geometry_valid_check([("Geometry invalid", "table", "column")])
    assert len(errors) == 1
    assert (
        errors[0]["RQ5"]["trace"][0]
        == "Found invalid geometry in table: table, column column, reason: Geometry invalid"
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    checks = list(geometry_valid_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "Self-intersection[1.00524682835986 -0.175021628271762]"
    assert checks[0][1] == "test_geometry_valid"
    assert checks[0][2] == "geometry"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(geometry_valid_check_query(dataset))
    assert len(checks) == 0
