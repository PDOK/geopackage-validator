import logging
from typing import Dict, List

from osgeo import ogr
from osgeo.ogr import DataSource

from geopackage_validator.gdal_utils import check_gdal_version, check_gdal_installed
from geopackage_validator.constants import VALID_GEOMETRIES
from geopackage_validator import __version__

logger = logging.getLogger(__name__)

ColumnDefinition = Dict[str, str]
TableDefinition = Dict[str, Dict[str, List[ColumnDefinition]]]


def columns_definition(table) -> List[ColumnDefinition]:
    layer_definition = table.GetLayerDefn()

    assert layer_definition, f'Invalid Layer {"" if not table else table.GetName()}'

    field_count = layer_definition.GetFieldCount()
    columns = [
        {
            "name": layer_definition.GetFieldDefn(column_id).name,
            "data_type": layer_definition.GetFieldDefn(column_id).GetTypeName(),
        }
        for column_id in range(field_count)
    ]

    geom_column = geometry_column_definition(table)
    if geom_column:
        return [geom_column] + columns

    return columns


def geometry_column_definition(table) -> ColumnDefinition:
    geom_type = ogr.GeometryTypeToName(table.GetGeomType()).upper().replace(" ", "")

    if geom_type == "NONE":
        return {}

    assert (
        geom_type in VALID_GEOMETRIES
    ), f"{geom_type} for {table.GetName()} is ot a valid geometry type, geometry type should be one of: {', '.join(VALID_GEOMETRIES)}."

    return {"name": table.GetGeometryColumn(), "data_type": geom_type}


def generate_table_definitions(dataset: DataSource) -> TableDefinition:
    projections = set()

    table_list = []
    for table in dataset:
        geo_column_name = table.GetGeometryColumn()
        if geo_column_name == "":
            continue

        table_list.append(
            {
                "name": table.GetName(),
                "geometry_column": geo_column_name,
                "columns": columns_definition(table),
            }
        )

        projections.add(table.GetSpatialRef().GetAuthorityCode(None))

    assert len(projections) == 1, "Expected one projection per geopackage."

    result = {
        "geopackage_validator_version": __version__,
        "projection": projections.pop(),
        "tables": table_list,
    }

    return result


def generate_definitions_for_path(gpkg_path: str) -> TableDefinition:
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(gpkg_path, 0)

    return generate_table_definitions(dataset)
