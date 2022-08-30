import pytest
from pytest_mock import MockerFixture

from tklife.controller import ControllerABC
from tklife.skel import SkeletonMixin

class TestControllerABC:
    @pytest.fixture
    def mock_view(self, mocker: MockerFixture):
        mock = mocker.Mock()
        mock.created = {
            'test_attr': 'tested_attr'
        }
        return mock

    @pytest.fixture
    def controller(self, mock_view):
        class TestController(ControllerABC):
            pass
        controller = TestController()
        controller.set_view(mock_view)
        return controller

    def test_getattr_fetches_item_from_view_created_attribute(
        self,
        mock_view,
        controller: ControllerABC
    ):
        actual = controller.test_attr
        assert actual == 'tested_attr'