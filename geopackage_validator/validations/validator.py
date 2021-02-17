from typing import Iterable, List, Dict
from abc import ABC, abstractmethod
from enum import Enum

from geopackage_validator.gdal_utils import open_dataset


class ValidationLevel(Enum):
    UNKNOWN = 0
    RQ = 1
    ERROR = 1
    RC = 2
    RECCOMENDATION = 2


VALIDATION_LEVELS = {
    ValidationLevel.UNKNOWN: "unknown_error",
    ValidationLevel.RQ: "error",
    ValidationLevel.RC: "recommendation",
}


class classproperty:
    """
    Property decorator that also works on classes.

    Taken from Django: https://docs.djangoproject.com/en/3.0/_modules/django/utils/decorators/
    """

    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


def format_result(
    validation_code: str,
    validation_description: str,
    level: ValidationLevel,
    trace: List[str],
):
    return {
        "validation_code": validation_code,
        "validation_description": validation_description,
        "level": VALIDATION_LEVELS[level],
        "locations": trace,
    }


class Validator(ABC):
    code: int
    level: ValidationLevel
    message: str

    def __init__(self, gpkg_path, table_definitions=None):
        self.gpkg_path = gpkg_path
        self.dataset = open_dataset(gpkg_path)
        self.table_definitions = table_definitions

    def validate(self) -> List[Dict[str, List[str]]]:
        """TODO"""
        results = list(self.check())
        if results:
            return [
                format_result(
                    validation_code=self.validation_code,
                    validation_description=self.__doc__,
                    level=self.level,
                    trace=results,
                ),
            ]
        return []

    @abstractmethod
    def check(self) -> Iterable[str]:
        """TODO"""
        ...

    @classproperty
    def validation_code(cls) -> str:
        return f"{cls.level.name}{cls.code}"
