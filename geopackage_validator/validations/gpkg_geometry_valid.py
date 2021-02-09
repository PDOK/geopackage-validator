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


def gpkg_geometry_match_table_check_query(dataset):
    geometry_type_names = dataset.ExecuteSQL(
        "SELECT table_name, geometry_type_name FROM gpkg_geometry_columns;"
    )

    for geometry_type_name in geometry_type_names:
        yield geometry_type_name[0], geometry_type_name[1]

    dataset.ReleaseResultSet(geometry_type_names)


def gpkg_geometry_match_table_check(table_geometry_type_names, gpkg_geometries):
    assert table_geometry_type_names is not None
    assert gpkg_geometries is not None

    results = []

    # todo: does not take into consideration that there could be multiple geometries -> there should be a test that takes this upfront
    gpkg_geometry_columns_table = {r[0]: r[1] for r in gpkg_geometries}
    # test = {r[0]: r[1] for r in table_geometry_type_names}

    for feature in table_geometry_type_names:
        table_name = feature[0]
        table_geometry_type = feature[1]

        # todo: There should be a test upfront that rules out that `gpkg_geometry_columns` matches the actual features
        if table_name not in gpkg_geometry_columns_table:
            raise Exception(
                f"`gpkg_geometry_columns` does not contain feature `{table_name}`"
            )

        actual_feature_type = gpkg_geometry_columns_table[table_name]

        if actual_feature_type != table_geometry_type:
            results.append(
                create_validation_message(
                    err_index="gpkg_geometry_match_table",
                    layer=table_name,
                    found_geometry=table_geometry_type,
                    gpkg_geometry=actual_feature_type,
                )
            )

    return result_format("gpkg_geometry_match_table", results)
