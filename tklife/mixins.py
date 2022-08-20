import abc
from tkinter import Widget
import tkinter
from typing import Any, Mapping, NamedTuple, Optional, Sequence
from tklife.constants import COLUMN, ROW, VARIABLE, TEXTVARIABLE

__all__ = ['Common']

def generate_event_for(function):
    """
    Returns a callable that will cause the widget the generate an event returned by the
    decorated function
    """
    def decorated(*args, **kwargs):
        if len(args) == 1:
            #Not an instance or class method
            widget = args[0]
            return lambda widget=widget: widget.event_generate(function(*args, **kwargs))
        else:
            self, widget = args
            return lambda self=self, widget=widget: widget.event_generate(function(*args, **kwargs))
    return decorated


class Common(object):
    """
    Defines common abstract methods for Toplevel and Tk
    """

    def __init__(self, master: Widget = None, **kwargs):
        """
        Initialize the Toplevel
        """
        super().__init__(master, **kwargs)
        self._create_vars()
        self._create_widgets()
        self._create_events()
        self._layout_widgets()

    def _create_events(self):
        """Creates the events for the class"""

    def _create_vars(self):
        """Creates variables for widgets"""

    def _create_widgets(self):
        """Creates the widgets for the class"""

    def _layout_widgets(self):
        """Layout of the widgets for the class"""


class WidgetConfig(NamedTuple):
    widget_type: Widget
    widget_kwargs: Mapping[str, Any]
    grid_kwargs: Mapping[str, Any]
    label: Optional[str] = None

GridConfig = Sequence[Sequence[WidgetConfig]]

class Skeleton(object):
    def __init__(self, master: Optional[Widget] = None, **kwargs):
        """
        Initialize the Toplevel
        """
        self.vars = {}
        self.named_widgets = {}
        super().__init__(master, **kwargs)
        self._create_all()

    @property
    @abc.abstractmethod
    def skeleton(self) -> GridConfig:
        pass

    @property
    def all_grid_kwargs(self):
        return {}

    def _create_all(self):
        config = self.skeleton
        for row_index, row in enumerate(config):
            for col_index, (widget_type, widget_kw, grid_kw, label) in enumerate(row):
                for key in (VARIABLE, TEXTVARIABLE):
                    try:
                        value = widget_kw[key]
                        if isinstance(value, tkinter.Variable):
                            widget_kw[key] = value(self)
                        elif isinstance(value, tuple):
                            var_type, initial_value = value
                            widget_kw[key] = var_type(self, value=initial_value)
                    except KeyError:
                        continue
                    if label:
                        self.vars[label] = widget_kw[key]
                    else:
                        raise ValueError("WidgetConfig with tkinter.variable must have label")

                w = widget_type(self, **widget_kw)
                w.grid(**{ROW: row_index, COLUMN: col_index, **grid_kw, **self.all_grid_kwargs})
                if label:
                    self.named_widgets[label] = w
