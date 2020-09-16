import sys
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
    geometry_type_check,
    geometry_type_check_query,
)
from geopackage_validator.validations.geometry_valid_check import (
    geometry_valid_check_query,
    geometry_valid_check,
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
from geopackage_validator.validations.table_definitions_check import (
    table_definitions_check,
)
from geopackage_validator.validations_overview.validations_overview import (
    error_format,
    get_errortype,
)


def validate_all(
    filename: str,
    table_definitions_path: str,
    validations: List[str],
    errors: List[Dict[str, Dict[str, List[str]]]],
):
    dataset = open_dataset(filename)

    try:

        # Error checks
        if get_errortype("layername")["errortype"] in validations:
            layernames = layername_check_query(dataset)
            errors.extend(layername_check(layernames))

        if get_errortype("layerfeature")["errortype"] in validations:
            layerfeature_count = layerfeature_check_query(dataset)
            errors.extend(layerfeature_check_featurecount(layerfeature_count))

        if get_errortype("layerfeature_ogr")["errortype"] in validations:
            layerfeature_count = layerfeature_check_query(dataset)
            errors.extend(layerfeature_check_ogr_index(layerfeature_count))

        if get_errortype("geometry_type")["errortype"] in validations:
            geometries = geometry_type_check_query(dataset)
            errors.extend(geometry_type_check(geometries))

        if get_errortype("db_views")["errortype"] in validations:
            views = db_views_check_query(dataset)
            errors.extend(db_views_check(views))

        if get_errortype("geometryvalid")["errortype"] in validations:
            geometries = geometry_valid_check_query(dataset)
            errors.extend(geometry_valid_check(geometries))

        if get_errortype("columnname")["errortype"] in validations:
            columns = columnname_check_query(dataset)
            errors.extend(columnname_check(columns))

        if get_errortype("feature_id")["errortype"] in validations:
            columns = feature_id_check_query(dataset)
            errors.extend(feature_id_check(columns))

        if get_errortype("rtree_present")["errortype"] in validations:
            indexes = rtree_present_check_query(dataset)
            errors.extend(rtree_present_check(indexes))

        if get_errortype("rtree_valid")["errortype"] in validations:
            indexes = rtree_valid_check_query(dataset)
            errors.extend(rtree_valid_check(indexes))

        if get_errortype("rtree_valid")["errortype"] in validations:
            if table_definitions_path is not None:
                table_definitions_current = generate_table_definitions(dataset)
                errors.extend(
                    table_definitions_check(
                        table_definitions_path, table_definitions_current
                    )
                )

        # Warning checks
        if get_errortype("geom_columnname")["errortype"] in validations:
            columns = geom_columnname_check_query(dataset)
            errors.extend(geom_columnname_check(columns))

        if get_errortype("geom_equal_columnnames")["errortype"] in validations:
            columns = geom_columnname_check_query(dataset)
            errors.extend(geom_equal_columnname_check(columns))

    except:
        return error_format("system", [str(sys.exc_info()[0])])
