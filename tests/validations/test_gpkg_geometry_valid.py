from geopackage_validator.gdal_utils import open_dataset
from geopackage_validator.validations.geometry_type_check import query_geometry_types
from geopackage_validator.validations.gpkg_geometry_valid import (
    GpkgGeometryTypeNameValidator,
    GeometryTypeEqualsGpkgDefinitionValidator,
    query_table_geometry_types,
    query_gpkg_metadata_geometry_types,
)


def test_gpkg_geometry_match_table_check():
    assert (
        len(
            GeometryTypeEqualsGpkgDefinitionValidator(
                None
            ).gpkg_geometry_match_table_check([], [])
        )
        == 0
    )


def test_gpkg_geometry_no_match_table_check():
    results = GeometryTypeEqualsGpkgDefinitionValidator(
        None
    ).gpkg_geometry_match_table_check(
        [("dummy_table", "GEOMETRY1")], [("dummy_table", "GEOMETRY2")]
    )
    assert len(results) == 1
    assert (
        results[0]
        == "Found geometry: GEOMETRY1, in layer: dummy_table, where gpkg_geometry is: GEOMETRY2."
    )


def test_gpkg_match_valid_gemometries():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    geometry_type_names = query_table_geometry_types(dataset)
    result = GpkgGeometryTypeNameValidator(dataset).gpkg_geometry_valid_check(
        geometry_type_names
    )
    assert len(result) == 0


def test_gpkg_geometry_match_table():
    dataset = open_dataset("tests/data/test_allcorrect.gpkg")
    table_geometry_type_names = query_geometry_types(dataset)
    geometry_type_names = query_gpkg_metadata_geometry_types(dataset)
    results = GeometryTypeEqualsGpkgDefinitionValidator(
        dataset
    ).gpkg_geometry_match_table_check(table_geometry_type_names, geometry_type_names)
    assert len(results) == 0
