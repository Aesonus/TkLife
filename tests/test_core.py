from tkinter import Variable
from typing import Iterable
from unittest.mock import call

import pytest
import pytest_mock
from pytest_mock import MockerFixture

from tklife.core import CreatedWidget, SkeletonMixin, SkelEventDef, SkelWidget
from tklife.event import BaseEvent
from tklife.proxy import CallProxyFactory


class TestSkelWidget:
    @pytest.fixture
    def skel_widget(self, mocked_widget):
        return SkelWidget(
            mocked_widget,
            {"init": "args"},
            {"grid": "args"},
            {"config": "args"},
            "label",
        )

    def test_that_skel_widget_is_iterable(self, skel_widget: SkelWidget, mocked_widget):
        widget, init_args, grid_args, config_args, label = skel_widget
        assert widget == mocked_widget
        assert init_args == {"init": "args"}
        assert grid_args == {"grid": "args"}
        assert config_args == {"config": "args"}
        assert label == "label"

    @pytest.mark.parametrize(
        "merged_init_args, expected_init_args",
        [
            ({"new": "initarg"}, {"init": "args", "new": "initarg"}),
            ({"init": "initarg"}, {"init": "initarg"}),
        ],
    )
    def test_skel_widget_init_method_returns_new_skel_widget_with_appended_args(
        self,
        merged_init_args,
        expected_init_args,
        mocked_widget,
        skel_widget: SkelWidget,
    ):
        actual = skel_widget.init(**merged_init_args)
        assert actual.widget == mocked_widget
        assert actual.init_args == expected_init_args
        assert actual.grid_args == {"grid": "args"}
        assert actual.config_args == {"config": "args"}
        assert actual.label == "label"
        assert actual is not skel_widget

    @pytest.mark.parametrize(
        "merged_grid_args, expected_grid_args",
        [
            ({"new": "gridarg"}, {"grid": "args", "new": "gridarg"}),
            ({"grid": "gridarg"}, {"grid": "gridarg"}),
        ],
    )
    def test_skel_widget_grid_method_returns_new_skel_widget_with_appended_args(
        self,
        merged_grid_args,
        expected_grid_args,
        mocked_widget,
        skel_widget: SkelWidget,
    ):
        actual = skel_widget.grid(**merged_grid_args)
        assert actual.widget == mocked_widget
        assert actual.init_args == {"init": "args"}
        assert actual.grid_args == expected_grid_args
        assert actual.config_args == {"config": "args"}
        assert actual.label == "label"
        assert actual is not skel_widget

    @pytest.mark.parametrize(
        "merged_config_args, expected_config_args",
        [
            ({"new": "configarg"}, {"config": "args", "new": "configarg"}),
            ({"config": "configarg"}, {"config": "configarg"}),
        ],
    )
    def test_skel_widget_config_method_returns_new_skel_widget_with_appended_args(
        self,
        merged_config_args,
        expected_config_args,
        mocked_widget,
        skel_widget: SkelWidget,
    ):
        actual = skel_widget.config(**merged_config_args)
        assert actual.widget == mocked_widget
        assert actual.init_args == {"init": "args"}
        assert actual.grid_args == {"grid": "args"}
        assert actual.config_args == expected_config_args
        assert actual.label == "label"
        assert actual is not skel_widget

    def test_skel_widget_set_label_method_returns_new_skel_widget_with_new_label(
        self, mocked_widget, skel_widget: SkelWidget
    ):
        actual = skel_widget.set_label("newlabel")
        assert actual.widget == mocked_widget
        assert actual.init_args == {"init": "args"}
        assert actual.grid_args == {"grid": "args"}
        assert actual.config_args == {"config": "args"}
        assert actual.label == "newlabel"
        assert actual is not skel_widget


