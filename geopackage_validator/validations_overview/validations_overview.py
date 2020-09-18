# Centralized overview of error messages so they can be maintained without having to look all over the code.
from typing import List, Dict

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
    "rtree_valid": {
        "errortype": "R10",
        "errormessage_template": "Invalid rtree index found for table: {table_name}",
        "validation": "All geometry table rtree indexes must be valid",
    },
    "layerfeature_ogr": {
        "errortype": "R11",
        "errormessage_template": "OGR index for feature count is not up to date for table: {layer}. Indexed feature count: {feature_count_ogr}, real feature count: {feature_count_real}",
        "validation": "OGR indexed feature counts must be up to date",
    },
    "srs": {
        "errortype": "R12",
        "errormessage_template": "Found in 'gpkg_spatial_ref_sys' {srs_organisation} {srs_id}. {srs_name} is not allowed.",
        "validation": "Only the following ESPG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409.",
    },
    "srs_equal": {
        "errortype": "R13",
        "errormessage_template": "Found srs are: {srs}",
        "validation": "It is required to give all GEOMETRY features the same default spatial reference system.",
    },
}


def get_validations_list(used_validations=None) -> Dict[str, str]:
    if used_validations is None:
        used_validations = []
    validations_list = {}
    for index in VALIDATIONS:
        message = VALIDATIONS[index]
        errortype = message["errortype"]
        if errortype.startswith("R") and (
            errortype in used_validations or len(used_validations) == 0
        ):
            validations_list[errortype] = message["validation"]

    return validations_list


def get_errortype(err_index) -> Dict[str, str]:
    template = VALIDATIONS[err_index]
    return {"errortype": template["errortype"], "validation": template["validation"]}


def create_errormessage(err_index, **kwargs) -> str:
    template = VALIDATIONS[err_index]

    error_message = template["errormessage_template"].format(**kwargs)
    return error_message


def error_format(
    err_index: str, errors: List[str]
) -> List[Dict[str, Dict[str, List[str]]]]:
    if len(errors) == 0:
        return []
    error = get_errortype(err_index)
    return [{error["errortype"]: {"errorinfo": error, "errors": errors}}]
