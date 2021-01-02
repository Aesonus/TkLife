from tklife.shortcuts import labelled_widgets
from _pytest.fixtures import SubRequest
import pytest

master = object()

def _Widget():
    """Used to mock tkinter widgets"""

def get_sizes():
    pass

@pytest.fixture(params=((2, 3, 3), (3, 2, 2)))
def test_args(request: SubRequest):
    return (
        tuple(("Label {}".format(index) for index in range(request.param[0]))),
        tuple((_Widget for index in range(request.param[1]))),
        tuple(({"kw_{}".format(index): index} for index in range(request.param[2]))),
    )

def test_labelled_widgets_raises_value_error_if_sizes_not_same(test_args):
    with pytest.raises(ValueError):
        labelled_widgets(master, *test_args)

