from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geometry_empty_check import (
    EmptyGeometryValidator
)


def test_with_gpkg_empty():
    dataset = open_dataset("tests/data/test_geometry_empty.gpkg")
    result = list(EmptyGeometryValidator(dataset).check())
    assert len(result) == 1
    assert (
        result[0]
        == "Found empty geometry in table: stations, column geom, 45 times, example id 129"
    )


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    result = list(EmptyGeometryValidator(dataset).check())
    assert len(result) == 0
