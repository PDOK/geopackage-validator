from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.feature_id_check import (
    feature_id_check,
    feature_id_check_query,
)


def test_valid_featureid():
    assert len(feature_id_check([("table", 1)])) == 0


def test_invalid_featureid():
    results = feature_id_check([("table", 0)])
    assert len(results) == 1
    assert results[0]["validation_code"] == "RQ7"
    assert results[0]["locations"][0] == "Error found in table: table"


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_featureid.gpkg")
    checks = list(feature_id_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_featureid"
    assert checks[0][1] == 0


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(feature_id_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == 1
