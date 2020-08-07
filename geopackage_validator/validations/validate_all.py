import sys

from osgeo import ogr

from geopackage_validator.validations.rtree_check import rtree_check, rtree_check_query
from geopackage_validator.validations.rtree_present import rtree_present_query, rtree_present
from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
)
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
from geopackage_validator.validations.table_definitions_check import (
    table_definitions_check,
)


def validate_all(filename, table_definitions_path, errors):
    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(filename, 0)
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

        indexes = rtree_present_query(dataset)
        errors.extend(rtree_present(indexes))

        indexes = rtree_check_query(dataset)
        errors.extend(rtree_check(indexes))

        if table_definitions_path is not None:
            table_definitions_current = generate_table_definitions(dataset)
            errors.extend(
                table_definitions_check(
                    table_definitions_path, table_definitions_current
                )
            )

    except:
        errors.append(create_errormessage("system", error=sys.exc_info()[0]))
