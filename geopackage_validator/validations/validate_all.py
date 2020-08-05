from geopackage_validator.validations.lowercasecheck import lowercasecheck


def validate_all():

    errors = lowercasecheck(["Hi", "hi", "HH"])

    print(errors)
