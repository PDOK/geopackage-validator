from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.feature_id_check import (
    FeatureIdValidator,
    query_feature_id,
)


def test_valid_featureid():
    assert len(FeatureIdValidator.check_feature_id([("table", 1)])) == 0


def test_invalid_featureid():
    results = FeatureIdValidator.check_feature_id([("table", 0)])
    assert len(results) == 1
    assert results[0] == "Error found in table: table"


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_featureid.gpkg")
    checks = list(query_feature_id(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_featureid"
    assert checks[0][1] == 0


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_feature_id(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == 1
