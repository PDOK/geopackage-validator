import sys

from osgeo import ogr

from geopackage_validator.errors.error_messages import create_errormessage
from geopackage_validator.validations.db_views_check import (
    db_views_check,
    db_views_check_query,
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


def validate_all(filename, errors):
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

        try:
            views = geometry_valid_check_query(dataset)
            errors.extend(geometry_valid_check(views))
        except:
            print(sys.exc_info())

    except:
        errors.append(create_errormessage("system", error=sys.exc_info()[0]))
