from typing import Iterable

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def db_views_check_query(dataset) -> Iterable[str]:
    views = dataset.ExecuteSQL(
        "SELECT name FROM `main`.sqlite_master where type = 'view';"
    )

    for view in views:
        yield view[0]

    dataset.ReleaseResultSet(views)


def db_views_check(db_views_check_list: Iterable[str]):
    assert db_views_check_list is not None

    results = []

    for db_views in db_views_check_list:
        results.append(create_validation_message(err_index="db_views", view=db_views))

    return result_format("db_views", results)
