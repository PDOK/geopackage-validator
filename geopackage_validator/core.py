import logging

from geopackage_validator.errors.validation_errors import create_errormessage
from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)
from geopackage_validator.validations.validate_all import validate_all

import json

logger = logging.getLogger(__name__)


def main():
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import
    from geopackage_validator.gdal.init import init_gdal

    errors = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        error = err_msg.replace("\n", " ")
        errors.append(create_errormessage("gdal", error=error))

    init_gdal(gdal_error_handler)

    validate_all("tests/data/GeopackageValidator.gpkg", errors)

    print(json.dumps(errors, indent=4, sort_keys=True))

    print("Validation done")
