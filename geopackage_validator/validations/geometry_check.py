from geopackage_validator.errors.validation_errors import create_errormessage


def geometry_check_query(dataset):
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(layer_index)
        for feature in layer:
            yield layer.GetName(), feature.GetGeometryRef().GetGeometryName()


VALID_GEOMETRIES = [
    "POINT",
    "LINESTRING",
    "POLYGON",
    "MULTIPOINT",
    "MULTILINESTRING",
    "MULTIPOLYGON",
]


def geometry_check(geometry_check_list=None):
    assert geometry_check_list is not None

    errors = []

    for geometry in geometry_check_list:
        if geometry[1] not in VALID_GEOMETRIES:
            errors.append(
                create_errormessage(
                    err_index="geometry",
                    layer=geometry[0],
                    found_geometry=geometry[1],
                    valid_geometries=",".join(VALID_GEOMETRIES),
                )
            )

    return errors
