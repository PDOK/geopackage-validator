import logging
from typing import Dict, List

from osgeo import ogr
from osgeo.ogr import DataSource

from geopackage_validator.gdal_utils import check_gdal_version, check_gdal_installed

logger = logging.getLogger(__name__)


TableDefinition = Dict[str, Dict[str, List[Dict[str, str]]]]


def generate_table_definitions(dataset: DataSource) -> TableDefinition:
    geometry_tables = dataset.ExecuteSQL(
        "SELECT distinct table_name FROM gpkg_geometry_columns;"
    )

    projection = None
    geo_column_name = None
    table_list = {}
    for table in geometry_tables:
        columns = dataset.ExecuteSQL(
            "SELECT column_name, geometry_type_name, srs_id FROM gpkg_geometry_columns where table_name = '{table_name}';".format(
                table_name=table[0]
            )
        )

        if columns[0][2] and not projection:
            projection = columns[0][2]

        if columns[0][0] and not geo_column_name:
            geo_column_name = columns[0][0]

        info = dataset.ExecuteSQL(
            "PRAGMA TABLE_INFO('{table_name}');".format(table_name=table[0])
        )

        column_list = [
            dict(column_name=item[1], data_type=item[2].split("(")[0]) for item in info
        ]

        table_list[table[0]] = {
            "table_name": table[0],
            "geometry_column": geo_column_name,
            "columns": column_list,
        }
        dataset.ReleaseResultSet(columns)
        dataset.ReleaseResultSet(info)

    dataset.ReleaseResultSet(geometry_tables)

    result = {"projection": projection}
    result.update(table_list)

    return result


def generate_definitions_for_path(gpkg_path: str) -> TableDefinition:
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(gpkg_path, 0)

    return generate_table_definitions(dataset)
