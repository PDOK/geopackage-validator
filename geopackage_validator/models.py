import copy
from typing import Optional, Tuple

from pydantic import BaseModel, Field, field_validator, ConfigDict
from semver import Version


class Named(BaseModel):
    name: str


class ColumnDefinition(Named):
    model_config = ConfigDict(frozen=True)

    type: str


class IndexDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    columns: Tuple[str, ...] = Field(min_length=1)
    unique: bool = False


class ColumnMapping(BaseModel):
    model_config = ConfigDict(frozen=True)

    src: str
    dst: str


class ForeignKeyDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    @field_validator("columns")
    @classmethod
    def unique_src_columns(
        cls, v: Tuple[ColumnMapping, ...]
    ) -> Tuple[ColumnMapping, ...]:
        src_columns = set()
        for c in v:
            if c.src in src_columns:
                raise ValueError(f"Duplicate src column detected: {c.src}")
            src_columns.add(c.src)
        return v

    table: str = Field(min_length=1)
    columns: Tuple[ColumnMapping, ...] = Field(min_length=1)


class TableDefinition(Named):
    model_config = ConfigDict(frozen=True)

    geometry_column: str = "geom"
    columns: Tuple[ColumnDefinition, ...] = tuple()
    """Ordered as in the table (left to right), but with FID and geometry columns always first.
    (This order is not validated.)"""
    indexes: Optional[Tuple[IndexDefinition, ...]] = None
    """None means: don't validate. Empty list means: there should be no indexes."""
    foreign_keys: Optional[Tuple[ForeignKeyDefinition, ...]] = None
    """None means: don't validate. Empty list means: there should be no foreign keys."""


class TablesDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    geopackage_validator_version: str = "0"
    projection: Optional[int]
    tables: Tuple[TableDefinition, ...]
    """Ordered by table name"""

    def with_indexes_and_fks(self) -> bool:
        for table in self.tables:
            if table.indexes is not None or table.foreign_keys is not None:
                return True
        return False


def migrate_tables_definition(original: dict) -> dict:
    """Migrate a possibly old tables definition to new schema/model"""
    # older versions were not versioned (?), so assuming "0.0.0" if there is no version
    version = Version.parse(original.get("geopackage_validator_version", "0.0.0"))
    if version == Version(0, 0, 0, "dev"):
        return original
    # nothing changed after v0.5.8
    if version > Version(0, 5, 8):
        return original
    migrated = copy.deepcopy(original)
    # until and including 0.5.8, column's "type" property was named "data_type"
    if version <= Version(0, 5, 8):
        for t in migrated.get("tables", []):
            for c in t.get("columns", []):
                c["type"] = c["data_type"]
                del c["data_type"]
    return migrated
