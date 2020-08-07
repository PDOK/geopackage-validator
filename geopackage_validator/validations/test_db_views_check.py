from geopackage_validator.validations.db_views_check import db_views_check


def test_zeroviews():
    assert len(db_views_check([])) == 0


def test_oneview():
    errors = db_views_check(["view1"])
    assert len(errors) == 1
    assert errors[0]["errormessage"] == "Found view: view1"
    assert errors[0]["errortype"] == "R4"
