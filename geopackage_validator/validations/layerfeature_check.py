from geopackage_validator.validations_overview.validations_overview import (
    create_errormessage,
    error_format,
)


def layerfeature_check_query(dataset):
    for i in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(i)
        yield layer.GetName(), layer.GetFeatureCount()


def layerfeature_check(layerfeaturecount_list=None):
    assert layerfeaturecount_list is not None

    errors = []

    for layername, feature_count in layerfeaturecount_list:
        if feature_count == 0:
            errors.append(
                create_errormessage(err_index="layerfeature", layer=layername)
            )

    return error_format("layerfeature", errors)
