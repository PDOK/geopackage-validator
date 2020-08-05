# -*- coding: utf-8 -*-
"""TODO Docstring."""
import logging
import sys

import click
import click_log

# Setup logging before package imports.
logger = logging.getLogger(__name__)
click_log.basic_config(logger)

from geopackage_validator.core import main
from geopackage_validator.error import AppError


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
    except AppError:
        logger.exception("geopackage_validator failed:")
        sys.exit(1)


@cli.command(name="s3", help="Geopackage validator validating file from s3 storage")
@click.option("--s3-endpoint-no-protocol", required=True,
    help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key",
    required=True,
    help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key",
    required=True,
    help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket",
    required=True,
    help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key",
    required=True,
    help="Key where the geopackage is in the bucket",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_s3(s3endpoint, s3accesskey, s3secretkey, s3bucket, s3key):
    try:
        main("")
    except AppError:
        logger.exception("geopackage_validator failed:")
        sys.exit(1)


if __name__ == "__main__":
    cli()
