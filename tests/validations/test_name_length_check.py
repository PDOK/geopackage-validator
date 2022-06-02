from typing import List, Tuple

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
                    ("table", "a_table_name_of_34_characters_long", 34),
                    ("column", "a_column_name_of_35_characters_long", 35),
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
                69,
            ),
        ]
    )
    assert len(results) == 1
    assert results == [
        "Error table too long: a_table_name_that_has_more_than_fifty_three_characters_returned_twice, with length: 69"
    ]


def test_column_name_too_long():
    results = NameLengthValidator.check_columns(
        names=[
            (
                "table",
                "a_table_name_that_has_more_than_fifty_three_characters_returned_twice",
                69,
            ),
            (
                "column",
                "a_column_name_that_has_more_than_fifty_three_characters_returned_twice",
                70,
            ),
        ]
    )
    assert len(results) == 2
    assert results == [
        "Error table too long: a_table_name_that_has_more_than_fifty_three_characters_returned_twice, with length: 69",
        "Error column too long: a_column_name_that_has_more_than_fifty_three_characters_returned_twice, with length: "
        "70",
    ]


def test_with_long_gpkg():
    dataset = open_dataset("tests/data/test_namelength.gpkg")
    checks = list(query_names(dataset))
    assert len(checks) == 4
    assert checks == [
        ("table", "a_table_name_that_has_more_than_fifty_three_characters", 54),
        (
            "column",
            "fid (table: a_table_name_that_has_more_than_fifty_three_characters)",
            3,
        ),
        (
            "column",
            "geom (table: a_table_name_that_has_more_than_fifty_three_characters)",
            4,
        ),
        (
            "column",
            "a_column_name_that_has_more_than_fifty_three_characters (table: "
            "a_table_name_that_has_more_than_fifty_three_characters)",
            55,
        ),
    ]


def test_names_allcorrect_gpkg():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_names(dataset))
    assert len(checks) == 3
    assert checks == [
        ("table", "test_allcorrect", 15),
        ("column", "fid (table: test_allcorrect)", 3),
        ("column", "geom (table: test_allcorrect)", 4),
    ]
