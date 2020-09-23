from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
)


ALLOWED_LIST = [
    28992,
    3034,
    3035,
    3038,
    3039,
    3040,
    3041,
    3042,
    3043,
    3044,
    3045,
    3046,
    3047,
    3048,
    3049,
    3050,
    3051,
    4258,
    4936,
    4937,
    5730,
    7409,
]


def srs_check_query(dataset) -> Iterable[Tuple[str, str]]:
    srs_list = dataset.ExecuteSQL(
        """
        SELECT organization, organization_coordsys_id AS id, srs_name 
        FROM gpkg_geometry_columns 
        JOIN gpkg_spatial_ref_sys gsrs on gsrs.srs_id = gpkg_geometry_columns.srs_id;"""
    )

    for srs in srs_list:
        yield srs[0], srs[1], srs[2]

    dataset.ReleaseResultSet(srs_list)


def srs_equal_check_query(dataset) -> Iterable[Tuple[str, str]]:
    srs_list = dataset.ExecuteSQL("SELECT srs_id FROM gpkg_geometry_columns;")

    for srs in srs_list:
        yield srs[0]

    dataset.ReleaseResultSet(srs_list)


def srs_check(srs_list: Iterable[Tuple[str, str]]):
    assert srs_list is not None

    errors = []

    for srs_organisation, srs_id, srs_name in srs_list:

        if srs_organisation != "EPSG":
            errors.append(
                create_errormessage(
                    err_index="srs",
                    srs_organisation=srs_organisation,
                    srs_id=srs_id,
                    srs_name=srs_name,
                )
            )

        if srs_id not in ALLOWED_LIST:
            errors.append(
                create_errormessage(
                    err_index="srs",
                    srs_organisation=srs_organisation,
                    srs_id=srs_id,
                    srs_name=srs_name,
                )
            )

    return error_format("srs", errors)


def srs_equal_check(srs_list: Iterable[Tuple[str, str]]):
    assert srs_list is not None

    errors = []
    srs_id_list = []

    for srs in srs_list:
        srs_id = srs[0]
        srs_id_list.append(srs_id)

    srs_id_list = set(srs_id_list)

    if len(srs_id_list) > 1:
        errors.append(
            create_errormessage(err_index="srs_equal", srs=", ".join(srs_id_list),)
        )

    return error_format("srs_equal", errors)
