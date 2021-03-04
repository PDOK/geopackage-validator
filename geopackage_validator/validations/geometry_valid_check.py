from typing import Iterable, Tuple
from geopackage_validator.validations import validator

SQL_TEMPLATE = """SELECT reason, count(reason) AS count, row_id
FROM(
    SELECT
        CASE INSTR(ST_IsValidReason("{column_name}"), '[')
            WHEN 0
                THEN ST_IsValidReason("{column_name}")
            ELSE substr(ST_IsValidReason("{column_name}"), 0, INSTR(ST_IsValidReason("{column_name}"), '['))
        END AS reason,
        cast(rowid AS INTEGER) AS row_id
    FROM "{table_name}" WHERE ST_IsValid("{column_name}") = 0
)
GROUP BY reason;"""


def query_geometry_valid(dataset) -> Iterable[Tuple[str, str, str, int]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )
    for table_name, column_name in columns:
        validations = dataset.ExecuteSQL(
            SQL_TEMPLATE.format(table_name=table_name, column_name=column_name)
        )
        for reason, count, row_id in validations:
            yield table_name, column_name, reason, count, row_id
        dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(columns)


class ValidGeometryValidator(validator.Validator):
    """Geometries should be valid."""

    code = 5
    level = validator.ValidationLevel.ERROR
    message = "Found invalid geometry in table: {table_name}, column {column_name}, reason: {reason}, {count} {count_label}, example id {row_id}"

    def check(self) -> Iterable[str]:
        result = query_geometry_valid(self.dataset)

        return [
            self.message.format(
                table_name=table_name,
                column_name=column_name,
                reason=reason,
                count=count,
                count_label=("time" if count == 1 else "times"),
                row_id=row_id,
            )
            for table_name, column_name, reason, count, row_id in result
        ]
