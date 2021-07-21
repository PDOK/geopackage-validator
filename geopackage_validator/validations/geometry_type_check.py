from typing import Iterable, Tuple

from geopackage_validator.constants import VALID_GEOMETRIES, MAX_VALIDATION_ITERATIONS
from geopackage_validator.validations import validator
from geopackage_validator import utils


def query_geometry_types(dataset) -> Iterable[Tuple[str, str]]:
    for layer in dataset:
        if not layer.GetGeometryColumn():
            continue

        layer_name = layer.GetName()

        c = 0
        for feature in layer:
            if c >= MAX_VALIDATION_ITERATIONS:
                break

            geom_type = feature.GetGeometryRef().GetGeometryName() or "UNKNOWN"
            feature_id = feature.GetFID()

            if geom_type not in VALID_GEOMETRIES:
                c += 1
                yield layer_name, geom_type, feature_id


SQL_TEMPLATE_TABLE_GEOMETRY_TYPES = """SELECT
    CASE ST_AsText("{column_name}")
        WHEN 'GEOMETRYCOLLECTION()'
            THEN 'GEOMETRYCOLLECTION'
        ELSE ST_GEOMETRYTYPE("{column_name}")
    END AS geom_type
    , count("{column_name}") AS count
    , cast(rowid AS INTEGER) AS row_id
FROM "{table_name}"
WHERE geom_type != '{expected_geometry}'
GROUP BY geom_type;"""


def query_unexpected_geometry_types(dataset) -> Iterable[Tuple[str, str]]:
    geometry_types = utils.dataset_geometry_tables(dataset)

    for table_name, column_name, expected_geometry in geometry_types:
        sql = SQL_TEMPLATE_TABLE_GEOMETRY_TYPES.format(
            table_name=table_name,
            column_name=column_name,
            expected_geometry=expected_geometry,
        )

        validations = dataset.ExecuteSQL(sql)

        if validations is not None:
            for (geometry_type, count, row_id) in validations:
                yield table_name, geometry_type, count, row_id, expected_geometry

        dataset.ReleaseResultSet(validations)


def aggregate(results):
    aggregate = {}

    for layer_name, geom_type, feature_id in results:
        key = (layer_name, geom_type).__hash__()

        if key in aggregate:
            aggregate[key]["amount"] += 1
            aggregate[key]["desc"] = "times, example record id's"
            if aggregate[key]["amount"] <= 5:
                aggregate[key]["rowid_list"] += [feature_id]

            if aggregate[key]["amount"] <= MAX_VALIDATION_ITERATIONS:
                aggregate[key]["desc"] = "times and possibly more, example record id's"
        else:
            aggregate[key] = {
                "layer": layer_name,
                "geometry": geom_type,
                "rowid_list": [feature_id],
                "amount": 1,
                "desc": "time, example record id",
            }

    return aggregate


class GeometryTypeValidator(validator.Validator):
    """Layer features should have an allowed geometry_type (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON)."""

    code = 3
    level = validator.ValidationLevel.ERROR
    message = "Error layer: {layer}, found geometry: {geometry}, {amount} {desc}: {rowid_list}"

    def check(self) -> Iterable[str]:
        geometries = query_geometry_types(self.dataset)
        aggregate_result = aggregate(geometries)
        return [self.message.format(**value) for key, value in aggregate_result.items()]


class GpkgGeometryTypeNameValidator(validator.Validator):
    """The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON."""

    code = 14
    level = validator.ValidationLevel.ERROR
    message = "Found geometry_type_name: {geometry_type} for table {table} (from the gpkg_geometry_columns table)."

    def check(self) -> Iterable[str]:
        geometry_types = utils.dataset_geometry_tables(self.dataset)
        return self.gpkg_geometry_valid_check(geometry_types)

    @classmethod
    def gpkg_geometry_valid_check(cls, geometry_type_names: Iterable[Tuple[str, str]]):
        assert geometry_type_names is not None
        return [
            cls.message.format(table=table, geometry_type=geometry_type)
            for table, _, geometry_type in geometry_type_names
            if geometry_type not in VALID_GEOMETRIES
        ]


class GeometryTypeEqualsGpkgDefinitionValidator(validator.Validator):
    """All table geometries types must match the geometry_type_name from the gpkg_geometry_columns table."""

    code = 15
    level = validator.ValidationLevel.ERROR
    message = "Error layer: {table_name}, found geometry: {geometry_type} that should be {expected_geometry}, {count} {count_label}, example id: {row_id}"

    def check(self) -> Iterable[str]:
        result = query_unexpected_geometry_types(self.dataset)

        return [
            self.message.format(
                table_name=table_name,
                geometry_type=geometry_type,
                count=count,
                count_label=("time" if count == 1 else "times"),
                row_id=row_id,
                expected_geometry=expected_geometry,
            )
            for table_name, geometry_type, count, row_id, expected_geometry in result
        ]
