from typing import Iterable, Tuple, List

from geopackage_validator.constants import SNAKE_CASE_REGEX
from geopackage_validator.validations import validator
from geopackage_validator import utils


def query_columnames(dataset) -> Iterable[Tuple[str, str]]:
    tables = utils.dataset_geometry_tables(dataset)

    for table, _, _ in tables:
        columns = dataset.ExecuteSQL(
            "PRAGMA TABLE_INFO('{table_name}');".format(table_name=table)
        )

        for _, column, *_ in columns:
            yield table, column

        dataset.ReleaseResultSet(columns)


class ColumnNameValidator(validator.Validator):
    """Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores."""

    code = 6
    level = validator.ValidationLevel.ERROR
    message = "Error found in table: {table_name}, column: {column_name}"

    def check(self) -> Iterable[str]:
        column_names = query_columnames(self.dataset)
        return self.check_columns(column_names)

    @classmethod
    def check_columns(cls, column_names: Iterable[Tuple[str, str]]) -> List[str]:
        assert column_names is not None
        return [
            cls.message.format(column_name=column_name, table_name=table_name)
            for table_name, column_name in column_names
            if not SNAKE_CASE_REGEX.fullmatch(column_name)
        ]