class TestSkeletonMixin:
    @pytest.fixture
    def no_template_skeleton(self, mock_mixin_class):
        class TestedSkeleton(SkeletonMixin, mock_mixin_class):
            def __init__(
                self,
                master=None,
                controller=None,
                global_grid_args=None,
                proxy_factory=None,
                **kwargs,
            ) -> None:
                self._calls = []  # For tests
                super().__init__(
                    master, controller, global_grid_args, proxy_factory, **kwargs
                )

            def _create_events(self):
                self._calls.append(call()._create_events())

            def __before_init__(self):
                self._calls.append(call().__before_init__())

            def __after_init__(self):
                self._calls.append(call().__after_init__())

            def __after_widgets__(self):
                self._calls.append(call().__after_widgets__())

        return TestedSkeleton

    @pytest.fixture
    def mock_tk_var(self, mocker: MockerFixture):
        return mocker.Mock(type(Variable))

    def test_dunder_init_sets_controller(
        self, no_template_skeleton, mock_master, mock_controller
    ):
        skeleton = no_template_skeleton(mock_master, mock_controller)
        assert skeleton.controller == mock_controller

    def test_dunder_init_calls_init_hooks_in_correct_order(
        self, no_template_skeleton, mock_master, mock_controller
    ):
        skeleton = no_template_skeleton(mock_master, mock_controller, other="arg")
        assert skeleton._calls == [
            call().__before_init__(),
            call(
                master=mock_master, other="arg"
            ),  # From mock_mixin_class.__init__ method
            call().__after_init__(),
            call().__after_widgets__(),
            call()._create_events(),
        ]

    @pytest.mark.parametrize(
        "mixin_class",
        [
            SkeletonMixin,
            type("SkeletonMixinSubclass", (SkeletonMixin,), {}),
        ],
    )
    def test_meta_dunder_new_typechecks_bases(self, mock_mixin_class, mixin_class):
        with pytest.raises(TypeError) as exc:

            class _TestedSkeleton(mock_mixin_class, mixin_class):
                @property
                def template(self):
                    return [[]]

        assert str(exc.value) == f"{mixin_class} should be first base class"

    def test_meta_dunder_new_does_not_raise_error_with_SkeletonMixin_subclass_as_first_base(
        self, mock_mixin_class
    ):
        class _TestedSkeleton(
            type("SkeletonMixinSubclass", (SkeletonMixin,), {}), mock_mixin_class
        ):
            pass

    def test_controller_attrgetter_returns_proxy_factory_if_controller_not_set(
        self, no_template_skeleton, mock_master
    ):
        skeleton = no_template_skeleton(mock_master, controller=None)
        assert isinstance(skeleton.controller, CallProxyFactory)

    def test_controller_setter_raises_exception_if_invalid_controller(
        self, no_template_skeleton, mock_master
    ):
        with pytest.raises(
            TypeError, match=r"Controller must be of type ControllerABC"
        ):
            no_template_skeleton(mock_master, object())

    def test_create_all_creates_and_grids_widgets_from_template(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {}),
                        SkelWidget(mocked_widget, {}, {}),
                    ],
                    [
                        SkelWidget(mocked_widget, {}, {}),
                        SkelWidget(mocked_widget, {}, {}),
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=0, column=0),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=0, column=1),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=1, column=0),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=1, column=1),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_init_args(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {"arg1": True}, {}),
                        SkelWidget(mocked_widget, {"arg2": True}, {}),
                    ],
                    [
                        SkelWidget(mocked_widget, {"arg3": True}, {}),
                        SkelWidget(mocked_widget, {"arg4": True}, {}),
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton, arg1=True),
            call().configure(),
            call().grid(row=0, column=0),
            call(skeleton, arg2=True),
            call().configure(),
            call().grid(row=0, column=1),
            call(skeleton, arg3=True),
            call().configure(),
            call().grid(row=1, column=0),
            call(skeleton, arg4=True),
            call().configure(),
            call().grid(row=1, column=1),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_grid_args(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {"arg1": True}),
                        SkelWidget(mocked_widget, {}, {"arg2": True}),
                    ],
                    [
                        SkelWidget(mocked_widget, {}, {"arg3": True}),
                        SkelWidget(mocked_widget, {}, {"arg4": True}),
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton),
            call().configure(),
            call().grid(row=0, column=0, arg1=True),
            call(skeleton),
            call().configure(),
            call().grid(row=0, column=1, arg2=True),
            call(skeleton),
            call().configure(),
            call().grid(row=1, column=0, arg3=True),
            call(skeleton),
            call().configure(),
            call().grid(row=1, column=1, arg4=True),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_global_grid_args(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {"arg1": True}),
                        SkelWidget(mocked_widget, {}, {"arg2": True}),
                    ],
                    [
                        SkelWidget(mocked_widget, {}, {"arg3": True}),
                        SkelWidget(mocked_widget, {}, {"arg4": True}),
                    ],
                )

        skeleton = Tested(mock_master, mock_controller, {"garg": True})
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton),
            call().configure(),
            call().grid(row=0, column=0, garg=True, arg1=True),
            call(skeleton),
            call().configure(),
            call().grid(row=0, column=1, garg=True, arg2=True),
            call(skeleton),
            call().configure(),
            call().grid(row=1, column=0, garg=True, arg3=True),
            call(skeleton),
            call().configure(),
            call().grid(row=1, column=1, garg=True, arg4=True),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_with_config_args(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {}, {"arg1": True}),
                        SkelWidget(mocked_widget, {}, {}, {"arg2": True}),
                    ],
                    [
                        SkelWidget(mocked_widget, {}, {}, {"arg3": True}),
                        SkelWidget(mocked_widget, {}, {}, {"arg4": True}),
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton),
            call().configure(arg1=True),
            call().grid(row=0, column=0),
            call(skeleton),
            call().configure(arg2=True),
            call().grid(row=0, column=1),
            call(skeleton),
            call().configure(arg3=True),
            call().grid(row=1, column=0),
            call(skeleton),
            call().configure(arg4=True),
            call().grid(row=1, column=1),
        ]

    def test_create_all_creates_and_grids_widgets_from_template_skipping_none(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {}),
                        SkelWidget(mocked_widget, {}, {}),
                    ],
                    [None, SkelWidget(mocked_widget, {}, {})],
                )

        skeleton = Tested(mock_master, mock_controller)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=0, column=0),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=0, column=1),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=1, column=1),
        ]

    def test_create_all_stores_image_init_arg_as_attribute_on_created_widget(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return ([SkelWidget(mocked_widget, {"image": "test"}, label="test")],)

        skeleton = Tested(mock_master, mock_controller)
        assert skeleton.created["test"].widget.__image__ == "test"

    def test_create_all_stores_image_config_arg_as_attribute_on_created_widget(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return ([SkelWidget(mocked_widget, label="test").config(image="test")],)

        skeleton = Tested(mock_master, mock_controller)
        assert skeleton.created["test"].widget.__image__ == "test"

    def test_create_all_updates_cache(
        self, mock_master, mock_controller, mock_mixin_class, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {}),
                        SkelWidget(mocked_widget, {}, {}),
                    ],
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
        self, mock_master, mock_controller, mock_mixin_class, mock_tk_var, mocked_widget
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return ([SkelWidget(mocked_widget, {"arg1": mock_tk_var}, {})],)

        skeleton = Tested(mock_master, mock_controller)
        mocked_widget.assert_called_once_with(skeleton, arg1=mock_tk_var.return_value)

        mocked_widget.return_value.grid.assert_called_once_with(row=0, column=0)

    def test_create_all_creates_and_grids_widgets_from_template_with_var_in_init_args_and_creates_label(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mock_tk_var,
        mocked_widget,
        mocker,
    ):
        mock_tk_var.return_value = mocker.Mock(Variable)

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(
                            mocked_widget, {"arg1": mock_tk_var}, {}, {}, "test_label"
                        )
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        mocked_widget.assert_called_once_with(skeleton, arg1=mock_tk_var.return_value)

        mocked_widget.return_value.grid.assert_called_once_with(row=0, column=0)

        assert skeleton.created["test_label"].as_dict() == {
            "widget": mocked_widget.return_value,
            "arg1": mock_tk_var.return_value,
        }

    def test_create_all_creates_and_grids_widgets_from_template_with_var_in_config_args_and_creates_label(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mock_tk_var,
        mocked_widget,
        mocker,
    ):
        mock_tk_var.return_value = mocker.Mock(Variable)

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(
                            mocked_widget, {}, {}, {"arg1": mock_tk_var}, "test_label"
                        )
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        mocked_widget.assert_called_once_with(skeleton)

        mocked_widget.return_value.grid.assert_called_once_with(row=0, column=0)

        assert skeleton.created["test_label"].as_dict() == {
            "widget": mocked_widget.return_value,
            "arg1": mock_tk_var.return_value,
        }

    @pytest.mark.parametrize(
        "grid_conf,expected_rowconfigure_calls,expected_columnconfigure_calls",
        [
            (([{"weight": 1}], [{}]), [call(0, weight=1)], []),
            (([{}, {"weight": 1}], [{}]), [call(1, weight=1)], []),
            (([{}, {}], [{"weight": 1}]), [], [call(0, weight=1)]),
            (([{}, {}], [{}, {"weight": 1}]), [], [call(1, weight=1)]),
            (
                ([{"weight": 1}, {"weight": 2}], [{"weight": 3}, {"weight": 4}]),
                [call(0, weight=1), call(1, weight=2)],
                [call(0, weight=3), call(1, weight=4)],
            ),
            # Test that missing rows and columns are ignored
            (
                ([{}, {"weight": 2}], [{}, {"weight": 4}]),
                [call(1, weight=2)],  # Missing column 0
                [call(1, weight=4)],  # Missing row 0
            ),
        ],
    )
    def test_create_all_configures_grid_using_return_value_from_grid_config_property(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mocked_widget,
        grid_conf,
        expected_rowconfigure_calls,
        expected_columnconfigure_calls,
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def grid_config(self):
                return grid_conf

            @property
            def template(self):
                return ([SkelWidget(mocked_widget, {}, {})],)

        created = Tested(mock_master, mock_controller)
        assert created.columnconfigure.mock_calls == expected_columnconfigure_calls
        assert created.rowconfigure.mock_calls == expected_rowconfigure_calls

    def test_create_all_configures_events_using_return_value_from_events_property(
        self, mock_master, mock_mixin_class, mocker
    ):
        mock_event = mocker.Mock(spec=BaseEvent)
        mock_action = mocker.MagicMock()
        bind_method = "bind"

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def events(self) -> Iterable[SkelEventDef]:
                return [
                    {
                        "event": mock_event,
                        "bind_method": bind_method,
                        "action": mock_action,
                    },
                ]

        created = Tested(mock_master)
        mock_event.bind.assert_called_once_with(created, action=mock_action, add="")

    def test_create_all_saves_bound_event_id_to_assigned_events_property(
        self, mock_master, mock_mixin_class, mocker
    ):
        mock_event = mocker.Mock(spec=BaseEvent)
        mock_action = mocker.MagicMock()

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def events(self) -> Iterable[SkelEventDef]:
                return [
                    {
                        "event": mock_event,
                        "action": mock_action,
                        "id": "testevent",
                    },
                ]

        created = Tested(mock_master)
        assert created.assigned_events["testevent"] == (
            mock_event,
            getattr(mock_event, "bind").return_value,
        )

    @pytest.mark.parametrize(
        "in_args",
        [
            "init_args",
            "config_args",
        ],
    )
    def test_create_all_image_arg_set_as_property_on_tk_widget(
        self, mock_master, mock_mixin_class, mocked_widget, mocker, in_args
    ):
        mock_image = mocker.Mock()

        kwargs = {
            "init_args": {"image": mock_image} if in_args == "init_args" else {},
            "config_args": {"image": mock_image} if in_args == "config_args" else {},
        }

        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(
                            mocked_widget, **kwargs, grid_args={}, label="test_label"
                        )
                    ],
                )

        created = Tested(mock_master)
        assert created.created["test_label"].widget.__image__ == mock_image

    @pytest.mark.parametrize(
        "raised_on_x_widget, expected_row, expected_col",
        [
            (0, 0, 0),
            (1, 0, 1),
            (2, 1, 1),
        ],
    )
    def test_exception_within_widget_create_output_row_and_col_of_what_template_failed_to_init(
        self,
        mock_master,
        mock_mixin_class,
        mocked_widget,
        raised_on_x_widget,
        expected_row,
        expected_col,
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget),
                        SkelWidget(mocked_widget),
                    ],
                    [None, SkelWidget(mocked_widget)],
                )

        expected_previous_message = "test"
        mocked_widget.side_effect = (
            [  # Only raise on the widget that is expected to fail
                (
                    Exception(expected_previous_message)
                    if i == raised_on_x_widget
                    else mocked_widget
                )
                for i in range(3)
            ]
        )
        with pytest.raises(
            Exception,
            match=f"Error initializing widget at row {expected_row}, column {expected_col}: ",
        ):
            Tested(mock_master)

    @pytest.mark.parametrize(
        "raised_on_x_widget, expected_row, expected_col",
        [
            (0, 0, 0),
            (1, 0, 1),
            (2, 1, 1),
        ],
    )
    def test_exception_within_widget_create_output_row_and_col_of_what_template_failed_to_configure(
        self,
        mock_master,
        mock_mixin_class,
        mocked_widget,
        raised_on_x_widget,
        expected_row,
        expected_col,
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget),
                        SkelWidget(mocked_widget),
                    ],
                    [None, SkelWidget(mocked_widget)],
                )

        expected_previous_message = "test"
        mocked_widget().configure.side_effect = (
            [  # Only raise on the widget that is expected to fail
                (
                    Exception(expected_previous_message)
                    if i == raised_on_x_widget
                    else mocked_widget
                )
                for i in range(3)
            ]
        )
        with pytest.raises(
            Exception,
            match=f"Error configuring widget at row {expected_row}, column {expected_col}:",
        ):
            Tested(mock_master)

    @pytest.mark.parametrize(
        "raised_on_x_widget, expected_row, expected_col",
        [
            (0, 0, 0),
            (1, 0, 1),
            (2, 1, 1),
        ],
    )
    def test_exception_within_widget_create_output_row_and_col_of_what_template_failed_to_grid(
        self,
        mock_master,
        mock_mixin_class,
        mocked_widget,
        raised_on_x_widget,
        expected_row,
        expected_col,
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget),
                        SkelWidget(mocked_widget),
                    ],
                    [None, SkelWidget(mocked_widget)],
                )

        expected_previous_message = "test"
        mocked_widget().grid.side_effect = (
            [  # Only raise on the widget that is expected to fail
                (
                    Exception(expected_previous_message)
                    if i == raised_on_x_widget
                    else mocked_widget
                )
                for i in range(3)
            ]
        )
        with pytest.raises(
            Exception,
            match=f"Error gridding widget at row {expected_row}, column {expected_col}:",
        ):
            Tested(mock_master)

    def test_set_controller_raises_exception_if_controller_not_of_type_controller_abc(
        self, mock_master, mock_mixin_class
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            pass

        with pytest.raises(
            TypeError, match=r"Controller must be of type ControllerABC"
        ):
            Tested(mock_master).controller = object()

    def test_set_controller_calls_controllers_set_view_method_to_self(
        self, mock_master, mock_mixin_class, mock_controller
    ):
        class Tested(SkeletonMixin, mock_mixin_class):
            pass

        tested = Tested(mock_master)
        tested.controller = mock_controller
        mock_controller.set_view.assert_called_once_with(tested)


class TestCreatedWidget:
    @pytest.fixture
    def textvariable(self, mocker: pytest_mock.MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def variable(self, mocker: pytest_mock.MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def listvariable(self, mocker: pytest_mock.MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def customvariable(self, mocker: pytest_mock.MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def created_widget(
        self,
        mocked_widget,
        textvariable,
        variable,
        listvariable,
        customvariable,
    ):
        return CreatedWidget(
            mocked_widget,
            textvariable=textvariable,
            variable=variable,
            listvariable=listvariable,
            customvariable=customvariable,
        )

    def test_widget_property_returns_widget(self, created_widget, mocked_widget):
        assert created_widget.widget == mocked_widget

    def test_textvariable_property_returns_textvariable(
        self, created_widget, textvariable
    ):
        assert created_widget.textvariable == textvariable

    def test_variable_property_returns_variable(self, created_widget, variable):
        assert created_widget.variable == variable

    def test_listvariable_property_returns_listvariable(
        self, created_widget, listvariable
    ):
        assert created_widget.listvariable == listvariable

    def test_customvariable_property_returns_customvariable(
        self, created_widget, customvariable
    ):
        assert created_widget.customvariable == customvariable

    def test_dunder_getattr_raises_attribute_error_if_attribute_not_found(
        self, created_widget
    ):
        with pytest.raises(AttributeError):
            created_widget.not_an_attribute

    def test_dunder_getitem_raises_attribute_error_if_attribute_not_found(
        self, created_widget
    ):
        with pytest.raises(KeyError):
            created_widget["not_an_attribute"]

    def test_dunder_setattr_raises_attribute_error_if_attribute_not_found(
        self, created_widget
    ):
        with pytest.raises(AttributeError):
            created_widget.not_an_attribute = "value"

    def test_dunder_setitem_raises_attribute_error(self, created_widget):
        with pytest.raises(AttributeError):
            created_widget["not_an_attribute"] = "value"
