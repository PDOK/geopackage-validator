from geopackage_validator.generate import generate_definitions_for_path
from geopackage_validator.validations.table_definitions_check import (
    table_definitions_check,
)


def test_table_definitions_check_correct():
    current_definitions = generate_definitions_for_path(
        "tests/data/test_allcorrect.gpkg"
    )
    assert (
        len(
            table_definitions_check(
                "tests/data/test_allcorrect_definition.json", current_definitions
            )
        )
        == 0
    )


def test_table_definitions_check_incorrect_geometry():
    current_definitions = {
        "test_allcorrect": {
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geometry", "data_type": "POLYGON"},
                {
                    "column_name": "geometry",
                    "geometry_type_name": "POINT",
                    "projection": 4326,
                },
            ],
            "table_name": "test_allcorrect",
        }
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert diff[0]["R8"] == {
        "errorinfo": {
            "errortype": "R8",
            "validation": "Geopackage must conform to given JSON definitions",
        },
        "errors": [
            "Difference: Value of root['test_allcorrect']['columns'][2]['geometry_type_name'] changed from \"POLYGON\" to \"POINT\"."
        ],
    }


def test_table_definitions_check_incorrect_projection():
    current_definitions = {
        "test_allcorrect": {
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geometry", "data_type": "POLYGON"},
                {
                    "column_name": "geometry",
                    "geometry_type_name": "POLYGON",
                    "projection": 4323,
                },
            ],
            "table_name": "test_allcorrect",
        }
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert diff[0]["R8"] == {
        "errorinfo": {
            "errortype": "R8",
            "validation": "Geopackage must conform to given JSON definitions",
        },
        "errors": [
            "Difference: Value of root['test_allcorrect']['columns'][2]['projection'] changed from 4326 to 4323."
        ],
    }


def test_table_definitions_check_incorrect_column_name():
    current_definitions = {
        "test_allcorrect": {
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geom", "data_type": "POLYGON"},
                {
                    "column_name": "geometry",
                    "geometry_type_name": "POLYGON",
                    "projection": 4326,
                },
            ],
            "table_name": "test_allcorrect",
        }
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert diff[0]["R8"] == {
        "errorinfo": {
            "errortype": "R8",
            "validation": "Geopackage must conform to given JSON definitions",
        },
        "errors": [
            "Difference: Value of root['test_allcorrect']['columns'][1]['column_name'] changed from \"geometry\" to \"geom\"."
        ],
    }


def test_table_definitions_check_table_changed():
    current_definitions = {
        "test_different_table": {
            "table_name": "test_different_table",
            "columns": [
                {
                    "column_name": "geometry",
                    "geometry_type_name": "POLYGON",
                    "projection": 4326,
                }
            ],
        }
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert diff[0]["R8"] == {
        "errorinfo": {
            "errortype": "R8",
            "validation": "Geopackage must conform to given JSON definitions",
        },
        "errors": [
            "Difference: Item root['test_different_table'] added to dictionary.",
            "Difference: Item root['test_allcorrect'] removed from dictionary.",
        ],
    }
