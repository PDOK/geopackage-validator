# geopackage-validator

## Table of Contents

* [geopackage-validator](#geopackage-validator)
  * [What does it do](#What-does-it-do)
  * [Installation](#installation)
    * [Ubuntu](#ubuntu)
    * [Windows](#windows)
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

| Validation code | Description                                                  |
| :-------------: | ------------------------------------------------------------ |
|       RQ0       | _LEGACY:_ * Geopackage must conform to table names in the given JSON or YAML definitions. |
|       RQ1       | Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. |
|       RQ2       | Layers must have at least one feature.                       |
|       RQ3       | _LEGACY:_ * Layer features should have an allowed geometry_type (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON). |
|       RQ4       | The geopackage should have no views defined.                 |
|       RQ5       | Geometry should be valid.                                    |
|       RQ6       | Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. |
|       RQ7       | Tables should have a feature id column with unique index.    |
|       RQ8       | Geopackage must conform to given JSON or YAML definitions.           |
|       RQ9       | All geometry tables must have an rtree index.                |
|       RQ10      | All geometry table rtree indexes must be valid.              |
|       RQ11      | OGR indexed feature counts must be up to date.               |
|       RQ12      | Only the following EPSG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409. |
|       RQ13      | It is required to give all GEOMETRY features the same default spatial reference system. |
|       RQ14      | The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON. |
|       RQ15      | All table geometries must match the geometry_type_name from the gpkg_geometry_columns table. |
|       RC1       | It is recommended to name all GEOMETRY type columns 'geom'.  |
|       RC2       | It is recommended to give all GEOMETRY type columns the same name. |
|       RC3       | It is recommended to only use multidimensional geometry coordinates (elevation and measurement) when necessary. |
|       RC3       | It is recommended that all (MULTI)POLYGON geometries have a counter-clockwise orientation for their exterior ring, and a clockwise direction for all interior rings. |

\* Legacy requirements are only executed with the validate command when explicitly requested in the validation set.  

## Installation

This package requires [GDAL](https://gdal.org/) version >= 3.2.1.
And python >= 3.8 to run.

### Ubuntu

Install GDAL:

```sudo
sudo apt-get install gdal-bin
```

Install the validator with:  

```bash
pip3 install pdok-geopackage-validator
```

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
geopackage-validator generate-definitions --gpkg-path /path/to/file.gpkg
````

### Validate

```bash
Usage: geopackage-validator validate [OPTIONS]

  Geopackage validator validating a local file or from s3 storage

Options:
  --gpkg-path FILE                Path pointing to the geopackage.gpkg file
                                  [env var: GPKG_PATH]

  -t, --table-definitions-path FILE
                                  Path pointing to the table-definitions JSON or YAML
                                  file (generate this file by calling the
                                  generate-definitions command)

  --validations-path FILE         Path pointing to the set of validations to
                                  run. If validations-path and validations are
                                  not given, validate runs all validations
                                  [env var: VALIDATIONS_FILE]

  --validations TEXT              Comma-separated list of validations to run
                                  (e.g. --validations R1,R2,R3). If
                                  validations-path and validations are not
                                  given, validate runs all validations  [env
                                  var: VALIDATIONS]

  --exit-on-fail                  Exit with code 1 when validation success is
                                  false.

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

  -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                  DEBUG

  --help                          Show this message and exit.
```

Examples:

```bash
pipenv run geopackage-validator validate -t /path/to/generated_definitions.json --gpkg-path tests/data/test_allcorrect.gpkg
```

Run with specific validations only

Specified in file:

```bash
pipenv run geopackage-validator validate --gpkg-path tests/data/test_allcorrect.gpkg --validations-path tests/validationsets/example-validation-set.json
```

Or specified on command line:

```bash
pipenv run geopackage-validator validate --gpkg-path tests/data/test_allcorrect.gpkg --validations R1,R2,R3
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

Generate Geopackage table definition JSON or YAML from given local or s3 package. This command generates a definition that describes the Geopackage layout, in JSON or YAML format. This output, when saved in a file, can be used in the validation step to validate a Geopackage against these table definitions.

```bash
Usage: geopackage-validator generate-definitions [OPTIONS]

  Generate Geopackage table definition file from given local or s3 package.
  Use the generated definition in the validation step by providing the
  table definitions with the --table-definitions-path parameter.

Options:
  --gpkg-path FILE                Path pointing to the geopackage.gpkg file
                                  [env var: GPKG_PATH]

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

  -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                  DEBUG

  --help                          Show this message and exit.
```

## Performance

On a PC with 32GB memory and Intel Core i7-8850H CPU @ 2.6 ghz, the following performance has been measured:

| Geopackage size | Time needed for validation | MB / minute     |
| --------------- | -------------------------- | --------------- |
| 315 MB          | 0.5 minutes                | 630 MB / minute |
| 6.3 GB          | 12.5 minutes               | 504 MB / minute |
| 9.9 GB          | 17.5 minutes               | 565 MB / minute |
| 15.7 GB         | 24 minutes                 | 654 MB / minute |

This is to give an indication of the performance and by no means a guarantee.

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
