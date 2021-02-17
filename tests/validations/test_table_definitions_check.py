from geopackage_validator.generate import generate_definitions_for_path
from geopackage_validator.validations.table_definitions_check import (
    TableDefinitionValidator,
)


def test_table_definitions_check_correct():
    current_definitions = generate_definitions_for_path(
        "tests/data/test_allcorrect.gpkg"
    )

    diff = TableDefinitionValidator(
        None, "tests/data/test_allcorrect_definition.json"
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

    diff = TableDefinitionValidator(
        None, table_definitions_path="tests/data/test_allcorrect_definition.json"
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

    diff = TableDefinitionValidator(
        None, "tests/data/test_allcorrect_definition.json"
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

    diff = TableDefinitionValidator(
        None, "tests/data/test_allcorrect_definition.json"
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

    diff = TableDefinitionValidator(
        None, "tests/data/test_allcorrect_definition.json"
    ).check_table_definitions(current_definitions)

    assert len(diff) == 2
