from typing import Iterable, Tuple
from geopackage_validator.validations import validator
from geopackage_validator import utils

SQL_VALID_TEMPLATE_V0 = """SELECT reason, count(reason) AS count, row_id
FROM(
    SELECT
        CASE ST_IsValid("{column_name}")
            WHEN 0
                THEN
                    CASE INSTR(ST_IsValidReason("{column_name}"), '[')
                        WHEN 0
                            THEN ST_IsValidReason("{column_name}")
                        ELSE substr(ST_IsValidReason("{column_name}"), 0, INSTR(ST_IsValidReason("{column_name}"), '['))
                    END
                ELSE
                    CASE
                        WHEN IsValidGPB("{column_name}") = 0
                            THEN 'Not GeoPackage geometry'
                    END
        END AS reason,
        cast(rowid AS INTEGER) AS row_id
    FROM "{table_name}"
    WHERE
        ST_IsValid("{column_name}") = 0 OR
        (IsValidGPB("{column_name}") = 0  AND ST_IsEmpty("{column_name}") = 0) -- Empty geometry is considered valid
)
GROUP BY reason;"""

SQL_VALID_TEMPLATE = """SELECT reason, count(reason) AS count, row_id
FROM(
    SELECT
        CASE ST_IsValid("{column_name}")
            WHEN 0
                THEN
                    CASE INSTR(ST_IsValidReason("{column_name}"), '[')
                        WHEN 0
                            THEN ST_IsValidReason("{column_name}")
                        ELSE substr(ST_IsValidReason("{column_name}"), 0, INSTR(ST_IsValidReason("{column_name}"), '['))
                    END
                ELSE
                    CASE
                        WHEN ST_IsSimple("{column_name}") = 0
                            THEN 'Not Simple'
                        WHEN IsValidGPB("{column_name}") = 0
                            THEN 'Not GeoPackage geometry'
                    END
        END AS reason,
        cast(rowid AS INTEGER) AS row_id
    FROM "{table_name}"
    WHERE
        ST_IsValid("{column_name}") = 0 OR
        ST_IsSimple("{column_name}") = 0 OR
        (IsValidGPB("{column_name}") = 0  AND ST_IsEmpty("{column_name}") = 0) -- Empty geometry is considered valid
)
GROUP BY reason;"""


def query_geometry_valid(dataset, sql_template) -> Iterable[Tuple[str, str, str, int]]:
    columns = utils.dataset_geometry_tables(dataset)

    for table_name, column_name, _ in columns:
        validations = dataset.ExecuteSQL(
            sql_template.format(table_name=table_name, column_name=column_name)
        )
        for reason, count, row_id in validations:
            yield table_name, column_name, reason, count, row_id
        dataset.ReleaseResultSet(validations)


class ValidGeometryValidatorV0(validator.Validator):
    """Legacy: use RQ23 * Geometries should be valid."""

    code = 5
    level = validator.ValidationLevel.ERROR
    message = "Found invalid geometry in table: {table_name}, column {column_name}, reason: {reason}, {count} {count_label}, example id {row_id}"

    def check(self) -> Iterable[str]:
        result = query_geometry_valid(self.dataset, SQL_VALID_TEMPLATE_V0)

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


class ValidGeometryValidator(validator.Validator):
    """Geometries should be valid and simple."""

    code = 23
    level = validator.ValidationLevel.ERROR
    message = "Found invalid geometry in table: {table_name}, column {column_name}, reason: {reason}, {count} {count_label}, example id {row_id}"

    def check(self) -> Iterable[str]:
        result = query_geometry_valid(self.dataset, SQL_VALID_TEMPLATE)

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
