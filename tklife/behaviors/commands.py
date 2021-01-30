"""Contains behaviors for ui functionality"""

__all__ = ['CommandHistory', 'Command']

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
            new_cursor = None
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
