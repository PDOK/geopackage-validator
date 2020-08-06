from minio import Minio
import tempfile
import os
from contextlib import contextmanager


@contextmanager
def minio_resource(
    s3_endpoint_no_protocol, s3_access_key, s3_secret_key, s3_bucket, s3_key
):
    # Code to acquire resource, e.g.:
    localfile = tempfile.NamedTemporaryFile(delete=False)
    localfilename = localfile.name + ".gpkg"
    localfile.close()

    try:
        minio_client = Minio(
            s3_endpoint_no_protocol,
            access_key=s3_access_key,
            secret_key=s3_secret_key,
            secure=False,
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
        except:
            raise Exception("Could not open file from S3")

    finally:
        if os.path.exists(localfilename):
            os.unlink(localfilename)
