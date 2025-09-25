from typing import Iterable, Tuple

from osgeo import gdal
from geopackage_validator.validations import validator


class AttributeNoGeometryValidator(validator.Validator):
    code = 26
    level = validator.ValidationLevel.ERROR
    message = "Found geometry column in non-geometry table: {table_name}"

    def check(self) -> List[str]:
        query = """
                SELECT gc.table_name \
                FROM gpkg_contents AS gc \
                         JOIN gpkg_geometry_columns AS ggc ON gc.table_name = ggc.table_name
                WHERE gc.data_type = 'attributes'; \
                """
        attribute_table_with_geom_column = self.dataset.ExecuteSQL(query)
        return (
            [
                self.message.format(table_name=attr[0])
                for attr in attribute_table_with_geom_column
            ]
            if attribute_table_with_geom_column
            else []
        )
