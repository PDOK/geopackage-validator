import pytest

from geopackage_validator.validations.lowercasecheck import lowercasecheck


def test_lowercasetable_success:
    assert len(lowercasecheck(tablename_list=["table", "lowercase", "is", "good"])) == 0