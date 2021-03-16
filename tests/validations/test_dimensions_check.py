from geopackage_validator.gdal_utils import open_dataset
from geopackage_validator.validations.geometry_dimension_check import query_dimensions


def test_with_gpkg():
    # test_dimensions.gpkg has 4 tables,
    expected = [
        ("test_dimensions3", "elevation (Z)"),
        ("test_dimensions4", "measurement (M)"),
        ("test_dimensions4", "elevation (Z)"),
    ]
    dataset = open_dataset("tests/data/test_dimensions.gpkg")
    checks = list(query_dimensions(dataset))
    assert checks == expected


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_dimensions(dataset))
    assert len(checks) == 0
