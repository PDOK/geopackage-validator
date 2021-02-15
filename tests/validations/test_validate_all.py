from geopackage_validator.validate import validations_to_use
from geopackage_validator.validations.validate_all import validate_all


def test_validate_all_no_validations():
    results = []
    validate_all("tests/data/test_allcorrect.gpkg", "", [], results=results)
    assert len(results) == 0


def test_validate_single_validation():
    results = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        requested_validations=["RQ1"],
        results=results,
    )
    assert len(results) == 1
    assert results[0]["locations"] == ["Error layer: test_LAYERNAME"]


def test_validate_single_validation_no_error():
    results = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        requested_validations=["RQ2"],
        results=results,
    )
    assert len(results) == 0


def test_validate_all_validations_no_error():
    results = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        requested_validations=validations_to_use(
            validations="ALL", validations_path=None
        ),
        results=results,
    )
    assert len(results) == 2
    assert results[0]["locations"] == ["Error layer: test_LAYERNAME"]
    assert results[1]["locations"] == [
        "Found in table: test_LAYERNAME, column: geometry"
    ]
