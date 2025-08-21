ARG GDAL_VERSION=3.9.3
FROM ghcr.io/osgeo/gdal:alpine-normal-${GDAL_VERSION}

WORKDIR /code

RUN python3 -m venv --system-site-packages venv

ADD local_entrypoint.sh /entry/local_entrypoint.sh
ENTRYPOINT ["/entry/local_entrypoint.sh"]