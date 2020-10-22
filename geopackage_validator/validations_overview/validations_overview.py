# Centralized overview of validation messages so they can be maintained without having to look all over the code.
from typing import List, Dict

VALIDATIONS = {
    "system": {
        "validation_code": "UNKNOWN",
        "level": "error",
        "validation_message_template": "Error occurred: {error}",
        "validation": "No unexpected errors must occur.",
    },
    "gdal": {
        "validation_code": "UNKNOWN_GDAL",
        "level": "error",
        "validation_message_template": "Error occurred: {error}",
        "validation": "No unexpected GDAL errors must occur.",
    },
    "layername": {
        "validation_code": "RQ1",
        "level": "error",
        "validation_message_template": "Error layer: {layer}",
        "validation": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.",
    },
    "layerfeature": {
        "validation_code": "RQ2",
        "level": "error",
        "validation_message_template": "Error layer: {layer}",
        "validation": "Layers must have at least one feature.",
    },
    "geometry_type": {
        "validation_code": "RQ3",
        "level": "error",
        "validation_message_template": "Error layer: {layer}, found geometry: {found_geometry}",
        "validation": "Layer features should have a valid geometry (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON). (random sample of up to 100)",
    },
    "db_views": {
        "validation_code": "RQ4",
        "level": "error",
        "validation_message_template": "Found view: {view}",
        "validation": "The geopackage should have no views defined.",
    },
    "geometryvalid": {
        "validation_code": "RQ5",
        "level": "error",
        "validation_message_template": "Found invalid geometry in table: {table}, id {rowid}, column {column}, reason: {reason}",
        "validation": "Geometry should be valid.",
    },
    "columnname": {
        "validation_code": "RQ6",
        "level": "error",
        "validation_message_template": "Error found in table: {table_name}, column: {column_name}",
        "validation": "Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.",
    },
    "feature_id": {
        "validation_code": "RQ7",
        "level": "error",
        "validation_message_template": "Error found in table: {table_name}",
        "validation": "Tables should have a feature id column with unique index.",
    },
    "table_definition": {
        "validation_code": "RQ8",
        "level": "error",
        "validation_message_template": "Difference: {difference}",
        "validation": "Geopackage must conform to given JSON definitions.",
    },
    "rtree_present": {
        "validation_code": "RQ9",
        "level": "error",
        "validation_message_template": "Table without index: {table_name}",
        "validation": "All geometry tables must have an rtree index",
    },
    "rtree_valid": {
        "validation_code": "RQ10",
        "level": "error",
        "validation_message_template": "Invalid rtree index found for table: {table_name}",
        "validation": "All geometry table rtree indexes must be valid",
    },
    "layerfeature_ogr": {
        "validation_code": "RQ11",
        "level": "error",
        "validation_message_template": "OGR index for feature count is not up to date for table: {layer}. Indexed feature count: {feature_count_ogr}, real feature count: {feature_count_real}",
        "validation": "OGR indexed feature counts must be up to date",
    },
    "srs": {
        "validation_code": "RQ12",
        "level": "error",
        "validation_message_template": "Found in 'gpkg_spatial_ref_sys' {srs_organisation} {srs_id}. {srs_name} is not allowed.",
        "validation": "Only the following ESPG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409.",
    },
    "srs_equal": {
        "validation_code": "RQ13",
        "level": "error",
        "validation_message_template": "Found srs are: {srs}",
        "validation": "It is required to give all GEOMETRY features the same default spatial reference system.",
    },
    "gpkg_geometry_valid": {
        "validation_code": "RQ14",
        "level": "error",
        "validation_message_template": "Found geometry_type_name: {found_geometry} (from the gpkg_geometry_columns table).",
        "validation": "The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON.",
    },
    "gpkg_geometry_match_table": {
        "validation_code": "RQ15",
        "level": "error",
        "validation_message_template": "Found geometry: {found_geometry}, in layer: {layer}, where gpkg_geometry is: {gpkg_geometry}.",
        "validation": "All table geometries must match the geometry_type_name from the gpkg_geometry_columns table. (random sample of up to 100)",
    },
    "geom_columnname": {
        "validation_code": "RC1",
        "level": "recommendation",
        "validation_message_template": "Found in table: {table_name}, column: {column_name}",
        "validation": "It is recommended to name all GEOMETRY type columns 'geom'.",
    },
    "geom_equal_columnnames": {
        "validation_code": "RC2",
        "level": "recommendation",
        "validation_message_template": "Found column names are: {column_names}",
        "validation": "It is recommended to give all GEOMETRY type columns the same name.",
    },
}


def get_validations_list(used_validations=None) -> Dict[str, str]:
    if used_validations is None:
        used_validations = []
    validations_list = {}
    for index in VALIDATIONS:
        message = VALIDATIONS[index]
        validation_code = message["validation_code"]
        if validation_code.startswith("R") and (
            validation_code in used_validations or len(used_validations) == 0
        ):
            validations_list[validation_code] = message["validation"]

    return validations_list


def get_validation_type(err_index) -> Dict[str, str]:
    template = VALIDATIONS[err_index]
    return {
        "validation_code": template["validation_code"],
        "validation": template["validation"],
        "level": template["level"],
    }


def create_validation_message(err_index, **kwargs) -> str:
    template = VALIDATIONS[err_index]

    validation_message = template["validation_message_template"].format(**kwargs)
    return validation_message


def result_format(err_index: str, trace: List[str]) -> List[Dict[str, List[str]]]:
    if len(trace) == 0:
        return []
    validation = get_validation_type(err_index)
    return [
        {
            "validation_code": validation["validation_code"],
            "validation_description": validation["validation"],
            "level": validation["level"],
            "locations": trace,
        }
    ]
