from geopackage_validator.errors.error_messages import create_errormessage


def db_views_check_query(dataset):
    views = dataset.ExecuteSQL(
        'SELECT name FROM "main".sqlite_master where type = "view";'
    )

    for view in views:
        yield view[0]

    dataset.ReleaseResultSet(views)


def db_views_check(db_views_check_list=None):
    assert db_views_check_list is not None

    errors = []

    for db_views in db_views_check_list:
        errors.append(create_errormessage(err_index="db_views", view=db_views))

    return errors
