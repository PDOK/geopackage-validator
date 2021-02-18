import json
from pathlib import Path
from typing import Dict, List, Iterable

from deepdiff import DeepDiff

from geopackage_validator.generate import TableDefinition
from geopackage_validator.validations import validator
from geopackage_validator.generate import generate_table_definitions


class TableDefinitionValidator(validator.Validator):
    """Geopackage must conform to given JSON definitions."""

    code = 8
    level = validator.ValidationLevel.ERROR
    message = "Difference: {difference}"

    def __init__(self, dataset, **kwargs):
        super().__init__(dataset)
        self.table_definitions = kwargs.get("table_definitions")

    def check(self) -> Iterable[str]:
        current_definitions = generate_table_definitions(self.dataset)
        return self.check_table_definitions(current_definitions)

    def check_table_definitions(self, definitions_current: TableDefinition):
        assert definitions_current is not None

        if self.table_definitions is None:
            return [
                self.message.format(
                    difference="Missing '--table-definitions-path' input"
                )
            ]

        deep_diff = DeepDiff(self.table_definitions, definitions_current).pretty()
        return [
            self.message.format(difference=difference)
            for difference in deep_diff.splitlines()
        ]
