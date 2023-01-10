# -*- coding: utf-8 -*-
"""Main CLI entry for the Geopackage validator tool."""
# Setup logging before package imports.
import logging
from datetime import datetime
from pathlib import Path
import sys
import time

import click
import click_log

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


from geopackage_validator import generate
from geopackage_validator import s3
from geopackage_validator import output
from geopackage_validator import validate
from geopackage_validator import utils


@click.group()
def cli():
    pass


@cli.command(
    name="validate",
    help=(
        "Geopackage validator validating a local file or a file from S3 storage. When the filepath is preceded with "
        "'/vsis3' or '/vsicurl' the gdal virtual file system will be used to access the file on S3 and will not be "
        "directly downloaded. See https://gdal.org/user/virtual_file_systems.html for further explanation how to use "
        "gdal virtual file systems. For convenience the gdal vsi environment parameters and optional parameters are "
        "provided with an S3_ instead of an AWS_ prefix. The AWS_ environment parameters will also work.\n\n"
        "Examples:\n\n"
        "viscurl:\n\n"
        "geopackage-validator validate --gpkg-path /vsicurl/http://minio-url.nl/bucketname/key/to/public.gpkg\n\n"
        "vsis3:\n\n"
        "geopackage-validator validate --gpkg-path /vsis3/bucketname/key/to/public.gpkg --s3-signing-region eu-central-1 --s3-secret-key secret --s3-access-key acces-key --s3-secure=false --s3-virtual-hosting false --s3-endpoint-no-protocol minio-url.nl\n\n"
        "S3_SECRET_KEY=secret S3_ACCESS_KEY=acces-key S3_SIGNING_REGION=eu-central-1 S3_SECURE=false S3_VIRTUAL_HOSTING=false S3_ENDPOINT_NO_PROTOCOL=minio-url.nl geopackage-validator validate --gpkg-path /vsis3/bucketname/key/to/public.gpkg\n\n"
        "AWS_SECRET_ACCESS_KEY=secret AWS_ACCESS_KEY_ID=acces-key AWS_DEFAULT_REGION=eu-central-1 AWS_HTTPS=NO AWS_VIRTUAL_HOSTING=FALSE AWS_S3_ENDPOINT=minio-url.nl geopackage-validator validate --gpkg-path /vsis3/bucketname/key/to/public.gpkg"
    ),
)
@click.option(
    "--gpkg-path",
    envvar="GPKG_PATH",
    show_envvar=True,
    required=False,
    default=None,
    help="Path pointing to the geopackage.gpkg file",
    type=click.types.Path(
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "-t",
    "--table-definitions-path",
    show_envvar=True,
    required=False,
    default=None,
    help=(
        "Path pointing to the table-definitions  JSON or YAML file (generate this file by calling the "
        "generate-definitions command)"
    ),
    type=click.types.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "--validations-path",
    show_envvar=True,
    required=False,
    default=None,
    envvar="VALIDATIONS_FILE",
    help=(
        "Path pointing to the set of validations to run. If validations-path and validations are not given, validate "
        "runs all validations"
    ),
    type=click.types.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "--validations",
    show_envvar=True,
    required=False,
    default="",
    envvar="VALIDATIONS",
    help=(
        "Comma-separated list of validations to run (e.g. --validations RQ1,RQ2,RQ3). If validations-path and "
        "validations are not given, validate runs all validations"
    ),
)
@click.option(
    "--exit-on-fail",
    required=False,
    is_flag=True,
    help="Exit with code 1 when validation success is false.",
)
@click.option(
    "--yaml",
    required=False,
    is_flag=True,
    help="Output yaml.",
)
@click.option(
    "--s3-endpoint-no-protocol",
    envvar="S3_ENDPOINT_NO_PROTOCOL",
    show_envvar=True,
    help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key",
    envvar="S3_ACCESS_KEY",
    show_envvar=True,
    help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key",
    envvar="S3_SECRET_KEY",
    show_envvar=True,
    help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket",
    envvar="S3_BUCKET",
    show_envvar=True,
    help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key",
    envvar="S3_KEY",
    show_envvar=True,
    help="Key where the geopackage is in the bucket",
)
@click.option(
    "--s3-secure",
    envvar="S3_SECURE",
    show_envvar=True,
    type=click.types.BoolParamType(),
    default="true",
    help="Use a secure TLS connection for S3.",
)
@click.option(
    "--s3-virtual-hosting",
    envvar="S3_VIRTUAL_HOSTING",
    show_envvar=True,
    help=(
        "TRUE value, identifies the bucket via a virtual bucket host name, e.g.: mybucket.cname.domain.com - FALSE "
        "value, identifies the bucket as the top-level directory in the URI, e.g.: cname.domain.com/mybucket. "
        "Convenience parameter, same as gdal AWS_VIRTUAL_HOSTING."
    ),
)
@click.option(
    "--s3-signing-region",
    envvar="S3_SIGNING_REGION",
    show_envvar=True,
    help="S3 signing region. Convenience parameter, same as gdal AWS_DEFAULT_REGION.",
)
@click.option(
    "--s3-no-sign-request",
    envvar="S3_NO_SIGN_REQUEST",
    show_envvar=True,
    help=(
        "When set, request signing is disabled. This option might be used for buckets with public access rights. "
        "Convenience parameter, same as gdal AWS_NO_SIGN_REQUEST."
    ),
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command(
    gpkg_path,
    table_definitions_path,
    validations_path,
    validations,
    exit_on_fail,
    yaml,
    s3_endpoint_no_protocol,
    s3_access_key,
    s3_secret_key,
    s3_bucket,
    s3_key,
    s3_secure,
    s3_virtual_hosting,
    s3_signing_region,
    s3_no_sign_request,
):
    start_time = datetime.now()
    duration_start = time.monotonic()
    gpkg_path_not_exists = s3_endpoint_no_protocol is None and (
        gpkg_path is None
        or (not gpkg_path.startswith("/vsi") and not Path(gpkg_path).exists())
    )
    if gpkg_path_not_exists:
        logger.error("Give --gpkg-path or s3 location")
        sys.exit(1)

    if gpkg_path is not None:
        utils.set_gdal_env(
            s3_endpoint_no_protocol=s3_endpoint_no_protocol,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            s3_secure=s3_secure,
            s3_virtual_hosting=s3_virtual_hosting,
            s3_signing_region=s3_signing_region,
            s3_no_sign_request=s3_no_sign_request,
        )
        filename = gpkg_path
        results, validations_executed, success = validate.validate(
            gpkg_path,
            table_definitions_path,
            validations_path,
            validations,
        )
    else:
        try:
            with s3.minio_resource(
                s3_endpoint_no_protocol,
                s3_access_key,
                s3_secret_key,
                s3_bucket,
                s3_key,
                s3_secure,
            ) as localfilename:
                filename = s3_key
                results, validations_executed, success = validate.validate(
                    localfilename,
                    table_definitions_path,
                    validations_path,
                    validations,
                )
        except (AssertionError, IOError) as e:
            logger.error(str(e))
            sys.exit(1)
    duration_seconds = time.monotonic() - duration_start
    output.log_output(
        filename=filename,
        results=results,
        validations_executed=validations_executed,
        start_time=start_time,
        duration_seconds=duration_seconds,
        success=success,
        as_yaml=yaml,
    )
    if exit_on_fail and not success:
        sys.exit(1)


@cli.command(
    name="generate-definitions",
    help=(
        "Generate table definition for a geopackage on local or S3 storage. Use the generated definition JSON or YAML "
        "in the validation step by providing the table definitions with the --table-definitions-path parameter. When "
        "the filepath is preceded with '/vsi' the gdal virtual file system method will be used to access the file on "
        "S3 and will not be directly downloaded. See https://gdal.org/user/virtual_file_systems.html for further "
        "explanation. For convenience the gdal vsi environment parameters and optional parameters are provided with "
        "an S3_ instead of an AWS_ prefix. The AWS_ environment parameters will also work.\n\n"
        "Examples:\n\n"
        "viscurl:\n\n"
        "geopackage-validator generate-definitions --gpkg-path /vsicurl/http://minio-url.nl/bucketname/key/to/public.gpkg\n\n"
        "vsis3:\n\n"
        "geopackage-validator generate-definitions --gpkg-path /vsis3/bucketname/key/to/public.gpkg --s3-signing-region eu-central-1 --s3-secret-key secret --s3-access-key acces-key --s3-secure=false --s3-virtual-hosting false --s3-endpoint-no-protocol minio-url.nl\n\n"
        "S3_SECRET_KEY=secret S3_ACCESS_KEY=acces-key S3_SIGNING_REGION=eu-central-1 S3_SECURE=false S3_VIRTUAL_HOSTING=false S3_ENDPOINT_NO_PROTOCOL=minio-url.nl geopackage-validator generate-definitions --gpkg-path /vsis3/bucketname/key/to/public.gpkg\n\n"
        "AWS_SECRET_ACCESS_KEY=secret AWS_ACCESS_KEY_ID=acces-key AWS_DEFAULT_REGION=eu-central-1 AWS_HTTPS=NO AWS_VIRTUAL_HOSTING=FALSE AWS_S3_ENDPOINT=minio-url.nl geopackage-validator generate-definitions --gpkg-path /vsis3/bucketname/key/to/public.gpkg"
    ),
)
@click.option(
    "--gpkg-path",
    envvar="GPKG_PATH",
    required=False,
    default=None,
    show_envvar=True,
    help="Path pointing to the geopackage.gpkg file",
    type=click.types.Path(
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        allow_dash=False,
    ),
)
@click.option(
    "--yaml",
    required=False,
    is_flag=True,
    help="Output yaml",
)
@click.option(
    "--s3-endpoint-no-protocol",
    envvar="S3_ENDPOINT_NO_PROTOCOL",
    show_envvar=True,
    help="Endpoint for the s3 service without protocol",
)
@click.option(
    "--s3-access-key",
    envvar="S3_ACCESS_KEY",
    show_envvar=True,
    help="Access key for the s3 service",
)
@click.option(
    "--s3-secret-key",
    envvar="S3_SECRET_KEY",
    show_envvar=True,
    help="Secret key for the s3 service",
)
@click.option(
    "--s3-bucket",
    envvar="S3_BUCKET",
    show_envvar=True,
    help="Bucket where the geopackage is on the s3 service",
)
@click.option(
    "--s3-key",
    envvar="S3_KEY",
    show_envvar=True,
    help="Key where the geopackage is in the bucket",
)
@click.option(
    "--s3-secure",
    envvar="S3_SECURE",
    show_envvar=True,
    type=click.types.BoolParamType(),
    default="true",
    help="Use a secure TLS connection for S3.",
)
@click.option(
    "--s3-virtual-hosting",
    envvar="S3_VIRTUAL_HOSTING",
    show_envvar=True,
    help=(
        "TRUE value, identifies the bucket via a virtual bucket host name, e.g.: mybucket.cname.domain.com - FALSE "
        "value, identifies the bucket as the top-level directory in the URI, e.g.: cname.domain.com/mybucket. "
        "Convenience parameter, same as gdal AWS_VIRTUAL_HOSTING."
    ),
)
@click.option(
    "--s3-signing-region",
    envvar="S3_SIGNING_REGION",
    show_envvar=True,
    help="S3 signing region. Convenience parameter, same as gdal AWS_DEFAULT_REGION.",
)
@click.option(
    "--s3-no-sign-request",
    envvar="S3_NO_SIGN_REQUEST",
    show_envvar=True,
    help=(
        "When set, request signing is disabled. This option might be used for buckets with public access rights. "
        "Convenience parameter, same as gdal AWS_NO_SIGN_REQUEST."
    ),
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_generate_table_definitions(
    gpkg_path,
    yaml,
    s3_endpoint_no_protocol,
    s3_access_key,
    s3_secret_key,
    s3_bucket,
    s3_key,
    s3_secure,
    s3_virtual_hosting,
    s3_signing_region,
    s3_no_sign_request,
):
    gpkg_path_not_exists = s3_endpoint_no_protocol is None and (
        gpkg_path is None
        or (not gpkg_path.startswith("/vsi") and not Path(gpkg_path).exists())
    )
    if gpkg_path_not_exists:
        logger.error("Give a valid --gpkg-path or (/vsi)s3 location")
        sys.exit(1)
    try:
        if gpkg_path is not None:
            utils.set_gdal_env(
                s3_endpoint_no_protocol=s3_endpoint_no_protocol,
                s3_access_key=s3_access_key,
                s3_secret_key=s3_secret_key,
                s3_bucket=s3_bucket,
                s3_key=s3_key,
                s3_secure=s3_secure,
                s3_virtual_hosting=s3_virtual_hosting,
                s3_signing_region=s3_signing_region,
                s3_no_sign_request=s3_no_sign_request,
            )
            definitionlist = generate.generate_definitions_for_path(gpkg_path)
        else:
            with s3.minio_resource(
                s3_endpoint_no_protocol,
                s3_access_key,
                s3_secret_key,
                s3_bucket,
                s3_key,
                s3_secure,
            ) as localfilename:
                definitionlist = generate.generate_definitions_for_path(localfilename)
        output.print_output(definitionlist, yaml)
    except Exception:
        logger.exception("Error while generating table definitions")
        sys.exit(1)


@cli.command(
    name="show-validations",
    help="Show all the possible validations that can be executed in the validate command.",
)
@click.option(
    "--yaml",
    required=False,
    is_flag=True,
    help="Output yaml",
)
@click_log.simple_verbosity_option(logger)
def geopackage_validator_command_show_validations(yaml):
    try:
        validation_codes = validate.get_validation_descriptions()
        output.print_output(validation_codes, yaml, yaml_indent=5)
    except Exception:
        logger.exception("Error while listing validations")
        sys.exit(1)


if __name__ == "__main__":
    cli()
