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
|       RQ1       | Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. |
|       RQ2       | Layers must have at least one feature.                       |
|       RQ3       | Layer features should have an allowed geometry_type (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON). |
|       RQ4       | The geopackage should have no views defined.                 |
|       RQ5       | Geometry should be valid.                                    |
|       RQ6       | Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores. |
|       RQ7       | Tables should have a feature id column with unique index.    |
|       RQ8       | Geopackage must conform to given JSON definitions.           |
|       RQ9       | All geometry tables must have an rtree index.                |
|       RQ10      | All geometry table rtree indexes must be valid.              |
|       RQ11      | OGR indexed feature counts must be up to date.               |
|       RQ12      | Only the following ESPG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409. |
|       RQ13      | It is required to give all GEOMETRY features the same default spatial reference system. |
|       RQ14      | The geometry_type_name from the gpkg_geometry_columns table must be one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON. |
|       RQ15      | All table geometries must match the geometry_type_name from the gpkg_geometry_columns table. |
|       RC1       | It is recommended to name all GEOMETRY type columns 'geom'.  |
|       RC2       | It is recommended to give all GEOMETRY type columns the same name. |

## Installation

This package requires [GDAL](https://gdal.org/) version >= 3.0.4.
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

### Windows


Either use anaconda to install gdal:

```bash
conda install -c conda-forge gdal
```

Or download and install [OSGeo4W](https://trac.osgeo.org/osgeo4w/). And download
[get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run it in the OSGeo4W shell:

```bash
python3 get-pip.py
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
                                  Path pointing to the table-definitions JSON
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

  --exit-on-fail                  Exit with code 1 when validation success
                                  is false.

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

Generate Geopackage table definition JSON from given local or s3 package. This command generates a definition that describes the Geopackage layout, in JSON format. This JSON, when saved in a file, can be used in the validation step to validate a Geopackage against these table definitions.

```bash
Usage: geopackage-validator generate-definitions [OPTIONS]

  Generate Geopackage table definition JSON from given local or s3 package.
  Use the generated definition JSON in the validation step by providing the
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

### Pipenv installation

We're installed with [pipenv](https://docs.pipenv.org/), a handy wrapper
around pip and virtualenv. Install that first with `pip install pipenv`.

Install the GDAL native library version 3.0.4 and development headers:

```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev -y
```

Make sure you have GDAL version 3.0.4:

```bash
$ gdalinfo --version
GDAL 3.0.4, released 2020/01/28
```

Then install the dependencies of this project:

```bash
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
PIPENV_VENV_IN_PROJECT=1 pipenv install --python 3.8 --dev
```

In case you do not have python 3.8 on your machine, install python using
[pyenv](https://github.com/pyenv/pyenv) and try the previous command again.
See install pyenv below for instructions.

If you need a new dependency (like `requests`), add it in `setup.py` in
`install_requires`. Afterwards, run install again to actually install your
dependency:

```bash
pipenv install --dev
```

### Pipenv usage

There will be a script you can run like this:

```bash
pipenv run geopackage-validator
```

### Code style

In order to get nicely formatted python files without having to spend manual
work on it, run the following command periodically:

```bash
pipenv run black geopackage_validator
```

### Tests

Run the tests regularly. This also checks with pyflakes and black:

```bash
pipenv run pytest
```

Code coverage:

```bash
pipenv run pytest --cov=geopackage_validator  --cov-report html
```

### Releasing

Release in github by creating and pushing a new tag to master and create a new release in github.  



## Install pyenv

We can install pyenv by running the following commands:

```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

Also make sure to put pyenv in your `.bashrc` or `.zshrc` as instructed by the previous commands.
