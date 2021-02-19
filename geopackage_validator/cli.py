# -*- coding: utf-8 -*-
"""Main CLI entry for the Geopackage validator tool."""
# Setup logging before package imports.
import logging
from datetime import datetime
import time

import click
import click_log

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


from geopackage_validator.generate import generate_definitions_for_path
from geopackage_validator.minio.minio_context import minio_resource
from geopackage_validator.output import log_output
from geopackage_validator.validate import validate, get_validation_descriptions
import json


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
    help="Path pointing to the table-definitions JSON file (generate this file by calling the generate-definitions command)",
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
    default="ALL",
    envvar="VALIDATIONS",
    help="Comma-separated list of validations to run (e.g. --validations R1,R2,R3). If validations-path and validations are not given, validate runs all validations",
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
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command(
    gpkg_path,
    table_definitions_path,
    validations_path,
    validations,
    s3_endpoint_no_protocol,
    s3_access_key,
    s3_secret_key,
    s3_bucket,
    s3_key,
):
    start_time = datetime.now()
    duration_start = time.monotonic()

    if gpkg_path is None and s3_endpoint_no_protocol is None:
        logger.error("Give --gpkg-path or s3 location")
        return

    if gpkg_path is not None:
        filename = gpkg_path
        results, validations_executed, success = validate(
            gpkg_path, table_definitions_path, validations_path, validations,
        )
    else:
        try:
            with minio_resource(
                s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
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
            return
    duration_seconds = time.monotonic() - duration_start
    log_output(
        filename=filename,
        results=results,
        validations_executed=validations_executed,
        start_time=start_time,
        duration_seconds=duration_seconds,
        success=success,
    )


@cli.command(
    name="generate-definitions",
    help="Generate Geopackage table definition JSON from given local or s3 package. Use the generated definition JSON in the validation step by providing the table definitions with the --table-definitions-path parameter.",
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
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_generate_table_definitions(
    gpkg_path, s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
):
    if gpkg_path is None and s3_endpoint_no_protocol is None:
        logger.error("Give --gpkg-path or s3 location")
        return

    try:
        if gpkg_path is not None:
            definitionlist = generate_definitions_for_path(gpkg_path)
        else:
            with minio_resource(
                s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
            ) as localfilename:
                definitionlist = generate_definitions_for_path(localfilename)
        print(json.dumps(definitionlist, indent=4))
    except:
        logger.exception("Error while generating table definitions")


@cli.command(
    name="show-validations",
    help="Show all the possible validations that can be executed in the validate command.",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_show_validations():
    try:
        validation_codes = get_validation_descriptions()
        print(json.dumps(validation_codes, indent=4, sort_keys=True))
    except Exception:
        logger.exception("Error while listing validations")


if __name__ == "__main__":
    cli()
