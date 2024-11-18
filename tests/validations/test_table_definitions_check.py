from geopackage_validator.generate import (
    generate_definitions_for_path,
    get_datasource_for_path,
)
from geopackage_validator.models import TablesDefinition
from geopackage_validator.validate import load_table_definitions
from geopackage_validator.validations.table_definitions_check import (
    TableDefinitionValidator,
    TableDefinitionValidatorV0,
)


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

    assert diff == []


def test_table_definitions_check_incorrect_geometry():
    current_definitions = {
        "projection": 28992,
        "tables": [
            {
                "name": "test_allcorrect",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POINT"},
                ],
            }
        ],
    }
    current_definitions = TablesDefinition.model_validate(current_definitions)

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
        "tables": [
            {
                "name": "test_allcorrect",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            }
        ],
    }
    current_definitions = TablesDefinition.model_validate(current_definitions)

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 1
    assert diff[0] == "different projections: 4326 changed to 28992"


def test_table_definitions_check_incorrect_column_name():
    current_definitions = {
        "projection": 28992,
        "tables": [
            {
                "name": "test_allcorrect",
                "geometry_column": "geometry",  # geom -> 1 error
                "columns": [
                    {
                        "name": "id",
                        "type": "INTEGER",
                    },  # name should be fid -> 2 errors (1 missing and 1 extra)
                    {"name": "geom", "type": "POLYGON"},
                ],
            }
        ],
    }
    current_definitions = TablesDefinition.model_validate(current_definitions)

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 3


def test_table_definitions_check_table_changed():
    current_definitions = {
        "projection": 28992,
        "tables": [
            {
                "name": "test_different_table",
                "geometry_column": "geometry",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            }
        ],
    }
    current_definitions = TablesDefinition.model_validate(current_definitions)

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidator(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert len(diff) == 2


def test_legacy_table_definitions_check_table_changed():
    current_definitions = {
        "projection": 28992,
        "tables": [
            {
                "name": "test_different_table",
                "geometry_column": "geometry",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            }
        ],
    }
    current_definitions = TablesDefinition.model_validate(current_definitions)

    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_definition.json"
    )

    diff = TableDefinitionValidatorV0(
        None, table_definitions=table_definitions
    ).check_table_definitions(current_definitions)

    assert diff == [
        "missing table(s): test_allcorrect",
        "extra table(s): test_different_table",
    ]


def gdal_error_handler_print_err(err_level, err_no, err_msg):
    print(f"GDAL error: err_level: {err_level}\nerr_no: {err_no}\nerr_msg: {err_msg}")


def test_table_definitions_check_changed_indexes_and_fks():
    datasource = get_datasource_for_path(
        "tests/data/test_allcorrect_with_indexes_and_fks.gpkg",
        gdal_error_handler_print_err,
    )
    table_definitions = load_table_definitions(
        "tests/data/test_changed_indexes_and_fks_definition.yml"
    )

    diff = TableDefinitionValidator(
        dataset=datasource, table_definitions=table_definitions
    ).check()

    assert set(diff) == {
        'table test_allcorrect has extra ForeignKeyDefinition: { "table": "test_foreign", "columns": [ { "src": "foreign_id", "dst": "id" } ] }',
        'table test_allcorrect has extra IndexDefinition: { "columns": [ "fid" ], "unique": true }',
        'table test_allcorrect misses ForeignKeyDefinition: { "table": "unexisting", "columns": [ { "src": "foreign_id", "dst": "id" } ] }',
        'table test_allcorrect misses IndexDefinition: { "columns": [ "foo" ], "unique": true }',
        'table test_foreign has extra IndexDefinition: { "columns": [ "name" ], "unique": true }',
        'table test_foreign has extra IndexDefinition: { "columns": [ "x", "y" ], "unique": false }',
        'table test_foreign misses IndexDefinition: { "columns": [ "name" ], "unique": false }',
        'table test_foreign misses IndexDefinition: { "columns": [ "x", "y" ], "unique": true }',
        'table test_multi_fk has extra ForeignKeyDefinition: { "table": "test_allcorrect", "columns": [ { "src": "allcorrect_id", "dst": "fid" } ] }',
    }


def test_table_definitions_check_fk_violation():
    datasource = get_datasource_for_path(
        "tests/data/test_foreign_key_violation.gpkg", gdal_error_handler_print_err
    )
    table_definitions = load_table_definitions(
        "tests/data/test_allcorrect_with_indexes_and_fks_definition.yml"
    )

    diff = TableDefinitionValidator(
        dataset=datasource, table_definitions=table_definitions
    ).check()

    assert set(diff) == {
        "foreign key violation in test_multi_fk for fk 0 to test_other on row 2",
        "foreign key violation in test_multi_fk for fk 1 to test_allcorrect on row 2",
    }
