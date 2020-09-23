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
        "projection": 28992,
        "test_allcorrect": {
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geometry", "data_type": "POLYGON"},
                {"column_name": "geometry", "geometry_type_name": "POINT"},
            ],
            "table_name": "test_allcorrect",
        },
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert "RQ8" in diff[0]


def test_table_definitions_check_incorrect_projection():
    current_definitions = {
        "projection": 4326,
        "test_allcorrect": {
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geometry", "data_type": "POLYGON"},
                {"column_name": "geometry", "geometry_type_name": "POLYGON"},
            ],
            "table_name": "test_allcorrect",
        },
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )

    assert len(diff) == 1
    assert diff[0]["RQ8"] == {
        "errorinfo": {
            "errortype": "RQ8",
            "validation": "Geopackage must conform to given JSON definitions.",
        },
        "trace": [
            "Difference: Value of root['projection'] changed from 28992 to 4326."
        ],
    }


def test_table_definitions_check_incorrect_column_name():
    current_definitions = {
        "projection": 28992,
        "test_allcorrect": {
            "columns": [
                {"column_name": "fid", "data_type": "INTEGER"},
                {"column_name": "geom", "data_type": "POLYGON"},
                {"column_name": "geometry", "geometry_type_name": "POLYGON"},
            ],
            "table_name": "test_allcorrect",
        },
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert "RQ8" in diff[0]


def test_table_definitions_check_table_changed():
    current_definitions = {
        "projection": 28992,
        "test_different_table": {
            "table_name": "test_different_table",
            "columns": [{"column_name": "geometry", "geometry_type_name": "POLYGON"}],
        },
    }

    diff = table_definitions_check(
        "tests/data/test_allcorrect_definition.json", current_definitions
    )
    assert len(diff) == 1
    assert "RQ8" in diff[0]
