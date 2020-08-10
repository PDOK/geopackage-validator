from geopackage_validator.validations.geometry_valid_check import geometry_valid_check


def test_valid_geometries():
    assert len(geometry_valid_check([])) == 0


def test_invalid_geometry():
    errors = geometry_valid_check([("Geometry invalid", "table", "column")])
    assert len(errors) == 1
    assert (
        errors[0]["R5"]["errors"][0]
        == "Found invalid geometry in table: table, column column, reason: Geometry invalid"
    )
