ARG GDAL_VERSION=3.9.1

FROM ghcr.io/osgeo/gdal:alpine-normal-${GDAL_VERSION} AS base
# docker run ghcr.io/osgeo/gdal:alpine-normal-3.9.1 python3 --version > Python 3.11.9

LABEL maintainer="Roel van den Berg <roel.vandenberg@kadaster.nl>"

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install --no-cache-dir setuptools pip --upgrade

WORKDIR /code

COPY ./geopackage_validator /code/geopackage_validator
COPY ./pyproject.toml /code/pyproject.toml
COPY ./setup.py /code/setup.py

# --- TEST-IMAGE ---
FROM base AS test-image
COPY ./tests /code/tests

RUN pip3 install --no-cache-dir .[test] && pytest

# --- BUILD IMAGE ---
FROM base AS build-image

RUN pip3 install --no-cache-dir .

ENTRYPOINT [ "geopackage-validator" ]
