from tkinter import Misc
from types import SimpleNamespace
import pytest

from tklife.event import CompositeEvent, EventsEnum


class TestEventEnum(object):
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
        return mocker.Mock(Misc)

    @pytest.mark.parametrize("kwargs", [
        {}, {"test": True}
    ], ids=["no kwargs", "with kwargs"])
    def test_bind_calls(self, custom_event, action_callable, mock_widget, kwargs):
        custom_event.TEST.bind(mock_widget, action_callable, **kwargs)
        mock_widget.bind.assert_called_once_with(
            custom_event.TEST.value, action_callable, **kwargs)

    @pytest.mark.parametrize("kwargs", [
        {}, {"test": True}
    ], ids=["no kwargs", "with kwargs"])
    def test_bind_all_calls(self, custom_event, action_callable, mock_widget, kwargs):
        custom_event.TEST.bind_all(mock_widget, action_callable, **kwargs)
        mock_widget.bind_all.assert_called_once_with(
            custom_event.TEST.value, action_callable, **kwargs)

    @pytest.mark.parametrize("kwargs", [
        {}, {"test": True}
    ], ids=["no kwargs", "with kwargs"])
    def test_bind_class_calls(self, custom_event, action_callable, mock_widget, kwargs):
        custom_event.TEST.bind_class(
            mock_widget, "classname", action_callable, **kwargs)
        mock_widget.bind_class.assert_called_once_with(
            "classname", custom_event.TEST.value, action_callable, **kwargs)

    def test_generate_returns_callable_that_calls_event_generate(
        self, custom_event, mock_widget
    ):
        callable_ = custom_event.TEST.generate(mock_widget)
        callable_()
        mock_widget.event_generate.assert_called_once_with(
            custom_event.TEST.value)


class TestCompositeEvent(object):
    @pytest.fixture
    def composite_event(self):
        return CompositeEvent("<<Test>>")

    @pytest.fixture
    def action_callable(self):
        return lambda __: None

    @pytest.fixture
    def mock_widget(self, mocker):
        return mocker.Mock(Misc)

    def test_composite_event_factory(self):
        expected = "<Mod-Event>"
        actual = CompositeEvent.factory(SimpleNamespace(
            value="<Mod>"), SimpleNamespace(value="<Event>"))
        assert actual.value == expected

    @pytest.mark.parametrize("kwargs", [
        {}, {"test": True}
    ], ids=["no kwargs", "with kwargs"])
    def test_bind_calls(self, composite_event, action_callable, mock_widget, kwargs):
        composite_event.bind(mock_widget, action_callable, **kwargs)
        mock_widget.bind.assert_called_once_with(
            composite_event.value, action_callable, **kwargs)

    @pytest.mark.parametrize("kwargs", [
        {}, {"test": True}
    ], ids=["no kwargs", "with kwargs"])
    def test_bind_all_calls(self, composite_event, action_callable, mock_widget, kwargs):
        composite_event.bind_all(mock_widget, action_callable, **kwargs)
        mock_widget.bind_all.assert_called_once_with(
            composite_event.value, action_callable, **kwargs)

    @pytest.mark.parametrize("kwargs", [
        {}, {"test": True}
    ], ids=["no kwargs", "with kwargs"])
    def test_bind_class_calls(self, composite_event, action_callable, mock_widget, kwargs):
        composite_event.bind_class(
            mock_widget, "classname", action_callable, **kwargs)
        mock_widget.bind_class.assert_called_once_with(
            "classname", composite_event.value, action_callable, **kwargs)

    def test_generate_returns_callable_that_calls_event_generate(
        self, composite_event, mock_widget
    ):
        callable_ = composite_event.generate(mock_widget)
        callable_()
        mock_widget.event_generate.assert_called_once_with(
            composite_event.value)


def test_event_addition():
    pass
