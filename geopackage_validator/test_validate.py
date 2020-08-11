from geopackage_validator.validate import determine_validations_to_use


def test_determine_validations_to_use_param():
    validations = determine_validations_to_use(
        validations="R2,R3", validations_path=None
    )
    assert validations == ["R2", "R3"]


def test_determine_validations_to_use_param_spaces():
    validations = determine_validations_to_use(
        validations="R10, R3", validations_path=None
    )
    assert validations == ["R10", "R3"]


def test_determine_validations_to_use_none():
    validations = determine_validations_to_use(validations=None, validations_path=None)
    assert validations == [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "R8",
        "R9",
        "R10",
        "R11",
    ]


def test_determine_validations_to_use_file():
    validations = determine_validations_to_use(
        validations=None,
        validations_path="tests/validationsets/example-validation-set.json",
    )
    assert validations == ["R1", "R2", "R3"]


def test_determine_validations_to_use_file_and_param():
    validations = determine_validations_to_use(
        validations="R7,R9",
        validations_path="tests/validationsets/example-validation-set.json",
    )
    assert validations == ["R1", "R2", "R3", "R7", "R9"]
