from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.layerfeature_check import (
    NonEmptyTableValidator,
    OGRIndexValidator,
    query_tablefeature_counts,
)


def test_zerofeatures():
    assert len(NonEmptyTableValidator.check_contains_features([("layer2", 1, 1)])) == 0


def test_onefeature():
    results = NonEmptyTableValidator.check_contains_features(
        [("layer1", 0, 0), ("layer2", 1, 1)]
    )
    assert len(results) == 1
    assert results[0] == "Error table: layer1"


def test_featurecount_index_not_uptodate():
    results = NonEmptyTableValidator.check_contains_features(
        [("layer1", 1, 1), ("layer2", 1, 0)]
    )
    assert len(results) == 0


def test_featurecount_index_not_uptodate_ogr_error():
    results = OGRIndexValidator.tablefeature_check_ogr_index(
        [("layer1", 1, 1), ("layer2", 1, 0)]
    )
    assert len(results) == 1
    assert (
        results[0]
        == "OGR index for feature count is not up to date for table: layer2. Indexed feature count: 0, real feature count: 1"
    )


def test_featurecount_index_not_uptodate_ogr_success():
    results = OGRIndexValidator.tablefeature_check_ogr_index(
        [("layer1", 1, 1), ("layer2", 1, 1)]
    )
    assert len(results) == 0


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_layerfeature.gpkg")
    checks = list(query_tablefeature_counts(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_layerfeature"
    assert checks[0][1] == 0
    assert checks[0][2] == 0


def test_with_gpkg_falsenegative():
    dataset = open_dataset("tests/data/test_layerfeature_falsenegative.gpkg")
    checks = list(query_tablefeature_counts(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_layerfeature_falsenegative"
    assert checks[0][1] == 1
    assert checks[0][2] == 0


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_tablefeature_counts(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == 1
    assert checks[0][2] == 1
