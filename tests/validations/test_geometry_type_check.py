from geopackage_validator.utils import open_dataset, dataset_geometry_types
from geopackage_validator.validations.geometry_type_check import (
    query_geometry_types,
    aggregate,
    GpkgGeometryTypeNameValidator,
    GeometryTypeEqualsGpkgDefinitionValidator,
)


def test_valid_geometry_type_aggregate():
    results = aggregate([])
    assert len(results) == 0


def test_invalid_geometry_type_aggregate():
    results = aggregate(
        [
            ("table_a", "type_a", 1),
            ("table_a", "type_a", 2),
            ("table_b", "type_a", 1),
            ("table_b", "type_a", 2),
            ("table_b", "type_a", 3),
        ]
    )

    assert len(results) == 2

    keys = list(results.keys())

    assert results[keys[0]]["layer"] == "table_a"
    assert results[keys[0]]["geometry"] == "type_a"
    assert len(results[keys[0]]["rowid_list"]) == 2

    assert results[keys[1]]["layer"] == "table_b"
    assert results[keys[1]]["geometry"] == "type_a"
    assert len(results[keys[1]]["rowid_list"]) == 3


def test_rq3_with_gpkg():
    dataset = open_dataset("tests/data/test_geometry_type.gpkg")
    checks = list(query_geometry_types(dataset))
    assert len(checks) == 1
    assert checks[0][0] == "test_geometry_type"
    assert checks[0][1] == "COMPOUNDCURVE"


def test_rq3_with_gpkg_allcorrect():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    checks = list(query_geometry_types(dataset))
    assert len(checks) == 0


def test_rq14_with_gpkg_geometry_type_valid_check():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    geometry_type_names = dataset_geometry_types(dataset)
    result = GpkgGeometryTypeNameValidator(dataset).gpkg_geometry_valid_check(
        geometry_type_names
    )
    assert len(result) == 0


def test_rq14_with_gpkg_geometry_type_invalid_check():
    dataset = open_dataset("tests/data/test_geometry_type.gpkg")
    geometry_type_names = dataset_geometry_types(dataset)
    result = GpkgGeometryTypeNameValidator(dataset).gpkg_geometry_valid_check(
        geometry_type_names
    )
    assert len(result) == 1
    assert (
        result[0]
        == "Found geometry_type_name: COMPOUNDCURVE for table test_geometry_type (from the gpkg_geometry_columns table)."
    )


def test_rq15_with_gpkg_geometry_type_equals_gpkg_definition_valid_check():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    result = list(GeometryTypeEqualsGpkgDefinitionValidator(dataset).check())
    assert len(result) == 0


def test_rq15_with_gpkg_geometry_type_equals_gpkg_definition_invalid_check():
    dataset = open_dataset("tests/data/test_geometry_type.gpkg")
    result = list(GeometryTypeEqualsGpkgDefinitionValidator(dataset).check())
    assert len(result) == 1
    assert (
        result[0]
        == "Error layer: test_geometry_type, found geometry: GEOMETRYCOLLECTION that should be COMPOUNDCURVE, 1 time, example id: 1"
    )
