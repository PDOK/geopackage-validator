from geopackage_validator.validate import determine_validations_to_use
from geopackage_validator.validations.validate_all import validate_all


def test_validate_all_no_validations():
    errors = []
    validate_all("tests/data/test_allcorrect.gpkg", "", [], errors=errors)
    assert len(errors) == 0


def test_validate_single_validation():
    errors = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        validations=["RQ1"],
        errors=errors,
    )
    assert len(errors) == 1
    assert errors[0]["RQ1"]["trace"] == ["Error layer: test_LAYERNAME"]


def test_validate_single_validation_no_error():
    errors = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        validations=["RQ2"],
        errors=errors,
    )
    assert len(errors) == 0


def test_validate_all_validations_no_error():
    errors = []
    validate_all(
        "tests/data/test_layername.gpkg",
        table_definitions_path="",
        validations=determine_validations_to_use(
            validations="ALL", validations_path=None
        ),
        errors=errors,
    )
    assert len(errors) == 1
    assert errors[0]["RQ1"]["trace"] == ["Error layer: test_LAYERNAME"]
