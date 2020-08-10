from geopackage_validator.validations.rtree_valid_check import rtree_valid_check


def test_rtree_valid_all_tables():
    assert len(rtree_valid_check(rtree_index_list=[])) == 0


def test_rtree_invalidvalid_one_tables():
    errors = rtree_valid_check(rtree_index_list=["tablename"])
    assert len(errors) == 1
    assert (
        errors[0]["R10"]["errors"][0]
        == "Invalid rtree index found for table: tablename"
    )
