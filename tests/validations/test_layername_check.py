from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.layername_check import (
    TableNameValidator,
    query_tablenames,
)


def test_lowercasetablename_success():
    assert (
        len(
            TableNameValidator.check_tablenames(
                tablenames=["table", "lower_case", "is", "good"]
            )
        )
        == 0
    )


def test_lowercasetablename_start_number():
    results = TableNameValidator.check_tablenames(tablenames=["1layer"])
    assert len(results) == 1
    assert results[0] == "Error table: 1layer"


def test_lowercasetablename_with_capitals():
    assert (
        len(
            TableNameValidator.check_tablenames(tablenames=["layeRR", "layer", "layer"])
        )
        == 1
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_layername.gpkg")
    checks = list(query_tablenames(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_LAYERNAME"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_tablenames(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_allcorrect"
