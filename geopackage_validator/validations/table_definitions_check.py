import json
import os
from typing import Dict, List, Iterable

from deepdiff import DeepDiff

from geopackage_validator.generate import Column
from geopackage_validator.validations import validator
from geopackage_validator.generate import generate_table_definitions


def get_definition_from_file(definitions_reference_path):
    with open(definitions_reference_path) as json_file:
        definitions_reference = json.load(json_file)
        return definitions_reference


class TableDefinitionValidator(validator.Validator):
    """Geopackage must conform to given JSON definitions."""

    code = 8
    level = validator.ValidationLevel.ERROR
    message = "Difference: {difference}"

    def check(self) -> Iterable[str]:
        current_definitions = generate_table_definitions(self.dataset)
        return self.check_table_definitions(current_definitions)

    def check_table_definitions(
        self, definitions_current: Dict[str, Dict[str, List[Column]]]
    ):
        assert definitions_current is not None
        deep_diff = DeepDiff(
            get_definition_from_file(self.table_definitions), definitions_current
        ).pretty()
        return [
            self.message.format(difference=difference)
            for difference in deep_diff.splitlines()
        ]
