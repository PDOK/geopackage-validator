from typing import Iterable, Tuple
from geopackage_validator.validations import validator
from geopackage_validator import utils

SQL_EMPTY_TEMPLATE = """SELECT count(row_id) AS count, row_id
FROM(
    SELECT
        cast(rowid AS INTEGER) AS row_id
    FROM "{table_name}" WHERE ST_IsEmpty("{column_name}") = 1
);"""


def query_geometry_empty(dataset, sql_template) -> Iterable[Tuple[str, str, str, int]]:
    columns = utils.dataset_geometry_tables(dataset)

    for table_name, column_name, _ in columns:
        validations = dataset.ExecuteSQL(
            sql_template.format(table_name=table_name, column_name=column_name)
        )
        for count, row_id in validations:
            yield table_name, column_name, count, row_id
        dataset.ReleaseResultSet(validations)


class ValidGeometryValidator(validator.Validator):
    """Geometries should not be empty."""

    code = 24
    level = validator.ValidationLevel.ERROR
    message = "Found empty geometry in table: {table_name}, column {column_name}, {count} {count_label}, example id {row_id}"

    def check(self) -> Iterable[str]:
        result = query_geometry_empty(self.dataset, SQL_EMPTY_TEMPLATE)

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
