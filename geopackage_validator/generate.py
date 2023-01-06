import logging
from typing import Dict, List, Union
from collections import OrderedDict

from osgeo import ogr
from osgeo.ogr import DataSource

from geopackage_validator import utils
from geopackage_validator import __version__

logger = logging.getLogger(__name__)

ColumnDefinition = List[Dict[str, str]]
TableDefinition = Dict[str, Union[int, Dict[str, ColumnDefinition]]]


def columns_definition(table, geometry_column) -> ColumnDefinition:
    layer_definition = table.GetLayerDefn()

    assert layer_definition, f'Invalid Layer {"" if not table else table.GetName()}'

    field_count = layer_definition.GetFieldCount()
    columns = [
        {
            "name": layer_definition.GetFieldDefn(column_id).name,
            "type": layer_definition.GetFieldDefn(column_id).GetTypeName().upper(),
        }
        for column_id in range(field_count)
    ]

    fid_column = fid_column_definition(table)

    return fid_column + [geometry_column] + columns


def fid_column_definition(table) -> ColumnDefinition:
    name = table.GetFIDColumn()
    if not name:
        return []
    return [{"name": name, "type": "INTEGER"}]


def generate_table_definitions(dataset: DataSource) -> TableDefinition:
    projections = set()
    table_geometry_types = {
        table_name: geometry_type_name
        for table_name, _, geometry_type_name in utils.dataset_geometry_tables(dataset)
    }

    table_list = []
    for table in dataset:
        geo_column_name = table.GetGeometryColumn()
        if geo_column_name == "":
            continue

        table_name = table.GetName()
        geometry_column = {
            "name": geo_column_name,
            "type": table_geometry_types[table_name],
        }
        table_list.append(
            OrderedDict(
                [
                    ("name", table_name),
                    ("geometry_column", geo_column_name),
                    ("columns", columns_definition(table, geometry_column)),
                ]
            )
        )

        projections.add(table.GetSpatialRef().GetAuthorityCode(None))

    assert len(projections) == 1, "Expected one projection per geopackage."

    result = OrderedDict(
        [
            ("geopackage_validator_version", __version__),
            ("projection", int(projections.pop())),
            ("tables", table_list),
        ]
    )

    return result


def generate_definitions_for_path(gpkg_path: str) -> TableDefinition:
    """Starts the geopackage validation."""
    utils.check_gdal_version()

    dataset = utils.open_dataset(gpkg_path)

    return generate_table_definitions(dataset)
