import tkinter
import pytest
from tklife.mixins import GridConfig, Skeleton, WidgetConfig
from pytest_mock import MockerFixture

class Dummy:
    pass

@pytest.fixture
def MockTk(mocker: MockerFixture):
    class MockTk():
        def __init__(self, *args, **kwargs) -> None:
            self.called_with = (args, kwargs)
    return MockTk


@pytest.fixture
def mock_widget_type(mocker: MockerFixture, mock_widget):
    mock_widget_type = mocker.patch.object(Dummy, '__init__')
    mock_widget_type.return_value = mock_widget
    return mock_widget_type


@pytest.fixture
def mock_widget(mocker: MockerFixture):
    return mocker.patch.object(tkinter, 'Widget')


@pytest.fixture
def TestApp(mock_widget_type, MockTk):
    class TestApp(Skeleton, MockTk):
        def __init__(self, skeleton=None, master=None, **kwargs):
            self._skeleton = skeleton
            super().__init__(master, **kwargs)
        @property
        def skeleton(self) -> GridConfig:
            return (
                [WidgetConfig(mock_widget_type, {'w_arg': True}, {
                              'grid_arg': True})],
            )

        @property
        def all_grid_kwargs(self):
            return dict(padx=6, pady=6)
    return TestApp


@pytest.mark.parametrize("skeleton_prop, expected_widget_args, expected_grid_args", [
    (1, 2, 3)
])
def test_widget_types_called_with_kwargs(
    skeleton_prop, expected_widget_args, expected_grid_args,
    mock_widget_type,
    mock_widget,
    TestApp,
    MockTk,
    mocker: MockerFixture
):
    expected_sibling_args = (None, {})

    app = TestApp()
    app.called_with = expected_sibling_args
    mock_widget_type.assert_called_once_with(app, w_arg=True)
    mock_widget.grid.assert_called_once_with(row=0, column=0, grid_arg=True, padx=6, pady=6)
