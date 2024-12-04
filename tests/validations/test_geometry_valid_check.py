from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geometry_valid_check import (
    query_geometry_valid,
    SQL_ONLY_VALID_TEMPLATE,
    SQL_VALID_TEMPLATE,
)


def test_with_gpkg_valid():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    checks = list(query_geometry_valid(dataset, SQL_ONLY_VALID_TEMPLATE))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_valid"
    assert checks[0][1] == "geometry"
    assert checks[0][2] == "Self-intersection"
    assert checks[0][3] == 1
    assert checks[0][4] == 1


def test_with_gpkg_simple():
    dataset = open_dataset("tests/data/test_geometry_simple.gpkg")
    checks = list(query_geometry_valid(dataset, SQL_VALID_TEMPLATE))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_simple"
    assert checks[0][1] == "geometry"
    assert checks[0][2] == "Not Simple"
    assert checks[0][3] == 1
    assert checks[0][4] == 1


def test_with_gpkg_valid_simple():
    dataset = open_dataset("tests/data/test_geometry_valid.gpkg")
    checks = list(query_geometry_valid(dataset, SQL_VALID_TEMPLATE))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_valid"
    assert checks[0][1] == "geometry"
    assert checks[0][2] == "Self-intersection"
    assert checks[0][3] == 1
    # assert checks[0][4] == 1


def test_with_gpkg_empty():
    # geometries that are empty are still considered valid
    dataset = open_dataset("tests/data/test_geometry_empty.gpkg")
    checks = list(query_geometry_valid(dataset, SQL_VALID_TEMPLATE))
    assert len(checks) == 0


def test_with_gpkg_null():
    # geometries that are null slip through
    dataset = open_dataset("tests/data/test_geometry_null.gpkg")
    checks = list(query_geometry_valid(dataset, SQL_VALID_TEMPLATE))
    assert len(checks) == 0


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_geometry_valid(dataset, SQL_VALID_TEMPLATE))
    assert len(checks) == 0
