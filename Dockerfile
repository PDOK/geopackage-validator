ARG GDAL_VERSION=3.6.2

FROM osgeo/gdal:alpine-normal-${GDAL_VERSION} AS base

LABEL maintainer="Roel van den Berg <roel.vandenberg@kadaster.nl>"

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install --no-cache-dir setuptools pip --upgrade

WORKDIR /code

COPY ./geopackage_validator /code/geopackage_validator
COPY ./pyproject.toml /code/pyproject.toml
COPY ./setup.cfg /code/setup.cfg
COPY ./setup.py /code/setup.py

# --- TEST-IMAGE ---
FROM base AS test-image
COPY ./tests /code/tests

RUN pip3 install --no-cache-dir .[test] && pytest

# --- BUILD IMAGE ---
FROM base AS build-image

RUN pip3 install --no-cache-dir .

ENTRYPOINT [ "geopackage-validator" ]
