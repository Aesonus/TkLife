from typing import Iterable, Optional
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from tklife.core import SkeletonMixin, SkelWidget
from tklife.dynamic import AppendableMixin


def _generate_expected_cache(
    range_size: int,
    insert_index: int,
    inserted: tuple[None | tuple[dict, dict, dict]],
    existing: Iterable[None | dict],
    widget,
    colsize: Optional[int] = 2,
):
    for row in range(range_size + 1):
        if row < insert_index:
            for col, grid_args in enumerate(existing):
                if grid_args is None:
                    yield (row, col), (None, None)
                else:
                    yield (row, col), (widget, grid_args)
                if col == colsize - 1:
                    break
        elif row == insert_index:
            for col, element in enumerate(inserted):
                if element is None:
                    yield (row, col), (None, None)
                else:
                    __, ___, gargs = element
                    yield (row, col), (widget, gargs)
        else:
            for col, grid_args in enumerate(existing):
                if grid_args is None:
                    yield (row, col), (None, None)
                else:
                    yield (row, col), (widget, grid_args)
                if col == colsize - 1:
                    break


def _generate_expected_calls(
    range_size: int,
    insert_index: int,
    inserted: tuple[None | tuple[dict, dict, dict]],
    skeleton: SkeletonMixin,
    existing: Iterable[None | dict],
    colsize: Optional[int] = 2,
):
    for row in range(range_size):
        if row < insert_index:
            for __ in range(colsize):
                next(existing)
            continue
        elif row == insert_index:
            for col, element in enumerate(inserted):
                grid_arg = next(existing)
                if element is None:
                    if grid_arg is None:
                        continue
                    yield call().grid(row=row + 1, column=col)  # Moved
                    continue
                iargs, cargs, gargs = element
                yield call(skeleton, **iargs)
                yield call().configure(**cargs)
                yield call().grid(row=row, column=col, **gargs)
                if grid_arg is None:
                    continue
                yield call().grid(row=row + 1, column=col)  # Moved
        else:
            for col in range(len(inserted)):
                grid_arg = next(existing)
                if grid_arg is None:
                    continue
                yield call().grid(row=row + 1, column=col)  # Moved


def _generate_new_row(
    widget,
    inserted: tuple[tuple[dict, dict, dict] | None],
):
    for i in inserted:
        if i is None:
            yield None
        else:
            iargs, cargs, gargs = i
            yield SkelWidget(widget, iargs, gargs, cargs)


def _generate_template(
    widget_class,
    existing: Iterable[None | dict],
    colsize: Optional[int] = 2,
):
    def g_rowlist(existing):
        for index, grid_arg in enumerate(existing):
            if grid_arg is None:
                yield None
            else:
                yield SkelWidget(widget_class, grid_args=grid_arg)
            if index == colsize - 1:
                break

    while yield_val := list(g_rowlist(existing)):
        yield yield_val


