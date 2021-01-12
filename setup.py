from setuptools import setup, find_packages
from configparser import ConfigParser

version = "0.4.2"

long_description = "\n\n".join([open("README.md").read(), open("CHANGES.md").read()])


def parse_pipfile(development=False):
    """Reads package requirements from Pipfile."""
    cfg = ConfigParser()
    cfg.read("Pipfile")
    dev_packages = [p.strip('"') for p in cfg["dev-packages"]]
    relevant_packages = [
        p.strip('"') for p in cfg["packages"] if "geopackage-validator" not in p
    ]
    if development:
        return dev_packages
    else:
        return relevant_packages


setup(
    name="pdok-geopackage-validator",
    version=version,
    description="Validate Geopackage files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python :: 3"],
    keywords=["geopackage-validator"],
    author="Daan van Etten",
    author_email="daan.vanetten@kadaster.nl",
    url="https://github.com/PDOK/geopackage-validator",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_pipfile(),
    tests_require=parse_pipfile(True),
    entry_points={
        "console_scripts": ["geopackage-validator = geopackage_validator.cli:cli"]
    },
)
