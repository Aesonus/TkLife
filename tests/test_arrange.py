import pytest
from tklife.arrange import Autogrid


def test_Autogrid_call():
    expected = (
        ('elema', {'column': 0, 'row': 0}), ('elemb', {'column': 1, 'row': 0}),
        ('elemc', {'column': 0, 'row': 1}), ('elemd', {'column': 1, 'row': 1}),
    )
    actual = Autogrid((2,))(('elema', 'elemb', 'elemc', 'elemd'))
    # print(tuple(actual))
    assert tuple(actual) == expected


def test_Autogrid_call_with_kwargs():
    expected = (
        ('elema', {'column': 0, 'row': 0, "arg1": 1}
         ), ('elemb', {'column': 1, 'row': 0, "arg2": 2}),
        ('elemc', {'column': 0, 'row': 1, "arg3": 3}
         ), ('elemd', {'column': 1, 'row': 1, "arg4": 4}),
    )
    actual = Autogrid((2, ))(('elema', 'elemb', 'elemc', 'elemd'), grid_kwargs=(
        {"arg1": 1}, {"arg2": 2}, {"arg3": 3}, {"arg4": 4}
    ))
    assert tuple(actual) == expected


def test_Autogrid_call_with_kwargs_and_default_kwargs():
    expected = (
        ('elema', {'column': 0, 'row': 0, "arg1": 1}
         ), ('elemb', {'column': 1, 'row': 0, "arg2": 2}),
        ('elemc', {'column': 0, 'row': 1, "arg3": 3}), ('elemd',
                                                        {'column': 1, 'row': 1, 'default': 'arg'}),
    )
    actual = Autogrid((2, ))(('elema', 'elemb', 'elemc', 'elemd'), grid_kwargs=(
        {"arg1": 1}, {"arg2": 2}, {"arg3": 3},
    ), fill_kwargs={'default': 'arg'})
    assert tuple(actual) == expected
