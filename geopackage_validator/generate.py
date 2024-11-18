import logging
from typing import List, Optional, Dict

from osgeo.ogr import DataSource, Layer

from geopackage_validator import __version__
from geopackage_validator import utils
from geopackage_validator.models import (
    ColumnDefinition,
    ColumnMapping,
    ForeignKeyDefinition,
    IndexDefinition,
    TableDefinition,
    TablesDefinition,
)
from geopackage_validator.utils import group_by

logger = logging.getLogger(__name__)


def column_definitions(table, geometry_column) -> List[ColumnDefinition]:
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

    fid_columns = fid_column_definition(table)

    return fid_columns + [geometry_column] + columns


def fid_column_definition(table) -> List[ColumnDefinition]:
    name = table.GetFIDColumn()
    if not name:
        return []
    return [ColumnDefinition(name=name, type="INTEGER")]


def get_index_definitions(
    dataset: DataSource, table_name: str
) -> List[IndexDefinition]:
    index_definitions: List[IndexDefinition] = []
    index_list = dataset.ExecuteSQL(
        f"select name, \"unique\", origin from pragma_index_list('{table_name}');"
    )
    pk_in_index_list = False
    for index_listing in index_list:
        pk_in_index_list = pk_in_index_list or index_listing["origin"] == "pk"
        index_definitions.append(
            IndexDefinition(
                columns=tuple(get_index_column_names(dataset, index_listing["name"])),
                unique=bool(int(index_listing["unique"])),
            )
        )
    dataset.ReleaseResultSet(index_list)
    index_definitions = sorted(index_definitions, key=lambda d: d.columns)

    if not pk_in_index_list:
        pk_index = get_pk_index(dataset, table_name)
        if pk_index is not None:
            index_definitions.insert(0, pk_index)

    return index_definitions


def get_pk_index(dataset: DataSource, table_name: str) -> Optional[IndexDefinition]:
    pk_columns = dataset.ExecuteSQL(
        f"select name from pragma_table_info('{table_name}') where pk;"
    )
    column_names = tuple(r["name"] for r in pk_columns)
    if len(column_names) == 0:
        return None
    return IndexDefinition(columns=column_names, unique=True)


def get_index_column_names(dataset: DataSource, index_name: str) -> List[str]:
    index_info = dataset.ExecuteSQL(
        f"select name from pragma_index_info('{index_name}');"
    )
    column_names: List[str] = [r["name"] for r in index_info]
    dataset.ReleaseResultSet(index_info)
    return column_names


def get_foreign_key_definitions(dataset, table_name) -> List[ForeignKeyDefinition]:
    foreign_key_list = dataset.ExecuteSQL(
        f'select id, seq, "table", "from", "to" from pragma_foreign_key_list(\'{table_name}\');'
    )
    foreign_key_definitions: List[ForeignKeyDefinition] = []
    for foreign_key_listing in group_by(foreign_key_list, lambda r: r["id"]):
        table: str = ""
        columns: Dict[str, str] = {}
        for column_reference in foreign_key_listing:
            table = column_reference["table"]
            to = column_reference["to"]
            if to is None:
                pk_index = get_pk_index(dataset, column_reference["table"])
                to = pk_index.columns[int(column_reference["seq"])]
            columns[column_reference["from"]] = to
        foreign_key_definitions.append(
            ForeignKeyDefinition(
                table=table,
                columns=tuple(
                    ColumnMapping(src=c[0], dst=c[1]) for c in columns.items()
                ),
            )
        )
    foreign_key_definitions = sorted(
        foreign_key_definitions, key=lambda fk: (fk.table, (c.src for c in fk.columns))
    )
    dataset.ReleaseResultSet(foreign_key_list)
    return foreign_key_definitions


def generate_table_definitions(
    dataset: DataSource, with_indexes_and_fks: bool = False
) -> TablesDefinition:
    projections = set()
    table_geometry_types = {
        table_name: geometry_type_name
        for table_name, _, geometry_type_name in utils.dataset_geometry_tables(dataset)
    }

    table_list: List[TableDefinition] = []
    for table in dataset:
        table: Layer
        geo_column_name = table.GetGeometryColumn()
        if geo_column_name == "":
            continue

        table_name = table.GetName()
        geometry_column = {
            "name": geo_column_name,
            "type": table_geometry_types[table_name],
        }
        columns = tuple(column_definitions(table, geometry_column))

        indexes = None
        foreign_keys = None
        if with_indexes_and_fks:
            indexes = tuple(get_index_definitions(dataset, table_name))
            foreign_keys = tuple(get_foreign_key_definitions(dataset, table_name))

        table_list.append(
            TableDefinition(
                name=table_name,
                geometry_column=geo_column_name,
                columns=columns,
                indexes=indexes,
                foreign_keys=foreign_keys,
            )
        )

        projections.add(table.GetSpatialRef().GetAuthorityCode(None))

    assert len(projections) == 1, "Expected one projection per geopackage."

    result = TablesDefinition(
        geopackage_validator_version=__version__,
        projection=int(projections.pop()),
        tables=tuple(sorted(table_list, key=lambda t: t.name)),
    )

    return result


def get_datasource_for_path(gpkg_path: str, error_handler=None) -> DataSource:
    """Starts the geopackage validation."""
    utils.check_gdal_version()
    return utils.open_dataset(gpkg_path, error_handler)


def generate_definitions_for_path(
    gpkg_path: str, with_indexes_and_fks: bool = False
) -> TablesDefinition:
    return generate_table_definitions(
        get_datasource_for_path(gpkg_path), with_indexes_and_fks
    )
