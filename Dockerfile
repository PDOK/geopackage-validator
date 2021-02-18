FROM osgeo/gdal:ubuntu-small-3.0.4 AS base

## In case you need base debian dependencies install them here.
#RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
#    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# --- COMPILE-IMAGE ---
FROM base AS compile-image
ENV DEBIAN_FRONTEND=noninteractive

# Install dev dependencies
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
        python3-pip && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade --no-cache-dir setuptools pip
RUN pip3 install --no-cache-dir pipenv

# Copy source
WORKDIR /code
COPY . /code

# Install packages, including the dev (test) packages.
RUN PIPENV_VENV_IN_PROJECT=1 pipenv --three --site-packages
RUN pipenv sync --dev

# Run pytest tests.
# pipenv check fails due to a github connection error. Pipenv check scans for python
# vulnerabilities amongst other things. We might want to debug and fix this:
# RUN PIPENV_PYUP_API_KEY="" pipenv check &&
#RUN pipenv run pytest

# Cleanup test packages. We want to use pipenv uninstall --all-dev but that command is
# broken. See: https://github.com/pypa/pipenv/issues/3722
RUN pipenv --rm && \
    PIPENV_VENV_IN_PROJECT=1 pipenv --three --site-packages && \
    pipenv sync

# --- BUILD IMAGE ---
FROM base AS build-image
WORKDIR /code

COPY --from=compile-image "/code/pdok_geopackage_validator.egg-info/" "/code/pdok_geopackage_validator.egg-info/"
COPY --from=compile-image "/code/geopackage_validator" "/code/geopackage_validator"
COPY --from=compile-image /code/.venv /code/.venv
COPY --from=compile-image "/usr/local/lib/python3.6/dist-packages" "/usr/local/lib/python3.6/dist-packages"

# Make sure we use the virtualenv:
ENV PATH="/code/.venv/bin:$PATH"

# Metadata params
ARG BUILD_DATE
ARG VERSION
ARG GIT_COMMIT_HASH

# Metadata
LABEL org.opencontainers.image.authors="Daan van Etten daan.vanetten@kadaster.nl" \
      org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.title="geopackage-validator" \
      org.opencontainers.image.description="Validate Geopackage files" \
      org.opencontainers.image.url="https://github.com/PDOK/geopackage-validator" \
      org.opencontainers.image.vendor="PDOK" \
      org.opencontainers.image.source="https://github.com/PDOK/geopackage-validator" \
      org.opencontainers.image.revision=$GIT_COMMIT_HASH \
      org.opencontainers.image.version=$VERSION

ENTRYPOINT [ "geopackage-validator" ]
