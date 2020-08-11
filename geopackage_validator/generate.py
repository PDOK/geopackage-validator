import logging
from typing import Dict, List, TypedDict

from osgeo import ogr
from osgeo.ogr import DataSource

from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)

logger = logging.getLogger(__name__)


class Column(TypedDict):
    column_name: str
    geometry_type_name: str
    projection: str
    data_type: str


def generate_table_definitions(
    dataset: DataSource,
) -> Dict[str, Dict[str, List[Column]]]:
    geometry_tables = dataset.ExecuteSQL(
        "SELECT distinct table_name FROM gpkg_geometry_columns;"
    )

    tablelist = {}
    for table in geometry_tables:
        columns = dataset.ExecuteSQL(
            "SELECT column_name, geometry_type_name, srs_id FROM gpkg_geometry_columns where table_name = '{table_name}';".format(
                table_name=table[0]
            )
        )
        info = dataset.ExecuteSQL(
            "PRAGMA TABLE_INFO('{table_name}');".format(table_name=table[0])
        )
        columnlist = [Column(column_name=item[1], data_type=item[2]) for item in info]
        columnlist.extend(
            [
                Column(
                    column_name=column[0],
                    geometry_type_name=column[1],
                    projection=column[2],
                )
                for column in columns
            ]
        )

        tablelist[table[0]] = {"table_name": table[0], "columns": columnlist}
        dataset.ReleaseResultSet(columns)
        dataset.ReleaseResultSet(info)
    dataset.ReleaseResultSet(geometry_tables)

    return tablelist


def generate_definitions_for_path(gpkg_path: str) -> Dict[str, Dict[str, List[Column]]]:
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(gpkg_path, 0)

    return generate_table_definitions(dataset)
