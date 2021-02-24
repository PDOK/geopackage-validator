import json
import logging
from pathlib import Path
import sys
import traceback

from geopackage_validator.generate import TableDefinition
from geopackage_validator import validations as validation
from geopackage_validator.validations.validator import (
    Validator,
    ValidationLevel,
    format_result,
)
from geopackage_validator import gdal_utils


logger = logging.getLogger(__name__)

RQ8 = "RQ8"


def validators_to_use(
    validation_codes="", validations_path=None, is_rq8_requested=False
):
    validator_classes = get_validator_classes()
    if validation_codes == "ALL" or (validations_path is None and not validation_codes):
        if not is_rq8_requested:
            return [v for v in validator_classes if v.validation_code != RQ8]
        else:
            return validator_classes

    codes = []

    if validations_path is not None:
        validations_from_file = Path(validations_path).read_text()
        try:
            codes += json.loads(validations_from_file)["validations"]
        except KeyError:
            raise Exception("Validation path file does not contain any validations")

    codes += [v for v in validation_codes.replace(" ", "").split(",") if v]

    validator_dict = {v.validation_code: v for v in validator_classes}

    return [validator_dict[code] for code in codes]


def validate(
    gpkg_path, table_definitions_path=None, validations_path=None, validations=""
):
    """Starts the geopackage validations."""
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

    dataset = gdal_utils.open_dataset(gpkg_path)

    if dataset is None:
        return results, None, False

    is_rq8_requested = table_definitions_path is not None
    table_definitions = (
        load_table_definitions(table_definitions_path) if is_rq8_requested else None
    )

    validators = validators_to_use(validations, validations_path, is_rq8_requested)

    validation_results = []
    success = True

    try:
        for validator in validators:
            result = validator(dataset, table_definitions=table_definitions).validate()

            if result is not None:
                validation_results.append(result)
                success = success and validator.level == ValidationLevel.RECCOMENDATION
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = [
            t.strip("\n")
            for t in traceback.format_exception(exc_type, exc_value, exc_traceback)
        ]
        output = format_result(
            validation_code="ERROR",
            validation_description="No unexpected errors must occur.",
            level=ValidationLevel.UNKNOWN,
            trace=trace,
        )
        return [output] + results, None, False

    # results has values when a gdal error is thrown:
    success = success and not results

    return results + validation_results, get_validation_codes(validators), success


def get_validation_descriptions():
    validation_classes = get_validator_classes()
    return {klass.validation_code: klass.__doc__ for klass in validation_classes}


def get_validation_codes(validators):
    return [validator.validation_code for validator in validators]


def get_validator_classes():
    validator_classes = [
        getattr(validation, validator)
        for validator in validation.__all__
        if issubclass(getattr(validation, validator), Validator)
    ]
    return sorted(validator_classes, key=lambda v: (v.level, v.code))


def load_table_definitions(table_definitions_path) -> TableDefinition:
    path = Path(table_definitions_path)
    assert path.exists()
    return json.loads(path.read_text())
