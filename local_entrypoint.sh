#!/usr/bin/env sh
# this entrypoint does just that: make sure the egg-info dir is available by installing (again) with pip.
if [ ! -d /code/pdok_geopackage_validator.egg-info/ ] || [ ! -d /code/venv/ ]
then
  python3 -m venv --system-site-packages /code/venv
  . /code/venv/bin/activate
  pip3 install -e .[test]
else
  . /code/venv/bin/activate
fi
exec "$@"
