from geopackage_validator.utils import Dataset
from geopackage_validator.validations.layername_check import (
    LayerNameValidator,
    query_layernames,
)


def test_lowercaselayername_success():
    assert (
        len(
            LayerNameValidator.check_layernames(
                layernames=["table", "lower_case", "is", "good"]
            )
        )
        == 0
    )


def test_lowercaselayername_start_number():
    results = LayerNameValidator.check_layernames(layernames=["1layer"])
    assert len(results) == 1
    assert results[0] == "Error layer: 1layer"


def test_lowercaselayername_with_capitals():
    assert (
        len(
            LayerNameValidator.check_layernames(layernames=["layeRR", "layer", "layer"])
        )
        == 1
    )


def test_with_gpkg():
    dataset = Dataset("tests/data/test_layername.gpkg")
    checks = list(query_layernames(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_LAYERNAME"


def test_with_gpkg_allcorrect():
    dataset = Dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_layernames(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_allcorrect"
