from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.rtree_valid_check import (
    rtree_valid_check,
    rtree_valid_check_query,
)


def test_rtree_valid_all_tables():
    assert len(rtree_valid_check(rtree_index_list=[])) == 0


def test_rtree_invalidvalid_one_tables():
    errors = rtree_valid_check(rtree_index_list=["tablename"])
    assert len(errors) == 1
    assert (
        errors[0]["RQ10"]["trace"][0]
        == "Invalid rtree index found for table: tablename"
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_rtree_valid.gpkg")
    checks = list(rtree_valid_check_query(dataset))
    assert len(checks) == 1
    assert checks[0] == "Found (1 -> 2) in %_rowid table, expected (1 -> 1)"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(rtree_valid_check_query(dataset))
    assert len(checks) == 0
