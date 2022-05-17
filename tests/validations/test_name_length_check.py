from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.name_length_check import (
    NameLengthValidator,
    query_names,
)


def test_name_length_success():
    assert (
        len(
            NameLengthValidator.check_columns(
                names=[
                    ("table", "a_table_name_of_34_characters_long"),
                    ("column", "a_column_name_of_35_characters_long"),
                ]
            )
        )
        == 0
    )


def test_table_name_too_long():
    results = NameLengthValidator.check_columns(
        names=[
            (
                "table",
                "a_table_name_that_has_more_than_fifty_three_characters_returned_twice",
            ),
        ]
    )
    assert len(results) == 1
    assert results == [
        "Error table too long: a_table_name_that_has_more_than_fifty_three_characters_returned_twice"
    ]


def test_column_name_too_long():
    results = NameLengthValidator.check_columns(
        names=[
            (
                "table",
                "a_table_name_that_has_more_than_fifty_three_characters_returned_twice",
            ),
            (
                "column",
                "a_column_name_that_has_more_than_fifty_three_characters_returned_twice",
            ),
        ]
    )
    assert len(results) == 2
    assert results == [
        "Error table too long: a_table_name_that_has_more_than_fifty_three_characters_returned_twice",
        "Error column too long: a_column_name_that_has_more_than_fifty_three_characters_returned_twice",
    ]


def test_with_long_gpkg():
    dataset = open_dataset("tests/data/test_namelength.gpkg")
    checks = list(query_names(dataset))
    assert len(checks) == 4
    assert checks == [
        ("table", "a_table_name_that_has_more_than_fifty_three_characters"),
        (
            "column",
            "fid (table: a_table_name_that_has_more_than_fifty_three_characters)",
        ),
        (
            "column",
            "geom (table: a_table_name_that_has_more_than_fifty_three_characters)",
        ),
        (
            "column",
            "a_column_name_that_has_more_than_fifty_three_characters (table: "
            "a_table_name_that_has_more_than_fifty_three_characters)",
        ),
    ]


def test_names_allcorrect_gpkg():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_names(dataset))
    assert len(checks) == 3
    assert checks == [
        ("table", "test_allcorrect"),
        ("column", "fid (table: test_allcorrect)"),
        ("column", "geom (table: test_allcorrect)"),
    ]
