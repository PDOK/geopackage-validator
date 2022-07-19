from typing import Iterable, Tuple

from geopackage_validator.validations import validator
from geopackage_validator import utils


class GeomColumnNameValidator(validator.Validator):
    """It is recommended to name all GEOMETRY type columns 'geom'."""

    code = 17
    level = validator.ValidationLevel.RECCOMENDATION
    message = "Found in table: {table_name}, column: {column_name}"

    def check(self) -> Iterable[str]:
        columns = utils.dataset_geometry_tables(self.dataset)
        return self.geom_columnname_check(columns)

    @classmethod
    def geom_columnname_check(cls, columns: Iterable[Tuple[str]]):
        return [
            cls.message.format(column_name=column_name, table_name=table_name)
            for table_name, column_name, _ in columns
            if column_name != "geom"
        ]


class GeomColumnNameEqualValidator(validator.Validator):
    """It is recommended to give all GEOMETRY type columns the same name."""

    code = 18
    level = validator.ValidationLevel.RECCOMENDATION
    message = "Found column names are unequal: {column_names}"

    def check(self) -> Iterable[str]:
        columns = utils.dataset_geometry_tables(self.dataset)
        return self.geom_equal_columnname_check(columns)

    @classmethod
    def geom_equal_columnname_check(cls, columns: Iterable[Tuple[str]]):
        unique_column_names = {column_name for _, column_name, _ in columns}

        if len(unique_column_names) > 1:
            return [cls.message.format(column_names=", ".join(unique_column_names))]
        return []
