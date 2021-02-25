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


def columns_definition(layer) -> List[ColumnDefinition]:
    layer_definition = layer.GetLayerDefn()

    assert layer_definition, f'Invalid Layer {"" if not layer else layer.GetName()}'

    field_count = layer_definition.GetFieldCount()
    columns = [
        {
            "name": layer_definition.GetFieldDefn(column_id).name,
            "data_type": layer_definition.GetFieldDefn(column_id).GetTypeName(),
        }
        for column_id in range(field_count)
    ]

    geom_column = geometry_column_definition(layer)
    if geom_column:
        return [geom_column] + columns

    return columns


def geometry_column_definition(layer) -> ColumnDefinition:
    geom_type = (
        ogr.GeometryTypeToName(layer.GetGeomType()).upper().replace(" ", "")
    )

    if geom_type == "NONE":
        return {}

    assert (
        geom_type in VALID_GEOMETRIES
    ), f"{geom_type} for {layer.GetName()} is ot a valid geometry type, geometry type should be one of: {', '.join(VALID_GEOMETRIES)}."

    return {"name": layer.GetGeometryColumn(), "data_type": geom_type}


def generate_table_definitions(dataset: DataSource) -> TableDefinition:
    srs_code = {
        layer.GetSpatialRef().GetAuthorityCode(None)
        for layer in dataset
        if layer.GetSpatialRef()
    }
    assert len(srs_code) == 1, "Expected one projection per geopackage."

    return {
        "geopackage_validator_version": __version__,
        "projection": srs_code.pop(),
        "tables": [
            {
                "name": layer.GetName(),
                "geometry_column": layer.GetGeometryColumn(),
                "columns": columns_definition(layer),
            }
            for layer in dataset
        ],
    }


def generate_definitions_for_path(gpkg_path: str) -> TableDefinition:
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import here

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(gpkg_path, 0)

    return generate_table_definitions(dataset)
