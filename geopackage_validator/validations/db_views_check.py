from typing import Iterable

from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
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

    errors = []

    for db_views in db_views_check_list:
        errors.append(create_errormessage(err_index="db_views", view=db_views))

    return error_format("db_views", errors)
