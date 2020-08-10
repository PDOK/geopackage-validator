from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
)


def geometry_valid_check_query(dataset):
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )
    for column in columns:
        validations = dataset.ExecuteSQL(
            'select ST_IsValidReason(GeomFromGPB("{column_name}")) as reason, '
            "'{table_name}' as table_name, "
            "'{column_name}' as column_name "
            'from "{table_name}" where ST_IsValid(GeomFromGPB("{column_name}")) = 0;'.format(
                table_name=column[0], column_name=column[1]
            )
        )
        for validation in validations:
            yield validation
        dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(columns)


def geometry_valid_check(geometry_check_list=None):
    assert geometry_check_list is not None

    errors = []

    for column in geometry_check_list:
        errors.append(
            create_errormessage(
                err_index="geometryvalid",
                reason=column[0],
                table=column[1],
                column=column[2],
            )
        )

    return error_format("geometryvalid", errors)
