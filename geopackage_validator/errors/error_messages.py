# Centralized overview of error messages so they can be maintained without having to look all over the code.

ERROR_MESSAGES = {
    "system": {
        "errortype": "UNKNOWN",
        "errormessage_template": "Unexpected error occured: {error}",
    },
    "gdal": {
        "errortype": "UNKNOWN_GDAL",
        "errormessage_template": "Unexpected GDAL error occured: {error}",
    },
    "layername": {
        "errortype": "R1",
        "errormessage_template": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. Error layer: {layer}",
    },
    "layerfeature": {
        "errortype": "R2",
        "errormessage_template": "Layers must have at least one feature. Error layer: {layer}",
    },
    "geometry_type": {
        "errortype": "R3",
        "errormessage_template": "Layer features should have a valid geometry (one of {valid_geometries}). Error layer: {layer}, found geometry: {found_geometry}",
    },
    "db_views": {
        "errortype": "R4",
        "errormessage_template": "There should be no views in the database. Found view: {view}",
    },
    "geometryvalid": {
        "errortype": "R5",
        "errormessage_template": "Geometry should be valid. Found invalid geometry in table: {table}, column {column}, reason: {reason}",
    },
    "columnname": {
        "errortype": "R6",
        "errormessage_template": "Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. Error found in table: {table_name}, column: {column_name}",
    },
}


def create_errormessage(err_index, **kwargs):
    template = ERROR_MESSAGES[err_index]

    error_message = {
        "errortype": template["errortype"],
        "errormessage": template["errormessage_template"].format(**kwargs),
    }
    return error_message
