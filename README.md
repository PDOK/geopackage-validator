# PDOK geopackage-validator

[![Tests](https://github.com/pdok/geopackage-validator/actions/workflows/pytest.yml/badge.svg)](https://github.com/pdok/geopackage-validator/actions/workflows/pytest.yml)[![PyPI version](https://badge.fury.io/py/pdok-geopackage-validator.svg)](https://pypi.org/project/pdok-geopackage-validator/)

Geopackages are a data format that have a deliberately broad application, so many of the requirements are dependend on your use.

The PDOK geopackage validator is used by [PDOK](https://www.pdok.nl/). PDOK is part of the Dutch government. This geopackage validator is used to validate a [set of requirements](#what-does-it-do) to make sure geopackages adhere to our standardized ETL pipeline. It is possible to use this for your own purposes as described [here](https://github.com/PDOK/geopackage-validator/issues/115#issuecomment-1529488733). The validations will not change (except for bugfixes); **new validations are always added to the list**. In  case you are looking for a more generic validator. These do exist and can be found:

- [teamengine](https://cite.opengeospatial.org/teamengine) (official OGC, Java)
  - [teamengine Github](https://github.com/opengeospatial/teamengine)
  - [OGC GeoPackage 1.2 Conformance Test Suite](https://github.com/opengeospatial/ets-gpkg12)
- [validate_gpkg.py](https://github.com/OSGeo/gdal/blob/master/swig/python/gdal-utils/osgeo_utils/samples/validate_gpkg.py) (part of gdal repo)

## Table of Contents

- [geopackage-validator](#pdok-geopackage-validator)
  - [Table of Contents](#table-of-contents)
  - [What does it do](#what-does-it-do)
  - [Geopackage versions](#geopackage-versions)
  - [Installation](#installation)
    - [Docker](#docker-installation)
  - [Usage](#usage)
    - [RQ8 Validation](#rq8-validation)
    - [Show validations](#show-validations)
    - [Generate table definitions](#generate-table-definitions)
  - [Local development](#local-development)
    - [Docker run](#docker-run)
    - [Python console](#python-console)
    - [Code style](#code-style)
    - [Tests](#tests)
    - [Releasing](#releasing)

## TL;DR Commands

Either run through [docker](#docker) or [locally](#local).

### Docker

Validate a GeoPackage with the default set of validation rules:

```sh
gpkg_path=relative/path/to/the.gpkg
docker run -v "$(pwd)":/gpkg --rm pdok/geopackage-validator validate --gpkg-path "/gpkg/${gpkg_path}"
```

Validate a GeoPackage with the default set of validation rules including a schema:

```sh
schema_path=relative/path/to/the/schema.json
gpkg_path=relative/path/to/the.gpkg
docker run -v "$(pwd)":/gpkg --rm pdok/geopackage-validator validate --gpkg-path "/gpkg/${gpkg_path}" --table-definitions-path "/gpkg/${schema_path}"
```

Generate a schema:

```sh
schema_path=relative/path/to/the/schema.json
gpkg_path=relative/path/to/the.gpkg
docker run -v "$(pwd)":/gpkg --rm pdok/geopackage-validator generate-definitions --gpkg-path "/gpkg/${gpkg_path}" > "$schema_path"
```

### Local

For a local setup we require/tested against python > 3.6 and gdal = 3.4.

```sh
gpkg_path=relative/path/to/the.gpkg
geopackage-validator validate --gpkg-path "/gpkg/${gpkg_path}"
```

Validate a GeoPackage with the default set of validation rules including a schema:

```sh
schema_path=relative/path/to/the/schema.json
gpkg_path=relative/path/to/the.gpkg
geopackage-validator validate --gpkg-path "/gpkg/${gpkg_path}" --table-definitions-path "/gpkg/${schema_path}"
```

Generate a schema:

```sh
schema_path=relative/path/to/the/schema.json
gpkg_path=relative/path/to/the.gpkg
geopackage-validator generate-definitions --gpkg-path "/gpkg/${gpkg_path}" > "$schema_path"
```

## What does it do

The Geopackage validator can validate .gkpg files to see if they conform to a set of standards.
The current checks are (see also the 'show-validations' command):

| Validation code** | Description                                                                                                                                                                                                              |
|:-----------------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   UNKNOWN_ERROR   | No unexpected (GDAL) errors must occur.                                                                                                                                                                                  |
|        RQ0        | _LEGACY:_ use RQ8 * Geopackage must conform to table names in the given JSON or YAML definitions.                                                                                                                        |
|        RQ1        | Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.                                                                                                                    |
|        RQ2        | Layers must have at least one feature.                                                                                                                                                                                   |
|        RQ3        | _LEGACY:_ use RQ14 * Layer features should have an allowed geometry_type (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON).                                                              |
|        RQ4        | The geopackage should have no views defined.                                                                                                                                                                             |
|        RQ5        | _LEGACY:_ use RQ23 * Geometry should be valid and in GeoPackage format.                                                                                                                                                                           |
|        RQ6        | Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.                                                                                                                   |
|        RQ7        | Tables should have a feature id column with unique index.                                                                                                                                                                |
|        RQ8        | Geopackage must conform to given JSON or YAML definitions.                                                                                                                                                               |
|        RQ9        | All geometry tables must have an rtree index.                                                                                                                                                                            |
|       RQ10        | All geometry table rtree indexes must be valid.                                                                                                                                                                          |
|       RQ11        | OGR indexed feature counts must be up to date.                                                                                                                                                                           |
|       RQ12        | _LEGACY:_ use RQ22 * Only the following EPSG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409. |
|       RQ13        | It is required to give all GEOMETRY features the same default spatial reference system.                                                                                                                                  |
|       RQ14        | The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON.                                                                     |
|       RQ15        | All table geometries must match the geometry_type_name from the gpkg_geometry_columns table.                                                                                                                             |
|       RQ16        | _LEGACY:_ use RQ21 * All layer and column names shall not be longer than 53 characters.                                                                                                                                  |
|       RQ21        | All layer and column names shall not be longer than 57 characters.                                                                                                                                                       |
|       RQ22        | Only the following EPSG spatial reference systems are allowed: 28992, 3034, 3035, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3857, 4258, 4326, 4936, 4937, 5730, 7409.                                  |
|       RQ23        | Geometry should be valid, simple and in GeoPackage format.                                                                                                                                                                                     |
|       RQ24        | Geometry should not be null or empty (e.g. 'POINT EMPTY', WKT 'POINT(NaN NaN)').                                                                                                                                         |
|       RC17        | It is recommended to name all GEOMETRY type columns 'geom'.                                                                                                                                                              |
|       RC18        | It is recommended to give all GEOMETRY type columns the same name.                                                                                                                                                       |
|       RC19        | It is recommended to only use multidimensional geometry coordinates (elevation and measurement) when necessary.                                                                                                          |
|       RC20        | It is recommended that all (MULTI)POLYGON geometries have a counter-clockwise orientation for their exterior ring, and a clockwise direction for all interior rings.                                                     |
| UNKNOWN_WARNINGS  | It is recommended that the unexpected (GDAL) warnings are looked into.                                                                                                                                                   |

\* Legacy requirements are only executed with the validate command when explicitly requested in the validation set.  
\** Since version 0.8.0 the recommendations are part of the same sequence as the requirements. From now on a check will always maintain the integer part of the code. Even if at a later time the validation type can shift between requirement and recommendation.

An explanation in Dutch with a reason for each rule can be found [here](https://www.pdok.nl/voor-data-aanbieders#:~:text=Regels%20in%20detail).

## Geopackage versions

The Geopackage validator support the following Geopackage versions:

- 1.4
- 1.3.1
- 1.3
- 1.2.1

## Installation

This package requires:

- [GDAL](https://gdal.org/) version >= 3.2.1.
- [Spatialite](https://www.gaia-gis.it/fossil/libspatialite/index) version >= 5.0.0
- And python >= 3.8 to run.

We recommend using the docker image. When above requirements are met the package can be installed using pip (`pip install pdok-geopackage-validator`).

### Docker Installation

Pull the latest version of the Docker image (only once needed, or after an update)

```bash
docker pull pdok/geopackage-validator:latest
```

Or build the Docker image from source:

```bash
docker build -t pdok/geopackage-validator .
```

The command is directly called so subcommands can be run in the container directly:

```bash
docker run -v ${PWD}:/gpkg --rm pdok/geopackage-validator validate -t /path/to/generated_definitions.json --gpkg-path /gpkg/tests/data/test_allcorrect.gpkg
```

## Usage

### RQ8 Validation

To validate RQ8 you have to generate definitions first.

```bash
docker run -v ${PWD}:/gpkg --rm pdok/geopackage-validator geopackage-validator generate-definitions --gpkg-path /path/to/file.gpkg
```

### Validate

```text
Usage: geopackage-validator validate [OPTIONS]

  Geopackage validator validating a local file or a file from S3 storage.
  When the filepath is preceded with '/vsis3' or '/vsicurl' the gdal virtual
  file system will be used to access the file on S3 and will not be directly
  downloaded. See https://gdal.org/user/virtual_file_systems.html for
  further explanation how to use gdal virtual file systems. For convenience
  the gdal vsi environment parameters and optional parameters are provided
  with an S3_ instead of an AWS_ prefix. The AWS_ environment parameters
  will also work.

  Examples:

  viscurl:

  geopackage-validator validate --gpkg-path /vsicurl/http://minio-
  url.nl/bucketname/key/to/public.gpkg

  vsis3:

  geopackage-validator validate --gpkg-path
  /vsis3/bucketname/key/to/public.gpkg --s3-signing-region eu-central-1
  --s3-secret-key secret --s3-access-key acces-key --s3-secure=false
  --s3-virtual-hosting false --s3-endpoint-no-protocol minio-url.nl

  S3_SECRET_KEY=secret S3_ACCESS_KEY=acces-key S3_SIGNING_REGION=eu-
  central-1 S3_SECURE=false S3_VIRTUAL_HOSTING=false
  S3_ENDPOINT_NO_PROTOCOL=minio-url.nl geopackage-validator validate --gpkg-
  path /vsis3/bucketname/key/to/public.gpkg

  AWS_SECRET_ACCESS_KEY=secret AWS_ACCESS_KEY_ID=acces-key
  AWS_DEFAULT_REGION=eu-central-1 AWS_HTTPS=NO AWS_VIRTUAL_HOSTING=FALSE
  AWS_S3_ENDPOINT=minio-url.nl geopackage-validator validate --gpkg-path
  /vsis3/bucketname/key/to/public.gpkg

Options:
  --gpkg-path FILE                Path pointing to the geopackage.gpkg file
                                  [env var: GPKG_PATH]

  -t, --table-definitions-path FILE
                                  Path pointing to the table-definitions  JSON
                                  or YAML file (generate this file by calling
                                  the generate-definitions command)

  --validations-path FILE         Path pointing to the set of validations to
                                  run. If validations-path and validations are
                                  not given, validate runs all validations
                                  [env var: VALIDATIONS_FILE]

  --validations TEXT              Comma-separated list of validations to run
                                  (e.g. --validations RQ1,RQ2,RQ3). If
                                  validations-path and validations are not
                                  given, validate runs all validations  [env
                                  var: VALIDATIONS]

  --exit-on-fail                  Exit with code 1 when validation success is
                                  false.

  --yaml                          Output yaml.
  --s3-endpoint-no-protocol TEXT  Endpoint for the s3 service without protocol
                                  [env var: S3_ENDPOINT_NO_PROTOCOL]

  --s3-access-key TEXT            Access key for the s3 service  [env var:
                                  S3_ACCESS_KEY]

  --s3-secret-key TEXT            Secret key for the s3 service  [env var:
                                  S3_SECRET_KEY]

  --s3-bucket TEXT                Bucket where the geopackage is on the s3
                                  service  [env var: S3_BUCKET]

  --s3-key TEXT                   Key where the geopackage is in the bucket
                                  [env var: S3_KEY]

  --s3-secure BOOLEAN             Use a secure TLS connection for S3.  [env
                                  var: S3_SECURE]

  --s3-virtual-hosting TEXT       TRUE value, identifies the bucket via a
                                  virtual bucket host name, e.g.:
                                  mybucket.cname.domain.com - FALSE value,
                                  identifies the bucket as the top-level
                                  directory in the URI, e.g.:
                                  cname.domain.com/mybucket. Convenience
                                  parameter, same as gdal AWS_VIRTUAL_HOSTING.
                                  [env var: S3_VIRTUAL_HOSTING]

  --s3-signing-region TEXT        S3 signing region. Convenience parameter,
                                  same as gdal AWS_DEFAULT_REGION.  [env var:
                                  S3_SIGNING_REGION]

  --s3-no-sign-request TEXT       When set, request signing is disabled. This
                                  option might be used for buckets with public
                                  access rights. Convenience parameter, same
                                  as gdal AWS_NO_SIGN_REQUEST.  [env var:
                                  S3_NO_SIGN_REQUEST]

  -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                  DEBUG

  --help                          Show this message and exit.
```

Examples:

```bash
docker run -v ${PWD}:/gpkg --rm pdok/geopackage-validator validate -t /path/to/generated_definitions.json --gpkg-path /gpkg/tests/data/test_allcorrect.gpkg
```

Run with specific validations only

Specified in file:

```bash
docker run -v ${PWD}:/gpkg --rm pdok/geopackage-validator validate --gpkg-path tests/data/test_allcorrect.gpkg --validations-path tests/validationsets/example-validation-set.json
```

Or specified on command line:

```bash
docker run -v ${PWD}:/gpkg --rm pdok/geopackage-validator validate --gpkg-path tests/data/test_allcorrect.gpkg --validations RQ1,RQ2,RQ3
```

### Show validations

Show all the possible validations that are executed in the validate command.

```text
Usage: geopackage-validator show-validations [OPTIONS]

  Show all the possible validations that are executed in the validate
  command.

Options:
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --help               Show this message and exit.
```

### Generate table definitions

```text
Usage: geopackage-validator generate-definitions [OPTIONS]

  Generate table definition for a geopackage on local or S3 storage. Use the
  generated definition JSON or YAML in the validation step by providing the
  table definitions with the --table-definitions-path parameter. When the
  filepath is preceded with '/vsi' the gdal virtual file system method will
  be used to access the file on S3 and will not be directly downloaded. See
  https://gdal.org/user/virtual_file_systems.html for further explanation.
  For convenience the gdal vsi environment parameters and optional
  parameters are provided with an S3_ instead of an AWS_ prefix. The AWS_
  environment parameters will also work.

  Examples:

  viscurl:

  geopackage-validator validate --gpkg-path /vsicurl/http://minio-
  url.nl/bucketname/key/to/public.gpkg

  vsis3:

  geopackage-validator generate-definitions --gpkg-path
  /vsis3/bucketname/key/to/public.gpkg --s3-signing-region eu-central-1
  --s3-secret-key secret --s3-access-key acces-key --s3-secure=false
  --s3-virtual-hosting false --s3-endpoint-no-protocol minio-url.nl

  S3_SECRET_KEY=secret S3_ACCESS_KEY=acces-key S3_SIGNING_REGION=eu-
  central-1 S3_SECURE=false S3_VIRTUAL_HOSTING=false
  S3_ENDPOINT_NO_PROTOCOL=minio-url.nl geopackage-validator generate-definitions --gpkg-
  path /vsis3/bucketname/key/to/public.gpkg

  AWS_SECRET_ACCESS_KEY=secret AWS_ACCESS_KEY_ID=acces-key
  AWS_DEFAULT_REGION=eu-central-1 AWS_HTTPS=NO AWS_VIRTUAL_HOSTING=FALSE
  AWS_S3_ENDPOINT=minio-url.nl geopackage-validator generate-definitions --gpkg-path
  /vsis3/bucketname/key/to/public.gpkg

Options:
  --gpkg-path FILE                Path pointing to the geopackage.gpkg file
                                  [env var: GPKG_PATH]

  --yaml                          Output yaml

  --with-indexes-and-fks          Include indexes (and unique constraints) and
                                  foreign keys in the definitions

  --s3-endpoint-no-protocol TEXT  Endpoint for the s3 service without protocol
                                  [env var: S3_ENDPOINT_NO_PROTOCOL]

  --s3-access-key TEXT            Access key for the s3 service  [env var:
                                  S3_ACCESS_KEY]

  --s3-secret-key TEXT            Secret key for the s3 service  [env var:
                                  S3_SECRET_KEY]

  --s3-bucket TEXT                Bucket where the geopackage is on the s3
                                  service  [env var: S3_BUCKET]

  --s3-key TEXT                   Key where the geopackage is in the bucket
                                  [env var: S3_KEY]

  --s3-secure BOOLEAN             Use a secure TLS connection for S3.  [env
                                  var: S3_SECURE]

  --s3-virtual-hosting TEXT       TRUE value, identifies the bucket via a
                                  virtual bucket host name, e.g.:
                                  mybucket.cname.domain.com - FALSE value,
                                  identifies the bucket as the top-level
                                  directory in the URI, e.g.:
                                  cname.domain.com/mybucket. Convenience
                                  parameter, same as gdal AWS_VIRTUAL_HOSTING.
                                  [env var: S3_VIRTUAL_HOSTING]

  --s3-signing-region TEXT        S3 signing region. Convenience parameter,
                                  same as gdal AWS_DEFAULT_REGION.  [env var:
                                  S3_SIGNING_REGION]

  --s3-no-sign-request TEXT       When set, request signing is disabled. This
                                  option might be used for buckets with public
                                  access rights. Convenience parameter, same
                                  as gdal AWS_NO_SIGN_REQUEST.  [env var:
                                  S3_NO_SIGN_REQUEST]

  -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                  DEBUG

  --help                          Show this message and exit.
```

## Local development

We advise using docker-compose for local development. This allows live editing and testing code with the correct gdal/ogr version with spatialite 5.0.0.
First build the local image with your machines user id and group id:

```bash
docker-compose build --build-arg USER_ID=`id -u` --build-arg GROUP_ID=`id -g`
```

### Docker run

There will be a script you can run like this:

```bash
docker-compose run --rm validator geopackage-validator
```

This command has direct access to the files found in this directory. In case you want
to point the docker-compose to other files, you can add or edit the volumes in the `docker-compose.yaml`

### Python console

Ipython is available in the docker:

```bash
docker-compose run --rm validator ipython
```

### Code style

In order to get nicely formatted python files without having to spend manual
work on it, run the following command periodically:

```bash
docker-compose run --rm validator black .
```

### Tests

Run the tests regularly. This also checks with pyflakes and black:

```bash
docker-compose run --rm validator pytest
```

### Releasing

Release in github by creating a new release in github.
