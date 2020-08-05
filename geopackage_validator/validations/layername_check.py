import re

from geopackage_validator.errors.validation_errors import create_errormessage


def layername_check_query(dataset):
    for i in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(i)
        yield layer.GetName()


def layername_check(layername_list=None):
    assert layername_list is not None

    errors = []

    for layername in layername_list:
        match_valid = re.fullmatch(r"^[a-z][a-z0-9_]*$", layername)
        if match_valid is None:
            errors.append(create_errormessage(err_index="layername", layer=layername))

    return errors
