from geopackage_validator.validations.layername_check import layername_check


def test_lowercaselayername_success():
    assert (
        len(layername_check(layername_list=["table", "lower_case", "is", "good"])) == 0
    )


def test_lowercaselayername_start_number():
    errors = layername_check(layername_list=["1layer"])
    assert len(errors) == 1
    assert errors[0]["errormessage"] == "Error layer: 1layer"
    assert errors[0]["errortype"] == "R1"


def test_lowercaselayername_with_capitals():
    assert len(layername_check(layername_list=["layeRR", "layer", "layer"])) == 1
