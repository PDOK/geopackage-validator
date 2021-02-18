from geopackage_validator.generate import generate_definitions_for_path
from geopackage_validator.validate import load_table_definitions
from geopackage_validator.validations.table_definitions_check import (
    TableDefinitionValidator,
)


def test_table_definitions_input_is_none():
    current_definitions = generate_definitions_for_path(
        "tests/data/test_allcorrect.gpkg"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=None
    ).check_table_definitions(current_definitions)

    assert len(diff) == 1
    assert diff[0] == "Difference: Missing '--table-definitions-path' input"


def test_table_definitions_check_correct():
    current_definitions = generate_definitions_for_path(
        "tests/data/test_allcorrect.gpkg"
    )

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 0


def test_table_definitions_check_incorrect_geometry():
    current_definitions = {
        "projection": 28992,
        "test_allcorrect": {
            "table_name": "test_allcorrect",
            "geometry_column": "geometry",
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geometry", "data_type": "POINT"},
            ],
        },
    }

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 1


def test_table_definitions_check_incorrect_projection():
    current_definitions = {
        "projection": 4326,
        "test_allcorrect": {
            "table_name": "test_allcorrect",
            "geometry_column": "geometry",
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geometry", "data_type": "POLYGON"},
            ],
        },
    }

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 1
    assert (
        diff[0] == "Difference: Value of root['projection'] changed from 28992 to 4326."
    )


def test_table_definitions_check_incorrect_column_name():
    current_definitions = {
        "projection": 28992,
        "test_allcorrect": {
            "table_name": "test_allcorrect",
            "geometry_column": "geometry",
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geom", "data_type": "POLYGON"},
            ],
        },
    }

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 1


def test_table_definitions_check_table_changed():
    current_definitions = {
        "projection": 28992,
        "test_different_table": {
            "table_name": "test_different_table",
            "geometry_column": "geometry",
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geom", "data_type": "POLYGON"},
            ],
        },
    }

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 2
