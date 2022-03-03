import sys
import os
import warnings
from contextlib import contextmanager
from functools import lru_cache

from pathlib import Path
import json
import yaml

from typing import Callable, Optional

try:
    from osgeo import ogr, osr, gdal

    assert ogr  # silence pyflakes
    assert osr  # silence pyflakes
    assert gdal  # silence pyflakes
except (ImportError, AssertionError):
    sys.exit(
        "ERROR: cannot find GDAL/OGR modules, follow the instructions in the README to install these."
    )

GDAL_ENV_MAPPING = {
    "s3_no_sign_request": (
        "AWS_NO_SIGN_REQUEST",
        {True: "YES", False: "NO", "true": "YES", "false": "NO"},
    ),
    "s3_endpoint_no_protocol": ("AWS_S3_ENDPOINT", None),
    "s3_access_key": ("AWS_ACCESS_KEY_ID", None),
    "s3_secret_key": ("AWS_SECRET_ACCESS_KEY", None),
    "s3_session_token": ("AWS_SESSION_TOKEN", None),
    "s3_secure": (
        "AWS_HTTPS",
        {True: "YES", False: "NO", "true": "YES", "false": "NO"},
    ),
    "s3_virtual_hosting": (
        "AWS_VIRTUAL_HOSTING",
        {True: "TRUE", False: "FALSE", "true": "TRUE", "false": "FALSE"},
    ),
    "s3_signing_region": ("AWS_SIGNING_REGION", None),
}


def open_dataset(filename=None, error_handler=None):
    if error_handler is not None:
        gdal.UseExceptions()
        gdal.PushErrorHandler(error_handler)

    @contextmanager
    def silence_gdal():
        if error_handler is None:
            warnings.warn("cannot silence gdal without error handler")
            return
        gdal.PopErrorHandler()
        yield
        gdal.PushErrorHandler(error_handler)

    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(filename, 0)

    if dataset is not None:
        dataset.silence_gdal = silence_gdal

    return dataset


def check_gdal_version():
    """This method checks if GDAL has the right version and exits with an error otherwise."""
    version_num = int(gdal.VersionInfo("VERSION_NUM"))
    if version_num < 1100000:
        sys.exit("ERROR: Python bindings of GDAL 1.10 or later required")


@lru_cache(None)
def dataset_geometry_tables(dataset):
    """
    Generate a list of geometry type names from the gpkg_geometry_columns table.
    """
    geometry_type_names_result = dataset.ExecuteSQL(
        "SELECT table_name, column_name, geometry_type_name FROM gpkg_geometry_columns;"
    )
    geometry_type_names = [
        (table_name, column_name, geometry_type_name)
        for table_name, column_name, geometry_type_name in geometry_type_names_result
    ]
    dataset.ReleaseResultSet(geometry_type_names_result)
    return geometry_type_names


def load_config(file_path):
    path = Path(file_path)
    assert path.exists()
    with path.open() as file_handler:
        if path.suffix in (".yaml", ".yml"):
            return yaml.load(file_handler, Loader=yaml.SafeLoader)
        return json.load(file_handler)


def set_gdal_env(**kwargs):
    for k, v in kwargs.items():
        gdal_env_map = GDAL_ENV_MAPPING.get(k)
        if gdal_env_map is not None:
            gdal_env_parameter, gdal_argument_mapping = gdal_env_map
            if gdal_env_parameter and gdal_argument_mapping:
                v = gdal_argument_mapping.get(v, v)
            if gdal_env_parameter not in os.environ:
                gdal.SetConfigOption(gdal_env_parameter, v)
