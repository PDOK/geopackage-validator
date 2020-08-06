from geopackage_validator.validations.columnname_check import columnname_check


def test_lowercasecolumnname_success():
    assert (
        len(
            columnname_check(
                columnname_list=[
                    ("table", "column"),
                    ("table", "lower_case"),
                    ("table", "is"),
                    ("table", "good"),
                ]
            )
        )
        == 0
    )


def test_lowercasecolumnname_start_number():
    errors = columnname_check(columnname_list=[("table", "1column")])
    assert len(errors) == 1
    assert errors[0] == {
        "errormessage": "Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. Error found in table: table, column: 1column",
        "errortype": "R6",
    }


def test_lowercasecolumnname_with_capitals():
    assert (
        len(
            columnname_check(
                columnname_list=[
                    ("table", "columnR"),
                    ("table", "column"),
                    ("table", "column"),
                ]
            )
        )
        == 1
    )
