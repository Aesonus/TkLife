import tkinter as tk
from types import SimpleNamespace

import pytest

from tklife.event import CompositeEvent, EventsEnum, TkEvent, TkEventMod


class TestEventEnum:
    @pytest.fixture
    def custom_event(self):
        class Custom(EventsEnum):
            TEST = "<<Test>>"

        return Custom

    @pytest.fixture
    def action_callable(self):
        return lambda __: None

    @pytest.fixture
    def mock_widget(self, mocker):
        return mocker.Mock(tk.Misc)

    @pytest.mark.parametrize(
        "kwargs", [{}, {"add": "+"}], ids=["no kwargs", "with kwargs"]
    )
    def test_bind_calls(self, custom_event, action_callable, mock_widget, kwargs):
        custom_event.TEST.bind(mock_widget, action_callable, **kwargs)
        mock_widget.bind.assert_called_once_with(
            custom_event.TEST.value, action_callable, add=kwargs.get("add", "")
        )

    @pytest.mark.parametrize(
        "kwargs", [{}, {"add": "+"}], ids=["no kwargs", "with kwargs"]
    )
    def test_bind_all_calls(self, custom_event, action_callable, mock_widget, kwargs):
        custom_event.TEST.bind(mock_widget, action_callable, classname="all", **kwargs)
        mock_widget.bind_class.assert_called_once_with(
            "all", custom_event.TEST.value, action_callable, add=kwargs.get("add", "")
        )

    @pytest.mark.parametrize(
        "kwargs", [{}, {"add": "+"}], ids=["no kwargs", "with kwargs"]
    )
    def test_bind_class_calls(self, custom_event, action_callable, mock_widget, kwargs):
        custom_event.TEST.bind(
            mock_widget, action_callable, classname="classname", **kwargs
        )
        mock_widget.bind_class.assert_called_once_with(
            "classname",
            custom_event.TEST.value,
            action_callable,
            add=kwargs.get("add", ""),
        )

    def test_generate_returns_callable_that_calls_event_generate(
        self, custom_event, mock_widget
    ):
        callable_ = custom_event.TEST.generate(mock_widget)
        callable_()
        mock_widget.event_generate.assert_called_once_with(custom_event.TEST.value)


class TestCompositeEvent:
    @pytest.fixture
    def composite_event(self):
        return CompositeEvent("<<Test>>")

    @pytest.fixture
    def action_callable(self):
        return lambda __: None

    @pytest.fixture
    def mock_widget(self, mocker):
        mock = mocker.Mock(tk.Misc)
        mock.tk = mocker.MagicMock()
        return mock

    def test_composite_event_factory(self):
        expected = "<Mod-Event>"
        actual = CompositeEvent.factory(
            SimpleNamespace(value="<Mod>"), SimpleNamespace(value="<Event>")
        )
        assert actual.value == expected

    def test_composite_event_factory_with_str(self):
        expected = "<Mod-A>"
        actual = CompositeEvent.factory(SimpleNamespace(value="<Mod>"), "<A>")
        assert actual.value == expected

    @pytest.mark.parametrize(
        "kwargs", [{}, {"add": "+"}], ids=["no kwargs", "with kwargs"]
    )
    def test_bind_calls(self, composite_event, action_callable, mock_widget, kwargs):
        composite_event.bind(mock_widget, action_callable, **kwargs)
        mock_widget.bind.assert_called_once_with(
            composite_event.value, action_callable, add=kwargs.get("add", "")
        )

    @pytest.mark.parametrize(
        "kwargs", [{}, {"add": "+"}], ids=["no kwargs", "with kwargs"]
    )
    def test_bind_all_calls(
        self, composite_event, action_callable, mock_widget, kwargs
    ):
        composite_event.bind(mock_widget, action_callable, classname="all", **kwargs)
        mock_widget.bind_class.assert_called_once_with(
            "all", composite_event.value, action_callable, add=kwargs.get("add", "")
        )

    @pytest.mark.parametrize(
        "kwargs", [{}, {"add": "+"}], ids=["no kwargs", "with kwargs"]
    )
    def test_bind_class_calls(
        self, composite_event, action_callable, mock_widget, kwargs
    ):
        composite_event.bind(
            mock_widget, action_callable, classname="classname", **kwargs
        )
        mock_widget.bind_class.assert_called_once_with(
            "classname",
            composite_event.value,
            action_callable,
            add=kwargs.get("add", ""),
        )

    def test_generate_returns_callable_that_calls_event_generate(
        self, composite_event, mock_widget
    ):
        callable_ = composite_event.generate(mock_widget)
        callable_()
        mock_widget.event_generate.assert_called_once_with(composite_event.value)

    def test_unbind_calls(self, composite_event, mock_widget):
        composite_event.unbind(mock_widget)
        mock_widget.tk.call.assert_called_once_with(
            "bind", str(mock_widget), composite_event.value, ""
        )


@pytest.mark.parametrize(
    "term1, term2, expected",
    [
        (TkEventMod.ALT, "<A>", "<Alt-A>"),
        (TkEventMod.DOUBLE, TkEvent.BUTTON, "<Double-Button>"),
    ],
)
def test_event_addition(term1, term2, expected):
    actual = term1 + term2
    assert actual.value == expected


@pytest.mark.integration
class TestEvents:
    @pytest.fixture
    def widget(self, master):
        return tk.Frame(master)

    @staticmethod
    def action(event):
        """Used as a dummy action for testing."""

    def test_get_bindings(self, widget):
        event = TkEvent.BUTTON + "<1>"
        funcid = event.bind(widget, self.action)
        assert event.get_bindings(widget) == {
            funcid: "{first}{funcid}{the_rest}".format(
                first='if {"[',
                funcid=funcid,
                the_rest=(
                    ' %# %b %f %h %k %s %t %w %x %y %A %E %K %N %W %T %X %Y %D]" '
                    '== "break"} break'
                ),
            )
        }

    def test_get_bindings_none(self, widget):
        event = TkEvent.BUTTON + "<1>"
        assert event.get_bindings(widget) == {}

    @pytest.mark.parametrize(
        "action",
        [
            lambda event: None,
            action,
        ],
    )
    def test_bind(self, widget, action):
        event = TkEvent.BUTTON + "<1>"

        func_id = event.bind(widget, action)

        assert func_id in event.get_bindings(widget)

    @pytest.mark.parametrize("func_count", [1, 2, 3])
    def test_bind_with_kwargs(self, widget, func_count):
        event = TkEvent.BUTTON + "<1>"
        expected_bindings = [
            event.bind(widget, self.action, add="+") for _ in range(func_count)
        ]

        assert list(event.get_bindings(widget).keys()) == expected_bindings

    def test_unbind(self, widget):
        event = TkEvent.BUTTON + "<1>"
        func_id = event.bind(widget, self.action)

        event.unbind(widget, func_id)

        assert func_id not in event.get_bindings(widget)

    def test_unbind_raises_keyerror_for_nonexistent_funcid(self, widget):
        """Test that unbind raises a KeyError when trying to unbind a non-existent
        funcid."""
        event = TkEvent.BUTTON + "<1>"
        nonexistent_funcid = "nonexistent123"

        with pytest.raises(KeyError):
            event.unbind(widget, nonexistent_funcid)

    def test_unbind_keyerror_message_contains_funcid(self, widget):
        """Test that the KeyError message contains the funcid that was not found."""
        event = TkEvent.BUTTON + "<1>"
        nonexistent_funcid = "nonexistent123"

        with pytest.raises(
            KeyError, match=r"Function ID 'nonexistent123' not found in bindings"
        ):
            event.unbind(widget, nonexistent_funcid)
