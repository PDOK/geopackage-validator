# -*- coding: utf-8 -*-
"""Main CLI entry for the Geopackage validator tool."""
# Setup logging before package imports.
import logging

import click
import click_log

from geopackage_validator.errors.error_messages import create_errormessage
from geopackage_validator.generate import generate_definitions
from geopackage_validator.minio.minio_context import minio_resource
from geopackage_validator.output import log_output

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

from geopackage_validator.validate import validate
import sys
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
    "--s3-endpoint-no-protocol", help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key", help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key", help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket", help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key", help="Key where the geopackage is in the bucket",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_local(
    gpkg_path, s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
):
    try:
        if gpkg_path is not None:
            validate(gpkg_path)
        else:
            with minio_resource(
                s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
            ) as localfilename:
                validate(localfilename)
    except:
        log_output([create_errormessage("system", error=sys.exc_info()[1])])


@cli.command(
    name="generate-definitions",
    help="Geopackage validator generate Geopackage definition JSON from given local or s3 package",
)
@click.option(
    "--gpkg-path",
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
    "--s3-endpoint-no-protocol", help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key", help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key", help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket", help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key", help="Key where the geopackage is in the bucket",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_generate_table_definitions(
    gpkg_path, s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
):
    try:
        if gpkg_path is not None:
            generate_definitions(gpkg_path)
        else:
            with minio_resource(
                s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
            ) as localfilename:
                definitionlist = generate_definitions(localfilename)
                print(json.dumps(definitionlist, indent=4, sort_keys=True))
    except:
        logger.exception("Error while generating table definitions")


if __name__ == "__main__":
    cli()
