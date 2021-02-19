from typing import Iterable, Tuple

from geopackage_validator.validations import validator

SQL_TEMPLATE = """SELECT 
    ST_IsValidReason("{column_name}") as reason, 
    '{table_name}' as table_name, 
    '{column_name}' as column_name,
    cast(rowid as INTEGER) as row_id
from "{table_name}" where ST_IsValid("{column_name}") = 0;"""


def geometry_valid_check_query(dataset) -> Iterable[Tuple[str, str, str, int]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )
    for table_name, column_name in columns:
        validations = dataset.ExecuteSQL(
            SQL_TEMPLATE.format(table_name=table_name, column_name=column_name)
        )
        for validation in validations:
            yield validation
        dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(columns)


class ValidGeometryValidator(validator.Validator):
    """Geometries should be valid."""

    code = 5
    level = validator.ValidationLevel.ERROR
    message = "Found invalid geometry in table: {table}, id {rowid}, column {column}, reason: {reason}"

    def check(self) -> Iterable[str]:
        geometry_check_list = geometry_valid_check_query(self.dataset)
        return self.geometry_valid_check(geometry_check_list)

    @classmethod
    def geometry_valid_check(
        cls, geometry_check_list: Iterable[Tuple[str, str, str, int]]
    ):
        assert geometry_check_list is not None

        return [
            cls.message.format(reason=reason, table=table, column=column, rowid=rowid)
            for reason, table, column, rowid in geometry_check_list
        ]
