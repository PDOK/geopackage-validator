# -*- coding: utf-8 -*-
"""Main CLI entry for the Geopackage validator tool."""
# Setup logging before package imports.
import logging
from datetime import datetime
import sys
import time

import click
import click_log

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


from geopackage_validator.generate import generate_definitions_for_path
from geopackage_validator.minio.minio_context import minio_resource
from geopackage_validator.output import log_output, print_output
from geopackage_validator.validate import validate, get_validation_descriptions


@click.group()
def cli():
    pass


@cli.command(
    name="validate",
    help="Geopackage validator validating a local file or from s3 storage",
)
@click.option(
    "--gpkg-path",
    envvar="GPKG_PATH",
    show_envvar=True,
    required=False,
    default=None,
    help="Path pointing to the geopackage.gpkg file",
    type=click.types.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "-t",
    "--table-definitions-path",
    show_envvar=True,
    required=False,
    default=None,
    help="Path pointing to the table-definitions  JSON or YAML file (generate this file by calling the generate-definitions command)",
    type=click.types.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "--validations-path",
    show_envvar=True,
    required=False,
    default=None,
    envvar="VALIDATIONS_FILE",
    help="Path pointing to the set of validations to run. If validations-path and validations are not given, validate runs all validations",
    type=click.types.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "--validations",
    show_envvar=True,
    required=False,
    default="",
    envvar="VALIDATIONS",
    help="Comma-separated list of validations to run (e.g. --validations R1,R2,R3). If validations-path and validations are not given, validate runs all validations",
)
@click.option(
    "--exit-on-fail",
    required=False,
    is_flag=True,
    help="Exit with code 1 when validation success is false.",
)
@click.option(
    "--yaml", required=False, is_flag=True, help="Output yaml.",
)
@click.option(
    "--s3-endpoint-no-protocol",
    envvar="S3_ENDPOINT_NO_PROTOCOL",
    show_envvar=True,
    help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key",
    envvar="S3_ACCESS_KEY",
    show_envvar=True,
    help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key",
    envvar="S3_SECRET_KEY",
    show_envvar=True,
    help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket",
    envvar="S3_BUCKET",
    show_envvar=True,
    help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key",
    envvar="S3_KEY",
    show_envvar=True,
    help="Key where the geopackage is in the bucket",
)
@click.option(
    "--s3-secure",
    envvar="S3_SECURE",
    show_envvar=True,
    type=click.types.BoolParamType(),
    default="true",
    help="Use a secure TLS connection for S3.",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command(
    gpkg_path,
    table_definitions_path,
    validations_path,
    validations,
    exit_on_fail,
    yaml,
    s3_endpoint_no_protocol,
    s3_access_key,
    s3_secret_key,
    s3_bucket,
    s3_key,
    s3_secure,
):
    start_time = datetime.now()
    duration_start = time.monotonic()

    if gpkg_path is None and s3_endpoint_no_protocol is None:
        logger.error("Give --gpkg-path or s3 location")
        sys.exit(1)

    if gpkg_path is not None:
        filename = gpkg_path
        results, validations_executed, success = validate(
            gpkg_path, table_definitions_path, validations_path, validations,
        )
    else:
        try:
            with minio_resource(
                s3_endpoint_no_protocol,
                s3_access_key,
                s3_secret_key,
                s3_bucket,
                s3_key,
                s3_secure,
            ) as localfilename:
                filename = s3_key
                results, validations_executed, success = validate(
                    localfilename,
                    table_definitions_path,
                    validations_path,
                    validations,
                )
        except (AssertionError, IOError) as e:
            logger.error(str(e))
            sys.exit(1)
    duration_seconds = time.monotonic() - duration_start
    log_output(
        filename=filename,
        results=results,
        validations_executed=validations_executed,
        start_time=start_time,
        duration_seconds=duration_seconds,
        success=success,
        as_yaml=yaml,
    )
    if exit_on_fail and not success:
        sys.exit(1)


@cli.command(
    name="generate-definitions",
    help="Generate Geopackage table definition  JSON or YAML from given local or s3 package. Use the generated definition  JSON or YAML in the validation step by providing the table definitions with the --table-definitions-path parameter.",
)
@click.option(
    "--gpkg-path",
    envvar="GPKG_PATH",
    required=False,
    default=None,
    show_envvar=True,
    help="Path pointing to the geopackage.gpkg file",
    type=click.types.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "--yaml", required=False, is_flag=True, help="Output yaml",
)
@click.option(
    "--s3-endpoint-no-protocol",
    envvar="S3_ENDPOINT_NO_PROTOCOL",
    show_envvar=True,
    help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key",
    envvar="S3_ACCESS_KEY",
    show_envvar=True,
    help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key",
    envvar="S3_SECRET_KEY",
    show_envvar=True,
    help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket",
    envvar="S3_BUCKET",
    show_envvar=True,
    help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key",
    envvar="S3_KEY",
    show_envvar=True,
    help="Key where the geopackage is in the bucket",
)
@click.option(
    "--s3-secure",
    envvar="S3_SECURE",
    show_envvar=True,
    type=click.types.BoolParamType(),
    default="true",
    help="Use a secure TLS connection for S3.",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_generate_table_definitions(
    gpkg_path,
    yaml,
    s3_endpoint_no_protocol,
    s3_access_key,
    s3_secret_key,
    s3_bucket,
    s3_key,
    s3_secure,
):
    if gpkg_path is None and s3_endpoint_no_protocol is None:
        logger.error("Give --gpkg-path or s3 location")
        sys.exit(1)

    try:
        if gpkg_path is not None:
            definitionlist = generate_definitions_for_path(gpkg_path)
        else:
            with minio_resource(
                s3_endpoint_no_protocol,
                s3_access_key,
                s3_secret_key,
                s3_bucket,
                s3_key,
                s3_secure,
            ) as localfilename:
                definitionlist = generate_definitions_for_path(localfilename)
        print_output(definitionlist, yaml)
    except Exception:
        logger.exception("Error while generating table definitions")
        sys.exit(1)


@cli.command(
    name="show-validations",
    help="Show all the possible validations that can be executed in the validate command.",
)
@click.option(
    "--yaml", required=False, is_flag=True, help="Output yaml",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_show_validations(yaml):
    try:
        validation_codes = get_validation_descriptions()
        print_output(validation_codes, yaml, yaml_indent=5)
    except Exception:
        logger.exception("Error while listing validations")
        sys.exit(1)


if __name__ == "__main__":
    cli()
