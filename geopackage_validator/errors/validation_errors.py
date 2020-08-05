# Centralized overview of error messages so they can be maintained without having to look all over the code.

ERROR_MESSAGES = {
    "layername": {
        "errortype": "R1",
        "errormessage_template": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. Error layer: {layer}",
    },
    "layerfeature": {
        "errortype": "R2",
        "errormessage_template": "Layers must have at least one feature. Error layer: {layer}",
    },
    "geometry": {
        "errortype": "R3",
        "errormessage_template": "Layer features should have a valid geometry (one of {valid_geometries}). Error layer: {layer}, found geometry: {found_geometry}",
    },
}


def create_errormessage(err_index, **kwargs):
    template = ERROR_MESSAGES[err_index]

    error_message = {
        "errortype": template["errortype"],
        "errormessage": template["errormessage_template"].format(**kwargs),
    }
    return error_message
