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


@cli.command(name="geopackage_validator")
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
def geopackage_validator_command(gpkg_path):
    """
    Validate the given Geopackage
    """
    try:
        main(gpkg_path)
    except AppError:
        logger.exception("geopackage_validator failed:")
        sys.exit(1)


if __name__ == "__main__":
    cli()
