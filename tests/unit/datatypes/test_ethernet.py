
import os

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
import pytest

from chapter10 import C10
from chapter10.datatypes import ethernet


SAMPLE = os.path.join(os.path.dirname(__file__), '..', 'eth.c10')


@pytest.mark.parametrize(
    ('data_type',), [(t,) for t in range(0x6A, 0x70)])
def test_reserved(data_type):
    with pytest.raises(NotImplementedError):
        e = ethernet.Ethernet(Mock(
            file=Mock(tell=Mock(return_value=0),
                      read=Mock(return_value=b'1234')),
            pos=0,
            data_type=data_type,
            data_length=2))
        e.parse()


def test_format_0_count():
    for packet in C10(SAMPLE):
        if packet.data_type == 0x68:
            break
    assert len(packet.body) == packet.body.number_of_frames


def test_format_1_count():
    for packet in C10(SAMPLE):
        if packet.data_type == 0x69:
            break
    assert len(packet.body) == packet.body.count