class TestAppendableMixin:
    def test_append_row_appends_a_row_of_widgets(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mocked_widget,
    ):
        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
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
        new_row = [
            SkelWidget(mocked_widget, {"iarg1": True}, {}),
            SkelWidget(mocked_widget, {}, {"garg1": True}),
        ]
        skeleton.append_row(new_row)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(skeleton),
            call().configure(),
            call().grid(row=0, column=0),
            call(skeleton),
            call().configure(),
            call().grid(row=0, column=1),
            call(skeleton),
            call().configure(),
            call().grid(row=1, column=1),
            call(skeleton, iarg1=True),
            call().configure(),
            call().grid(row=2, column=0),
            call(skeleton),
            call().configure(),
            call().grid(row=2, column=1, garg1=True),
        ]
        assert skeleton.widget_cache == {
            (0, 0): (mocked_widget.return_value, {}),
            (0, 1): (mocked_widget.return_value, {}),
            (1, 0): (None, None),
            (1, 1): (mocked_widget.return_value, {}),
            (2, 0): (mocked_widget.return_value, {}),
            (2, 1): (mocked_widget.return_value, {"garg1": True}),
        }

    def test_append_row_appends_a_row_of_widgets_that_has_a_none_value(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
        mocked_widget,
    ):
        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
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
        new_row = [
            SkelWidget(mocked_widget, {"iarg1": True}, {}),
            None,
        ]
        skeleton.append_row(new_row)
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
            call(skeleton, iarg1=True),
            call().configure(),
            call().grid(row=2, column=0),
        ]
        assert skeleton.widget_cache == {
            (0, 0): (mocked_widget.return_value, {}),
            (0, 1): (mocked_widget.return_value, {}),
            (1, 0): (None, None),
            (1, 1): (mocked_widget.return_value, {}),
            (2, 0): (mocked_widget.return_value, {}),
            (2, 1): (None, None),
        }

    @pytest.mark.parametrize(
        "destroy_row, destroy_calls, grid_calls, expect_cache_gargs",
        [
            (
                0,
                [call().destroy(), call().destroy()],
                [call().grid(row=0, column=1, garg2=True)],
                {(0, 0): None, (0, 1): {"garg2": True}},
            ),
            (
                1,
                [call().destroy()],
                [
                    call().grid(row=0, column=0, garg1=True),
                    call().grid(row=0, column=1),
                ],
                {(0, 0): {"garg1": True}, (0, 1): {}},
            ),
        ],
    )
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
    ):
        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widget, {}, {"garg1": True}, label="label"),
                        SkelWidget(mocked_widget, {}, {}, label="label2"),
                    ],
                    [
                        None,
                        SkelWidget(mocked_widget, {}, {"garg2": True}, label="label3"),
                    ],
                )

        skeleton = Tested(mock_master, mock_controller)
        skeleton.destroy_row(destroy_row)
        actual = mocked_widget.mock_calls
        assert actual == [
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=0, column=0, garg1=True),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=0, column=1),
            call(
                skeleton,
            ),
            call().configure(),
            call().grid(row=1, column=1, garg2=True),
            *destroy_calls,
            *grid_calls,
        ]
        assert skeleton.widget_cache == {
            k: (mocked_widget.return_value if value is not None else None, value)
            for k, value in expect_cache_gargs.items()
        }

    @pytest.mark.parametrize(
        "widget_label, expected", [("0", 0), ("1", 0), ("2", 1), ("3", None)]
    )
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

        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
            @property
            def template(self):
                return (
                    [
                        SkelWidget(mocked_widgets[0], {}, {}, {}, "0"),
                        SkelWidget(mocked_widgets[1], {}, {}, {}, "1"),
                    ],
                    [None, SkelWidget(mocked_widgets[2], {}, {}, {}, "2")],
                )

        skeleton = Tested(mock_master, mock_controller)
        actual = skeleton.find_row_of(widget_label)
        assert actual == expected

    def test_find_row_of_returns_none_if_no_rows_in_template(
        self,
        mock_master,
        mock_controller,
        mock_mixin_class,
    ):
        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
            pass

        skeleton = Tested(mock_master, mock_controller)
        actual = skeleton.find_row_of("0")
        assert actual is None

    def test_insert_row_at_inserts_row_at_last_plus_1_index(
        self, mock_mixin_class, mocked_widget, mock_master, mock_controller
    ):
        index = 2
        expected_w_args = [
            ({"iarg1": True}, {}),
            ({"iarg2": True}, {"garg1": True}),
        ]
        expected_cache = {
            (0, 0): (mocked_widget.return_value, {}),
            (0, 1): (mocked_widget.return_value, {}),
            (1, 0): (None, None),
            (1, 1): (mocked_widget.return_value, {}),
            (2, 0): (mocked_widget.return_value, {}),
            (2, 1): (mocked_widget.return_value, {"garg1": True}),
        }
        new_row = [
            SkelWidget(mocked_widget, iarg, garg) for iarg, garg in expected_w_args
        ]

        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
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
        expected_calls = [
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
            # Inserted
            call(skeleton, iarg1=True),
            call().configure(),
            call().grid(row=2, column=0),
            call(skeleton, iarg2=True),
            call().configure(),
            call().grid(row=2, column=1, garg1=True),
        ]

        skeleton.insert_row_at(index, new_row)

        assert mocked_widget.mock_calls == expected_calls
        assert skeleton.widget_cache == expected_cache

    @pytest.mark.parametrize("index", [0, 1, 2])
    @pytest.mark.parametrize(
        "inserted",
        [
            (None, ({"init_arg": True}, {}, {"grid_arg": True})),
            (({"init_arg": True}, {}, {"grid_arg": True}), None),
            (
                ({"init_arg": True}, {}, {"grid_arg": True}),
                ({"init_arg": True}, {}, {"grid_arg": True}),
            ),
        ],
        ids=[
            "None, New",
            "New, None",
            "New, New",
        ],
    )
    @pytest.mark.parametrize(
        "existing",
        (
            [{}, {}, {}, {}, {}, {}],
            [None, {}, {}, {}, {}, {}],
            [{}, {}, None, None, {}, {}],
        ),
    )
    def test_insert_row_at_inserts_row_with_none_before_given_index(
        self,
        mock_mixin_class,
        mocked_widget,
        mock_master,
        mock_controller,
        index,
        inserted,
        existing,
    ):
        colsize = len(inserted)
        range_size = int(len(existing) / colsize)

        expected_cache = dict(
            _generate_expected_cache(
                range_size,
                index,
                inserted,
                iter(existing),
                mocked_widget.return_value,
                colsize=colsize,
            )
        )

        new_row = list(_generate_new_row(mocked_widget, inserted))

        template = tuple(
            _generate_template(mocked_widget, iter(existing), colsize=colsize)
        )

        class Tested(SkeletonMixin, AppendableMixin, mock_mixin_class):
            @property
            def template(self):
                return template

        # Set up the template
        skeleton = Tested(mock_master, mock_controller)

        # Set up the expected calls
        expected_calls = list(
            _generate_expected_calls(
                range_size, index, inserted, skeleton, iter(existing), colsize=colsize
            )
        )

        skeleton.insert_row_at(index, new_row)

        assert skeleton.widget_cache == expected_cache
        # Lop off the first calls as those are setup calls
        assert (
            mocked_widget.mock_calls[len([e for e in existing if e is not None]) * 3 :]
            == expected_calls
        )
