from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from tklife.behaviors.commands import Command, CommandHistory


class TestCommandHistory:
    @pytest.fixture
    def mock_command(self, mocker: MockerFixture) -> Mock:
        return mocker.Mock(Command)

    @pytest.fixture
    def mock_command_list(self, mocker: MockerFixture) -> list[Mock]:
        return list(mocker.Mock(Command) for __ in range(3))

    @pytest.fixture
    def command_history(self, mock_command_list):
        command_history = CommandHistory()
        command_history.history.extend(mock_command_list)
        return command_history

    def test_add_history_adds_command_and_calls_command_execute(
        self, mock_command: Mock
    ):
        command_history = CommandHistory()
        command_history.add_history(mock_command)
        mock_command.execute.assert_called_once_with()

    @pytest.mark.parametrize("cursor", [0, 1, 2])
    def test_undo_calls_command_reverse(
        self, cursor, command_history: CommandHistory, mock_command_list: list[Mock]
    ):
        # Setup
        command_history.cursor = cursor

        command_history.undo()
        mock_command_list[cursor].reverse.assert_called_once_with()

    @pytest.mark.parametrize("until", [None, 1, 2])
    def test_undo_all_calls_command_reverse_on_history_until(
        self, until, command_history: CommandHistory, mock_command_list: list[Mock]
    ):
        command_history.cursor = len(mock_command_list) - 1

        command_history.undo_all(until=until)
        for command in mock_command_list[until:]:
            command.reverse.assert_called_once_with()

        if until is not None:
            for command in mock_command_list[0:until]:
                assert command.reverse.call_count == 0

    def test_undo_returns_none_if_no_history(self):
        command_history = CommandHistory()

        assert command_history.undo() is None

    @pytest.mark.parametrize("cursor", [None, 0, 1])
    def test_redo_calls_command_execute(
        self, cursor, command_history: CommandHistory, mock_command_list: list[Mock]
    ):
        command_history.cursor = cursor
        command_history.redo()
        mock_command_list[
            cursor + 1 if cursor is not None else 0
        ].execute.assert_called_once_with()

    def test_redo_calls_no_command_if_cursor_maxed(
        self, command_history, mock_command_list
    ):
        command_history.cursor = 2
        command_history.redo()
        for command in mock_command_list:
            assert command.execute.call_count == 0

    def test_redo_returns_none_if_no_history(self):
        command_history = CommandHistory()
        assert command_history.redo() is None

    @pytest.mark.parametrize(
        "range_size, cursor, expected",
        [
            (0, None, 0),
            (0, 0, 0),
            (1, 0, 1),
            (1, 0, 1),
            (2, 1, 2),
            (2, None, 0),
            (3, 0, 1),
            (3, 1, 2),
            (3, 2, 3),
            (3, None, 0),
        ],
    )
    def test_len_returns_history_length_that_can_be_undone(
        self, range_size, cursor, expected, mocker: MockerFixture
    ):
        command_history = CommandHistory()
        command_history.history = [mocker.Mock(Command) for __ in range(range_size)]
        command_history.cursor = cursor

        assert len(command_history) == expected

    def test_add_command_clears_redo_commands(
        self, command_history: CommandHistory, mock_command_list: list[Mock], mocker
    ):
        command_history.cursor = 1
        command_history.add_history(mocker.Mock(Command))

        # Assert that the redoable command is not in history anymore
        assert mock_command_list[2] not in command_history.history
        # Assert that the command history is still 3 due to the new command being added
        assert len(command_history.history) == 3

    def test_add_command_increments_cursor(self, mock_command_list):
        command_history = CommandHistory()
        for cmd in mock_command_list:
            command_history.add_history(cmd)
        assert command_history.cursor == 2

    def test_reset_clears_history_and_cursor(self, command_history):
        command_history.reset()
        assert len(command_history.history) == 0
        assert command_history.cursor == None
