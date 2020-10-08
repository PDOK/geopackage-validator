import re
from typing import Iterable

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def layername_check_query(dataset) -> Iterable[str]:
    for i in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(i)
        yield layer.GetName()


def layername_check(layername_list: Iterable[str]):
    assert layername_list is not None

    results = []

    for layername in layername_list:
        match_valid = re.fullmatch(r"^[a-z][a-z0-9_]*$", layername)
        if match_valid is None:
            results.append(
                create_validation_message(err_index="layername", layer=layername)
            )

    return result_format("layername", results)
