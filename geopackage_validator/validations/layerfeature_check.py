from typing import Iterable, Tuple

from geopackage_validator.validations import validator


def query_layerfeature_counts(dataset) -> Iterable[Tuple[str, int, int]]:
    for layer in dataset:
        layer_name = layer.GetName()

        table_featurecount = dataset.ExecuteSQL(
            'SELECT count(*) from "{table_name}"'.format(table_name=layer_name)
        )
        (table_count,) = table_featurecount.GetNextFeature()

        dataset.ReleaseResultSet(table_featurecount)

        yield layer_name, table_count, layer.GetFeatureCount()


class NonEmptyLayerValidator(validator.Validator):
    """Layers must have at least one feature."""

    code = 2
    level = validator.ValidationLevel.ERROR
    message = "Error layer: {layer}"

    def check(self) -> Iterable[str]:
        counts = query_layerfeature_counts(self.dataset)
        return self.check_contains_features(counts)

    @classmethod
    def check_contains_features(cls, counts: Iterable[Tuple[str, int, int]]):
        assert counts is not None
        return [
            cls.message.format(layer=layer) for layer, count, _ in counts if count == 0
        ]


class OGRIndexValidator(validator.Validator):
    """OGR indexed feature counts must be up to date"""

    code = 11
    level = validator.ValidationLevel.ERROR
    message = "OGR index for feature count is not up to date for table: {layer}. Indexed feature count: {ogr_count}, real feature count: {count}"

    def check(self) -> Iterable[str]:
        counts = query_layerfeature_counts(self.dataset)
        return self.layerfeature_check_ogr_index(counts)

    @classmethod
    def layerfeature_check_ogr_index(cls, layers: Iterable[Tuple[str, int, int]]):
        assert layers is not None

        return [
            cls.message.format(layer=name, count=count, ogr_count=ogr_count)
            for name, count, ogr_count in layers
            if count != ogr_count
        ]
