import json
import logging
import time
from datetime import datetime
from typing import Optional

from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)
from geopackage_validator.output import log_output
from geopackage_validator.validations.validate_all import validate_all
from geopackage_validator.validations_overview.validations_overview import (
    result_format,
    VALIDATIONS,
)

logger = logging.getLogger(__name__)


def determine_validations_to_use(
    validations_path: Optional[str], validations: Optional[str]
):
    used_validations = []

    if validations_path is not None:
        used_validations = get_validations_from_file(validations_path)

    if validations is not None and validations != "ALL":
        used_validations.extend(validations.replace(" ", "").split(","))

    if len(used_validations) == 0:
        used_validations = get_all_validations()

    return used_validations


def get_all_validations():
    used_validations = [
        v["validation_code"]
        for k, v in VALIDATIONS.items()
        if v["validation_code"].startswith("R")
    ]

    return used_validations


def get_validations_from_file(validations_path):
    used_validations = []

    with open(validations_path) as json_file:
        used_validations.extend(json.load(json_file)["validations"])
        if len(used_validations) == 0:
            raise Exception("Validation path file does not contain any validations")

    return used_validations


def validate(
    gpkg_path: str,
    filename: str,
    table_definitions_path: str,
    validations_path: str,
    validations: str,
):
    """Starts the geopackage validation."""
    start_time = datetime.now()
    duration_start = time.monotonic()
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here
    from geopackage_validator.gdal.init import init_gdal

    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        results.append(result_format("gdal", [error.replace("\n", " ")]))

    init_gdal(gdal_error_handler)

    validations_executed = determine_validations_to_use(validations_path, validations)

    validate_all(gpkg_path, table_definitions_path, validations_executed, results)

    duration_seconds = time.monotonic() - duration_start

    log_output(
        results=results,
        filename=filename,
        validations_executed=validations_executed,
        start_time=start_time,
        duration_seconds=duration_seconds,
    )
