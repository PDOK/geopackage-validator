import json

from click.testing import CliRunner

from geopackage_validator.cli import cli
from geopackage_validator import __version__


def test_show_validations():
    runner = CliRunner()
    result = runner.invoke(cli, ["show-validations"])
    assert result.exit_code == 0
    assert (
        'RQ1": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores."'
        in result.output
    )


def test_generate_definitions_no_gpkg():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate-definitions"])
    assert result.exit_code == 1
    assert "Give a valid --gpkg-path or (/vsi)s3 location" in result.output


def test_generate_definitions_error_s3():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["generate-definitions", "--s3-endpoint-no-protocol", "s3host"]
    )
    assert result.exit_code == 1
    assert "S3 access key has to be given" in result.output


def test_generate_definitions_with_gpkg():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["generate-definitions", "--gpkg-path", "tests/data/test_allcorrect.gpkg"]
    )
    expected = {
        "geopackage_validator_version": __version__,
        "projection": 28992,
        "tables": [
            {
                "name": "test_allcorrect",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            }
        ],
    }

    assert result.exit_code == 0
    assert json.loads(result.output) == expected


def test_generate_definitions_with_ndimension_geometries():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["generate-definitions", "--gpkg-path", "tests/data/test_dimensions.gpkg"]
    )
    expected = {
        "geopackage_validator_version": __version__,
        "projection": 28992,
        "tables": [
            {
                "name": "test_dimensions",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            },
            {
                "name": "test_dimensions3",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            },
            {
                "name": "test_dimensions4",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            },
            {
                "name": "test_dimensions4_correct",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            },
            {
                "name": "test_dimensions3_correct",
                "geometry_column": "geom",
                "columns": [
                    {"name": "fid", "type": "INTEGER"},
                    {"name": "geom", "type": "POLYGON"},
                ],
            },
        ],
    }

    assert result.exit_code == 0
    assert json.loads(result.output) == expected


EXPECTED_VALIDATION_YAML = """geopackage_validator_version: {version}
projection: 28992
tables:
- name: test_allcorrect
  geometry_column: geom
  columns:
  - name: fid
    type: INTEGER
  - name: geom
    type: POLYGON"""


def test_generate_definitions_with_gpkg_yaml_output():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "generate-definitions",
            "--gpkg-path",
            "tests/data/test_allcorrect.gpkg",
            "--yaml",
        ],
    )

    assert result.exit_code == 0
    assert result.output.strip("\n") == EXPECTED_VALIDATION_YAML.format(
        version=__version__
    )


def test_validate_no_gpkg():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 1
    assert "Give --gpkg-path or s3 location" in result.output


def test_validate_error_s3():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--s3-endpoint-no-protocol", "s3host"])
    assert result.exit_code == 1
    assert "S3 access key has to be given" in result.output


def test_validate_with_gpkg():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["validate", "--gpkg-path", "tests/data/test_allcorrect.gpkg"]
    )
    assert result.exit_code == 0
    assert '"geopackage_validator_version": ' in result.output
    assert '"success": true' in result.output


def test_validate_with_rq8_missing_definitions_path():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "validate",
            "--gpkg-path",
            "tests/data/test_allcorrect.gpkg",
            "--validations",
            "RQ8",
        ],
    )
    assert result.exit_code == 0
    assert "Missing '--table-definitions-path' input" in result.output


def test_validate_with_rq8_with_yaml_definitions_path():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "validate",
            "--gpkg-path",
            "tests/data/test_allcorrect.gpkg",
            "--table-definitions-path",
            "tests/data/test_allcorrect_definition.yml",
        ],
    )
    assert result.exit_code == 0
    assert "RQ8" in result.output


def test_validate_with_rq8_with_json_definitions_path():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "validate",
            "--gpkg-path",
            "tests/data/test_allcorrect.gpkg",
            "--table-definitions-path",
            "tests/data/test_allcorrect_definition.json",
        ],
    )
    assert result.exit_code == 0
    assert "RQ8" in result.output


def test_validate_with_rq8_with_old_definitions_path():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "validate",
            "--gpkg-path",
            "tests/data/test_allcorrect.gpkg",
            "--table-definitions-path",
            "tests/data/test_allcorrect_old_definition.json",
        ],
    )
    assert result.exit_code == 0
    assert "RQ8" in result.output
