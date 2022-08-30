from tkinter import Variable, Widget
from typing import Iterable
from unittest.mock import MagicMock, Mock, call

import pytest
from pytest_mock import MockerFixture
from tklife.controller import ControllerABC
from tklife.proxy import CallProxyFactory
from tklife.skel import CreatedWidget, Menu, MenuMixin, SkeletonMixin, SkelWidget


class TestSkelWidget(object):
    @pytest.fixture
    def mocked_widget(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def skel_widget(self, mocked_widget):
        return SkelWidget(mocked_widget, {'init': 'args'}, {'grid': 'args'}, 'label')

    def test_skel_widget_iterable(self, skel_widget: SkelWidget, mocked_widget):
        widget, init_args, grid_args, label = skel_widget
        assert widget == mocked_widget
        assert init_args == {'init': 'args'}
        assert grid_args == {'grid': 'args'}
        assert label == 'label'

    @pytest.mark.parametrize("merged_init_args, expected_init_args", [
        ({'new': 'initarg'}, {'init': 'args', 'new': 'initarg'}),
        ({'init': 'initarg'}, {'init': 'initarg'}),
    ])
    def test_skel_widget_init_method_returns_new_skel_widget_with_appended_args(
        self,
        merged_init_args, expected_init_args,
        mocked_widget, skel_widget: SkelWidget
    ):
        actual = skel_widget.init(**merged_init_args)
        assert actual.widget == mocked_widget
        assert actual.init_args == expected_init_args
        assert actual.grid_args == {'grid': 'args'}
        assert actual.label == 'label'
        assert actual != skel_widget

    @pytest.mark.parametrize("merged_grid_args, expected_grid_args", [
        ({'new': 'gridarg'}, {'grid': 'args', 'new': 'gridarg'}),
        ({'grid': 'gridarg'}, {'grid': 'gridarg'}),
    ])
    def test_skel_widget_grid_method_returns_new_skel_widget_with_appended_args(
        self,
        merged_grid_args, expected_grid_args,
        mocked_widget, skel_widget: SkelWidget
    ):
        actual = skel_widget.grid(**merged_grid_args)
        assert actual.widget == mocked_widget
        assert actual.init_args == {'init': 'args'}
        assert actual.grid_args == expected_grid_args
        assert actual.label == 'label'
        assert actual != skel_widget

    def test_skel_widget_set_label_method_returns_new_skel_widget_with_new_label(
        self,
        mocked_widget, skel_widget: SkelWidget
    ):
        actual = skel_widget.set_label('newlabel')
        assert actual.widget == mocked_widget
        assert actual.init_args == {'init': 'args'}
        assert actual.grid_args == {'grid': 'args'}
        assert actual.label == 'newlabel'


class TestSkeletonMixin(object):

    @pytest.fixture
    def mock_master(self, mocker: MockerFixture):
        return mocker.Mock()

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

            def create_events(self):
                self.created_events = True
        return TestedSkeleton

    @pytest.fixture
    def mock_tk_var(self, mocker: MockerFixture):
        return mocker.Mock(type(Variable))

    @pytest.fixture
    def mocked_widget(self, mocker):
        return mocker.Mock()

    def test_init(self, no_template_skeleton: SkeletonMixin, mock_master, mock_controller):
        """
        Test that the sibling __init__ is called with correct arguments,
        and the controller is updated with the view
        """
        skeleton = no_template_skeleton(mock_master, mock_controller)
        assert skeleton._init_args == (mock_master, )
        assert skeleton._init_kwargs == {}
        assert skeleton.controller == mock_controller
        mock_controller.set_view.assert_called_once_with(skeleton)

    def test_init_calls_create_events(self, no_template_skeleton, mock_master, mock_controller):
        skeleton = no_template_skeleton(mock_master, mock_controller)
        assert skeleton.created_events == True

    def test_controller_attrgetter_returns_proxy_factory_if_controller_not_set(self,
                                                                               no_template_skeleton, mock_master
                                                                               ):
        skeleton = no_template_skeleton(mock_master, controller=None)
        assert isinstance(skeleton.controller, CallProxyFactory)

    def test_controller_setter_raises_exception_if_invalid_controller(
            self,
            no_template_skeleton,
            mock_master):
        with pytest.raises(TypeError, match=r"Controller must be of type ControllerABC"):
            no_template_skeleton(mock_master, object())

    def test_create_all_creates_and_grids_widgets_from_template(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mocked_widget):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {}),
                     SkelWidget(mocked_widget, {}, {})],
                    [SkelWidget(mocked_widget, {}, {}),
                     SkelWidget(mocked_widget, {}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton,), call().grid(row=0, column=0),
            call(skeleton,), call().grid(row=0, column=1),
            call(skeleton,), call().grid(row=1, column=0),
            call(skeleton,), call().grid(row=1, column=1),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_init_args(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mocked_widget):

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {'arg1': True}, {}), SkelWidget(
                        mocked_widget, {'arg2': True}, {})],
                    [SkelWidget(mocked_widget, {'arg3': True}, {}), SkelWidget(
                        mocked_widget, {'arg4': True}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton, arg1=True), call().grid(row=0, column=0),
            call(skeleton, arg2=True), call().grid(row=0, column=1),
            call(skeleton, arg3=True), call().grid(row=1, column=0),
            call(skeleton, arg4=True), call().grid(row=1, column=1),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_grid_args(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mocked_widget):

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {'arg1': True}), SkelWidget(
                        mocked_widget, {}, {'arg2': True})],
                    [SkelWidget(mocked_widget, {}, {'arg3': True}), SkelWidget(
                        mocked_widget, {}, {'arg4': True})],
                )
        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton), call().grid(row=0, column=0, arg1=True),
            call(skeleton), call().grid(row=0, column=1, arg2=True),
            call(skeleton), call().grid(row=1, column=0, arg3=True),
            call(skeleton), call().grid(row=1, column=1, arg4=True),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_global_grid_args(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mocked_widget):

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {'arg1': True}), SkelWidget(
                        mocked_widget, {}, {'arg2': True})],
                    [SkelWidget(mocked_widget, {}, {'arg3': True}), SkelWidget(
                        mocked_widget, {}, {'arg4': True})],
                )
        skeleton = Tested(mock_master, mock_controller, {'garg': True})
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton), call().grid(row=0, column=0, garg=True, arg1=True),
            call(skeleton), call().grid(row=0, column=1, garg=True, arg2=True),
            call(skeleton), call().grid(row=1, column=0, garg=True, arg3=True),
            call(skeleton), call().grid(row=1, column=1, garg=True, arg4=True),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_skipping_none(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mocked_widget):

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {}),
                     SkelWidget(mocked_widget, {}, {})],
                    [None, SkelWidget(mocked_widget, {}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton,), call().grid(row=0, column=0),
            call(skeleton,), call().grid(row=0, column=1),
            call(skeleton,), call().grid(row=1, column=1),
        ]

    def test_create_all_updates_cache(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mocked_widget):

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {}),
                     SkelWidget(mocked_widget, {}, {})],
                    [None, SkelWidget(mocked_widget, {}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        assert skeleton.widget_cache == {
            (0, 0): (mocked_widget.return_value, {}),
            (0, 1): (mocked_widget.return_value, {}),
            (1, 0): (None, None),
            (1, 1): (mocked_widget.return_value, {}),
        }

    def test_create_all_creates_and_grids_widgets_from_template_with_var_in_init_args(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mock_tk_var,
            mocked_widget):

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {'arg1': mock_tk_var}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        mocked_widget.assert_called_once_with(
            skeleton, arg1=mock_tk_var.return_value)

        mocked_widget.return_value.grid.assert_called_once_with(
            row=0, column=0)

    def test_create_all_creates_and_grids_widgets_from_template_with_var_in_init_args_and_creates_label(
            self,
            mock_master,
            mock_controller,
            mock_mixin_class,
            mock_tk_var,
            mocked_widget,
            mocker):
        mock_tk_var.return_value = mocker.Mock(Variable)

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(
                        mocked_widget, {'arg1': mock_tk_var}, {}, 'test_label')],
                )
        skeleton = Tested(mock_master, mock_controller)
        mocked_widget.assert_called_once_with(
            skeleton, arg1=mock_tk_var.return_value)

        mocked_widget.return_value.grid.assert_called_once_with(
            row=0, column=0)

        assert skeleton.created["test_label"].as_dict() == {
            "widget": mocked_widget.return_value,
            "arg1": mock_tk_var.return_value
        }

    def test_append_row_appends_a_row_of_widgets(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mocked_widget,
        mocker: MockerFixture
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {}),
                     SkelWidget(mocked_widget, {}, {})],
                    [None, SkelWidget(mocked_widget, {}, {})],
                )
        skeleton = Tested(mock_master, mock_controller)
        new_row = [SkelWidget(mocked_widget, {'iarg1': True}, {}),
                   SkelWidget(mocked_widget, {}, {'garg1': True})]
        skeleton.append_row(new_row)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton,), call().grid(row=0, column=0),
            call(skeleton,), call().grid(row=0, column=1),
            call(skeleton,), call().grid(row=1, column=1),
            call(skeleton, iarg1=True), call().grid(row=2, column=0),
            call(skeleton,), call().grid(row=2, column=1, garg1=True),
        ]
        assert skeleton.widget_cache == {
            (0, 0): (mocked_widget.return_value, {}),
            (0, 1): (mocked_widget.return_value, {}),
            (1, 0): (None, None),
            (1, 1): (mocked_widget.return_value, {}),
            (2, 0): (mocked_widget.return_value, {}),
            (2, 1): (mocked_widget.return_value, {'garg1': True}),
        }

    @pytest.mark.parametrize("destroy_row, destroy_calls, grid_calls, expect_cache_gargs", [
        (0, [
            call().destroy(), call().destroy()
        ], [
            call().grid(row=0, column=1, garg2=True)
        ], {
            (0, 0): None,
            (0, 1): {'garg2': True}
        }),
        (1, [
            call().destroy()
        ], [
            call().grid(row=0, column=0, garg1=True), call().grid(row=0, column=1)
        ], {
            (0, 0): {'garg1': True},
            (0, 1): {}
        }),
    ])
    def test_destroy_row_destroys_a_row_of_widgets_and_regrids_remaining(
        self,
        destroy_row,
        destroy_calls,
        grid_calls,
        expect_cache_gargs,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mocked_widget,
        mocker: MockerFixture
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [SkelWidget(mocked_widget, {}, {'garg1': True}),
                     SkelWidget(mocked_widget, {}, {})],
                    [None, SkelWidget(mocked_widget, {}, {'garg2': True})],
                )
        skeleton = Tested(mock_master, mock_controller)
        skeleton.destroy_row(destroy_row)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton,), call().grid(row=0, column=0, garg1=True),
            call(skeleton,), call().grid(row=0, column=1),
            call(skeleton,), call().grid(row=1, column=1, garg2=True),
            *destroy_calls,
            *grid_calls
        ]
        assert skeleton.widget_cache == {
            k: (mocked_widget.return_value if value is not None else None, value) for k, value in expect_cache_gargs.items()
        }

    @pytest.mark.parametrize("widget_label, expected", [
        ('0', 0),
        ('1', 0),
        ('2', 1),
        ('3', None)
    ])
    def test_find_row_of_returns_row_index(
        self,
        widget_label,
        expected,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mocker: MockerFixture,
    ):
        mocked_widgets = [mocker.Mock() for __ in range(3)]

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widgets[0], {}, {}, '0'),
                        SkelWidget(mocked_widgets[1], {}, {}, '1'),
                    ],
                    [None, SkelWidget(mocked_widgets[2], {}, {}, '2')],
                )
        skeleton = Tested(mock_master, mock_controller)
        actual = skeleton.find_row_of(widget_label)
        assert actual == expected


