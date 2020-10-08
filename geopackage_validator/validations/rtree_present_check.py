from typing import Iterable

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def rtree_present_check_query(dataset) -> Iterable[str]:
    # Check if gpkg_extensions table is present
    gpkg_extensions_present = dataset.ExecuteSQL(
        "select * from sqlite_master where type = 'table' and name = 'gpkg_extensions';"
    )

    if gpkg_extensions_present.GetFeatureCount() == 0:
        yield "no table has an rtree index"
        dataset.ReleaseResultSet(gpkg_extensions_present)
        return

    indexes = dataset.ExecuteSQL(
        "select gc.table_name from gpkg_contents gc "
        "where not exists(select * from gpkg_extensions gce where gce.table_name = gc.table_name "
        "and extension_name = 'gpkg_rtree_index');"
    )
    for index in indexes:
        yield index[0]

    dataset.ReleaseResultSet(indexes)


def rtree_present_check(rtree_present_check_list: Iterable[str]):
    assert rtree_present_check_list is not None

    results = []

    for table in rtree_present_check_list:
        results.append(
            create_validation_message(err_index="rtree_present", table_name=table)
        )

    return result_format("rtree_present", results)
