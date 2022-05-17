from typing import Iterable, Tuple, List

from geopackage_validator.constants import SNAKE_CASE_REGEX
from geopackage_validator.validations import validator
from geopackage_validator import utils


def query_names(dataset) -> Iterable[Tuple[str, str]]:
    tables = utils.dataset_geometry_tables(dataset)

    for table, _, _ in tables:
        yield "table", table
        columns = dataset.ExecuteSQL(f"PRAGMA TABLE_INFO('{table}');")

        for _, column, *_ in columns:
            yield "column", f"{column} (table: {table})"

        dataset.ReleaseResultSet(columns)


class NameLengthValidator(validator.Validator):
    """All names must be maximally 53 characters long."""

    code = 16
    level = validator.ValidationLevel.ERROR
    message = "Error {name_type} too long: {name}"

    def check(self) -> Iterable[str]:
        column_names = query_names(self.dataset)
        return self.check_columns(column_names)

    @classmethod
    def check_columns(cls, names: Iterable[Tuple[str, str]]) -> List[str]:
        assert names is not None
        return [
            cls.message.format(name=name, name_type=name_type)
            for name_type, name in names
            if len(name) > 53
        ]
