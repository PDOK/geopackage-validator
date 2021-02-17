import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)
from geopackage_validator.output import log_output
from geopackage_validator import validations
from geopackage_validator.validations.validator import Validator
from geopackage_validator.generate import TableDefinition


from geopackage_validator.validations_overview.validations_overview import (
    result_format,
    VALIDATIONS,
)

logger = logging.getLogger(__name__)


# TODO: this is really complex for what it ought to do. this can be 10 lines tops.


def validations_to_use(validations_path="", validations=""):
    if validations == "ALL" or (not validations_path and not validations):
        return "ALL"

    validations = validations.replace(" ", "").split(",")

    if validations_path:
        validations_from_file = Path(validations_path).read_text()
        try:
            validations += json.loads(validations_from_file)["validations"]
        except KeyError:
            raise Exception("Validation path file does not contain any validations")

    return validations


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

    # TODO: handle with Validator or create ErrorHandler that is inherited by Validator?
    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        result = result_format("gdal", [error.replace("\n", " ")])
        results.extend(result)

    init_gdal(gdal_error_handler)

    validations_to_execute = validations_to_use(validations_path, validations)

    # todo: load in lower level or refactor lower code
    table_definitions = load_table_definitions(table_definitions_path)

    results += validate_all(gpkg_path, validations_to_execute, table_definitions)

    duration_seconds = time.monotonic() - duration_start

    log_output(
        results=results,
        filename=filename,
        validations_executed=validations_to_execute,
        start_time=start_time,
        duration_seconds=duration_seconds,
    )


def validate_all(gpkg_path, requested_validations, table_definitions):
    validator_classes = [getattr(validations, v) for v in validations.__all__]
    results = []

    for validator in validator_classes:
        is_validator = issubclass(validator, Validator)
        validator_is_requested = is_validator and (
            requested_validations == "ALL"
            or validator.validation_code in requested_validations
        )
        if validator_is_requested:
            results += validator(gpkg_path, table_definitions).validate()

    return results


def load_table_definitions(definitions_path) -> TableDefinition:
    # path = Path(definitions_path)
    # assert path.exists()
    # return json.loads(path.read_text())
    pass
