#!/usr/bin/env sh

# this entrypoint does just that: make sure the egg-info dir is available by installing (again) with pip.
if [ ! -d ./pdok_geopackage_validator.egg-info/ ]
then
  pip3 install --no-cache-dir -e .
fi
exec "$@"
