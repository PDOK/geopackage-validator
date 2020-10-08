from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def feature_id_check_query(dataset) -> Iterable[Tuple[str, int]]:
    tables = dataset.ExecuteSQL("SELECT table_name FROM gpkg_geometry_columns;")
    tablelist = []
    for table in tables:
        tablelist.append(table[0])
    dataset.ReleaseResultSet(tables)

    for table in tablelist:
        validations = dataset.ExecuteSQL(
            "SELECT '{table_name}' as table_name, count(*) as pk_present FROM pragma_table_info('{table_name}') where pk > 0".format(
                table_name=table
            )
        )
        for validation in validations:
            yield validation

        dataset.ReleaseResultSet(validations)


def feature_id_check(feature_id_list: Iterable[Tuple[str, int]]):
    assert feature_id_list is not None
    results = []

    for table in feature_id_list:
        if table[1] != 1:
            results.append(
                create_validation_message(err_index="feature_id", table_name=table[0])
            )

    return result_format("feature_id", results)
