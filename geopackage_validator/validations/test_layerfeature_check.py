from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.layerfeature_check import (
    layerfeature_check,
    layerfeature_check_query,
)


def test_zerofeatures():
    assert len(layerfeature_check([("layer2", 1)])) == 0


def test_onefeature():
    errors = layerfeature_check([("layer1", 0), ("layer2", 1)])
    assert len(errors) == 1
    assert errors[0]["R2"]["errors"][0] == "Error layer: layer1"


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_layerfeature.gpkg")
    checks = list(layerfeature_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_layerfeature"
    assert checks[0][1] == 0


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(layerfeature_check_query(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_allcorrect"
    assert checks[0][1] == 1
