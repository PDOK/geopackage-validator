import tempfile, shutil
from osgeo import ogr

from geopackage_validator.validate import (
    validators_to_use,
    get_validation_codes,
    validate,
)


def test_determine_validations_to_use_param():
    validations = get_validation_codes(validators_to_use(validation_codes="RQ2,RQ3"))
    assert validations == ["RQ2", "RQ3"]


def test_determine_validations_to_use_param_spaces():
    validations = get_validation_codes(validators_to_use(validation_codes="RQ10, RQ3"))
    assert validations == ["RQ10", "RQ3"]


def test_determine_validations_to_use_none():
    validations = get_validation_codes(validators_to_use("ALL"))
    assert validations == [
        "RQ1",
        "RQ2",
        "RQ4",
        "RQ6",
        "RQ7",
        "RQ9",
        "RQ10",
        "RQ11",
        "RQ13",
        "RQ14",
        "RQ15",
        "RQ21",
        "RQ22",
        "RQ23",
        "RQ24",
        "RC17",
        "RC18",
        "RC19",
        "RC20",
    ]


def test_determine_validations_to_use_json_file():
    validations = get_validation_codes(
        validators_to_use(
            validation_codes="",
            validations_path="tests/data/validationsets/example-validation-set.json",
        )
    )
    assert validations == ["RQ1", "RQ2", "RQ3"]


def test_determine_validations_to_use_yaml_file():
    validations = get_validation_codes(
        validators_to_use(
            validation_codes="",
            validations_path="tests/data/validationsets/example-validation-set.yaml",
        )
    )
    assert validations == ["RQ1", "RQ2", "RQ3"]


def test_determine_validations_to_use_file_and_param():
    validations = get_validation_codes(
        validators_to_use(
            validation_codes="RQ7,RQ9",
            validations_path="tests/data/validationsets/example-validation-set.json",
        )
    )
    assert validations == ["RQ1", "RQ2", "RQ3", "RQ7", "RQ9"]


def test_validate_all_no_validations():
    results, validations_executed, success = validate(
        gpkg_path="tests/data/test_allcorrect.gpkg",
        validations="ALL",
    )
    assert success
    assert len(results) == 0


def test_validate_single_validation():
    results, validations_executed, success = validate(
        gpkg_path="tests/data/test_layername.gpkg",
        validations="RQ1",
    )
    assert not success
    assert len(results) == 1
    assert results[0]["locations"] == ["Error layer: test_LAYERNAME"]


def test_validate_single_validation_no_error():
    results, validations_executed, success = validate(
        gpkg_path="tests/data/test_layername.gpkg", validations="RQ2"
    )
    assert success
    assert len(results) == 0


def test_validate_all_validations_no_error():
    results, validations_executed, success = validate(
        gpkg_path="tests/data/test_layername.gpkg", validations="ALL"
    )
    assert len(results) == 2
    assert results[0]["locations"] == ["Error layer: test_LAYERNAME"]
    assert results[1]["locations"] == [
        "Found in table: test_LAYERNAME, column: geometry"
    ]


def test_validate_all_validations_with_broken_gpkg_throws_gdal_error():

    results, validations_executed, success = validate(
        gpkg_path="tests/data/test_broken_geopackage.gpkg", validations="ALL"
    )

    assert len(results) == 1
    print(results)
    assert results[0]["locations"] == [
        "At least one of the required GeoPackage tables, gpkg_spatial_ref_sys or gpkg_contents, is missing"
    ]


def test_validate_all_properly_closes_all_gpkg_connections():
    tmp_gpkg = tempfile.NamedTemporaryFile(delete=True, suffix=".gpkg")
    filename = tmp_gpkg.name
    shutil.copy2("tests/data/test_allcorrect.gpkg", filename)
    results, validations_executed, success = validate(
        gpkg_path=filename,
        validations="ALL",
        table_definitions_path="tests/data/test_allcorrect_definition.json",
    )
    assert success
    assert len(results) == 0

    driver = ogr.GetDriverByName("GPKG")
    gpkg_src = driver.Open(filename, update=True)
    error_code = gpkg_src.DeleteLayer(0)
    assert error_code == 0
