# -*- coding: utf-8 -*-
"""Main CLI entry for the Geopackage validator tool."""
# Setup logging before package imports.
import logging
import sys
import traceback

import click
import click_log

from geopackage_validator.generate import generate_definitions_for_path
from geopackage_validator.minio.minio_context import minio_resource
from geopackage_validator.output import log_output
from geopackage_validator.validations_overview.validations_overview import (
    get_validations_list,
    result_format,
)

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

from geopackage_validator.validate import validate
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
    try:
        if gpkg_path is None and s3_endpoint_no_protocol is None:
            logger.error("Give --gpkg-path or s3 location")
            return

        if gpkg_path is not None:
            validate(
                gpkg_path,
                gpkg_path,
                table_definitions_path,
                validations_path,
                validations,
            )
        else:
            with minio_resource(
                s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
            ) as localfilename:
                validate(
                    localfilename,
                    s3_key,
                    table_definitions_path,
                    validations_path,
                    validations,
                )
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log_output(
            result_format(
                "system",
                trace=[
                    t.strip("\n")
                    for t in traceback.format_exception(
                        exc_type, exc_value, exc_traceback
                    )
                ],
            )
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
        validations_list = get_validations_list()
        print(json.dumps(validations_list, indent=4, sort_keys=True))
    except:
        logger.exception("Error while listing validations")


if __name__ == "__main__":
    cli()
