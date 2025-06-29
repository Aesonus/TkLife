import tkinter as tk

import pytest
import pytest_mock

import tklife


@pytest.fixture
def mock_master(mocker: pytest_mock.MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def mock_controller(mocker: pytest_mock.MockerFixture):
    return mocker.Mock(tklife.controller.ControllerABC)


@pytest.fixture
def mock_mixin_class(mocker: pytest_mock.MockerFixture):
    """This is a mixin class that acts as a skeleton for testing purposes."""

    class Misc:
        def __init__(self, *args, **kwargs) -> None:
            self.mocks = {}
            self._calls.append(mocker.call(*args, **kwargs))

        def __getattr__(self, attrname):
            if attrname not in self.mocks:
                self.mocks[attrname] = mocker.MagicMock()
            return self.mocks[attrname]

    return Misc


@pytest.fixture
def mocked_widget(mocker: pytest_mock.MockerFixture):
    return mocker.Mock()


def pump_events(root):
    while root.dooneevent(tk._tkinter.ALL_EVENTS | tk._tkinter.DONT_WAIT):
        pass


@pytest.fixture(scope="function")
def master():
    root = tk.Tk()
    root.geometry("0x0")
    pump_events(root)
    yield root
    root.destroy()
