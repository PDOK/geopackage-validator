from geopackage_validator.utils import Dataset
from geopackage_validator.validations.geometry_dimension_check import query_dimensions


def test_with_gpkg():
    expected = [
        ("test_dimensions", "more than two dimensions."),
        ("test_dimensions3", "more than two dimensions."),
        ("test_dimensions3", "an elevation (Z) dimension that are all 0."),
        ("test_dimensions4", "more than two dimensions."),
        ("test_dimensions4", "a measurement (M) dimension that are all 0."),
        ("test_dimensions4", "an elevation (Z) dimension that are all 0."),
        ("test_dimensions4_correct", "more than two dimensions."),
        ("test_dimensions3_correct", "more than two dimensions."),
    ]
    dataset = Dataset("tests/data/test_dimensions.gpkg")
    checks = list(query_dimensions(dataset))
    assert checks == expected


def test_with_gpkg_allcorrect():
    dataset = Dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_dimensions(dataset))
    assert len(checks) == 0
