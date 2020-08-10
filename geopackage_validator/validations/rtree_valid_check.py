from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
)


def rtree_valid_check_query(dataset):
    # Check if gpkg_extensions table is present
    gpkg_extensions_present = dataset.ExecuteSQL(
        "select * from sqlite_master where type = 'table' and name = 'gpkg_extensions';"
    )

    if gpkg_extensions_present.GetFeatureCount() == 0:
        dataset.ReleaseResultSet(gpkg_extensions_present)
        return

    indexes = dataset.ExecuteSQL(
        "select gc.table_name, gc.column_name from gpkg_geometry_columns gc "
        "where exists(select * from gpkg_extensions gce where gce.table_name = gc.table_name "
        "and extension_name = 'gpkg_rtree_index');"
    )
    for index in indexes:
        validations = dataset.ExecuteSQL(
            'select rtreecheck("{index_name}");'.format(
                index_name="rtree_" + index[0] + "_" + index[1]
            )
        )
        for validation in validations:
            if validation[0] != "ok":
                yield validation[0]
        dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(indexes)


def rtree_valid_check(rtree_index_list=None):
    assert rtree_index_list is not None

    errors = []

    for table in rtree_index_list:
        errors.append(
            create_errormessage(err_index="rtree_valid_check", table_name=table)
        )

    return errors
