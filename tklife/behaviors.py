"""Contains behaviors for ui functionality"""
from queue import Empty, Queue

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
            return
        self.history[self.cursor].reverse()
        new_cursor = self.cursor - 1
        if new_cursor < 0:
            self.cursor = None
            return
        self.cursor = new_cursor

    def redo(self):
        """Calls execute on the next command"""
        if self.cursor is None and len(self.history) == 0:
            return
        if self.cursor is None and len(self.history) > 0:
            self.cursor = -1
        if self.cursor == self.history.index(self.history[-1]):
            return
        self.cursor += 1
        self.history[self.cursor].execute()

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
        return len(self.history)

class Command:
    """Abstract class for a command"""
    def execute(self):
        """
        Executes this command
        """
        raise NotImplementedError

    def reverse(self):
        """
        Reverses this command
        """
        raise NotImplementedError

class ThreadEvent:
    def __init__(self, args=(), kwargs={}):
        self.args = args
        self.kwargs = kwargs

class ThreadEventDispatcher:
    def __init__(self, *listeners, queue=None) -> None:
        self.queue = Queue() if queue is None else queue()
        self.__listeners = dict()
        for event, listener in listeners:
            self.register_listener(event, listener)

    def register_listener(self, event, listener):
        try:
            self.__listeners[event].append(listener)
        except KeyError:
            self.__listeners[event] = [listener]

    def poll(self):
        try:
            event = self.queue.get_nowait()
        except Empty:
            return None
        for event_queue, listeners in self.__listeners.items():
            if not isinstance(event, event_queue):
                continue
            [listener(*event.args, **event.kwargs) for listener in listeners]    