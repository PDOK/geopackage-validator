from osgeo import ogr
from osgeo.ogr import DataSource


def open_dataset(filename: str) -> DataSource:
    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.Open(filename, 0)
    return dataset
