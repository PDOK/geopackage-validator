from typing import Iterable, List, Dict
from abc import ABC, abstractmethod
from enum import Enum


class ValidationLevel(Enum):
    RQ = 1
    ERROR = 1
    RC = 2
    RECCOMENDATION = 2


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


class Validator(ABC):
    code: int
    level: ValidationLevel
    message: str

    def __init__(self, dataset, table_definitions=None):
        self.dataset = dataset
        self.table_definitions = table_definitions # todo: Not sure if this should be in the abstract class

    def validate(self) -> List[Dict[str, List[str]]]:
        """TODO"""
        return self.format(list(self.check()))

    def format(self, trace: List[str]) -> List[Dict[str, List[str]]]:
        """TODO"""
        if len(trace) == 0:
            return []

        return [
            {
                "validation_code": self.validation_code,
                "validation_description": self.__doc__,
                "level": self.level.name,
                "locations": trace,
            }
        ]

    @abstractmethod
    def check(self) -> Iterable[str]:
        """TODO"""
        ...

    @classproperty
    def validation_code(cls) -> str:
        return f"{cls.level.name}{cls.code}"
