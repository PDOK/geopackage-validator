#!/usr/bin/env sh
export PIPENV_VENV_IN_PROJECT=1

if [ ! -d ./.venv/ ]
then
  echo "No pipenv environment found. Install a .venv/ directory in this directory."
  pipenv install --dev --site-packages -v
fi
pipenv run "$@"
