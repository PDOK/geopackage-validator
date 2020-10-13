from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def geometry_valid_check_query(dataset) -> Iterable[Tuple[str, str, str, int]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )
    for column in columns:
        validations = dataset.ExecuteSQL(
            'select ST_IsValidReason("{column_name}") as reason, '
            "'{table_name}' as table_name, "
            "'{column_name}' as column_name, "
            "cast(rowid as INTEGER) as row_id "
            'from "{table_name}" where ST_IsValid("{column_name}") = 0;'.format(
                table_name=column[0], column_name=column[1]
            )
        )
        for validation in validations:
            yield validation
        dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(columns)


def geometry_valid_check(geometry_check_list: Iterable[Tuple[str, str, str, int]]):
    assert geometry_check_list is not None

    results = []

    for column in geometry_check_list:
        results.append(
            create_validation_message(
                err_index="geometryvalid",
                reason=column[0],
                table=column[1],
                column=column[2],
                rowid=column[3],
            )
        )

    return result_format("geometryvalid", results)
