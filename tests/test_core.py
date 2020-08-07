# -*- coding: utf-8 -*-
"""Tests for validate.py"""

# import pytest

from geopackage_validator.validate import validate


# TODO
def test_noop():
    assert True


def test_main():
    validate("", "", "")
