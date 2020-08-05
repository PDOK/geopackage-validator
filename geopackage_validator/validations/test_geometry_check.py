from geopackage_validator.validations.geometry_check import geometry_check


def test_valid_geometries():
    geometries = [
        ("layer1", "POINT"),
        ("layer2", "LINESTRING"),
        ("layer2", "POLYGON"),
        ("layer2", "MULTIPOINT"),
        ("layer2", "MULTILINESTRING"),
        ("layer2", "MULTIPOLYGON"),
    ]

    assert len(geometry_check(geometries)) == 0


def test_invalid_geometry():
    assert len(geometry_check([("layer2", "WRONG_GEOMETRY")])) == 1


def test_mixed_geometries():
    assert (
        len(geometry_check([("layer2", "WRONG_GEOMETRY"), ("layer3", "POINT"),])) == 1
    )
