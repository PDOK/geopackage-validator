import json

from deepdiff import DeepDiff

from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
)


def table_definitions_check(definitions_reference_path=None, definitions_current=None):
    assert definitions_reference_path is not None
    assert definitions_current is not None

    definitions_reference = {}
    with open(definitions_reference_path) as json_file:
        definitions_reference = json.load(json_file)

    errors = []

    ddiff = DeepDiff(definitions_reference, definitions_current).pretty()

    for difference in ddiff.splitlines():
        errors.append(
            create_errormessage(err_index="table_definition", difference=difference,)
        )

    return errors
