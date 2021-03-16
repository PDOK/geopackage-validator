from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geometry_ccw_check import query_ccw


def test_ccw_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    checks = list(query_ccw(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_valid"
    assert checks[0][1] == 1
    assert checks[0][2] == 1


def test_ccw_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_ccw(dataset))
    assert len(checks) == 0
