import pytest

from geopackage_validator import utils
from geopackage_validator.validations.columnname_check import query_columnames
from geopackage_validator.validations.geometry_dimension_check import query_dimensions


class FakeDataset:
    def __init__(self):
        self.queries = []

    def ExecuteSQL(self, query):
        self.queries.append(query)
        return []

    def ReleaseResultSet(self, _):
        return None


def test_quote_sqlite_string():
    assert utils.quote_sqlite_string("a'b") == "'a''b'"


def test_quote_sqlite_identifier():
    assert utils.quote_sqlite_identifier('a"b') == '"a""b"'


def test_quote_sqlite_string_rejects_nul():
    with pytest.raises(ValueError, match="NUL"):
        utils.quote_sqlite_string("a\x00b")


def test_quote_sqlite_identifier_rejects_nul():
    with pytest.raises(ValueError, match="NUL"):
        utils.quote_sqlite_identifier("a\x00b")


def test_query_columnnames_escapes_table_name(monkeypatch):
    dataset = FakeDataset()
    monkeypatch.setattr(
        "geopackage_validator.validations.columnname_check.utils.dataset_geometry_tables",
        lambda _: [("x'; select 1; --", "geom", "POINT")],
    )

    list(query_columnames(dataset))

    assert dataset.queries == ["PRAGMA TABLE_INFO('x''; select 1; --');"]


def test_query_dimensions_escapes_identifiers(monkeypatch):
    dataset = FakeDataset()
    monkeypatch.setattr(
        "geopackage_validator.validations.geometry_dimension_check.utils.dataset_geometry_tables",
        lambda _: [('demo" WHERE 0 UNION SELECT 1 --', 'g"eom', "POINT")],
    )

    list(query_dimensions(dataset))

    query = dataset.queries[0]
    assert 'FROM "demo"" WHERE 0 UNION SELECT 1 --"' in query
    assert 'st_ndims("g""eom") > 2' in query
