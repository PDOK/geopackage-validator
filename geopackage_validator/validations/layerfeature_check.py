from typing import Iterable, Tuple

from geopackage_validator.validations_overview.validations_overview import (
    create_validation_message,
    result_format,
)


def layerfeature_check_query(dataset) -> Iterable[Tuple[str, int, int]]:
    for i in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(i)

        table_featurecount = dataset.ExecuteSQL(
            "SELECT count(*) from {table_name}".format(table_name=layer.GetName())
        )
        table = table_featurecount.GetNextFeature()

        dataset.ReleaseResultSet(table_featurecount)

        yield layer.GetName(), table[0], layer.GetFeatureCount()


def layerfeature_check_featurecount(
    layerfeaturecount_list: Iterable[Tuple[str, int, int]]
):
    assert layerfeaturecount_list is not None

    results = []

    for layername, feature_count_real, feature_count_ogr in layerfeaturecount_list:
        if feature_count_real == 0:
            results.append(
                create_validation_message(err_index="layerfeature", layer=layername)
            )

    return result_format("layerfeature", results)


def layerfeature_check_ogr_index(
    layerfeaturecount_list: Iterable[Tuple[str, int, int]]
):
    assert layerfeaturecount_list is not None

    results = []

    for layername, feature_count_real, feature_count_ogr in layerfeaturecount_list:
        if feature_count_real != feature_count_ogr:
            results.append(
                create_validation_message(
                    err_index="layerfeature_ogr",
                    layer=layername,
                    feature_count_real=feature_count_real,
                    feature_count_ogr=feature_count_ogr,
                )
            )

    return result_format("layerfeature_ogr", results)
