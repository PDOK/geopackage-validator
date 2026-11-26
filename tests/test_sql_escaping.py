import shutil
import sqlite3
from contextlib import nullcontext
from unittest.mock import Mock

import pytest
from osgeo import ogr, osr

from geopackage_validator import generate, utils
from geopackage_validator.sql import quote_identifier, quote_literal
from geopackage_validator.validations.columnname_check import query_columnames
from geopackage_validator.validations.feature_id_check import (
    query_feature_id,
    query_sequence_for_autoincrement,
)
from geopackage_validator.validations.geometry_ccw_check import query_ccw
from geopackage_validator.validations.geometry_dimension_check import query_dimensions
from geopackage_validator.validations.geometry_empty_check import (
    SQL_EMPTY_TEMPLATE,
    query_geometry_empty,
)
from geopackage_validator.validations.geometry_type_check import (
    query_unexpected_geometry_types,
)
from geopackage_validator.validations.geometry_valid_check import (
    SQL_VALID_TEMPLATE,
    SQL_VALID_TEMPLATE_V0,
    query_geometry_valid,
)
from geopackage_validator.validations.layerfeature_check import (
    query_layerfeature_counts,
)
from geopackage_validator.validations.name_length_check import query_names
from geopackage_validator.validations.rtree_valid_check import rtree_valid_check_query


TABLE = """foo'" UNION SELECT 1 --"""
GEOMETRY = 'geom" || 0 OR 1=1 OR "'
INDEX = "idx' UNION SELECT 'injected' --"
PRAGMA_TABLE = "decoy' ); --"
FEATURE_ID_TABLE = "x' AS table_name, 1 AS pk_present -- "


@pytest.fixture
def quoted_dataset(tmp_path):
    path = str(tmp_path / "quoted.gpkg")
    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.CreateDataSource(path)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(28992)
    layer = dataset.CreateLayer(
        TABLE,
        srs,
        ogr.wkbPolygon25D,
        options=[f"GEOMETRY_NAME={GEOMETRY}", "SPATIAL_INDEX=NO"],
    )
    layer.CreateField(ogr.FieldDefn("BadColumn", ogr.OFTString))
    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetGeometry(
        ogr.CreateGeometryFromWkt("POLYGON Z ((0 0 0,0 1 0,1 0 0,0 0 0))")
    )
    assert layer.CreateFeature(feature) == 0
    feature = None
    layer = None
    dataset = None

    with sqlite3.connect(path) as connection:
        connection.execute(
            f"CREATE INDEX {quote_identifier(INDEX)} ON {quote_identifier(TABLE)} (BadColumn)"
        )
        connection.execute(
            f"CREATE TABLE {quote_identifier('child' + TABLE)} "
            f"(id INTEGER PRIMARY KEY, parent_id INTEGER REFERENCES {quote_identifier(TABLE)}(fid))"
        )
        connection.execute("CREATE TABLE decoy (valid TEXT)")
        connection.execute(
            f"CREATE TABLE {quote_identifier(PRAGMA_TABLE)} (BadName TEXT)"
        )
        connection.execute(
            f"CREATE TABLE {quote_identifier(FEATURE_ID_TABLE)} (id TEXT)"
        )
    return utils.open_dataset(path)


@pytest.mark.parametrize("quote", [quote_identifier, quote_literal])
def test_quote_rejects_nul(quote):
    with pytest.raises(ValueError, match="NUL"):
        quote("name\x00suffix")


def test_quotes_roundtrip_in_sqlite():
    identifier = """name'" --"""
    value = """value'" --"""
    with sqlite3.connect(":memory:") as connection:
        connection.execute(f"CREATE TABLE {quote_identifier(identifier)} (v TEXT)")
        connection.execute(
            f"INSERT INTO {quote_identifier(identifier)} VALUES ({quote_literal(value)})"
        )
        assert connection.execute(
            f"SELECT v FROM {quote_identifier(identifier)}"
        ).fetchone() == (value,)


