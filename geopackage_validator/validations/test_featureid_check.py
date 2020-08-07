from geopackage_validator.validations.feature_id_check import feature_id_check


def test_valid_featureid():
    assert len(feature_id_check([("table", 1)])) == 0


def test_invalid_featureid():
    errors = feature_id_check([("table", 0)])
    assert len(errors) == 1
    assert errors[0]["errormessage"] == "Error found in table: table"
    assert errors[0]["errortype"] == "R7"
