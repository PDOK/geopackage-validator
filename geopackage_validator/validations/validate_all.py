from typing import Dict, List

from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.generate import generate_table_definitions
from geopackage_validator.validations.columnname_check import (
    columnname_check_query,
    columnname_check,
)
from geopackage_validator.validations.db_views_check import (
    db_views_check,
    db_views_check_query,
)
from geopackage_validator.validations.feature_id_check import (
    feature_id_check,
    feature_id_check_query,
)
from geopackage_validator.validations.geom_column_check import (
    geom_columnname_check_query,
    geom_columnname_check,
    geom_equal_columnname_check,
)
from geopackage_validator.validations.geometry_type_check import (
    geometry_type_check_query,
    geometry_type_check,
)
from geopackage_validator.validations.geometry_valid_check import (
    geometry_valid_check_query,
    geometry_valid_check,
)
from geopackage_validator.validations.gpkg_geometry_valid import (
    gpkg_geometry_valid_check_query,
    gpkg_geometry_match_table_check,
    gpkg_geometry_valid_check,
)
from geopackage_validator.validations.layerfeature_check import (
    layerfeature_check_query,
    layerfeature_check_ogr_index,
    layerfeature_check_featurecount,
)
from geopackage_validator.validations.layername_check import (
    layername_check,
    layername_check_query,
)
from geopackage_validator.validations.rtree_present_check import (
    rtree_present_check_query,
    rtree_present_check,
)
from geopackage_validator.validations.rtree_valid_check import (
    rtree_valid_check,
    rtree_valid_check_query,
)
from geopackage_validator.validations.srs_check import (
    srs_check_query,
    srs_check,
    srs_equal_check_query,
    srs_equal_check,
)
from geopackage_validator.validations.table_definitions_check import (
    table_definitions_check,
)
from geopackage_validator.validations_overview.validations_overview import (
    get_validation_type,
)


def results_gpkg_geometry_valid(results):
    for result in results:
        if result["validation_code"] == "RQ14":
            return False
    return True


def validate_all(
    filename: str,
    table_definitions_path: str,
    validations: List[str],
    results: List[Dict[str, List[str]]],
):
    dataset = open_dataset(filename)
    # Validation required checks
    if get_validation_type("layername")["validation_code"] in validations:
        layernames = layername_check_query(dataset)
        results.extend(layername_check(layernames))

    if get_validation_type("layerfeature")["validation_code"] in validations:
        layerfeature_count = layerfeature_check_query(dataset)
        results.extend(layerfeature_check_featurecount(layerfeature_count))

    if get_validation_type("layerfeature_ogr")["validation_code"] in validations:
        layerfeature_count = layerfeature_check_query(dataset)
        results.extend(layerfeature_check_ogr_index(layerfeature_count))

    if get_validation_type("geometry_type")["validation_code"] in validations:
        geometries = geometry_type_check_query(dataset)
        results.extend(geometry_type_check(geometries))

    if get_validation_type("db_views")["validation_code"] in validations:
        views = db_views_check_query(dataset)
        results.extend(db_views_check(views))

    if get_validation_type("geometryvalid")["validation_code"] in validations:
        geometries = geometry_valid_check_query(dataset)
        results.extend(geometry_valid_check(geometries))

    if get_validation_type("columnname")["validation_code"] in validations:
        columns = columnname_check_query(dataset)
        results.extend(columnname_check(columns))

    if get_validation_type("feature_id")["validation_code"] in validations:
        columns = feature_id_check_query(dataset)
        results.extend(feature_id_check(columns))

    if get_validation_type("rtree_present")["validation_code"] in validations:
        indexes = rtree_present_check_query(dataset)
        results.extend(rtree_present_check(indexes))

    if get_validation_type("rtree_valid")["validation_code"] in validations:
        indexes = rtree_valid_check_query(dataset)
        results.extend(rtree_valid_check(indexes))

    if get_validation_type("rtree_valid")["validation_code"] in validations:
        if table_definitions_path:
            table_definitions_current = generate_table_definitions(dataset)
            results.extend(
                table_definitions_check(
                    table_definitions_path, table_definitions_current
                )
            )

    if get_validation_type("srs")["validation_code"] in validations:
        srs = srs_check_query(dataset)
        results.extend(srs_check(srs))

    if get_validation_type("srs_equal")["validation_code"] in validations:
        srs = srs_equal_check_query(dataset)
        results.extend(srs_equal_check(srs))

    if get_validation_type("gpkg_geometry_valid")["validation_code"] in validations:
        geometry_type_names = gpkg_geometry_valid_check_query(dataset)
        results.extend(gpkg_geometry_valid_check(geometry_type_names))

    if get_validation_type("gpkg_geometry_match_table")[
        "validation_code"
    ] in validations and results_gpkg_geometry_valid(results):
        table_geometry_type_names = geometry_type_check_query(dataset)
        geometry_type_names = gpkg_geometry_valid_check_query(dataset)
        results.extend(
            gpkg_geometry_match_table_check(
                table_geometry_type_names, geometry_type_names
            )
        )

    # Validation recommendation checks
    if get_validation_type("geom_columnname")["validation_code"] in validations:
        columns = geom_columnname_check_query(dataset)
        results.extend(geom_columnname_check(columns))

    if get_validation_type("geom_equal_columnnames")["validation_code"] in validations:
        columns = geom_columnname_check_query(dataset)
        results.extend(geom_equal_columnname_check(columns))
