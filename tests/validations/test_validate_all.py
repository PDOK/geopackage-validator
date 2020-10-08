from geopackage_validator.validate import determine_validations_to_use
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
        validations=["RQ1"],
        results=results,
    )
    assert len(results) == 1
    assert results[0]["locations"] == ["Error layer: test_LAYERNAME"]


def test_validate_single_validation_no_error():
    results = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        validations=["RQ2"],
        results=results,
    )
    assert len(results) == 0


def test_validate_all_validations_no_error():
    results = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        validations=determine_validations_to_use(
            validations="ALL", validations_path=None
        ),
        results=results,
    )
    assert len(results) == 1
    assert results[0]["locations"] == ["Error layer: test_LAYERNAME"]
