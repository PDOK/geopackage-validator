import logging
from typing import Dict, List, Union
from collections import OrderedDict

from osgeo import ogr, osr
from osgeo.ogr import DataSource

from geopackage_validator import utils
from geopackage_validator import __version__

logger = logging.getLogger(__name__)

ColumnDefinition = List[Dict[str, str]]
TableDefinition = Dict[str, Union[int, Dict[str, ColumnDefinition]]]


OGR_GEOMETRY_TYPES = {
    "POINT": ogr.wkbPoint,
    "LINESTRING": ogr.wkbLineString,
    "POLYGON": ogr.wkbPolygon,
    "MULTIPOINT": ogr.wkbMultiPoint,
    "MULTILINESTRING": ogr.wkbMultiLineString,
    "MULTIPOLYGON": ogr.wkbMultiPolygon,
}


OGR_FIELD_TYPES = dict(
    **OGR_GEOMETRY_TYPES,
    **{
        "DATE": ogr.OFTDate,
        "DATETIME": ogr.OFTDateTime,
        "TIME": ogr.OFTTime,
        "INTEGER": ogr.OFTInteger,
        "INTEGER64": ogr.OFTInteger64,
        "REAL": ogr.OFTReal,
        "STRING": ogr.OFTString,
        "BINARY": ogr.OFTBinary,
        "INTEGERLIST": ogr.OFTIntegerList,
        "INTEGER64LIST": ogr.OFTInteger64List,
        "REALLIST": ogr.OFTRealList,
        "STRINGLIST": ogr.OFTStringList,
        "WIDESTRING": ogr.OFTWideString,
        "WIDESTRINGLIST": ogr.OFTWideStringList,
    },
)


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


def generate_geopackage_from_table_definition(
    dataset: DataSource, table_definition: TableDefinition
):
    projection = int(table_definition["projection"])
    tables = table_definition["tables"]

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(projection)

    for table in tables:
        try:
            columns = {c["name"]: c["type"] for c in table["columns"]}
        except KeyError:
            try:
                columns = {c["name"]: c["data_type"] for c in table["columns"]}
            except KeyError:
                raise ValueError(
                    f"Table defintion is incomplete or its version is too old"
                )
        try:
            geometry_type = OGR_GEOMETRY_TYPES[columns[table["geometry_column"]]]
        except KeyError:
            raise ValueError(f"Unknown geometry type for table {table['name']}")

        layer = dataset.CreateLayer(table["name"], srs=srs, geom_type=geometry_type)
        try:
            fields = [
                ogr.FieldDefn(column["name"], OGR_FIELD_TYPES[column["type"]])
                for column in table["columns"]
                if column["name"] != table["geometry_column"]
            ]
        except KeyError:
            try:
                fields = [
                    ogr.FieldDefn(column["name"], OGR_FIELD_TYPES[column["data_type"]])
                    for column in table["columns"]
                    if column["name"] != table["geometry_column"]
                ]
            except KeyError:
                raise ValueError(f"Unknown field type for table {table['name']}")

        layer.CreateFields(fields)


def generate_definitions_for_path(gpkg_path: str) -> TableDefinition:
    """Starts the geopackage validation."""
    utils.check_gdal_version()

    dataset = utils.open_dataset(gpkg_path)

    return generate_table_definitions(dataset)


def generate_empty_geopackage(gpkg_path: str, table_definition_path: str):
    utils.check_gdal_version()

    dataset = utils.create_dataset(gpkg_path)
    table_definition = load_table_definitions(table_definition_path)

    return generate_geopackage_from_table_definition(dataset, table_definition)


def load_table_definitions(table_definitions_path) -> TableDefinition:
    return utils.load_config(table_definitions_path)
