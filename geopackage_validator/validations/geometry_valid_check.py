from typing import Iterable, Tuple

from geopackage_validator.constants import MAX_VALIDATION_ITERATIONS
from geopackage_validator.validations import validator

import re

SQL_TEMPLATE = """SELECT 
    ST_IsValidReason("{column_name}") as reason, 
    '{table_name}' as table_name, 
    '{column_name}' as column_name,
    cast(rowid as INTEGER) as row_id
from "{table_name}" where ST_IsValid("{column_name}") = 0 LIMIT {limit};"""

def geometry_valid_check_query(dataset) -> Iterable[Tuple[str, str, str, int]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )
    for table_name, column_name in columns:
        validations = dataset.ExecuteSQL(
            SQL_TEMPLATE.format(table_name=table_name, column_name=column_name, limit=MAX_VALIDATION_ITERATIONS)
        )
        for validation in validations:
            yield validation
        dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(columns)


class ValidGeometryValidator(validator.Validator):
    """Geometries should be valid."""

    code = 5
    level = validator.ValidationLevel.ERROR
    message = "Found invalid geometry in table: {table}, column {column}, reason: {reason}, {amount} {desc}: {rowid_list}"

    def check(self) -> Iterable[str]:
        geometry_check_list = geometry_valid_check_query(self.dataset)
        results = self.geometry_valid_check(geometry_check_list)

        return self.aggregate(results)

    @classmethod
    def geometry_valid_check(
        cls, geometry_check_list: Iterable[Tuple[str, str, str, int]]
    ):
        assert geometry_check_list is not None
        return geometry_check_list

    def aggregate(self, results) -> Iterable[str]:
        aggregate = {}

        for reason, table, column, rowid in results:
            reason = re.sub(r"\[.*\]", "", reason)
            key = (reason, table, column).__hash__()

            if key in aggregate:
                aggregate[key]["amount"] += 1
                aggregate[key]["desc"] = "times, example record id's"
                if aggregate[key]["amount"] <= 5:
                    aggregate[key]["rowid_list"] += [rowid]

                if aggregate[key]["amount"] <= MAX_VALIDATION_ITERATIONS:
                    aggregate[key]["desc"] = "times and possibly more, example record id's"
            else:
                aggregate[key] = {
                    "table": table,
                    "column": column,
                    "reason": reason,
                    "rowid_list": [rowid],
                    "amount": 1,
                    "desc": "time, example record id"
                }

        return [self.message.format(**value) for key, value in aggregate.items()]
