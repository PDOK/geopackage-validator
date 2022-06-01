ARG GDAL_VERSION=3.5.0

FROM osgeo/gdal:alpine-normal-${GDAL_VERSION} AS base

LABEL maintainer="Roel van den Berg <roel.vandenberg@kadaster.nl>"

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV PYTHON_VERSION=3.9

# --- COMPILE-IMAGE ---
FROM base AS compile-image
ENV DEBIAN_FRONTEND=noninteractive

# Install dev dependencies
RUN python3 -m ensurepip

RUN pip3 install --no-cache-dir setuptools pip pipenv --upgrade

# Copy source
WORKDIR /code
COPY . /code

# Install packages, and check for deprecations and vulnerabilities
RUN PIPENV_VENV_IN_PROJECT=1 pipenv --python ${PYTHON_VERSION} --site-packages
# Ignore numpy vulnerabilities for now that comes from osgeo/gdal:alpine-normal-3.5.0
RUN pipenv sync & pipenv check -i 44716 -i 44717 -i 44715

# Run pytest tests.
# Install packages, including the dev (test) packages.
RUN pipenv sync --dev && pipenv run pytest

# Cleanup test packages. We want to use pipenv uninstall --all-dev but that command is
# broken. See: https://github.com/pypa/pipenv/issues/3722
RUN pipenv --rm && \
    PIPENV_VENV_IN_PROJECT=1 pipenv --python ${PYTHON_VERSION} --site-packages && \
    pipenv sync

# --- BUILD IMAGE ---
FROM base AS build-image

WORKDIR /code

COPY --from=compile-image "/code/pdok_geopackage_validator.egg-info/" "/code/pdok_geopackage_validator.egg-info/"
COPY --from=compile-image "/code/geopackage_validator" "/code/geopackage_validator"
COPY --from=compile-image /code/.venv /code/.venv
COPY --from=compile-image "/usr/local/lib/python${PYTHON_VERSION}/dist-packages" "/usr/local/lib/python${PYTHON_VERSION}/dist-packages"

# Make sure we use the virtualenv:
ENV PATH="/code/.venv/bin:$PATH"

ENTRYPOINT [ "geopackage-validator" ]
