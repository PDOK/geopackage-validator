from typing import Iterable

from geopackage_validator.generate import TableDefinition
from geopackage_validator.validations import validator
from geopackage_validator.generate import generate_table_definitions


def prepare_comparison(new_, old_):
    new_dict = {item["name"]: item for item in new_}
    old_dict = {item["name"]: item for item in old_}
    missing = old_dict.keys() - new_dict.keys()
    added = new_dict.keys() - old_dict.keys()
    intersection = set(new_dict.keys()).intersection(set(old_dict.keys()))
    return new_dict, old_dict, ", ".join(missing), ", ".join(added), intersection


def compare_column_definitions(new_columns, old_columns, table_name):
    assert (
        old_columns is not None
    ), f"table {table_name} in table definition misses columns"
    new_dict, old_dict, missing, added, intersection = prepare_comparison(
        new_columns, old_columns
    )

    result = []
    if missing:
        result.append(f"table {table_name} misses column(s): {missing}")
    if added:
        result.append(f"table {table_name} has extra column(s): {added}")

    wrong_types = [
        f"table {table_name}, column {k} changed type {old_dict[k]['data_type']} to {new_dict[k]['data_type']}"
        for k in intersection
        if old_dict[k]["data_type"] != new_dict[k]["data_type"]
    ]

    return result + wrong_types


def compare_table_definitions(new_definition, old_definition):
    results = []

    new_tables, old_tables, missing, added, intersection = prepare_comparison(
        new_definition["tables"], old_definition["tables"]
    )

    if missing:
        results.append(f"missing table(s): {missing}")
    if added:
        results.append(f"extra table(s): {added}")

    new_projection = new_definition["projection"]
    old_projection = old_definition.get("projection")
    if new_projection != old_projection:
        results.append(
            f"different projections: {new_projection} changed to {old_projection}"
        )

    for table_name in intersection:
        old_table = old_tables[table_name]
        new_table = new_tables[table_name]
        old_geometry = old_table.get("geometry_column")
        new_geometry = old_table.get("geometry_column")
        if old_geometry != new_geometry:
            results.append(
                f"{table_name} geometry_column changed from {old_geometry} to {new_geometry}"
            )
        results += compare_column_definitions(
            new_table["columns"], old_table.get("columns"), table_name
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

    def check_table_definitions(self, definitions_current: TableDefinition):
        assert definitions_current is not None

        if self.table_definitions is None:
            return ["Missing '--table-definitions-path' input"]

        return compare_table_definitions(definitions_current, self.table_definitions)
