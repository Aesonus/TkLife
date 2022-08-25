import pytest
from pytest_mock import MockerFixture

from tklife.proxy import CallProxy, CallProxyFactory, TklProxyError

class TestCallProxy:
    def test_will_call_method_by_name_with_args_on_skel_controller(self, mocker: MockerFixture):
        skel = mocker.Mock()
        func = 'test_func'
        args = (1, 2)
        kwargs = {'3': 4}

        proxy = CallProxy(skel, func)
        proxy(*args, **kwargs)
        skel.controller.test_func.assert_called_once_with(*args, **kwargs)

    def test_call_proxy_raises_error_if_controller_not_set_on_skel(self, mocker: MockerFixture):
        skel = mocker.Mock()
        skel.controller = CallProxyFactory(skel)
        with pytest.raises(TklProxyError):
            proxy = CallProxy(skel, "func")
            proxy()

class TestCallProxyFactory:
    def test_dunder_get_attr_returns_new_call_proxy(self, mocker: MockerFixture):
        skel = mocker.Mock()
        expected = CallProxy(skel, "func")
        assert CallProxyFactory(skel).func == expected
