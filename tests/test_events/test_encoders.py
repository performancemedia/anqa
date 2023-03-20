import pytest

from anqa.events import CloudEvent
from anqa.events.encoders.json import JsonEncoder
from anqa.events.encoders.msgpack import MsgPackEncoder
from anqa.events.encoders.pickle import PickleEncoder


@pytest.mark.parametrize("encoder", (JsonEncoder, MsgPackEncoder, PickleEncoder))
@pytest.mark.parametrize("data", (1, "2", 3.0, [None], {"key": "value", "1": 2}))
def test_encoders_simple_data(encoder, data):
    encoded = encoder.encode(data)
    assert isinstance(encoded, bytes)
    decoded = encoder.decode(encoded)
    assert decoded == data


@pytest.mark.parametrize("encoder", (JsonEncoder, PickleEncoder))
@pytest.mark.parametrize("data", (1, "2", 3.0, [None], {"key": "value", "1": 2}))
def test_encoder_cloud_events(encoder, data):
    ce = CloudEvent(topic="test.topic", data=data, type="TestEvent")
    ce_dict = ce.dict()
    assert data == ce_dict["data"]
    encoded = encoder.encode(ce_dict)
    assert isinstance(encoded, bytes)
    decoded = encoder.decode(encoded)
    assert decoded["data"] == ce_dict["data"]
