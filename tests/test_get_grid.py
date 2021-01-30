import pytest
from tklife.arrange import Autogrid

def test_grid_one_size_more_at_end():
    """
    """
    expected = (
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
    )
    actual=Autogrid((1,)).grid_tuples(6)
    assert tuple(actual) == expected

def test_grid_two_size():
    """
    """
    expected = (
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
    )
    actual=Autogrid((2,3)).grid_tuples(10)
    assert tuple(actual) == expected

def test_grid_two_size_more_at_end():
    """
    """
    expected = (
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
    )
    actual=Autogrid((2,3)).grid_tuples(16)
    assert tuple(actual) == expected

def test_grid_three_size_more_at_end():
    """
    """
    expected = (
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3)
    )
    actual= Autogrid((2,3,4)).grid_tuples(26)
    assert tuple(actual) == expected

def test_grid_four_size_more_at_end():
    """
    """
    expected = (
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
        (0, 3), (1, 3), (2, 3), (3, 3),
        (0, 4), (1, 4), (2, 4), (3, 4)
    )
    actual = Autogrid((2,3,4,2)).grid_tuples(26)
    assert tuple(actual) == expected

def test_grid_dicts():
    expected = (
        {'a': 0, 'b':0}, {'a': 1, 'b':0},
        {'a': 0, 'b':1}, {'a': 1, 'b':1},
    )
    actual = Autogrid((1, )).grid_dicts(4, 'ab')
    assert tuple(actual) == expected

def test_zip_dicts():
    expected = (
        ('elema', {'a': 0, 'b':0}), ('elemb', {'a': 1, 'b':0}),
        ('elemc', {'a': 0, 'b':1}), ('elemd', {'a': 1, 'b':1}),
    )
    actual = Autogrid((1, )).zip_dicts(('elema', 'elemb', 'elemc', 'elemd'), 'ab')
    assert tuple(actual) == expected

def test_zip_dicts_with_kwargs():
    expected = (
        ('elema', {'a': 0, 'b':0}, {"arg1": 1}), ('elemb', {'a': 1, 'b':0}, {"arg2": 2}),
        ('elemc', {'a': 0, 'b':1}, {"arg3": 3}), ('elemd', {'a': 1, 'b':1}, {"arg4": 4}),
    )
    actual = Autogrid((1, )).zip_dicts(('elema', 'elemb', 'elemc', 'elemd'), 'ab', grid_kwargs=(
        {"arg1": 1}, {"arg2": 2}, {"arg3": 3}, {"arg4": 4}
    ))
    assert tuple(actual) == expected

def test_zip_dicts_with_kwargs_and_default_kwargs():
    expected = (
        ('elema', {'a': 0, 'b':0}, {"arg1": 1}), ('elemb', {'a': 1, 'b':0}, {"arg2": 2}),
        ('elemc', {'a': 0, 'b':1}, {"arg3": 3}), ('elemd', {'a': 1, 'b':1}, {'default': 'arg'}),
    )
    actual = Autogrid((1, )).zip_dicts(('elema', 'elemb', 'elemc', 'elemd'), 'ab', grid_kwargs=(
        {"arg1": 1}, {"arg2": 2}, {"arg3": 3},
    ), default_grid_kwargs={'default': 'arg'})
    assert tuple(actual) == expected
