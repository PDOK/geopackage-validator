from typing import Iterable, List

from geopackage_validator.validations import validator
from geopackage_validator.constants import SNAKE_CASE_REGEX


def query_tablenames(dataset) -> List[str]:
    return [table.GetName() for table in dataset]


class TableNameValidator(validator.Validator):
    """Table names must start with a letter, and valid characters are lowercase a-z, numbers or underscores."""

    code = 1
    level = validator.ValidationLevel.ERROR
    message = "Error table: {table}"

    def check(self) -> Iterable[str]:
        tablenames = query_tablenames(self.dataset)
        return self.check_tablenames(tablenames)

    @classmethod
    def check_tablenames(cls, tablenames: Iterable[str]):
        assert tablenames is not None
        return [
            cls.message.format(table=tablename)
            for tablename in tablenames
            if not SNAKE_CASE_REGEX.fullmatch(tablename)
        ]
