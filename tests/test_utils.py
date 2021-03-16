from geopackage_validator.utils import open_dataset, dataset_geometry_tables


def test_with_gpkg():
    dataset = open_dataset("tests/data/test_geom_columnname.gpkg")
    checks = list(dataset_geometry_tables(dataset))
    assert len(checks) == 3
    assert checks[0][0] == "test_columnname"
    assert checks[0][1] == "geom"
    assert checks[1][0] == "test_columnname2"
    assert checks[1][1] == "geometry"
    assert checks[2][0] == "test_columnname3"
    assert checks[2][1] == "geometry"
