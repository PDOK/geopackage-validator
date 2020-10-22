from typing import Iterable, Tuple

from geopackage_validator.constants import VALID_GEOMETRIES
from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def gpkg_geometry_valid_check_query(dataset) -> Iterable[Tuple[str, str]]:
    geometry_type_names = dataset.ExecuteSQL(
        "SELECT distinct geometry_type_name FROM gpkg_geometry_columns;"
    )

    for geometry_type_name in geometry_type_names:
        yield geometry_type_name[0]

    dataset.ReleaseResultSet(geometry_type_names)


def gpkg_geometry_valid_check(geometry_type_names: Iterable[Tuple[str, str]]):
    assert geometry_type_names is not None

    results = []

    for geometry in geometry_type_names:
        if geometry not in VALID_GEOMETRIES:
            results.append(
                create_validation_message(
                    err_index="gpkg_geometry_valid",
                    found_geometry=geometry,
                    valid_geometries=",".join(VALID_GEOMETRIES),
                )
            )

    return result_format("gpkg_geometry_valid", results)


def gpkg_geometry_match_table_check(
    table_geometry_type_names: Iterable[Tuple[str, str]], gpkg_geometries
):
    assert table_geometry_type_names is not None

    results = []

    for gpkg_geometry in gpkg_geometries:
        for table_geometry in table_geometry_type_names:
            if table_geometry[1] != gpkg_geometry:
                results.append(
                    create_validation_message(
                        err_index="gpkg_geometry_match_table",
                        layer=table_geometry[0],
                        found_geometry=table_geometry[1],
                        gpkg_geometry=gpkg_geometry,
                    )
                )

    return result_format("gpkg_geometry_match_table", results)
