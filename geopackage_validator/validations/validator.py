from typing import Iterable, List, Dict
from abc import ABC, abstractmethod
from enum import IntEnum


class ValidationLevel(IntEnum):
    UNKNOWN_ERROR = 0
    UNKNOWN_WARNING = 0
    RQ = 1
    ERROR = 1
    RC = 2
    RECCOMENDATION = 2


VALIDATION_LEVELS = {
    ValidationLevel.UNKNOWN_ERROR: "unknown_error",
    ValidationLevel.UNKNOWN_WARNING: "unknown_warning",
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

    def __init__(self, dataset, **kwargs):
        self.dataset = dataset

    def validate(self) -> Dict[str, List[str]]:
        """Run validation at geopackage."""
        results = list(self.check())
        if results:
            return format_result(
                validation_code=self.validation_code,
                validation_description=self.__doc__,
                level=self.level,
                trace=results,
            )

    @abstractmethod
    def check(self) -> Iterable[str]:
        """Check the geopackage and return a list of validation results."""
        ...

    @classproperty
    def validation_code(cls) -> str:
        return f"{cls.level.name}{cls.code}"
