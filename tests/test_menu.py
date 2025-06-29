from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from tklife.core import SkeletonMixin
from tklife.menu import Menu, MenuMixin


class TestMenuMixin:
    @pytest.fixture
    def mock_winfo_toplevel(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def mock_widget_class(self, mocker: MockerFixture, mock_winfo_toplevel):
        class Frame:
            def __init__(self, *args, **kwargs) -> None:
                self.mock_calls = []

            def option_add(self, *args, **kwargs):
                self.mock_calls.append(call.option_add(*args, **kwargs))

            def winfo_toplevel(self, *args, **kwargs):
                return mock_winfo_toplevel

            def __setitem__(self, key, value):
                self.mock_calls.append(call.__setitem__(key, value))

        return Frame

    @pytest.fixture
    def tk_menu_patch(self, mocker: MockerFixture):
        return mocker.patch("tklife.menu.tkinter")

    def test_create_menu_calls_methods(
        self, mock_widget_class, mock_master, tk_menu_patch, mock_winfo_toplevel
    ):
        class TestMenu(SkeletonMixin, MenuMixin, mock_widget_class):
            @property
            def menu_template(self):
                return {
                    Menu.cascade("File", underline=0): {
                        Menu.add(): "separator",
                    },
                    Menu.command("Test Command"): None,
                }

        new_frame = TestMenu(mock_master)
        tk_menu_patch.Menu.add_command.assert_called_once_with(
            tk_menu_patch.Menu.return_value, label="Test Command", command=None
        )
        tk_menu_patch.Menu.add.assert_called_once_with(
            tk_menu_patch.Menu.return_value, "separator"
        )
        tk_menu_patch.Menu.add_cascade.assert_called_once_with(
            tk_menu_patch.Menu.return_value,
            label="File",
            underline=0,
            menu=tk_menu_patch.Menu.return_value,
        )
        tk_menu_patch.Menu.assert_called_with(mock_winfo_toplevel)
        assert tk_menu_patch.Menu.call_count == 2
        assert new_frame.mock_calls == [
            call.option_add("*tearOff", 0),
            call.__setitem__("menu", tk_menu_patch.Menu.return_value),
        ]
