# Centralized overview of error messages so they can be maintained without having to look all over the code.

VALIDATIONS = {
    "system": {
        "errortype": "UNKNOWN",
        "errormessage_template": "Error occured: {error}",
        "validation": "No unexpected errors must occur.",
    },
    "gdal": {
        "errortype": "UNKNOWN_GDAL",
        "errormessage_template": "Error occured: {error}",
        "validation": "No unexpected GDAL errors must occur.",
    },
    "layername": {
        "errortype": "R1",
        "errormessage_template": "Error layer: {layer}",
        "validation": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.",
    },
    "layerfeature": {
        "errortype": "R2",
        "errormessage_template": "Error layer: {layer}",
        "validation": "Layers must have at least one feature.",
    },
    "geometry_type": {
        "errortype": "R3",
        "errormessage_template": "Error layer: {layer}, found geometry: {found_geometry}",
        "validation": "Layer features should have a valid geometry (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON).",
    },
    "db_views": {
        "errortype": "R4",
        "errormessage_template": "Found view: {view}",
        "validation": "The geopackage should have no views defined.",
    },
    "geometryvalid": {
        "errortype": "R5",
        "errormessage_template": "Found invalid geometry in table: {table}, column {column}, reason: {reason}",
        "validation": "Geometry should be valid.",
    },
    "columnname": {
        "errortype": "R6",
        "errormessage_template": "Error found in table: {table_name}, column: {column_name}",
        "validation": "Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.",
    },
    "feature_id": {
        "errortype": "R7",
        "errormessage_template": "Error found in table: {table_name}",
        "validation": "Tables should have a feature id column with unique index.",
    },
    "table_definition": {
        "errortype": "R8",
        "errormessage_template": "Difference: {difference}",
        "validation": "Geopackage must conform to given JSON definitions",
    },
    "rtree_present": {
        "errortype": "R9",
        "errormessage_template": "Table without index: {table_name}",
        "validation": "All geometry tables must have an rtree index",
    },
    "rtree_valid_check": {
        "errortype": "R10",
        "errormessage_template": "Invalid rtree index found for table: {table_name}",
        "validation": "All geometry table rtree indexes must be valid",
    },
}


def get_validations_list():
    validations_list = {}
    for index in VALIDATIONS:
        message = VALIDATIONS[index]
        errortype = message["errortype"]
        if errortype.startswith("R"):
            validations_list[errortype] = message["validation"]

    return validations_list


def create_errormessage(err_index, **kwargs):
    template = VALIDATIONS[err_index]

    error_message = {
        "errortype": template["errortype"],
        "validation": template["validation"],
        "errormessage": template["errormessage_template"].format(**kwargs),
    }
    return error_message
