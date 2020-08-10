import re

from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
)


def columnname_check_query(dataset):
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )

    for column in columns:
        yield column

    dataset.ReleaseResultSet(columns)


def columnname_check(columnname_list=None):
    assert columnname_list is not None

    errors = []

    for columnname in columnname_list:
        match_valid = re.fullmatch(r"^[a-z][a-z0-9_]*$", columnname[1])
        if match_valid is None:
            errors.append(
                create_errormessage(
                    err_index="columnname",
                    column_name=columnname[1],
                    table_name=columnname[0],
                )
            )

    return error_format("columnname", errors)
