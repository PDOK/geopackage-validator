from geopackage_validator.gdal_utils import open_dataset
from geopackage_validator.validations.rtree_present_check import (
    RTreeExistsValidator,
    query_rtree_presence,
)


def test_rtree_present_all_tables():
    assert (
        len(
            RTreeExistsValidator(None).check_rtree_is_present(
                rtree_present_check_list=[]
            )
        )
        == 0
    )


def test_rtree_present_no_tables():
    results = RTreeExistsValidator(None).check_rtree_is_present(
        rtree_present_check_list=["no table has an rtree index"]
    )
    assert len(results) == 1
    assert results[0] == "Table without index: no table has an rtree index"


def test_rtree_absent_one_table():
    assert (
        len(
            RTreeExistsValidator(None).check_rtree_is_present(
                rtree_present_check_list=["index_failed"]
            )
        )
        == 1
    )


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_rtree_present_alltables.gpkg")
    checks = list(query_rtree_presence(dataset))
    assert len(checks) == 1
    assert checks[0] == "no table has an rtree index"


def test_singletable_with_gpkg():
    dataset = open_dataset("tests/data/test_rtree_present_single_table.gpkg")
    checks = list(query_rtree_presence(dataset))
    assert len(checks) == 1
    assert checks[0] == "test_rtree_present_single_table"


def test_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_rtree_presence(dataset))
    assert len(checks) == 0
