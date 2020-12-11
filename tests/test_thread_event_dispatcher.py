from tklife.behaviors import ThreadEventDispatcher
import pytest

class Listened(Exception):
    pass

class ShouldNotHaveListened(Exception):
    pass

@pytest.fixture
def dispatcher():
    def not_used_listener(event):
        raise ShouldNotHaveListened(event)
    dispatcher = ThreadEventDispatcher(("Not Used Event", not_used_listener))
    dispatcher.queue.put_nowait("Event")
    return dispatcher

def test_poll_calls_methods_in_listeners_list(dispatcher: ThreadEventDispatcher):
    def listener_func(event):
        raise Listened(event)
    dispatcher.register_listener('Event', listener_func)
    with pytest.raises(Listened, match='Event') as info:
        dispatcher.poll()
    