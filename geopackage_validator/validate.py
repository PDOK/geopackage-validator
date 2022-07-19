from collections import OrderedDict
import logging
import sys
import traceback

from osgeo import gdal

from geopackage_validator.generate import TableDefinition
from geopackage_validator import validations as validation
from geopackage_validator.validations.validator import (
    Validator,
    ValidationLevel,
    format_result,
)
from geopackage_validator import utils


logger = logging.getLogger(__name__)

RQ0 = "RQ0"
RQ3 = "RQ3"
RQ8 = "RQ8"

# Drop legacy requirements
DROP_LEGACY_RQ_FROM_ALL = [RQ0, RQ3]


def validators_to_use(
    validation_codes="", validations_path=None, is_rq8_requested=False
):
    validator_classes = get_validator_classes()
    if validation_codes == "ALL" or (validations_path is None and not validation_codes):
        if not is_rq8_requested:
            rq_drop_list = DROP_LEGACY_RQ_FROM_ALL + [RQ8]
        else:
            rq_drop_list = DROP_LEGACY_RQ_FROM_ALL

        return [v for v in validator_classes if v.validation_code not in rq_drop_list]

    codes = []

    if validations_path is not None:
        try:
            codes += utils.load_config(validations_path)["validations"]
        except KeyError:
            raise Exception("Validation path file does not contain any validations")

    codes += [v for v in validation_codes.replace(" ", "").split(",") if v]

    validator_dict = {v.validation_code: v for v in validator_classes}

    unknown_codes = set(codes) - set(validator_dict.keys())
    if len(unknown_codes):
        if any(
            code
            in (
                "RC1",
                "RC2",
                "RC3",
                "RC4",
            )
            for code in unknown_codes
        ):
            logger.error(
                "unknown validation codes: %s, since pdok-geopackage-validator version 0.8.0 recommendation codes have"
                " been renumbered see: https://github.com/PDOK/geopackage-validator#what-does-it-do for the new codes",
                ",".join(unknown_codes),
            )
        else:
            logger.error("unknown validation codes: %s", ",".join(unknown_codes))
        sys.exit(1)

    return [validator_dict[code] for code in codes]


def validate(
    gpkg_path, table_definitions_path=None, validations_path=None, validations=""
):
    """Starts the geopackage validations."""
    utils.check_gdal_version()

    gdal_error_traces = []
    gdal_warning_traces = []

    # Register GDAL error handler function
    def gdal_error_handler(err_class, err_num, error):
        trace = error.replace("\n", " ")
        # import pdb
        # pdb.set_trace()
        if err_class == gdal.CE_Warning:
            gdal_warning_traces.append(trace)
        else:
            gdal_error_traces.append(trace)

    dataset = utils.open_dataset(gpkg_path, gdal_error_handler)
    if len(gdal_error_traces):
        initial_gdal_traces = [
            gdal_error_traces.pop() for _ in range(len(gdal_error_traces))
        ]
        initial_gdal_errors = [
            format_result(
                validation_code="UNKNOWN_ERROR",
                validation_description="No unexpected (GDAL) errors must occur.",
                level=ValidationLevel.UNKNOWN_ERROR,
                trace=initial_gdal_traces,
            )
        ]
    else:
        initial_gdal_errors = []

    if dataset is None:
        if len(initial_gdal_errors) == 0:
            return (
                [
                    format_result(
                        validation_code="GDAL_ERROR",
                        validation_description="Could not open gpkg.",
                        level=ValidationLevel.UNKNOWN_ERROR,
                        trace=[],
                    )
                ],
                None,
                False,
            )
        return initial_gdal_errors, None, False

    is_rq8_requested = table_definitions_path is not None
    table_definitions = (
        load_table_definitions(table_definitions_path) if is_rq8_requested else None
    )

    validators = validators_to_use(validations, validations_path, is_rq8_requested)

    validation_results = []
    success = not initial_gdal_errors

    for validator in validators:
        validation_error = False
        try:
            result = validator(dataset, table_definitions=table_definitions).validate()

            if result is not None:
                validation_results.append(result)
                validation_error = True
                success = success and validator.level == ValidationLevel.RECCOMENDATION
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = [
                t.strip("\n")
                for t in traceback.format_exception(exc_type, exc_value, exc_traceback)
            ]
            output = format_result(
                validation_code=validator.validation_code,
                validation_description=f"No unexpected errors must occur for: {validator.__doc__}",
                level=validator.level,
                trace=trace,
            )
            validation_results.append(output)
            validation_error = True
            success = False
        current_gdal_error_traces = [
            gdal_error_traces.pop() for _ in range(len(gdal_error_traces))
        ]
        if current_gdal_error_traces:
            success = False
            if validation_error:
                validation_results[-1]["locations"].extend(current_gdal_error_traces)
            else:
                output = format_result(
                    validation_code=validator.validation_code,
                    validation_description=f"No unexpected errors must occur for: {validator.__doc__}",
                    level=validator.level,
                    trace=current_gdal_error_traces,
                )
                validation_results.append(output)

    if gdal_warning_traces:
        output = format_result(
            validation_code="UNKNOWN_WARNINGS",
            validation_description="It is recommended that these unexpected (GDAL) warnings are looked into.",
            level=ValidationLevel.UNKNOWN_WARNING,
            trace=gdal_warning_traces,
        )
        validation_results.append(output)

    return (
        initial_gdal_errors + validation_results,
        get_validation_codes(validators),
        success,
    )


def get_validation_descriptions():
    validation_classes = get_validator_classes()
    return OrderedDict(
        (klass.validation_code, klass.__doc__) for klass in validation_classes
    )


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
    return utils.load_config(table_definitions_path)
