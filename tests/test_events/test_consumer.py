from anqa.events.context import Context


async def test_consumer_process(test_consumer, ce):
    res = await test_consumer.process(ce, Context())
    assert res == 42


async def test_generic_consumer_process(generic_test_consumer, ce):
    res = await generic_test_consumer.process(ce, Context())
    assert res == 42
