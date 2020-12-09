"""Contains behaviors for ui functionality"""

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

class PlayerLevelIncrease(Command):
    """Increase in level command"""
    def __init__(self, player):
        """
        Sets the actor and window for the actor
        """
        self.player = player

    def execute(self):
        """
        Executes the level increase
        """
        self.player.actor['level'] += 1

    def reverse(self):
        """
        Reverses the level increase
        """
        self.player.actor['level'] -= 1

class PlayerLevelDecrease(Command):
    """Increase in level command"""
    def __init__(self, player):
        """
        Sets the actor and window for the actor
        """
        self.player = player

    def execute(self):
        """
        Executes the level decrease
        """
        self.player.actor['level'] -= 1

    def reverse(self):
        """
        Reverses the level decrease
        """
        self.player.actor['level'] += 1

class SkillLevelIncrease(Command):
    """
    A skill level increase. Woo!
    """
    def __init__(self, player, skill_name):
        """
        Sets the actor and window for the actor
        """
        self.skill_name = skill_name
        self.player = player

    def execute(self):
        """
        Executes the level decrease
        """
        self.player.update_skill_level(self.skill_name, 1, relative=True)

    def reverse(self):
        """
        Reverses the level decrease
        """
        self.player.update_skill_level(self.skill_name, -1, relative=True)

class SkillLevelDecrease(Command):
    """
    A skill level decrease. Boo!
    """
    def __init__(self, player, skill_name):
        """
        Sets the actor and window for the actor
        """
        self.skill_name = skill_name
        self.player = player

    def execute(self):
        """
        Executes the level decrease
        """
        self.player.update_skill_level(self.skill_name, -1, relative=True)

    def reverse(self):
        """
        Reverses the level decrease
        """
        self.player.update_skill_level(self.skill_name, 1, relative=True)
