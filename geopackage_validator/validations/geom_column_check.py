from typing import Iterable, Tuple
from functools import lru_cache

from geopackage_validator.validations import validator


@lru_cache(None)
def query_geom_columnname(dataset) -> Iterable[Tuple[str, str]]:
    column_info_list = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )

    for table_name, column_name in column_info_list:
        yield table_name, column_name

    dataset.ReleaseResultSet(column_info_list)


class GeomColumnNameValidator(validator.Validator):
    """It is recommended to name all GEOMETRY type columns 'geom'."""

    code = 1
    level = validator.ValidationLevel.RECCOMENDATION
    message = "Found in table: {table_name}, column: {column_name}"

    def check(self) -> Iterable[str]:
        columns = query_geom_columnname(self.dataset)
        return self.geom_columnname_check(columns)

    @classmethod
    def geom_columnname_check(cls, columns: Iterable[Tuple[str, str]]):
        assert columns is not None
        return [
            cls.message.format(column_name=column_name, table_name=table_name)
            for table_name, column_name in columns
            if column_name != "geom"
        ]


class GeomColumnNameEqualValidator(validator.Validator):
    """It is recommended to give all GEOMETRY type columns the same name."""

    code = 2
    level = validator.ValidationLevel.RECCOMENDATION
    message = "Found column names are unequal: {column_names}"

    def check(self) -> Iterable[str]:
        columns = query_geom_columnname(self.dataset)
        return self.geom_equal_columnname_check(columns)

    @classmethod
    def geom_equal_columnname_check(cls, columns: Iterable[Tuple[str, str]]):
        assert columns is not None
        unique_column_names = {column_name for _, column_name in columns}

        if len(unique_column_names) > 1:
            return [cls.message.format(column_names=", ".join(unique_column_names))]
        return []
