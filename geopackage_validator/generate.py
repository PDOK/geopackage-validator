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


def generate_table_definitions(
    dataset: DataSource,
) -> Dict[str, Dict[str, List[Column]]]:
    tables = dataset.ExecuteSQL(
        "SELECT distinct table_name FROM gpkg_geometry_columns;"
    )

    tablelist = {}
    for table in tables:
        columns = dataset.ExecuteSQL(
            "SELECT column_name, geometry_type_name, srs_id FROM gpkg_geometry_columns where table_name = '{table_name}';".format(
                table_name=table[0]
            )
        )
        columnlist = []
        for column in columns:
            columnlist.append(
                Column(
                    column_name=column[0],
                    geometry_type_name=column[1],
                    projection=column[2],
                )
            )

        tablelist[table[0]] = {"table_name": table[0], "columns": columnlist}
        dataset.ReleaseResultSet(columns)
    dataset.ReleaseResultSet(tables)

    return tablelist


def generate_definitions_for_path(gpkg_path: str) -> Dict[str, Dict[str, List[Column]]]:
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(gpkg_path, 0)

    return generate_table_definitions(dataset)
