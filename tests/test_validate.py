from geopackage_validator.validate import validators_to_use, get_validation_codes


def test_determine_validations_to_use_param():
    validations = get_validation_codes(
        validators_to_use(validation_codes="RQ2,RQ3", validations_path="")
    )
    assert validations == ["RQ2", "RQ3"]


def test_determine_validations_to_use_param_spaces():
    validations = get_validation_codes(
        validators_to_use(validation_codes="RQ10, RQ3", validations_path="")
    )
    assert validations == ["RQ10", "RQ3"]


def test_determine_validations_to_use_none():
    validations = get_validation_codes(
        validators_to_use(validation_codes="", validations_path="")
    )
    assert validations == [
        "RQ1",
        "RQ2",
        "RQ3",
        "RQ4",
        "RQ5",
        "RQ6",
        "RQ7",
        "RQ8",
        "RQ9",
        "RQ10",
        "RQ11",
        "RQ12",
        "RQ13",
        "RQ14",
        "RQ15",
        "RC1",
        "RC2",
    ]


def test_determine_validations_to_use_file():
    validations = get_validation_codes(
        validators_to_use(
            validation_codes="",
            validations_path="tests/data/validationsets/example-validation-set.json",
        )
    )
    assert validations == ["RQ1", "RQ2", "RQ3"]


def test_determine_validations_to_use_file_and_param():
    validations = get_validation_codes(
        validators_to_use(
            validation_codes="RQ7,RQ9",
            validations_path="tests/data/validationsets/example-validation-set.json",
        )
    )
    assert validations == ["RQ1", "RQ2", "RQ3", "RQ7", "RQ9"]
