from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
)


def geom_columnname_check_query(dataset) -> Iterable[Tuple[str, str]]:
    column_info_list = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )

    for column_info in column_info_list:
        yield column_info[0], column_info[1]

    dataset.ReleaseResultSet(column_info_list)


def geom_columnname_check(column_info_list: Iterable[Tuple[str, str]]):
    assert column_info_list is not None

    errors = []
    for column_info in column_info_list:

        table_name = column_info[0]
        column_name = column_info[1]

        if column_name != "geom":
            errors.append(
                create_errormessage(
                    err_index="geom_columnname",
                    column_name=column_name,
                    table_name=table_name,
                )
            )

    return error_format("geom_columnname", errors)


def geom_equal_columnname_check(column_info_list: Iterable[Tuple[str, str]]):
    assert column_info_list is not None

    errors = []
    column_name_list = []

    for column_info in column_info_list:

        column_name = column_info[1]
        column_name_list.append(column_name)

    column_names = set(column_name_list)

    if len(column_names) > 1:
        errors.append(
            create_errormessage(
                err_index="geom_equal_columnnames",
                column_names=", ".join(column_names),
            )
        )

    return error_format("geom_equal_columnnames", errors)
