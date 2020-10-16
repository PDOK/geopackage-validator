from typing import Iterable, Tuple

from geopackage_validator.constants import ALLOWED_PROJECTIONS_LIST
from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


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

    results = []

    for srs_organisation, srs_id, srs_name in srs_list:

        if srs_organisation != "EPSG":
            results.append(
                create_validation_message(
                    err_index="srs",
                    srs_organisation=srs_organisation,
                    srs_id=srs_id,
                    srs_name=srs_name,
                )
            )

        if srs_id not in ALLOWED_PROJECTIONS_LIST:
            results.append(
                create_validation_message(
                    err_index="srs",
                    srs_organisation=srs_organisation,
                    srs_id=srs_id,
                    srs_name=srs_name,
                )
            )

    return result_format("srs", results)


def srs_equal_check(srs_list: Iterable[Tuple[str, str]]):
    assert srs_list is not None

    results = []
    srs_id_list = []

    for srs_id in srs_list:
        srs_id_list.append(srs_id)

    srs_id_list = set(srs_id_list)

    if len(srs_id_list) > 1:
        results.append(
            create_validation_message(
                err_index="srs_equal", srs=", ".join(srs_id_list),
            )
        )

    return result_format("srs_equal", results)
