from geopackage_validator.validations.geometry_type_check import geometry_type_check


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
        errors[0]["errormessage"]
        == "Error layer: layer2, found geometry: WRONG_GEOMETRY"
    )
    assert errors[0]["errortype"] == "R3"


def test_mixed_geometries():
    assert (
        len(geometry_type_check([("layer2", "WRONG_GEOMETRY"), ("layer3", "POINT")]))
        == 1
    )
