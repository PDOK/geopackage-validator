from geopackage_validator.validations.layername_check import layername_check


def test_lowercaselayername_success():
    assert (
        len(layername_check(layername_list=["table", "lower_case", "is", "good"])) == 0
    )


def test_lowercaselayername_start_number():
    assert len(layername_check(layername_list=["1layer"])) == 1


def test_lowercaselayername_with_capitals():
    assert len(layername_check(layername_list=["layeRR", "layer", "layer"])) == 1
