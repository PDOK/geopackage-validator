import sys
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
except:
    sys.exit(
        "ERROR: cannot find GDAL/OGR modules, follow the instructions in the README to install these."
    )


class Dataset(ogr.DataSource):
    """Wrapper around an ogr Datasource."""

    def __new__(cls, filename=None, error_handler=None, *args, **kwargs):
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
