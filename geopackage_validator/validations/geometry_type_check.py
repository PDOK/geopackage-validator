from random import randint
from typing import Iterable, Tuple, List

from geopackage_validator.constants import VALID_GEOMETRIES
from geopackage_validator.validations import validator


def query_geometry_types(dataset) -> Iterable[Tuple[str, str]]:
    for layer in dataset:
        feature_count = layer.GetFeatureCount()
        layer_name = layer.GetName()

        random_feature_indexes = {
            randint(1, feature_count) for _ in range(min(feature_count, 100))
        }
        for random_index in random_feature_indexes:
            feature = layer.GetFeature(random_index)
            yield layer_name, feature.GetGeometryRef().GetGeometryName() or "UNKNOWN"


class GeometryTypeValidator(validator.Validator):
    """Layer features should have a valid geometry (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON). (random sample of up to 100)"""

    code = 3
    level = validator.ValidationLevel.ERROR
    message = "Error layer: {layer}, found geometry: {geometry}"

    def check(self) -> Iterable[str]:
        geometries = query_geometry_types(self.dataset)
        return self.check_geometry_type(geometries)

    def check_geometry_type(self, geometries: Iterable[Tuple[str, str]]):
        assert geometries is not None

        return [
            self.message.format(layer=layer, geometry=geometry)
            for layer, geometry in geometries
            if geometry not in VALID_GEOMETRIES
        ]
