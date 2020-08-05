# geopackage-validator
Introduction



## Installation

We can be installed with:

```bash
pip install geopackage-validator
```

### GDAL

This package uses bindings for GDAL and has a runtime dependency on an installed GDAL (when not running through Docker)

## Usage

```
NAME:
   geopackage-validator local - geopackage validator validating a local file

USAGE:
   geopackage-validator local [command options] [arguments...]

OPTIONS:
   --config-path value  Path pointing to a json file with configuration (./config.json) [$CONFIG_PATH]
   --gpkg-path value    Path pointing to the geopackage (./geopackage.gpkg) [$GPKG_PATH]
```

# Running

Place your geopackage in the example directory.

You can run this tool from a directory containing geopackages. The tool will then attempt to validate all geopackages present in the directory.

e.g.
* docker  build -t test .
* docker run --rm test


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

It runs the `main()` function in `geopackage-validator/scripts.py`,
adjust that if necessary. The script is configured in `setup.py` (see
`entry_points`).

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

