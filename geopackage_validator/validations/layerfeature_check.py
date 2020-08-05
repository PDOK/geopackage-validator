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
                {
                    "errortype": "R2",
                    "errormessage": "Layers must have at least one feature. Error layer: {layer}".format(
                        layer=layername
                    ),
                }
            )

    return errors
