import json
import logging
import time
from datetime import datetime
from pathlib import Path

from geopackage_validator.constants import EXCLUDED_VALIDATIONS_FROM_ALL
from geopackage_validator.output import log_output
from geopackage_validator import validations
from geopackage_validator.validations.validator import (
    Validator,
    ValidationLevel,
    format_result,
)
from geopackage_validator import gdal_utils


logger = logging.getLogger(__name__)


def validators_to_use(validations_path="", validation_codes=""):
    validator_classes = get_validator_classes()
    if validation_codes == "ALL" or (not validations_path and not validation_codes):
        return [v for v in validator_classes if v.code not in EXCLUDED_VALIDATIONS_FROM_ALL]

    codes = []

    if validations_path:
        validations_from_file = Path(validations_path).read_text()
        try:
            codes += json.loads(validations_from_file)["validations"]
        except KeyError:
            raise Exception("Validation path file does not contain any validations")

    codes += [v for v in validation_codes.replace(" ", "").split(",") if v]

    validator_dict = {v.validation_code: v for v in validator_classes}

    return [validator_dict[code] for code in codes]


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
    gdal_utils.check_gdal_installed()
    gdal_utils.check_gdal_version()

    # Explicit import here
    from geopackage_validator.gdal_utils import init_gdal

    results = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        result = format_result(
            validation_code="GDAL_ERROR",
            validation_description="No unexpected GDAL errors must occur.",
            level=ValidationLevel.UNKNOWN,
            trace=[error.replace("\n", " ")],
        )
        results.append(result)

    init_gdal(gdal_error_handler)

    validators = validators_to_use(validations_path, validations)

    context = {"table_definitions_path": table_definitions_path}

    dataset = gdal_utils.open_dataset(gpkg_path)
    results += [validator(dataset, **context).validate() for validator in validators]

    duration_seconds = time.monotonic() - duration_start

    log_output(
        results=results,
        filename=filename,
        validations_executed=get_validation_codes(validators),
        start_time=start_time,
        duration_seconds=duration_seconds,
    )


def get_validation_descriptions():
    validation_classes = get_validator_classes()
    return {klass.validation_code: klass.__doc__ for klass in validation_classes}


def get_validation_codes(validators):
    return [validator.validation_code for validator in validators]


def get_validator_classes():
    validator_classes = [
        getattr(validations, validator)
        for validator in validations.__all__
        if issubclass(getattr(validations, validator), Validator)
    ]
    return sorted(validator_classes, key=lambda v: (v.level, v.code))
