from typing import Iterable

from geopackage_validator import utils
from geopackage_validator.validations import validator


def rtree_valid_check_query(dataset) -> Iterable[str]:
    # Check if gpkg_extensions table is present
    gpkg_extensions_present = dataset.ExecuteSQL(
        "select * from sqlite_master where type = 'table' and name = 'gpkg_extensions';"
    )

    has_extensions = gpkg_extensions_present.GetFeatureCount() == 0
    dataset.ReleaseResultSet(gpkg_extensions_present)
    if has_extensions:
        return

    indexes = dataset.ExecuteSQL(
        "select gc.table_name, gc.column_name from gpkg_geometry_columns gc "
        "where exists(select * from gpkg_extensions gce where gce.table_name = gc.table_name "
        "and extension_name = 'gpkg_rtree_index');"
    )
    for index in indexes:
        with dataset.silence_gdal():
            index_name = f"rtree_{index[0]}_{index[1]}"
            index_name_quoted = utils.quote_sqlite_string(index_name)
            validations = dataset.ExecuteSQL(f"select rtreecheck({index_name_quoted});")

            if validations is None:
                yield index[0]
                dataset.ReleaseResultSet(validations)
                continue

            for validation in validations:
                if validation[0] != "ok":
                    yield validation[0]
            dataset.ReleaseResultSet(validations)

    dataset.ReleaseResultSet(indexes)


class ValidRtreeValidator(validator.Validator):
    """All geometry table rtree indexes must be valid."""

    code = 10
    level = validator.ValidationLevel.ERROR
    message = "Invalid rtree index found for table: {table_name}"

    def check(self) -> Iterable[str]:
        rtree_index_list = rtree_valid_check_query(self.dataset)
        return self.check_rtree_is_valid(rtree_index_list)

    @classmethod
    def check_rtree_is_valid(cls, rtree_index_list: Iterable[str]):
        assert rtree_index_list is not None
        return [cls.message.format(table_name=table) for table in rtree_index_list]
