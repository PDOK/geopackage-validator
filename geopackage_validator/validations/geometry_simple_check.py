from typing import Iterable, Tuple
from geopackage_validator.validations import validator
from geopackage_validator import utils


SQL_TEMPLATE = """SELECT 
count(rowid) AS count, 
cast(rowid AS INTEGER) AS row_id
FROM "{table_name}" WHERE ST_IsSimple("{column_name}") = 0"""


def query_geometry_simple(dataset) -> Iterable[Tuple[str, str, int]]:
    columns = utils.dataset_geometry_tables(dataset)

    for table_name, column_name, _ in columns:

        validations = dataset.ExecuteSQL(
            SQL_TEMPLATE.format(table_name=table_name, column_name=column_name)
        )
        for count, row_id in validations:
            if count > 0:
                yield table_name, column_name, count, row_id
        dataset.ReleaseResultSet(validations)


class SimpleGeometryValidator(validator.Validator):
    """Geometries should be simple."""

    code = 23
    level = validator.ValidationLevel.ERROR
    message = "Found not simple geometry in table: {table_name}, column {column_name}, {count} {count_label}, example id {row_id}"

    def check(self) -> Iterable[str]:
        result = query_geometry_simple(self.dataset)

        return [
            self.message.format(
                table_name=table_name,
                column_name=column_name,
                count=count,
                count_label=("time" if count == 1 else "times"),
                row_id=row_id,
            )
            for table_name, column_name, count, row_id in result
        ]
