def quote_identifier(value: str) -> str:
    """Quote a SQLite identifier, including embedded double quotes."""
    if "\x00" in value:
        raise ValueError("SQL identifiers cannot contain NUL characters")
    return '"' + value.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    """Quote a SQLite string literal, including embedded single quotes."""
    if "\x00" in value:
        raise ValueError("SQL string literals cannot contain NUL characters")
    return "'" + value.replace("'", "''") + "'"
