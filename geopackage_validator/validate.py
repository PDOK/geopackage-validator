import logging

from geopackage_validator.errors.error_messages import create_errormessage
from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)
from geopackage_validator.output import log_output
from geopackage_validator.validations.validate_all import validate_all


logger = logging.getLogger(__name__)


def validate(gpkg_path):
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here
    from geopackage_validator.gdal.init import init_gdal

    errors = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        errors.append(create_errormessage("gdal", error=error.replace("\n", " ")))

    init_gdal(gdal_error_handler)

    validate_all(gpkg_path, errors)

    log_output(errors)
