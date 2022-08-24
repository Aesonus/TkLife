import pytest
from pytest_mock import MockerFixture

from tklife.proxy import CallProxy

class TestCallProxy:
    def test_call_proxy_will_call_method_by_name_with_args_on_skel_controller(self, mocker: MockerFixture):
        skel = mocker.Mock()
        func = 'test_func'
        args = (1, 2)
        kwargs = {'3': 4}

        proxy = CallProxy(skel, func, args, kwargs)
        proxy()
        skel.controller.test_func.assert_called_once_with(*args, **kwargs)
