"""Contains behaviors for ui functionality"""
from queue import Empty, Queue
from typing import Any

class CommandHistory:
    """Saves command history for undo and redo"""
    def __init__(self):
        """
        Initializes the tracking dict
        """
        self.history = []
        # The cursor will be on the command to be undone or None if
        # all history is undone or history is empty
        self.cursor = None

    def add_history(self, command):
        """Adds a command to the command chain and calls it's execute method"""
        self._clear()
        self.history.append(command)
        self.cursor = self.history.index(command)
        command.execute()

    def undo(self):
        """Calls reverse on the previous command"""
        if self.cursor is None:
            return None
        command = self.history[self.cursor]
        command.reverse()
        new_cursor = self.cursor - 1
        if new_cursor < 0:
            self.cursor = None
            return None
        self.cursor = new_cursor
        return command

    def redo(self):
        """Calls execute on the next command"""
        if self.cursor is None and len(self.history) == 0:
            return None
        if self.cursor is None and len(self.history) > 0:
            self.cursor = -1
        if self.cursor == self.history.index(self.history[-1]):
            return None
        self.cursor += 1
        command = self.history[self.cursor]
        command.execute()
        return command

    def undo_all(self, until=None):
        """Calls undo on all of the history"""
        while self.cursor != until:
            self.undo()

    def reset(self):
        """Clears the history completely"""
        self.history.clear()
        self.cursor = None

    def _clear(self):
        """
        Clears the history after the cursor
        """
        if self.cursor is None:
            self.history = []
            return
        self.history = self.history[:self.cursor + 1]
    
    def __len__(self):
        """
        Returns the commands that can be reversed (undo)
        Useful for unsaved indicators and warnings
        """
        return len(tuple(self.iter_history()))

    def iter_history(self):
        """
        Yields each item in history up to the cursor position
        Useful for displaying all changes
        """
        for command in (self.history[:self.cursor + 1] if self.cursor is not None else []):
            yield command

class Command:
    """Abstract class for a command"""
    def execute(self) -> None:
        """
        Executes this command
        """
        raise NotImplementedError

    def reverse(self) -> None:
        """
        Reverses this command
        """
        raise NotImplementedError

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