# geopackage-validator

The Geopackage validator can validate .gkpg files to see if they conform to a set of standards.
The current checks are (see also the 'show-validations' command:

    "R1": "Layer names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.",
    "R2": "Layers must have at least one feature.",
    "R3": "Layer features should have a valid geometry (one of POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, or MULTIPOLYGON).",
    "R4": "The geopackage should have no views defined.",
    "R5": "Geometry should be valid.",
    "R6": "Column names must start with a letter, and valid characters are lowercase a-z, numbers or underscores.",
    "R7": "Tables should have a feature id column with unique index.",
    "R8": "Geopackage must conform to given JSON definitions",
    "R9": "All geometry tables must have an rtree index"
    "R10": "All geometry table rtree indexes must be valid",

## Usage through Docker



## Installation

Running with Docker is the recommended way of running this package. That way installation of all the dependencies is not necessary, as the Docker image is self contained. 

The geopackage-validator can be installed with:

```bash
pip install geopackage-validator
```

### GDAL

This package uses [Python bindings for GDAL](https://pypi.org/project/GDAL/)) and has a runtime dependency on an installed [GDAL](https://gdal.org/) (when not running through Docker, which is the recommended way of running this package.)

## Usage

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

  --s3-endpoint-no-protocol TEXT  Endpoint for the s3 service without protocol
                                  [env var: S3_ENDPOINT_NO_PROTOCOL]

  --s3-access-key TEXT            Access key for the s3 service  [env var:
                                  S3_ACCESS_KEY]

  --s3-secret-key TEXT            Secret key for the s3 service  [env var:
                                  S3_SECRET_KEY]

  --s3-bucket TEXT                Bucket where the geopackage is on the s3
                                  service  [env var: ssssss]

  --s3-key TEXT                   Key where the geopackage is in the bucket
                                  [env var: S3_KEY]

  -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                  DEBUG

  --help                          Show this message and exit.
```

### Show validations
```
Usage: geopackage-validator show-validations [OPTIONS]

  Show all the possible validations that are executed in the validate
  command.

Options:
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --help               Show this message and exit.
```

### Generate definitions
```
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

# Running with Docker

Place your geopackage somewhere on disk or in an S3 storage repository.

Build the Docker container (only once needed, or after an update)

```
docker build -t geopackage-validator .
```

Run the Docker image, mounting the current directory to /gpkg (adjust where needed)
```
docker run -v ${PWD}:/gpkg --rm geopackage-validator validate --gpkg-path /gpkg/tests/data/test_allcorrect.gpkg
```


## Development installation of this project itself

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

There will be a script you can run like this:

```bash
pipenv run geopackage-validator
```

In order to get nicely formatted python files without having to spend manual
work on it, run the following command periodically:

```bash
pipenv run black geopackage_validator
```

Run the tests regularly. This also checks with pyflakes, black and it reports
coverage. Pure luxury:

```bash
pipenv run pytest
```

If you need a new dependency (like `requests`), add it in `setup.py` in
`install_requires`. Afterwards, run install again to actually install your
dependency:

```bash
pipenv install --dev
```

## Releasing 
Pipenv installs zest.releaser which allows you to release the package to a git(hub) repo. It has a 
`fullrelease` command that asks you a few questions, which you all respond to with `<enter>`:

```bash
pipenv run fullrelease
```
# Install pyenv
We can install pyenv by running the following commands: 

```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

Also make sure to put pyenv in your `.bashrc` or `.zshrc` as instructed by the previous commands. 