class TestCreatedWidget:
    @pytest.fixture
    def mock_widget(self, mocker: MockerFixture):
        return mocker.Mock(Widget)

    @pytest.fixture
    def created_widget(self, mock_widget):
        return CreatedWidget(
            mock_widget
        )

    @pytest.fixture
    def mock_var(self, mocker: MockerFixture):
        return mocker.Mock(Variable)

    @pytest.mark.parametrize("attr,", [
        "custom_attr",
        "textvariable",
        "listvariable",
        "variable",
    ])
    def test_readonly_attribute(self, attr: str, created_widget: 'CreatedWidget'):
        with pytest.raises(AttributeError, match=r"Cannot set '" + attr + r"'; <class 'tklife.skel.CreatedWidget'> is read-only"):
            setattr(created_widget, attr, True)

    @pytest.mark.parametrize("attr,", [
        "custom_attr",
        "textvariable",
        "listvariable",
        "variable",
    ])
    def test_raises_exception_when_setting_item(self, attr: str, created_widget: 'CreatedWidget'):
        with pytest.raises(AttributeError, match=r"Cannot set '" + attr + r"'; <class 'tklife.skel.CreatedWidget'> is read-only"):
            created_widget[attr] = True

    def test_raises_exception_when_attribute_not_found(self, created_widget: 'CreatedWidget'):
        with pytest.raises(AttributeError, match=r"'attr' not found"):
            print(created_widget.attr)

    def test_raises_exception_when_item_not_found(self, created_widget: 'CreatedWidget'):
        with pytest.raises(AttributeError, match=r"'attr' not found"):
            print(created_widget['attr'])

    @pytest.mark.parametrize("attr", [
        "custom_attr",
        "textvariable",
        "listvariable",
        "variable",
    ])
    def test_dunder_getattr_for_all_values(self, attr, mock_widget, mock_var):
        created_widget = CreatedWidget(mock_widget, **{attr: mock_var})
        assert getattr(created_widget, attr) == mock_var

    @pytest.mark.parametrize("attr", [
        "custom_attr",
        "textvariable",
        "listvariable",
        "variable",
    ])
    def test_dunder_getitem_for_all_values(self, attr, mock_widget, mock_var):
        created_widget = CreatedWidget(mock_widget, **{attr: mock_var})
        assert created_widget[attr] == mock_var


