from geopackage_validator.utils import open_dataset
from geopackage_validator.validations.rtree_valid_check import (
    ValidRtreeValidator,
    rtree_valid_check_query,
)


def test_rtree_valid_all_tables():
    assert len(ValidRtreeValidator.check_rtree_is_valid(rtree_index_list=[])) == 0


def test_rtree_invalidvalid_one_tables():
    results = ValidRtreeValidator.check_rtree_is_valid(rtree_index_list=["tablename"])
    assert len(results) == 1
    assert results[0] == "Invalid rtree index found for table: tablename"


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_rtree_valid.gpkg")
    checks = list(rtree_valid_check_query(dataset))
    assert len(checks) == 1
    assert checks[0] == "Found (1 -> 2) in %_rowid table, expected (1 -> 1)"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(rtree_valid_check_query(dataset))
    assert len(checks) == 0
