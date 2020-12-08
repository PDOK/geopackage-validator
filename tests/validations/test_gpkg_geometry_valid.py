from geopackage_validator.gdal.dataset import open_dataset
from geopackage_validator.validations.geometry_type_check import (
    geometry_type_check_query,
)
from geopackage_validator.validations.gpkg_geometry_valid import (
    gpkg_geometry_match_table_check,
    gpkg_geometry_valid_check_query,
    gpkg_geometry_valid_check,
)


def test_gpkg_geometry_match_table_check():
    assert len(gpkg_geometry_match_table_check([], [])) == 0


def test_gpkg_geometry_no_match_table_check():
    results = gpkg_geometry_match_table_check(
        [("dummy_table", "GEOMETRY1")], ["GEOMETRY2"]
    )
    assert len(results) == 1
    assert results[0]["validation_code"] == "RQ15"
    assert (
        results[0]["locations"][0]
        == "Found geometry: GEOMETRY1, in layer: dummy_table, where gpkg_geometry is: GEOMETRY2."
    )


def test_gpkg_match_valid_gemometries():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    geometry_type_names = gpkg_geometry_valid_check_query(dataset)
    result = gpkg_geometry_valid_check(geometry_type_names)
    assert len(result) == 0


def test_gpkg_geometry_match_table():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    table_geometry_type_names = geometry_type_check_query(dataset)
    geometry_type_names = gpkg_geometry_valid_check_query(dataset)
    results = gpkg_geometry_match_table_check(
        table_geometry_type_names, geometry_type_names
    )
    assert len(results) == 0