import pytest
from tklife.behaviors import CommandHistory, Command

class MockCommand(Command):
    """Mocks a command"""
    def __init__(self):
        super().__init__()
        self.last_call = None

    def execute(self):
        self.last_call = self.execute

    def reverse(self):
        self.last_call = self.reverse

@pytest.fixture
def command_history_no_history():
    return CommandHistory()

@pytest.fixture
def command_history_with_some_history():
    commands = [
        MockCommand(),
        MockCommand(),
        MockCommand(),
    ]
    history = CommandHistory()
    history.history = commands
    history.cursor = 2
    returns = []
    returns.append(history)
    returns.extend(commands)
    return tuple(returns)

def test_add_history_appends_a_command_to_the_command_list(
        command_history_no_history
):
    """
    Test that the Command.add_history method adds the given command
    to the history list, calls its execute method and sets the cursor
    to the last command in list
    """
    command = MockCommand()
    test_obj = command_history_no_history
    test_obj.add_history(command)

    assert command == test_obj.history[-1]
    assert command.last_call == command.execute
    assert test_obj.cursor == test_obj.history.index(command)

def test_undo_calls_reverse_on_last_command_and_moves_cursor_position_back(
    command_history_with_some_history
):
    test_obj, command1, command2, command3 = command_history_with_some_history
    test_obj.undo()

    assert command3.last_call == command3.reverse
    assert test_obj.cursor == test_obj.history.index(command2)

def test_undo_does_nothing_if_no_history(command_history_no_history):
    test_obj = command_history_no_history
    test_obj.undo()

def test_add_history_deletes_history_after_cursor(command_history_with_some_history):
    test_obj, command1, command2, command3 = command_history_with_some_history
    test_obj.cursor = 1
    new_command = MockCommand()
    test_obj.add_history(new_command)

    assert test_obj.history.index(command1) == 0
    assert test_obj.history.index(command2) == 1
    assert test_obj.cursor == test_obj.history.index(new_command)
    with pytest.raises(ValueError):
        test_obj.history.index(command3)

def test_redo_executes_command_at_cursor_and_advances_it_to_next_command(command_history_with_some_history):
    test_obj, command1, command2, command3 = command_history_with_some_history
    test_obj.cursor = 1

    test_obj.redo()
    assert command2.last_call is None
    assert command3.last_call == command3.execute
    assert test_obj.cursor == test_obj.history.index(command3)

def test_redo_does_nothing_if_cursor_is_on_last_command(command_history_with_some_history):
    test_obj, command1, command2, command3 = command_history_with_some_history

    test_obj.redo()

    assert command3.last_call is None
    assert test_obj.cursor == test_obj.history.index(command3)

def test_redo_does_nothing_if_no_history(command_history_no_history):
    test_obj = command_history_no_history

    test_obj.redo()
    assert test_obj.cursor is None

def test_redo_executes_next_command_if_cursor_is_none_and_commands_are_in_history(command_history_with_some_history):
    test_obj, command1, command2, command3 = command_history_with_some_history
    test_obj.cursor = None
    test_obj.redo()
    assert command1.last_call == command1.execute

def test_undo_all_reverts_entire_history(command_history_with_some_history):
    test_obj, command1, command2, command3 = command_history_with_some_history
    test_obj.undo_all()
    assert command1.last_call == command1.reverse
    assert command2.last_call == command2.reverse
    assert command3.last_call == command3.reverse
    
