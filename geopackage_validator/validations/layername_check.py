from typing import Iterable, List

from geopackage_validator.validations import validator
from geopackage_validator.constants import SNAKE_CASE_REGEX


def query_layernames(dataset) -> List[str]:
    return [layer.GetName() for layer in dataset]


class LayerNameValidator(validator.Validator):
    """Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores."""

    code = 1
    level = validator.ValidationLevel.ERROR
    message = "Error layer: {layer}"

    def check(self) -> Iterable[str]:
        layernames = query_layernames(self.dataset)
        return self.check_layernames(layernames)

    @classmethod
    def check_layernames(cls, layernames: Iterable[str]):
        assert layernames is not None
        return [
            cls.message.format(layer=layername)
            for layername in layernames
            if not SNAKE_CASE_REGEX.fullmatch(layername)
        ]
