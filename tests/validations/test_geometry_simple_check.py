from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geometry_simple_check import query_geometry_simple


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_simple.gpkg")
    checks = list(query_geometry_simple(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_simple"
    assert checks[0][1] == "geometry"
    assert checks[0][2] == 1
    assert checks[0][3] == 1


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_geometry_simple(dataset))
    assert len(checks) == 0
