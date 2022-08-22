from tkinter import Variable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from tklife.controller import ControllerABC
from tklife.skel import SkeletonMixin, SkelWidget


class TestSkeletonMixin(object):

    @pytest.fixture
    def mock_master(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def mock_controller(self, mocker: MockerFixture):
        return mocker.Mock(ControllerABC)

    @pytest.fixture
    def mock_mixin_class(self, mocker: MockerFixture):
        class Misc(object):
            def __init__(self, *args, **kwargs) -> None:
                self._init_args = args
                self._init_kwargs = kwargs
        return Misc

    @pytest.fixture
    def no_template_skeleton(self, mock_mixin_class):
        class TestedSkeleton(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [],
                )
        return TestedSkeleton

    @pytest.fixture
    def mock_tk_var(self, mocker: MockerFixture):
        return mocker.Mock(type(Variable))

    def test_init(self, no_template_skeleton, mock_master, mock_controller: MagicMock):
        """
        Test that the sibling __init__ is called with correct arguments,
        and the controller is updated with the view
        """
        skeleton = no_template_skeleton(mock_master, mock_controller)
        assert skeleton._init_args == (mock_master, )
        assert skeleton._init_kwargs == {}
        assert skeleton.controller == mock_controller
        mock_controller.set_view.assert_called_once_with(skeleton)

    def test_controller_setter_raises_exception_if_invalid_controller(self,
                                                                      no_template_skeleton,
                                                                      mock_master):
        with pytest.raises(TypeError, match=r"Controller must be of type ControllerABC"):
            no_template_skeleton(mock_master, object())

    def test_create_all_creates_and_grids_widgets_from_template(self,
                                                                mock_master,
                                                                mock_controller,
                                                                mock_mixin_class,
                                                                mocker: MockerFixture):
        mocked_widgets = [
            [mocker.Mock(), mocker.Mock()],
            [mocker.Mock(), mocker.Mock()],
        ]

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widgets[0][0], {}, {}),
                     SkelWidget(mocked_widgets[0][1], {}, {})],
                    [SkelWidget(mocked_widgets[1][0], {}, {}),
                     SkelWidget(mocked_widgets[1][1], {}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        mocked_widgets[0][0].assert_called_once_with(skeleton)
        mocked_widgets[0][1].assert_called_once_with(skeleton)
        mocked_widgets[1][0].assert_called_once_with(skeleton)
        mocked_widgets[1][1].assert_called_once_with(skeleton)

        mocked_widgets[0][0].return_value.grid.assert_called_once_with(
            row=0, column=0)
        mocked_widgets[0][1].return_value.grid.assert_called_once_with(
            row=0, column=1)
        mocked_widgets[1][0].return_value.grid.assert_called_once_with(
            row=1, column=0)
        mocked_widgets[1][1].return_value.grid.assert_called_once_with(
            row=1, column=1)

    def test_create_all_creates_and_grids_widgets_from_template_with_init_args(self,
                                                                               mock_master,
                                                                               mock_controller,
                                                                               mock_mixin_class,
                                                                               mocker: MockerFixture):
        mocked_widgets = [
            [mocker.Mock(), mocker.Mock()],
            [mocker.Mock(), mocker.Mock()],
        ]

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widgets[0][0], {'arg1': True}, {}), SkelWidget(
                        mocked_widgets[0][1], {'arg2': True}, {})],
                    [SkelWidget(mocked_widgets[1][0], {'arg3': True}, {}), SkelWidget(
                        mocked_widgets[1][1], {'arg4': True}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        mocked_widgets[0][0].assert_called_once_with(skeleton, arg1=True)
        mocked_widgets[0][1].assert_called_once_with(skeleton, arg2=True)
        mocked_widgets[1][0].assert_called_once_with(skeleton, arg3=True)
        mocked_widgets[1][1].assert_called_once_with(skeleton, arg4=True)

        mocked_widgets[0][0].return_value.grid.assert_called_once_with(
            row=0, column=0)
        mocked_widgets[0][1].return_value.grid.assert_called_once_with(
            row=0, column=1)
        mocked_widgets[1][0].return_value.grid.assert_called_once_with(
            row=1, column=0)
        mocked_widgets[1][1].return_value.grid.assert_called_once_with(
            row=1, column=1)

    def test_create_all_creates_and_grids_widgets_from_template_with_grid_args(self,
                                                                               mock_master,
                                                                               mock_controller,
                                                                               mock_mixin_class,
                                                                               mocker: MockerFixture):
        mocked_widgets = [
            [mocker.Mock(), mocker.Mock()],
            [mocker.Mock(), mocker.Mock()],
        ]

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widgets[0][0], {}, {'arg1': True}), SkelWidget(
                        mocked_widgets[0][1], {}, {'arg2': True})],
                    [SkelWidget(mocked_widgets[1][0], {}, {'arg3': True}), SkelWidget(
                        mocked_widgets[1][1], {}, {'arg4': True})],
                )
        skeleton = Tested(mock_master, mock_controller)
        mocked_widgets[0][0].assert_called_once_with(skeleton)
        mocked_widgets[0][1].assert_called_once_with(skeleton)
        mocked_widgets[1][0].assert_called_once_with(skeleton)
        mocked_widgets[1][1].assert_called_once_with(skeleton)

        mocked_widgets[0][0].return_value.grid.assert_called_once_with(
            row=0, column=0, arg1=True)
        mocked_widgets[0][1].return_value.grid.assert_called_once_with(
            row=0, column=1, arg2=True)
        mocked_widgets[1][0].return_value.grid.assert_called_once_with(
            row=1, column=0, arg3=True)
        mocked_widgets[1][1].return_value.grid.assert_called_once_with(
            row=1, column=1, arg4=True)

    def test_create_all_creates_and_grids_widgets_from_template_skipping_none(self,
                                                                              mock_master,
                                                                              mock_controller,
                                                                              mock_mixin_class,
                                                                              mocker: MockerFixture):
        mocked_widgets = [
            [mocker.Mock(), mocker.Mock()],
            [None, mocker.Mock()],
        ]

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widgets[0][0], {}, {}),
                     SkelWidget(mocked_widgets[0][1], {}, {})],
                    [None, SkelWidget(mocked_widgets[1][1], {}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        mocked_widgets[0][0].assert_called_once_with(skeleton)
        mocked_widgets[0][1].assert_called_once_with(skeleton)
        mocked_widgets[1][1].assert_called_once_with(skeleton)

        mocked_widgets[0][0].return_value.grid.assert_called_once_with(
            row=0, column=0)
        mocked_widgets[0][1].return_value.grid.assert_called_once_with(
            row=0, column=1)
        mocked_widgets[1][1].return_value.grid.assert_called_once_with(
            row=1, column=1)

    def test_create_all_creates_and_grids_widgets_from_template_with_var_in_init_args(self,
                                                                                      mock_master,
                                                                                      mock_controller,
                                                                                      mock_mixin_class,
                                                                                      mock_tk_var,
                                                                                      mocker: MockerFixture):
        mock_widget = mocker.Mock()

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mock_widget, {'arg1': mock_tk_var}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        mock_widget.assert_called_once_with(
            skeleton, arg1=mock_tk_var.return_value)

        mock_widget.return_value.grid.assert_called_once_with(row=0, column=0)

    def test_create_all_creates_and_grids_widgets_from_template_with_var_in_init_args_and_creates_label(self,
                                                                                                        mock_master,
                                                                                                        mock_controller,
                                                                                                        mock_mixin_class,
                                                                                                        mock_tk_var,
                                                                                                        mocker: MockerFixture):
        mock_widget = mocker.Mock()
        mock_tk_var.return_value = mocker.Mock(Variable)

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(
                        mock_widget, {'arg1': mock_tk_var}, {}, 'test_label')],
                )
        skeleton = Tested(mock_master, mock_controller)
        mock_widget.assert_called_once_with(
            skeleton, arg1=mock_tk_var.return_value)

        mock_widget.return_value.grid.assert_called_once_with(row=0, column=0)
        assert skeleton.created["test_label"] == {
            "widget": mock_widget.return_value,
            "arg1": mock_tk_var.return_value
        }
