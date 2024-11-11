from typing import Iterable, List, Dict, Set, Tuple

from geopackage_validator.generate import generate_table_definitions
from geopackage_validator.models import (
    Named,
    ColumnDefinition,
    TableDefinition,
    TablesDefinition,
)
from geopackage_validator.validations import validator


def prepare_comparison(
    new_: List[Named], old_: List[Named]
) -> Tuple[Dict[str, Named], Dict[str, Named], str, str, Set[str]]:
    new_dict = {item.name: item for item in new_}
    old_dict = {item.name: item for item in old_}
    missing = old_dict.keys() - new_dict.keys()
    added = new_dict.keys() - old_dict.keys()
    intersection = set(new_dict.keys()).intersection(set(old_dict.keys()))
    return new_dict, old_dict, ", ".join(missing), ", ".join(added), intersection


def compare_column_definitions(
    new_columns: List[ColumnDefinition],
    old_columns: List[ColumnDefinition],
    table_name: str,
) -> List[str]:
    assert old_columns, f"table {table_name} in table definition misses columns"
    new_dict, old_dict, missing, added, intersection = prepare_comparison(
        new_columns, old_columns
    )
    new_dict: Dict[str, ColumnDefinition]
    old_dict: Dict[str, ColumnDefinition]

    result = []
    if missing:
        result.append(f"table {table_name} misses column(s): {missing}")
    if added:
        result.append(f"table {table_name} has extra column(s): {added}")

    wrong_types = [
        f"table {table_name}, column {k} changed type {old_dict[k].type} to {new_dict[k].type}"
        for k in intersection
        if old_dict[k].type != new_dict[k].type
    ]

    return result + wrong_types


def compare_table_definitions(
    new_definition: TablesDefinition,
    old_definition: TablesDefinition,
    compare_columns=True,
) -> List[str]:
    results = []

    new_tables, old_tables, missing, added, intersection = prepare_comparison(
        new_definition.tables, old_definition.tables
    )

    if missing:
        results.append(f"missing table(s): {missing}")
    if added:
        results.append(f"extra table(s): {added}")

    new_projection = new_definition.projection
    old_projection = old_definition.projection
    if new_projection != old_projection:
        results.append(
            f"different projections: {new_projection} changed to {old_projection}"
        )

    new_tables: Dict[str, TableDefinition]
    old_tables: Dict[str, TableDefinition]
    for table_name in intersection:
        old_table = old_tables[table_name]
        new_table = new_tables[table_name]
        if old_table.geometry_column != new_table.geometry_column:
            results.append(
                f"{table_name} geometry_column changed from {old_table.geometry_column} to {new_table.geometry_column}"
            )
        if compare_columns:
            results += compare_column_definitions(
                new_table.columns, old_table.columns, table_name
            )

    return results


class TableDefinitionValidator(validator.Validator):
    """Geopackage must conform to given JSON definitions."""

    code = 8
    level = validator.ValidationLevel.ERROR

    def __init__(self, dataset, **kwargs):
        super().__init__(dataset)
        self.table_definitions = kwargs.get("table_definitions")

    def check(self) -> Iterable[str]:
        current_definitions = generate_table_definitions(self.dataset)
        return self.check_table_definitions(current_definitions)

    def check_table_definitions(self, definitions_current: TablesDefinition):
        assert definitions_current is not None

        if self.table_definitions is None:
            return ["Missing '--table-definitions-path' input"]

        return compare_table_definitions(definitions_current, self.table_definitions)


class TableDefinitionValidatorV0(validator.Validator):
    """LEGACY: use RQ8 * Geopackage must conform to table names in the given JSON definitions."""

    code = 0
    level = validator.ValidationLevel.ERROR

    def __init__(self, dataset, **kwargs):
        super().__init__(dataset)
        self.table_definitions = kwargs.get("table_definitions")

    def check(self) -> Iterable[str]:
        current_definitions = generate_table_definitions(self.dataset)
        return self.check_table_definitions(current_definitions)

    def check_table_definitions(self, definitions_current: TablesDefinition):
        assert definitions_current is not None

        if self.table_definitions is None:
            return ["Missing '--table-definitions-path' input"]

        return compare_table_definitions(
            definitions_current, self.table_definitions, compare_columns=False
        )
