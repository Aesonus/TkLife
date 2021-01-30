from tkinter import Widget

__all__ = ['Common']

def generate_event(function):
    def decorated(master: Widget = None):
        master.event_generate(function(master))
    return decorated

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


class Common:
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
