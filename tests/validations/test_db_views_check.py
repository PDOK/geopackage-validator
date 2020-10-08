from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.db_views_check import (
    db_views_check,
    db_views_check_query,
)


def test_zeroviews():
    assert len(db_views_check([])) == 0


def test_oneview():
    results = db_views_check(["view1"])
    assert len(results) == 1
    assert results[0]["validation_code"] == "RQ4"
    assert results[0]["locations"][0] == "Found view: view1"


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_db_views.gpkg")
    checks = list(db_views_check_query(dataset))
    assert len(checks) == 1
    assert checks[0] == "wrong_view"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(db_views_check_query(dataset))
    assert len(checks) == 0
