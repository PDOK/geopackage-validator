from typing import Iterable, List, Dict, Set, Tuple

from osgeo.ogr import DataSource
from pydantic import BaseModel

from geopackage_validator.generate import generate_table_definitions
from geopackage_validator.models import (
    Named,
    ColumnDefinition,
    TableDefinition,
    TablesDefinition,
)
from geopackage_validator.validations import validator


def prepare_comparison(
    new_: Iterable[Named], old_: Iterable[Named]
) -> Tuple[Dict[str, Named], Dict[str, Named], str, str, Set[str]]:
    new_dict = {item.name: item for item in new_}
    old_dict = {item.name: item for item in old_}
    missing = old_dict.keys() - new_dict.keys()
    added = new_dict.keys() - old_dict.keys()
    intersection = set(new_dict.keys()).intersection(set(old_dict.keys()))
    return new_dict, old_dict, ", ".join(missing), ", ".join(added), intersection


def compare_column_definitions(
    new_columns: Iterable[ColumnDefinition],
    old_columns: Iterable[ColumnDefinition],
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


def compare_object_lists(
    current: Iterable[object],
    expected: Iterable[object],
    table_name: str,
) -> List[str]:
    messages: List[str] = []
    added = set(current)
    for o in expected:
        if o in added:
            added.remove(o)
        else:
            messages.append(
                f"table {table_name} misses {o.__class__.__name__}: {o_repr_oneline(o)}"
            )
    for o in added:
        messages.append(
            f"table {table_name} has extra {o.__class__.__name__}: {o_repr_oneline(o)}"
        )
    return messages


def o_repr_oneline(o: object) -> str:
    r = repr(o) if not isinstance(o, BaseModel) else o.model_dump_json(indent=0)
    return r.replace("\n", " ")


def compare_table_definitions(
    new_definition: TablesDefinition,
    old_definition: TablesDefinition,
    compare_columns=True,
    compare_indexes_and_fks=True,
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
            f"different projections: {old_projection} changed to {new_projection}"
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
        if compare_indexes_and_fks:
            if old_table.indexes is None:
                results.append(
                    f"index checking is enabled but {table_name} misses the list"
                )
            else:
                results += compare_object_lists(
                    new_table.indexes, old_table.indexes, table_name
                )
            if old_table.foreign_keys is None:
                results.append(
                    f"foreign keys checking is enabled but {table_name} misses the list"
                )
            else:
                results += compare_object_lists(
                    new_table.foreign_keys, old_table.foreign_keys, table_name
                )

    return results


def get_foreign_key_violations(datasource: DataSource) -> List[str]:
    # This used to be a per-table operation. But it's not due to
    # a bug in sqlite: https://sqlite.org/forum/info/30cd7db3d0b2f12e
    # used in github ubuntu 20-04:
    #   https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2004-Readme.md#installed-apt-packages
    messages: List[str] = []
    foreign_key_violations = datasource.ExecuteSQL(
        f'select "table", rowid, parent, fkid from pragma_foreign_key_check();'
    )
    for v in foreign_key_violations:
        messages.append(
            f"foreign key violation in {v['table']} for fk {v['fkid']} to {v['parent']} on row {v['rowid']}"
        )
    return messages


class TableDefinitionValidator(validator.Validator):
    """Geopackage must conform to given JSON definitions."""

    code = 8
    level = validator.ValidationLevel.ERROR

    def __init__(self, dataset, **kwargs):
        super().__init__(dataset)
        self.table_definitions: TablesDefinition = kwargs.get("table_definitions")

    def check(self) -> Iterable[str]:
        if self.table_definitions is None:
            return ["Missing '--table-definitions-path' input"]
        current_definitions = generate_table_definitions(
            self.dataset, self.table_definitions.with_indexes_and_fks()
        )
        return (
            self.check_table_definitions(current_definitions)
            + self.check_foreign_keys()
        )

    def check_table_definitions(
        self, definitions_current: TablesDefinition
    ) -> List[str]:
        assert definitions_current is not None
        return compare_table_definitions(
            definitions_current,
            self.table_definitions,
            compare_indexes_and_fks=self.table_definitions.with_indexes_and_fks(),
        )

    def check_foreign_keys(self) -> List[str]:
        messages: List[str] = []
        if not self.table_definitions.with_indexes_and_fks():
            return messages
        for table_definition in self.table_definitions.tables:
            if table_definition.foreign_keys is None:
                messages += f"foreign keys checking is enabled but {table_definition.name} misses the list"
        messages += get_foreign_key_violations(self.dataset)
        return messages


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
            definitions_current,
            self.table_definitions,
            compare_columns=False,
            compare_indexes_and_fks=False,
        )
