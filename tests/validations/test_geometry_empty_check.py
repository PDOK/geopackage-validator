from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.geometry_empty_check import (
    query_geometry_empty,
    SQL_EMPTY_TEMPLATE,
)


def test_with_gpkg_empty():
    dataset = open_dataset('tests/data/test_geometry_empty.gpkg')
    checks = list(query_geometry_empty(dataset, SQL_EMPTY_TEMPLATE))
    assert len(checks) == 1
    assert checks[0][0] == 'stations'
    assert checks[0][1] == 'geom'
    assert checks[0][2] == 45
    assert checks[0][3] == 129


def test_with_gpkg_allcorrect():
    dataset = open_dataset('tests/data/test_allcorrect.gpkg')
    checks = list(query_geometry_empty(dataset, SQL_EMPTY_TEMPLATE))
    assert len(checks) == 1
    assert checks[0][0] == 'test_allcorrect'
    assert checks[0][1] == 'geom'
    assert checks[0][2] == 0
    assert checks[0][3] is None
