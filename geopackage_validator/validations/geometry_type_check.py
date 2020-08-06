from geopackage_validator.errors.error_messages import create_errormessage


def geometry_type_check_query(dataset):
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(layer_index)
        for feature in layer:
            if feature.GetGeometryRef() is not None:
                yield layer.GetName(), feature.GetGeometryRef().GetGeometryName()
            else:
                yield layer.GetName(), "UNKNOWN"


VALID_GEOMETRIES = [
    "POINT",
    "LINESTRING",
    "POLYGON",
    "MULTIPOINT",
    "MULTILINESTRING",
    "MULTIPOLYGON",
]


def geometry_type_check(geometry_check_list=None):
    assert geometry_check_list is not None

    errors = []

    for geometry in geometry_check_list:
        if geometry[1] not in VALID_GEOMETRIES:
            errors.append(
                create_errormessage(
                    err_index="geometry_type",
                    layer=geometry[0],
                    found_geometry=geometry[1],
                    valid_geometries=",".join(VALID_GEOMETRIES),
                )
            )

    return errors
