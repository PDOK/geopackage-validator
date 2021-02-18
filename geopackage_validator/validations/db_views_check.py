from typing import Iterable

from geopackage_validator.validations import validator


def query_db_views(dataset) -> Iterable[str]:
    views = dataset.ExecuteSQL(
        "SELECT name FROM `main`.sqlite_master where type = 'view';"
    )

    for view in views:
        yield view[0]

    dataset.ReleaseResultSet(views)


class ViewsValidator(validator.Validator):
    """The geopackage should have no views defined."""

    code = 4
    level = validator.ValidationLevel.ERROR
    message = "Found view: {view}"

    def check(self) -> Iterable[str]:
        views = query_db_views(self.dataset)
        return self.db_views_check(views)

    @classmethod
    def db_views_check(cls, views: Iterable[str]):
        assert views is not None
        return [cls.message.format(view=view) for view in views]