class TestMenuMixin(object):
    @pytest.fixture
    def mock_widget_class(self, mocker: MockerFixture):
        class Misc(object):
            def __init__(self, *args, **kwargs) -> None:
                self._init_args = args
                self._init_kwargs = kwargs
                self.calls = [
                    call(*args, **kwargs)
                ]

            def option_add(self, *args, **kwargs):
                self.calls.append(
                    call().option_add(*args, **kwargs)
                )

            def winfo_toplevel(self, *args, **kwargs):
                self.calls.append(
                    call().winfo_toplevel(*args, **kwargs)
                )

            def __setitem__(self, key, value):
                self.calls.append(
                    call().__setitem__(key, value)
                )
        return Misc

    @pytest.fixture
    def mock_master(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def tk_menu_patch(self, mocker: MockerFixture):
        return mocker.patch("tklife.skel.tkinter")

    def test_create_menu_calls_methods(self, mock_widget_class,
                                       mock_master,
                                       tk_menu_patch):
        class TestMenu(MenuMixin, mock_widget_class):
            @property
            def menu_template(self):
                return {
                    Menu.cascade(label="File", underline=0): {
                        Menu.add(): 'separator',
                    },
                    Menu.command(label="Test Command"): None
                }
        m = TestMenu(mock_master)
        tk_menu_patch.Menu.add_command.assert_called_once_with(
            tk_menu_patch.Menu.return_value, label="Test Command", command=None
        )
        tk_menu_patch.Menu.add.assert_called_once_with(
            tk_menu_patch.Menu.return_value, 'separator'
        )
        tk_menu_patch.Menu.add_cascade.assert_called_once_with(
            tk_menu_patch.Menu.return_value, label="File", underline=0, menu=tk_menu_patch.Menu.return_value
        )
