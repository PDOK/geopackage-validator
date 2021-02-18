from typing import Iterable, Tuple

from geopackage_validator.constants import VALID_GEOMETRIES
from geopackage_validator.validations import validator


def query_table_geometry_types(dataset) -> Iterable[Tuple[str, str]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )
    for table_name, column_name in columns:
        dataset.ExecuteSQL(f"SELECT load_extension('mod_spatialite');")
        validations = dataset.ExecuteSQL(
            f"SELECT DISTINCT GeometryType({column_name}) as geometry_type FROM {table_name};"
        )
        for (geometry_type,) in validations:
            yield table_name, geometry_type
        dataset.ReleaseResultSet(validations)
    dataset.ReleaseResultSet(columns)


def query_gpkg_metadata_geometry_types(dataset):
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
    message = "Found geometry_type_name: {geometry} for table {table} (from the gpkg_geometry_columns table)."

    def check(self) -> Iterable[str]:
        geometry_types = query_gpkg_metadata_geometry_types(self.dataset)
        return self.gpkg_geometry_valid_check(geometry_types)

    def gpkg_geometry_valid_check(self, geometry_type_names: Iterable[Tuple[str, str]]):
        assert geometry_type_names is not None
        return [
            self.message.format(table=table, geometry_type=geometry_type)
            for table, geometry_type in geometry_type_names
            if geometry_type not in VALID_GEOMETRIES
        ]


class GeometryTypeEqualsGpkgDefinitionValidator(validator.Validator):
    """All table geometries types must match the geometry_type_name from the gpkg_geometry_columns table."""

    code = 15
    level = validator.ValidationLevel.ERROR
    message = "Found geometry: {found_geometry}, in layer: {layer}, where gpkg_geometry is: {gpkg_geometry}."

    def check(self) -> Iterable[str]:
        table_geometry_types = query_table_geometry_types(self.dataset)
        gpkg_table_geometry_types = query_gpkg_metadata_geometry_types(self.dataset)
        return self.gpkg_geometry_match_table_check(
            table_geometry_types, gpkg_table_geometry_types
        )

    @classmethod
    def gpkg_geometry_match_table_check(
        cls,
        table_geometry_type_names: Iterable[Tuple[str, str]],
        gpkg_table_geometry_types: Iterable[Tuple[str, str]],
    ):
        assert table_geometry_type_names is not None
        assert gpkg_table_geometry_types is not None

        results = []

        gpkg_geometry_columns_table = dict(gpkg_table_geometry_types)

        for table_name, table_geometry_type in table_geometry_type_names:

            if table_name not in gpkg_geometry_columns_table.keys():
                raise Exception(f"`{table_name}` not in `gpkg_geometry_columns`")

            feature_type = gpkg_geometry_columns_table[table_name]

            if feature_type != table_geometry_type:
                results.append(
                    cls.message.format(
                        layer=table_name,
                        found_geometry=table_geometry_type,
                        gpkg_geometry=feature_type,
                    )
                )

        return results
