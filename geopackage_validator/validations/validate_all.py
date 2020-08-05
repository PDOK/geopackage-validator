from geopackage_validator.validations.lowercasecheck import *


def validate_all():
    errors = lowercasecheck(["Hi", "hi", "HH"])

    print(errors)

