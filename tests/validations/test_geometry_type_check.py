from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.geometry_type_check import (
    geometry_type_check,
    geometry_type_check_query,
)


def test_valid_geometries():
    geometries = [
        ("layer1", "POINT"),
        ("layer2", "LINESTRING"),
        ("layer2", "POLYGON"),
        ("layer2", "MULTIPOINT"),
        ("layer2", "MULTILINESTRING"),
        ("layer2", "MULTIPOLYGON"),
    ]

    assert len(geometry_type_check(geometries)) == 0


def test_invalid_geometry():
    errors = geometry_type_check([("layer2", "WRONG_GEOMETRY")])
    assert len(errors) == 1
    assert (
        errors[0]["RQ3"]["trace"][0]
        == "Error layer: layer2, found geometry: WRONG_GEOMETRY"
    )


def test_mixed_geometries():
    assert (
        len(geometry_type_check([("layer2", "WRONG_GEOMETRY"), ("layer3", "POINT")]))
        == 1
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_type.gpkg")
    checks = list(geometry_type_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_type"
    assert checks[0][1] == "COMPOUNDCURVE"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(geometry_type_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == "POLYGON"
