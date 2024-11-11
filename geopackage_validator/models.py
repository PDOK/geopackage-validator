import copy
from typing import List, Optional

from pydantic import BaseModel


class Named(BaseModel):
    name: str


class ColumnDefinition(Named):
    type: str


class TableDefinition(Named):
    geometry_column: str = "geom"
    columns: List[ColumnDefinition] = []


class TablesDefinition(BaseModel):
    geopackage_validator_version: str = "0"
    projection: Optional[int]
    tables: List[TableDefinition]


def migrate_tables_definition(old: dict) -> dict:
    """Migrate a possibly old tables definition to new schema/model"""
    version = old.get("geopackage_validator_version", "0")
    # older versions where not versioned (?), so assuming "0" if there is no version
    version_tuple = tuple(int(v) for v in version.split("."))
    if version_tuple == (0, 0, 0, "-dev") or version_tuple > (
        0,
        5,
        8,
    ):  # no changes after 0.5.8
        return old
    new = copy.deepcopy(old)
    if version_tuple <= (
        0,
        5,
        8,
    ):  # until 0.5.8, column's "type" property was named "data_type"
        for t in new.get("tables", []):
            for c in t.get("columns", []):
                c["type"] = c["data_type"]
                del c["data_type"]
    return new
