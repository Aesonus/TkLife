from tkinter import Frame, LabelFrame, Variable
import tkinter.ttk as ttk
from typing import Dict, Type, TypeVar
from ..constants import COLUMN, ROW

_Container = TypeVar('_Container', Frame, ttk.Frame,
                     LabelFrame, ttk.Labelframe)

__all__ = [
    'TkVars',
    'widgets',
    'layout',
    'Skeleton',
]


class _MetaTkVars(type):
    def __getattribute__(self, name: str) -> Variable:
        if name.startswith('_'):
            return type.__getattribute__(self, name)
        if self._current_frame is None:
            return
        try:
            return getattr(self._current_frame, name)
        except AttributeError:
            setattr(self._current_frame, name, type.__getattribute__(
                self, name)(master=self._current_frame))
            return getattr(self._current_frame, name)
        raise AttributeError


class TkVars(object, metaclass=_MetaTkVars):
    _current_frame = None


def widgets(frame: _Container, widget_rows):
    frame.widgets = []
    for y, row in enumerate(widget_rows):
        w_row = []
        frame.widgets.append(w_row)
        for x, wdef in enumerate(row):
            for widget_type, kw in wdef.items():
                # print("({}, {}) {} - {}".format(
                #    x, y, widget_type, kw
                # ))
                w_row.append(widget_type(frame, **kw))


def layout(frame: _Container, widget_rows):
    for (y, row), wr in zip(enumerate(widget_rows), frame.widgets):
        for (x, kw), w in zip(enumerate(row), wr):
            kw.update({
                COLUMN: x,
                ROW: y
            })
            w.grid(**kw)


class Skeleton(object):
    """
    Mixin to be used with a container type widget to elegantly configure its
    widgets.
    """
    def __init__(self, vars: Type[TkVars] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.vars = vars
        self.vars._current_frame = self
        for func, input in self.skeleton_configure():
            func(self, input)

    def skeleton_configure(self) -> Dict:
        raise NotImplementedError
