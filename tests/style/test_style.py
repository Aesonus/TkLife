from tkinter.ttk import Style
from unittest.mock import call
import pytest
from tklife.style.style import TEntry, BaseStyle
from pytest_mock import MockerFixture

parametrize = pytest.mark.parametrize

class TestBaseStyle:
    @pytest.mark.parametrize("subclass, expected", [
        (type("TestEntry", (TEntry,), {}), "TestEntry.TEntry"),
        (type("HigherLevel", (type("TestEntry", (TEntry,), {}),), {}), "HigherLevel.TestEntry.TEntry"),
    ])
    def test_ttk_style_returns_ttk_style_name_based_on_inheritance_structure(
        self, subclass, expected
    ):
        assert subclass.ttk_style == expected


    @pytest.fixture
    def defined_styles(self):
        class Table(TEntry):
            configure = {
                "foreground": "purple"
            }
        class Green(Table):
            configure = {
                "fieldbackground": "white"
            }
            map = {
                "fieldbackground": [
                    ("readonly", "green")
                ],
                "foreground": [
                    ("readonly", "white")
                ]
            }
        return Table, Green

    def test_dunder_get_item_on_base_style_returns_style_class(self, defined_styles):
        Table, Green = defined_styles
        assert BaseStyle["Green.Table.TEntry"] == Green

    def test_dunder_get_item_on_base_style_raises_key_error_when_not_found(self, defined_styles):
        Table, Green = defined_styles
        with pytest.raises(KeyError):
            assert BaseStyle["Bad.Table.TEntry"] == Green

    def test_dunder_get_item_on_tentry_style_returns_style_class(self, defined_styles):
        Table, Green = defined_styles
        assert TEntry["Green.Table"] == Green

    def test_dunder_get_item_on_tentry_style_raises_key_error_when_not_found(self, defined_styles):
        Table, Green = defined_styles
        with pytest.raises(KeyError):
            assert TEntry["Green.Table.TEntry"] == Green

    def test_dunder_get_item_on_table_style_returns_style_class(self, defined_styles):
        Table, Green = defined_styles
        assert Table["Green"] == Green

    def test_dunder_get_item_on_table_style_raises_key_error_when_not_found(self, defined_styles):
        Table, Green = defined_styles
        with pytest.raises(KeyError):
            assert Table["Green.Table"] == Green

    def test_define_all_calls_all_definitions(self, mocker: MockerFixture, defined_styles):
        Table, Green = defined_styles
        mock_style = mocker.Mock(spec=Style)
        BaseStyle.define_all(mock_style)

        assert call("TEntry") in mock_style.configure.mock_calls
        assert call("TEntry") in mock_style.map.mock_calls
        assert call("Table.TEntry", **Table.configure) in mock_style.configure.mock_calls
        assert call("Green.Table.TEntry", **Green.configure) in mock_style.configure.mock_calls
        assert call("Table.TEntry", **Table.map) in mock_style.map.mock_calls
        assert call("Green.Table.TEntry", **Green.map) in mock_style.map.mock_calls

    @parametrize("clsname,expected", [
        ("Table", "Table.TEntry"),
        ("Green", "Green.Table.TEntry"),
    ])
    def test_set_style_sets_style_coption(self, mocker: MockerFixture, defined_styles, clsname, expected):
        style_classes = dict(zip(("Table", "Green"), defined_styles))
        mock_widget = mocker.MagicMock()
        style_classes[clsname].set_style(mock_widget)
        mock_widget.__setitem__.assert_called_once_with("style", expected)

    @parametrize("clsname,expected", [
        ("Table", {"style": "Table.TEntry"}),
        ("Green", {"style": "Green.Table.TEntry"}),
    ])
    def test_as_dict_returns_style_as_dict_for_widget_config(self, mocker: MockerFixture, defined_styles, clsname, expected):
        style_classes = dict(zip(("Table", "Green"), defined_styles))
        assert style_classes[clsname].as_dict() == expected