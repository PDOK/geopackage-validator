import pytest

from geopackage_validator import generate


def test_generate_definitions_for_path_with_broken_gpkg_raises_generator_error():
    with pytest.raises(generate.GeneratorError) as exc_info:
        generate.generate_definitions_for_path("tests/data/test_broken_geopackage.gpkg")

    assert str(exc_info.value) == "Could not open gpkg."
    assert exc_info.value.trace == [
        "At least one of the required GeoPackage tables, gpkg_spatial_ref_sys or gpkg_contents, is missing"
    ]


def test_generate_definitions_for_path_with_correct_gpkg():
    result = generate.generate_definitions_for_path("tests/data/test_allcorrect.gpkg")
    assert result.projection == 28992
    assert len(result.tables) == 1
