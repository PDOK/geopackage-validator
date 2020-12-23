from random import randint
from typing import Iterable, Tuple, List

from geopackage_validator.constants import VALID_GEOMETRIES
from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def geometry_type_check_query(dataset) -> Iterable[Tuple[str, str]]:
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(layer_index)
        features = layer.GetFeatureCount()
        if features == 1:
            for feature in layer:
                yield from get_layer_name_and_geometry_name(feature, layer)
        else:
            # select a maximum of 100 random elements/features from the layer
            random_feature_indexes: List[int] = [
                randint(1, features) for _ in range(min(features, 100))
            ]
            for randomIndex in random_feature_indexes:
                feature = layer.GetFeature(randomIndex)
                yield from get_layer_name_and_geometry_name(feature, layer)


def get_layer_name_and_geometry_name(feature, layer):
    if feature.GetGeometryRef() is not None:
        yield layer.GetName(), feature.GetGeometryRef().GetGeometryName()
    else:
        yield layer.GetName(), "UNKNOWN"


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
