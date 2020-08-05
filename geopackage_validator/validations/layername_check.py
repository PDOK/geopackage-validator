import re


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
            errors.append(
                {
                    "errortype": "R1",
                    "errormessage": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. Error layer: {layer}".format(
                        layer=layername
                    ),
                }
            )

    return errors
