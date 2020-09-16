from geopackage_validator.validate import determine_validations_to_use


def test_determine_validations_to_use_param():
    validations = determine_validations_to_use(
        validations="RQ2,RQ3", validations_path=None
    )
    assert validations == ["RQ2", "RQ3"]


def test_determine_validations_to_use_param_spaces():
    validations = determine_validations_to_use(
        validations="RQ10, RQ3", validations_path=None
    )
    assert validations == ["RQ10", "RQ3"]


def test_determine_validations_to_use_none():
    validations = determine_validations_to_use(validations=None, validations_path=None)
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
        "RC1",
        "RC2",
    ]


def test_determine_validations_to_use_file():
    validations = determine_validations_to_use(
        validations=None,
        validations_path="tests/data/validationsets/example-validation-set.json",
    )
    assert validations == ["RQ1", "RQ2", "RQ3"]


def test_determine_validations_to_use_file_and_param():
    validations = determine_validations_to_use(
        validations="RQ7,RQ9",
        validations_path="tests/data/validationsets/example-validation-set.json",
    )
    assert validations == ["RQ1", "RQ2", "RQ3", "RQ7", "RQ9"]
