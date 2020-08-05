from geopackage_validator.validations.db_views_check import db_views_check


def test_zeroviews():
    assert len(db_views_check([])) == 0


def test_oneview():
    errors = db_views_check(["view1"])
    assert len(errors) == 1
    assert errors[0] == {
        "errormessage": "There should be no views in the database. Found view: view1",
        "errortype": "R4",
    }
