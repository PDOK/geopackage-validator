import re
from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def columnname_check_query(dataset) -> Iterable[Tuple[str, str]]:
    tables = dataset.ExecuteSQL("SELECT table_name FROM gpkg_contents;")

    for table in tables:
        columns = dataset.ExecuteSQL(
            "PRAGMA TABLE_INFO('{table_name}');".format(table_name=table[0])
        )

        for column in columns:
            yield table[0], column[1]

        dataset.ReleaseResultSet(columns)
    dataset.ReleaseResultSet(tables)


def columnname_check(columnname_list: Iterable[Tuple[str, str]]):
    assert columnname_list is not None

    results = []

    for columnname in columnname_list:
        match_valid = re.fullmatch(r"^[a-z][a-z0-9_]*$", columnname[1])
        if match_valid is None:
            results.append(
                create_validation_message(
                    err_index="columnname",
                    column_name=columnname[1],
                    table_name=columnname[0],
                )
            )

    return result_format("columnname", results)
