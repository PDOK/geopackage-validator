from minio import Minio
import tempfile
import os
from contextlib import contextmanager


@contextmanager
def minio_resource(
    s3_endpoint_no_protocol: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_bucket: str,
    s3_key: str,
    secure: bool = True,
    minio=Minio,
) -> str:
    assert s3_endpoint_no_protocol is not None, "S3 endpoint has to be given"
    assert s3_access_key is not None, "S3 access key has to be given"
    assert s3_secret_key is not None, "S3 secret key has to be given"
    assert s3_bucket is not None, "S3 bucket has to be given"
    assert s3_key is not None, "S3 key has to be given"

    # Code to acquire resource, e.g.:
    localfile = tempfile.NamedTemporaryFile(delete=False)
    localfilename = localfile.name + ".gpkg"
    localfile.close()

    try:
        minio_client = minio(
            s3_endpoint_no_protocol,
            access_key=s3_access_key,
            secret_key=s3_secret_key,
            secure=secure,
        )

        if not minio_client.bucket_exists(s3_bucket):
            # This will throw an exception if no connection can be made
            pass

        minio_client.stat_object(bucket_name=s3_bucket, object_name=s3_key)

        try:
            # Download file
            minio_client.fget_object(
                bucket_name=s3_bucket, object_name=s3_key, file_path=localfilename
            )

            yield localfilename
        except (ValueError, IOError):
            raise IOError("Could not open file from S3")

    finally:
        if os.path.exists(localfilename):
            os.unlink(localfilename)
