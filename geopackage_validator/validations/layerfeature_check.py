from typing import Iterable, Tuple

from geopackage_validator.validations import validator


# TODO: layer or table: make a choice

def layerfeature_check_query(dataset) -> Iterable[Tuple[str, int, int]]:
    for layer in dataset:
        layer_name = layer.GetName()

        table_featurecount = dataset.ExecuteSQL(
            "SELECT count(*) from {table_name}".format(table_name=layer_name)
        )
        (table_count, ) = table_featurecount.GetNextFeature()

        dataset.ReleaseResultSet(table_featurecount)

        yield layer_name, table_count, layer.GetFeatureCount()


class NonEmptyLayerValidator(validator.Validator):
    """Layers must have at least one feature."""

    code = 2
    level = validator.ValidationLevel.ERROR
    message = "Error layer: {layer}"

    def check(self) -> Iterable[str]:
        counts = layerfeature_check_query(self.dataset)
        return self.layerfeature_check_featurecount(counts)

    def layerfeature_check_featurecount(self, counts: Iterable[Tuple[str, int, int]]):
        assert counts is not None
        return [self.message.format(layer=layer) for layer, count, _ in counts if counts == 0]


class OGRIndexValidator(validator.Validator):
    """OGR indexed feature counts must be up to date"""

    code = 11
    level = validator.ValidationLevel.ERROR
    message = "OGR index for feature count is not up to date for table: {layer}. Indexed feature count: {ogr_count}, real feature count: {count}"

    def layerfeature_check_ogr_index(
        self, layers: Iterable[Tuple[str, int, int]]
    ):
        assert layers is not None

        return [
            self.message.format(layer=name, count=count, ogr_count=ogr_count)
            for name, count, ogr_count in layers if count != ogr_count
        ]
