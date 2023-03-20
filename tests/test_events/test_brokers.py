import pytest

from anqa.events.broker import Broker
from anqa.events.brokers.kafka import KafkaBroker
from anqa.events.brokers.nats import JetStreamBroker, NatsBroker
from anqa.events.brokers.rabbitmq import RabbitmqBroker

brokers = [NatsBroker, JetStreamBroker, KafkaBroker, RabbitmqBroker]


@pytest.mark.parametrize("broker", brokers)
def test_is_subclass(broker):
    assert issubclass(broker, Broker)
