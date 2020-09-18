import re
from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
)


def srs_check_query(dataset) -> Iterable[Tuple[str, str]]:
    srs_list = dataset.ExecuteSQL(
        "SELECT organization, organization_coordsys_id AS id FROM gpkg_spatial_ref_sys WHERE id > 0;"
    )

    for srs in srs_list:
        yield srs[0], srs[1]

    dataset.ReleaseResultSet(srs_list)


def srs_equal_check_query(dataset) -> Iterable[Tuple[str, str]]:
    srs_list = dataset.ExecuteSQL("SELECT srs_id FROM gpkg_geometry_columns;")

    for srs in srs_list:
        yield srs[0]

    dataset.ReleaseResultSet(srs_list)


def srs_check(srs_list: Iterable[Tuple[str, str]]):
    assert srs_list is not None

    errors = []
    allowed_list = [28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045,
                    3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409]

    for srs in srs_list:

        organisation = srs[0]
        organization_coordsys_id = srs[1]

        if organisation.lower() is "":
            errors.append(
                create_errormessage(
                    err_index="srs",
                    organisation=organisation,
                    organization_coordsys_id=organization_coordsys_id,
                )
            )

        if organization_coordsys_id not in allowed_list:
            errors.append(
                create_errormessage(
                    err_index="srs",
                    organisation=organisation,
                    organization_coordsys_id=organization_coordsys_id,
                )
            )

    return error_format("columnname", errors)


def srs_equal_check(srs_list: Iterable[Tuple[str, str]]):
    assert srs_list is not None

    errors = []
    srs_check_list = []

    # todo: Finish this
    for columnname in srs_list:
        pass

    return error_format("columnname", errors)