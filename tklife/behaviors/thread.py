
from queue import Empty, Queue

__all__ = ['ThreadEvent', 'ThreadEventDispatcher']

class ThreadEvent:
    def __init__(self, args=(), kwargs={}):
        """
        Class that describes the event from a thread.
        args and kwargs will be passed to the listener function
        by the event dispatcher
        """
        self.args = args
        self.kwargs = kwargs

class ThreadEventDispatcher:
    def __init__(self, *listeners, queue=None) -> None:
        """
        Sets up the event queue

        You may pass listeners in the following format:
        iterable(
            tuple(event_class, listener_function),
            ...
        )

        You may specify your own queue class if desired
        """
        self.queue = Queue() if queue is None else queue()
        self.__listeners = dict()
        for event, listener in listeners:
            self.register_listener(event, listener)

    def register_listener(self, event, listener):
        """
        Registers a listener for the given event class
        The listeners are called in the same order they are added
        """
        try:
            self.__listeners[event].append(listener)
        except KeyError:
            self.__listeners[event] = [listener]

    def remove_listener(self, event, listener):
        """
        Removes the listener given for the given event.
        Does nothing if there is no event listeners registered
        """
        try:
            self.__listeners[event].remove(listener)
        except KeyError:
            pass

    def poll(self, call_after=None):
        """
        Gets the next event from the queue and calls all of the
        listeners with the arguments given to the event instance

        Calls the call_after function if it is given. Usually this
        should be the tkinter.Widget.after method to run this method
        on a schedule
        """
        try:
            event = self.queue.get_nowait()
        except Empty:
            pass
        else:
            for event_queue, listeners in self.__listeners.items():
                if not isinstance(event, event_queue):
                    continue
                [listener(*event.args, **event.kwargs) for listener in listeners]
        if callable(call_after):
            call_after()