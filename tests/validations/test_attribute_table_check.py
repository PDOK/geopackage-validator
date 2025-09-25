from geopackage_validator.utils import open_dataset
from geopackage_validator.validations import AttributeNoGeometryValidator


def test_rq_26_with_valid_table():
    dataset = open_dataset("tests/data/test_correct_attribute_with_many_to_many.gpkg")
    geom_colums = AttributeNoGeometryValidator(dataset).check()
    assert len(geom_colums) == 0


def test_rq_26_with_invalid_table():
    dataset = open_dataset("tests/data/test_incorrect_attribute_with_many_to_many.gpkg")
    geom_colums = AttributeNoGeometryValidator(dataset).check()
    assert len(geom_colums) == 1
