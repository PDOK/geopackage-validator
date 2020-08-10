import logging
import time
from datetime import datetime

from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)
from geopackage_validator.output import log_output
from geopackage_validator.validations.validate_all import validate_all
from geopackage_validator.validations_overview.validations_overview import (
    get_validations_list,
    error_format,
)

logger = logging.getLogger(__name__)


def validate(gpkg_path, filename, table_definitions_path):
    start_time = datetime.now()
    duration_start = time.monotonic()
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here
    from geopackage_validator.gdal.init import init_gdal

    errors = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        errors.append(error_format("gdal", [error.replace("\n", " ")]))

    init_gdal(gdal_error_handler)

    validate_all(gpkg_path, table_definitions_path, errors)

    duration_seconds = time.monotonic() - duration_start

    log_output(
        errors,
        validations=get_validations_list(),
        filename=filename,
        start_time=start_time,
        duration_seconds=duration_seconds,
    )
