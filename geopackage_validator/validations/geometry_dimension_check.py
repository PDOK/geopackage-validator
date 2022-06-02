from typing import Iterable, Tuple

from geopackage_validator.validations import validator
from geopackage_validator import utils


DIMENSION_QUERY = """
SELECT DISTINCT
    (ST_MinZ("{geom_column_name}") == 0 AND ST_MaxZ("{geom_column_name}") == 0) as z_check,
    (ST_MinM("{geom_column_name}") IS NOT NULL AND
     ST_MinM("{geom_column_name}") == 0 AND ST_MaxM("{geom_column_name}") == 0) as m_check,
     st_ndims("{geom_column_name}") as ndims
FROM "{table_name}" where st_ndims("{geom_column_name}") > 2;
"""

MEASUREMENT_COORDINATE_MESSAGE = "a measurement (M) dimension that are all 0."
ELEVATION_COORDINATE_MESSAGE = "an elevation (Z) dimension that are all 0."
MULTI_DIMENSION_MESSAGE = "more than two dimensions."


def query_dimensions(dataset) -> Iterable[Tuple[str, str]]:
    tables = utils.dataset_geometry_tables(dataset)

    for table_name, column_name, _ in tables:
        validations = dataset.ExecuteSQL(
            DIMENSION_QUERY.format(table_name=table_name, geom_column_name=column_name)
        )

        if validations is not None:
            validation_list = [(z, m, ndims) for z, m, ndims in validations]
            four_dimensions = all(ndims == 4 for z, m, ndims in validation_list)
            m_coordinates_all_0 = all(m for z, m, ndims in validation_list)
            z_coordinates_all_0 = all(z for z, m, ndims in validation_list)
            if len(validation_list):
                yield table_name, MULTI_DIMENSION_MESSAGE
            if four_dimensions and m_coordinates_all_0:
                yield table_name, MEASUREMENT_COORDINATE_MESSAGE
            if z_coordinates_all_0:
                if not m_coordinates_all_0 and four_dimensions:
                    continue
                yield table_name, ELEVATION_COORDINATE_MESSAGE

        dataset.ReleaseResultSet(validations)


class GeometryDimensionValidator(validator.Validator):
    """It is recommended to only use multidimensional geometry coordinates (elevation and measurement) when necessary."""

    code = 19
    level = validator.ValidationLevel.RECCOMENDATION
    message = "Table: {table}, has features with {message}"

    def check(self) -> Iterable[str]:
        query_result = query_dimensions(self.dataset)
        return [
            self.message.format(table=table_name, message=message)
            for table_name, message in query_result
        ]
