
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
import pytest

from chapter10.datatypes import base


@pytest.fixture
def body():
    return base.Base(Mock(data_type=0, data_length=5, file=Mock(
        tell=Mock(return_value=5),
        read=Mock(return_value=b'1234'))))


def test_parse(body):
    body.parse()
    assert 'data' in body.__dict__