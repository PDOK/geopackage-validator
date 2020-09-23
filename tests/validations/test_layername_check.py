from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.layername_check import (
    layername_check,
    layername_check_query,
)


def test_lowercaselayername_success():
    assert (
        len(layername_check(layername_list=["table", "lower_case", "is", "good"])) == 0
    )


def test_lowercaselayername_start_number():
    errors = layername_check(layername_list=["1layer"])
    assert len(errors) == 1
    assert errors[0]["RQ1"]["trace"][0] == "Error layer: 1layer"


def test_lowercaselayername_with_capitals():
    assert len(layername_check(layername_list=["layeRR", "layer", "layer"])) == 1


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_layername.gpkg")
    checks = list(layername_check_query(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_LAYERNAME"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(layername_check_query(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_allcorrect"
