from geopackage_validator.gdal_utils import open_dataset
from geopackage_validator.validations.geometry_valid_check import query_geometry_valid


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    checks = list(query_geometry_valid(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_valid"
    assert checks[0][1] == "geometry"
    assert checks[0][2] == "Self-intersection"
    assert checks[0][3] == 1
    assert checks[0][4] == 1


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_geometry_valid(dataset))
    assert len(checks) == 0
