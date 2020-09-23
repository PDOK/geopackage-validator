from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.layerfeature_check import (
    layerfeature_check_featurecount,
    layerfeature_check_query,
    layerfeature_check_ogr_index,
)


def test_zerofeatures():
    assert len(layerfeature_check_featurecount([("layer2", 1, 1)])) == 0


def test_onefeature():
    errors = layerfeature_check_featurecount([("layer1", 0, 0), ("layer2", 1, 1)])
    assert len(errors) == 1
    assert errors[0]["RQ2"]["trace"][0] == "Error layer: layer1"


def test_featurecount_index_not_uptodate():
    errors = layerfeature_check_featurecount([("layer1", 1, 1), ("layer2", 1, 0)])
    assert len(errors) == 0


def test_featurecount_index_not_uptodate_ogr_error():
    errors = layerfeature_check_ogr_index([("layer1", 1, 1), ("layer2", 1, 0)])
    assert len(errors) == 1
    assert (
        errors[0]["RQ11"]["trace"][0]
        == "OGR index for feature count is not up to date for table: layer2. Indexed feature count: 0, real feature count: 1"
    )


def test_featurecount_index_not_uptodate_ogr_success():
    errors = layerfeature_check_ogr_index([("layer1", 1, 1), ("layer2", 1, 1)])
    assert len(errors) == 0


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_layerfeature.gpkg")
    checks = list(layerfeature_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_layerfeature"
    assert checks[0][1] == 0
    assert checks[0][2] == 0


def test_with_gpkg_falsenegative():
    dataset = open_dataset("tests/data/test_layerfeature_falsenegative.gpkg")
    checks = list(layerfeature_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_layerfeature_falsenegative"
    assert checks[0][1] == 1
    assert checks[0][2] == 0


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(layerfeature_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == 1
    assert checks[0][2] == 1
