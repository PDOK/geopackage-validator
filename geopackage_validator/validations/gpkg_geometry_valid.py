from typing import Iterable, Tuple

from geopackage_validator.constants import VALID_GEOMETRIES
from geopackage_validator.validations import validator


def query_gpkg_geometry_type_names(dataset) -> Iterable[Tuple[str, str]]:
    geometry_type_names = dataset.ExecuteSQL(
        "SELECT distinct geometry_type_name FROM gpkg_geometry_columns;"
    )

    for geometry_type_name, in geometry_type_names:
        yield geometry_type_name

    dataset.ReleaseResultSet(geometry_type_names)


def gpkg_geometry_match_table_check_query(dataset):
    geometry_type_names = dataset.ExecuteSQL(
        "SELECT table_name, geometry_type_name FROM gpkg_geometry_columns;"
    )

    for table_name, geometry_type_name in geometry_type_names:
        yield table_name, geometry_type_name

    dataset.ReleaseResultSet(geometry_type_names)


class GpkgGeometryTypeNameValidator(validator.Validator):
    """The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON."""

    code = 14
    level = validator.ValidationLevel.ERROR
    message = "Found geometry_type_name: {geometry} (from the gpkg_geometry_columns table)."

    def check(self) -> Iterable[str]:
        geometry_types = gpkg_geometry_match_table_check_query(self.dataset)
        return self.gpkg_geometry_valid_check(geometry_types)

    def gpkg_geometry_valid_check(self, geometry_type_names: Iterable[Tuple[str, str]]):
        assert geometry_type_names is not None
        return [self.message.format(geometry=geometry) for geometry in geometry_type_names if geometry not in VALID_GEOMETRIES]


# TODO: this check is not what they advertise.
class GeometryTypeEqualsGpkgDefinitionValidator(validator.Validator):
    """All table geometries types must match the geometry_type_name from the gpkg_geometry_columns table. (random sample of up to 100)"""

    code = 15
    level = validator.ValidationLevel.ERROR
    message = "Found geometry: {found_geometry}, in layer: {layer}, where gpkg_geometry is: {gpkg_geometry}."

    def check(self) -> Iterable[str]:
        table_geometry_type_names = gpkg_geometry_match_table_check_query(self.dataset)
        gpkg_geometries = query_gpkg_geometry_type_names(self.dataset)
        return self.gpkg_geometry_match_table_check(table_geometry_type_names, gpkg_geometries)

    def gpkg_geometry_match_table_check(self, table_geometry_type_names: Iterable[Tuple[str, str]], gpkg_geometries: Iterable[Tuple[str, str]]):
        assert table_geometry_type_names is not None
        assert gpkg_geometries is not None

        results = []

        gpkg_geometry_columns_table = dict(gpkg_geometries)

        for table_name, table_geometry_type in table_geometry_type_names:

            if table_name not in gpkg_geometry_columns_table.keys():
                raise Exception(f"`{table_name}` not in `gpkg_geometry_columns`")

            feature_type = gpkg_geometry_columns_table[table_name]

            if feature_type != table_geometry_type:
                results.append(
                    self.message.format(
                        layer=table_name,
                        found_geometry=table_geometry_type,
                        gpkg_geometry=feature_type
                    )
                )

        return results
