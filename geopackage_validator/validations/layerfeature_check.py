from geopackage_validator.errors.error_messages import create_errormessage


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

    return errors