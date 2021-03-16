from typing import Iterable, Tuple

from geopackage_validator.validations import validator

DIMENSION_QUERY = """
SELECT DISTINCT
    (ST_MinZ({geom_column_name}) == 0 AND ST_MaxZ({geom_column_name}) == 0) as z_check,
    (ST_MinM({geom_column_name}) IS NOT NULL AND
     ST_MinM({geom_column_name}) == 0 AND ST_MaxM({geom_column_name}) == 0) as m_check,
     st_ndims({geom_column_name}) as ndims
FROM {table_name} where st_ndims({geom_column_name}) > 2;
"""

MEASUREMENT_COORDINATE_NAME = "measurement (M)"
ELEVATION_COORDINATE_NAME = "elevation (Z)"


def query_dimensions(dataset) -> Iterable[Tuple[str, str]]:
    columns = dataset.ExecuteSQL(
        "SELECT table_name, column_name FROM gpkg_geometry_columns;"
    )

    for table_name, column_name in columns:
        validations = dataset.ExecuteSQL(
            DIMENSION_QUERY.format(table_name=table_name, geom_column_name=column_name)
        )

        if validations is not None:
            validation_list = [(z, m, ndims) for z, m, ndims in validations]
            four_dimensions = all(ndims == 4 for z, m, ndims in validation_list)
            m_coordinates_all_0 = all(m for z, m, ndims in validation_list)
            z_coordinates_all_0 = all(z for z, m, ndims in validation_list)
            if four_dimensions and m_coordinates_all_0:
                yield table_name, MEASUREMENT_COORDINATE_NAME
            if z_coordinates_all_0:
                if not m_coordinates_all_0 and four_dimensions:
                    continue
                yield table_name, ELEVATION_COORDINATE_NAME

        dataset.ReleaseResultSet(validations)
    dataset.ReleaseResultSet(columns)


class GeometryDimensionValidator(validator.Validator):
    """It is recommended that multidimensional geometry coordinates (elevation and measurement) contain values."""

    code = 3
    level = validator.ValidationLevel.RECCOMENDATION
    message = (
        "Table: {table}, has features with a {dimension_name} dimension that are all 0."
    )

    def check(self) -> Iterable[str]:
        query_result = query_dimensions(self.dataset)
        return [
            self.message.format(table=table_name, dimension_name=dimension_name)
            for table_name, dimension_name in query_result
        ]
