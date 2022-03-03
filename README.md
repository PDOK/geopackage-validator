# geopackage-validator

## Table of Contents

* [geopackage-validator](#geopackage-validator)
  * [What does it do](#What-does-it-do)
  * [Installation](#installation)
    * [Ubuntu](#ubuntu)
    * [Docker](#docker)
  * [Usage](#usage)
    * [Validate](#validate)
    * [Show validations](#show-validations)
    * [Generate table definitions](#generate-table-definitions)
  * [Performance](#performance)
  * [Local development](#local-development)
    * [Installation](#pipenv-installation)
    * [Usage](#pipenv-usage)
    * [Code style](#pipenv-code-style)
    * [Tests](#pipenv-tests)
    * [Releasing](#releasing)

## What does it do

The Geopackage validator can validate .gkpg files to see if they conform to a set of standards.
The current checks are (see also the 'show-validations' command):

| Validation code  | Description                                                                                                                                                                                         |
|:----------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  UNKNOWN_ERROR   | No unexpected (GDAL) errors must occur.                                                                                                                                                             |
|       RQ0        | _LEGACY:_ * Geopackage must conform to table names in the given JSON or YAML definitions.                                                                                                           |
|       RQ1        | Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.                                                                                               |
|       RQ2        | Layers must have at least one feature.                                                                                                                                                              |
|       RQ3        | _LEGACY:_ * Layer features should have an allowed geometry_type (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON).                                                  |
|       RQ4        | The geopackage should have no views defined.                                                                                                                                                        |
|       RQ5        | Geometry should be valid.                                                                                                                                                                           |
|       RQ6        | Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.                                                                                              |
|       RQ7        | Tables should have a feature id column with unique index.                                                                                                                                           |
|       RQ8        | Geopackage must conform to given JSON or YAML definitions.                                                                                                                                          |
|       RQ9        | All geometry tables must have an rtree index.                                                                                                                                                       |
|       RQ10       | All geometry table rtree indexes must be valid.                                                                                                                                                     |
|       RQ11       | OGR indexed feature counts must be up to date.                                                                                                                                                      |
|       RQ12       | Only the following EPSG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409. |
|       RQ13       | It is required to give all GEOMETRY features the same default spatial reference system.                                                                                                             |
|       RQ14       | The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON.                                                |
|       RQ15       | All table geometries must match the geometry_type_name from the gpkg_geometry_columns table.                                                                                                        |
|       RC1        | It is recommended to name all GEOMETRY type columns 'geom'.                                                                                                                                         |
|       RC2        | It is recommended to give all GEOMETRY type columns the same name.                                                                                                                                  |
|       RC3        | It is recommended to only use multidimensional geometry coordinates (elevation and measurement) when necessary.                                                                                     |
|       RC4        | It is recommended that all (MULTI)POLYGON geometries have a counter-clockwise orientation for their exterior ring, and a clockwise direction for all interior rings.                                |
| UNKNOWN_WARNINGS | It is recommended that the unexpected (GDAL) warnings are looked into.                                                                                                                              |

\* Legacy requirements are only executed with the validate command when explicitly requested in the validation set.  

## Installation

This package requires [GDAL](https://gdal.org/) version >= 3.2.1.
And python >= 3.8 to run.

We recommend using the docker image. When above requirements are met the package can be installed using pip (`pip install pdok-geopackage-validator`).  

### Docker

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
````

### Validate

```bash
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
docker run -v ${PWD}:/gpkg --rm pdok/geopackage-validator validate -t /path/to/generated_definitions.json --gpkg-path tests/data/test_allcorrect.gpkg
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

```bash
Usage: geopackage-validator show-validations [OPTIONS]

  Show all the possible validations that are executed in the validate
  command.

Options:
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --help               Show this message and exit.
```

### Generate table definitions

```bash
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
docker-compose build --build-arg uid=`id -u` --build-arg gid=`id -g`
```

### Usage

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

Code coverage:

```bash
docker-compose run --rm --cov=geopackage_validator  --cov-report html
```

### Releasing

Release in github by bumping the `__version__` in [`geopackage_validator.constants.py`](geopackage_validator/constants.py) and by creating and pushing a new tag to master and create a new release in github.  
