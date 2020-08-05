import logging

from geopackage_validator.gdal.prerequisites import (
    check_gdal_installed,
    check_gdal_version,
)
from geopackage_validator.validations.validate_all import validate_all

logger = logging.getLogger(__name__)


def main():
    """Starts the geopackage validation."""
    check_gdal_installed()
    check_gdal_version()

    # Explicit import
    from geopackage_validator.gdal.init import init_gdal

    init_gdal()

    validate_all()

    print("Validation done")
