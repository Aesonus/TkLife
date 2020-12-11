from tklife.behaviors import ThreadEvent, ThreadEventDispatcher
import pytest

class Listened(Exception):
    pass

class ShouldNotHaveListened(Exception):
    pass

class Event(ThreadEvent):
    pass

class NotListenedEvent(ThreadEvent):
    pass

@pytest.fixture(params=[((), {}), (('arg',), {})])
def calls_fixture(request):
    def not_used_listener(event):
        raise ShouldNotHaveListened(event)
    dispatcher = ThreadEventDispatcher((NotListenedEvent, not_used_listener))
    event = Event(*request.param)
    dispatcher.queue.put_nowait(event)
    return (dispatcher, request.param)

def test_poll_calls_methods_in_listeners_list(calls_fixture):
    dispatcher, expected_args = calls_fixture
    def listener_func(*args, **kwargs):
        raise Listened(args, kwargs)
    dispatcher.register_listener(Event, listener_func)
    with pytest.raises(Listened) as info:
        dispatcher.poll()
    assert info.value.args == expected_args