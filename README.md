# geopackage-validator
Introduction

Usage, etc.


## Installation

We can be installed with:

```bash
pip install geopackage-validator
```


## Development installation of this project itself

We're installed with [pipenv](https://docs.pipenv.org/), a handy wrapper
around pip and virtualenv. Install that first with `pip install pipenv`. Then run:

**Bash:**
```bash
PIPENV_VENV_IN_PROJECT=1 pipenv install --python 3.8 --dev
```

**Windows CMD prompt:**
```
set PIPENV_VENV_IN_PROJECT=1
pipenv install --python 3.8 --dev
```


In case you do not have python 3.8 on your machine, install python using 
[pyenv](https://github.com/pyenv/pyenv) and try the previous command again.
See install pyenv below for instructions. 

There will be a script you can run like this::

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

