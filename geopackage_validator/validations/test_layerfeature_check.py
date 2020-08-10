from geopackage_validator.validations.layerfeature_check import layerfeature_check


def test_zerofeatures():
    assert len(layerfeature_check([("layer2", 1)])) == 0


def test_onefeature():
    errors = layerfeature_check([("layer1", 0), ("layer2", 1)])
    assert len(errors) == 1
    assert errors[0]["R2"]["errors"][0] == "Error layer: layer1"
