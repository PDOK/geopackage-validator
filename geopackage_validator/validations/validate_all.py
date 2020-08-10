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
    layerfeature_check,
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
from geopackage_validator.validations_overview.validations_overview import error_format


def validate_all(
    filename: str,
    table_definitions_path: str,
    errors: List[Dict[str, Dict[str, List[str]]]],
):
    dataset = open_dataset(filename)
    try:
        layernames = layername_check_query(dataset)
        errors.extend(layername_check(layernames))

        layerfeature_count = layerfeature_check_query(dataset)
        errors.extend(layerfeature_check(layerfeature_count))

        geometries = geometry_type_check_query(dataset)
        errors.extend(geometry_type_check(geometries))

        views = db_views_check_query(dataset)
        errors.extend(db_views_check(views))

        geometries = geometry_valid_check_query(dataset)
        errors.extend(geometry_valid_check(geometries))

        columns = columnname_check_query(dataset)
        errors.extend(columnname_check(columns))

        columns = feature_id_check_query(dataset)
        errors.extend(feature_id_check(columns))

        indexes = rtree_present_check_query(dataset)
        errors.extend(rtree_present_check(indexes))

        indexes = rtree_valid_check_query(dataset)
        errors.extend(rtree_valid_check(indexes))

        if table_definitions_path is not None:
            table_definitions_current = generate_table_definitions(dataset)
            errors.extend(
                table_definitions_check(
                    table_definitions_path, table_definitions_current
                )
            )

    except:
        return error_format("system", [str(sys.exc_info()[0])])
