from geopackage_validator.validations.layerfeature_check import layerfeature_check


def test_zerofeatures():
    assert len(layerfeature_check([("layer2", 1)])) == 0


def test_onefeature():
    assert len(layerfeature_check([("layer1", 0), ("layer2", 1)])) == 1
