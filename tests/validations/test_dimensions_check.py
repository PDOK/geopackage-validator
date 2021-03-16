from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geometry_dimension_check import query_dimensions


def test_with_gpkg():
    # test_dimensions.gpkg has 4 tables,
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
    dataset = open_dataset("tests/data/test_dimensions.gpkg")
    checks = list(query_dimensions(dataset))
    assert checks == expected


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_dimensions(dataset))
    assert len(checks) == 0
