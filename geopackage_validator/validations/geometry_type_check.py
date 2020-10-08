from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def geometry_type_check_query(dataset) -> Iterable[Tuple[str, str]]:
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


def geometry_type_check(geometry_check_list: Iterable[Tuple[str, str]]):
    assert geometry_check_list is not None

    results = []

    for geometry in geometry_check_list:
        if geometry[1] not in VALID_GEOMETRIES:
            results.append(
                create_validation_message(
                    err_index="geometry_type",
                    layer=geometry[0],
                    found_geometry=geometry[1],
                    valid_geometries=",".join(VALID_GEOMETRIES),
                )
            )

    return result_format("geometry_type", results)
