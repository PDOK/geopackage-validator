import json
import os
from typing import Dict, List

from deepdiff import DeepDiff

from geopackage_validator.generate import Column
from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def table_definitions_check(
    definitions_reference_path: str,
    definitions_current: Dict[str, Dict[str, List[Column]]],
):
    assert definitions_reference_path is not None
    assert definitions_current is not None
    assert os.path.exists(definitions_reference_path)

    with open(definitions_reference_path) as json_file:
        definitions_reference = json.load(json_file)

    results = []

    ddiff = DeepDiff(definitions_reference, definitions_current).pretty()

    for difference in ddiff.splitlines():
        results.append(
            create_validation_message(
                err_index="table_definition", difference=difference,
            )
        )

    return result_format("table_definition", results)