def test_quoted_table_and_geometry_names_in_validations(quoted_dataset):
    assert (TABLE, "BadColumn") in list(query_columnames(quoted_dataset))
    assert ("column", f"BadColumn (table: {TABLE})", 9) in list(
        query_names(quoted_dataset)
    )
    assert list(query_feature_id(quoted_dataset)) == [(TABLE, 1)]
    assert list(query_sequence_for_autoincrement(quoted_dataset)) == [(TABLE, 1)]
    assert list(query_layerfeature_counts(quoted_dataset)) == [(TABLE, 1, 1)]
    assert list(query_dimensions(quoted_dataset)) == [
        (TABLE, "more than two dimensions."),
        (TABLE, "an elevation (Z) dimension that are all 0."),
    ]
    assert list(query_geometry_empty(quoted_dataset, SQL_EMPTY_TEMPLATE)) == []
    for template in (SQL_VALID_TEMPLATE_V0, SQL_VALID_TEMPLATE):
        assert list(query_geometry_valid(quoted_dataset, template)) == []
    assert list(query_unexpected_geometry_types(quoted_dataset)) == []
    assert list(query_ccw(quoted_dataset)) == [(TABLE, 1, 1)]


def test_geometry_type_literal_is_escaped(quoted_dataset, monkeypatch):
    monkeypatch.setattr(
        utils,
        "dataset_geometry_tables",
        lambda dataset: [(TABLE, GEOMETRY, "POLYGON' OR 1=1 --")],
    )
    assert list(query_unexpected_geometry_types(quoted_dataset)) == [
        (TABLE, "POLYGON", 1, 1, "POLYGON' OR 1=1 --")
    ]


def test_generated_definitions_handle_quoted_names(quoted_dataset):
    assert generate.get_index_column_names(quoted_dataset, INDEX) == ["BadColumn"]
    result = generate.generate_table_definitions(
        quoted_dataset, with_indexes_and_fks=True
    )
    table = result.tables[0]
    assert table.name == TABLE
    assert table.geometry_column == GEOMETRY
    assert any(index.columns == ("BadColumn",) for index in table.indexes)
    foreign_keys = generate.get_foreign_key_definitions(quoted_dataset, "child" + TABLE)
    assert len(foreign_keys) == 1
    assert foreign_keys[0].table == TABLE
    assert foreign_keys[0].columns[0].src == "parent_id"


def test_feature_id_injection_cannot_fabricate_primary_key(quoted_dataset, monkeypatch):
    monkeypatch.setattr(
        utils,
        "dataset_geometry_tables",
        lambda dataset: [(FEATURE_ID_TABLE, "geom", "POINT")],
    )
    assert list(query_feature_id(quoted_dataset)) == [(FEATURE_ID_TABLE, 0)]


def test_pragma_injection_cannot_select_another_table(quoted_dataset, monkeypatch):
    monkeypatch.setattr(
        utils,
        "dataset_geometry_tables",
        lambda dataset: [(PRAGMA_TABLE, "geom", "POINT")],
    )
    assert list(query_columnames(quoted_dataset)) == [(PRAGMA_TABLE, "BadName")]
    assert list(query_names(quoted_dataset)) == [
        ("table", PRAGMA_TABLE, len(PRAGMA_TABLE)),
        ("column", f"BadName (table: {PRAGMA_TABLE})", 7),
    ]


def test_sequence_injection_cannot_match_another_table(quoted_dataset, monkeypatch):
    table = "x' OR 1=1 -- "
    monkeypatch.setattr(
        utils, "dataset_geometry_tables", lambda dataset: [(table, "geom", "POINT")]
    )
    assert list(query_sequence_for_autoincrement(quoted_dataset)) == [(table, 0)]


def test_layer_count_injection_cannot_count_another_table(tmp_path):
    path = str(tmp_path / "layers.gpkg")
    shutil.copyfile("tests/data/test_allcorrect.gpkg", path)
    dataset = ogr.GetDriverByName("GPKG").Open(path, update=1)
    table = 'test_allcorrect" UNION SELECT 1 --'
    layer = dataset.CreateLayer(
        table, geom_type=ogr.wkbPoint, options=["SPATIAL_INDEX=NO"]
    )
    assert layer is not None
    layer = None
    dataset = None

    counts = dict(
        (name, (count, ogr_count))
        for name, count, ogr_count in query_layerfeature_counts(
            utils.open_dataset(path)
        )
    )
    assert counts["test_allcorrect"] == (1, 1)
    assert counts[table] == (0, 0)


def test_rtree_name_is_a_string_literal():
    extensions = Mock()
    extensions.GetFeatureCount.return_value = 1
    dataset = Mock()
    dataset.silence_gdal.return_value = nullcontext()
    dataset.ExecuteSQL.side_effect = [extensions, [(TABLE, GEOMETRY)], [("ok",)]]
    assert list(rtree_valid_check_query(dataset)) == []
    assert dataset.ExecuteSQL.call_args.args[0] == (
        f"select rtreecheck({quote_literal('rtree_' + TABLE + '_' + GEOMETRY)});"
    )
