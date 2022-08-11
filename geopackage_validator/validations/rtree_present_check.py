from typing import Iterable

from geopackage_validator.validations import validator


def query_rtree_presence(dataset) -> Iterable[str]:
    # Check if gpkg_extensions table is present
    gpkg_extensions = dataset.ExecuteSQL(
        "select * from sqlite_master where type = 'table' and name = 'gpkg_extensions';"
    )
    has_gpkg_extensions = len(gpkg_extensions) > 0
    dataset.ReleaseResultSet(gpkg_extensions)

    if not has_gpkg_extensions:
        yield "no table has an rtree index"
        return

    indexes = dataset.ExecuteSQL(
        "select gc.table_name from gpkg_contents gc "
        "where gc.data_type = 'features' and "
        "not exists(select * from gpkg_extensions gce "
        "   where gce.table_name = gc.table_name "
        "   and extension_name = 'gpkg_rtree_index');"
    )
    for (index,) in indexes:
        yield index

    dataset.ReleaseResultSet(indexes)


class RTreeExistsValidator(validator.Validator):
    """All geometry tables must have an rtree index."""

    code = 9
    level = validator.ValidationLevel.ERROR
    message = "Table without index: {table_name}"

    def check(self) -> Iterable[str]:
        rtrees = query_rtree_presence(self.dataset)
        return self.check_rtree_is_present(rtrees)

    @classmethod
    def check_rtree_is_present(cls, rtree_present_check_list: Iterable[str]):
        assert rtree_present_check_list is not None
        return [
            cls.message.format(table_name=table) for table in rtree_present_check_list
        ]
