import os
from minio import Minio


from geopackage_validator.minio import minio_resource


def test_minio_context(mocker):
    s3_endpoint_no_protocol = "endpoint"
    s3_access_key = "s3_access_key"
    s3_secret_key = "s3_secret_key"
    s3_bucket = "s3_bucket"
    s3_key = "s3_key"

    bucket_exists_stub = mocker.stub(name="bucket_exists_stub")
    stat_object_stub = mocker.stub(name="stat_object_stub")
    fget_object_stub = mocker.stub(name="fget_object_stub")

    stub = Minio
    stub.bucket_exists = bucket_exists_stub
    stub.stat_object = stat_object_stub
    stub.fget_object = fget_object_stub

    with minio_resource(
        s3_endpoint_no_protocol,
        s3_access_key,
        s3_secret_key,
        s3_bucket,
        s3_key,
        minio=stub,
    ) as localfilename:
        assert os.path.exists(localfilename.replace(".gpkg", ""))
        bucket_exists_stub.assert_called_once_with(s3_bucket)
        stat_object_stub.assert_called_once_with(
            bucket_name=s3_bucket, object_name=s3_key
        )
        fget_object_stub.assert_called_once_with(
            bucket_name=s3_bucket, object_name=s3_key, file_path=localfilename
        )
