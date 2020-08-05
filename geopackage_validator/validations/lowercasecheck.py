

def lowercasecheck(tablename_list=None):
    if tablename_list is None:
        tablename_list = [""]

    errors = []

    for tablename in tablename_list:
        if tablename.lower() != tablename:
            errors.append({"R1", "Table names must have all lowercase characters. Error table: {table}".format(table = tablename)})

    return errors