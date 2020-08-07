from geopackage_validator.validations.rtree_present_check import rtree_present_check


def test_rtree_present_all_tables():
    assert len(rtree_present_check(rtree_present_check_list=[])) == 0


def test_rtree_present_no_tables():
    errors = rtree_present_check(
        rtree_present_check_list=["no table has an rtree index"]
    )
    assert len(errors) == 1
    assert (
        errors[0]["errormessage"] == "Table without index: no table has an rtree index"
    )
    assert errors[0]["errortype"] == "R9"


def test_rtree_absent_one_table():
    assert len(rtree_present_check(rtree_present_check_list=["index_failed"])) == 1
