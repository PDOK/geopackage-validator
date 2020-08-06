# -*- coding: utf-8 -*-
"""Main CLI entry for the Geopackage validator tool."""
# Setup logging before package imports.
import logging

import click
import click_log

from geopackage_validator.errors.error_messages import create_errormessage
from geopackage_validator.minio.minio_context import minio_resource
from geopackage_validator.output import log_output

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

from geopackage_validator.core import main
import sys


@click.group()
def cli():
    pass


@cli.command(name="local", help="Geopackage validator validating a local file")
@click.option(
    "--gpkg-path",
    required=True,
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
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_local(gpkg_path):
    try:
        main(gpkg_path)
    except:
        log_output([create_errormessage("system", error=sys.exc_info()[1])])


@cli.command(name="s3", help="Geopackage validator validating file from s3 storage")
@click.option(
    "--s3-endpoint-no-protocol",
    required=True,
    help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key", required=True, help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key", required=True, help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket",
    required=True,
    help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key", required=True, help="Key where the geopackage is in the bucket",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_s3(
    s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
):
    try:
        with minio_resource(
            s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
        ) as localfilename:
            main(localfilename)
    except:
        log_output([create_errormessage("system", error=sys.exc_info()[1])])


if __name__ == "__main__":
    cli()
