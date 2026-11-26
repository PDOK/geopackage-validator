from typing import Iterable, Tuple

from geopackage_validator import utils
from geopackage_validator.validations import validator


def query_ccw(dataset) -> Iterable[Tuple[str, str]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns "
        "  WHERE geometry_type_name in ('POLYGON', 'MULTIPOLYGON');"
    )

    for table_name, column_name in columns:
        table_name_quoted = utils.quote_sqlite_identifier(table_name)
        column_name_quoted = utils.quote_sqlite_identifier(column_name)
        sql = (
            f"SELECT cast(rowid AS INTEGER) AS row_id, count({column_name_quoted}) as amount "
            f"FROM {table_name_quoted} WHERE NOT ST_IsPolygonCCW({column_name_quoted});"
        )
        validations = dataset.ExecuteSQL(sql)

        if validations is not None:
            for (row_id, count) in validations:
                if count > 0:
                    yield table_name, row_id, count

        dataset.ReleaseResultSet(validations)
    dataset.ReleaseResultSet(columns)


class PolygonWindingOrderValidator(validator.Validator):
    """It is recommended that all (MULTI)POLYGON geometries have a counter-clockwise orientation for their exterior ring, and a clockwise direction for all interior rings."""

    code = 20
    level = validator.ValidationLevel.RECOMMENDATION
    message = "Warning layer: {layer}, example id: {row_id}, has {count} features that do not have a counter-clockwise exterior ring and/or a clockwise interior ring."

    def check(self) -> Iterable[str]:
        result = query_ccw(self.dataset)
        return [
            self.message.format(layer=layer_name, row_id=row_id, count=count)
            for layer_name, row_id, count in result
        ]
