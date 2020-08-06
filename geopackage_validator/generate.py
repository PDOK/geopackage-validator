import logging

from osgeo import ogr

from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)

logger = logging.getLogger(__name__)


def generate_definitions(gpkg_path):
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(gpkg_path, 0)

    tables = dataset.ExecuteSQL(
        "SELECT distinct table_name FROM gpkg_geometry_columns;"
    )
    definitionlist = []
    for table in tables:
        columns = dataset.ExecuteSQL(
            "SELECT column_name, geometry_type_name, srs_id FROM gpkg_geometry_columns where table_name = '{table_name}';".format(
                table_name=table[0]
            )
        )
        columnlist = []
        for column in columns:
            columnlist.append(
                {
                    "column_name": column[0],
                    "geometry_type_name": column[1],
                    "projection": column[2],
                }
            )

        definitionlist.append({"table_name": table[0], "columns": columnlist})
        dataset.ReleaseResultSet(columns)
    dataset.ReleaseResultSet(tables)

    return definitionlist
