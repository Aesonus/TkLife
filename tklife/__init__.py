from tkinter import Toplevel, Frame, Button, Tk

class Common:
    """
    Defines common abstract methods for Toplevel and Tk
    """
    def __init__(self, **kwargs):
        """
        Initialize the Toplevel
        """
        try:
            master = kwargs.pop('master')
        except KeyError:
            master = None
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

class ModalDialog(Common, Toplevel):
    """
    A modal dialog that demands attention
    """
    def __init__(self, **kwargs):
        """
        Initializes the dialog, instantiate this directly if you don't care about return values

        kwargs

        master - The master of this dialog
        """
        super().__init__(**kwargs)
        self.transient(kwargs['master'])
        self.withdraw()
        self.cancelled = False
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind('<Escape>', lambda _: self._on_cancel())

    def _on_cancel(self):
        """
        Default behavior is to set self.cancelled = True and destroy the dialog
        """
        self.cancelled = True
        self.destroy()

    @classmethod
    def show(dialog_class, master, **kwargs):
        """Shows this dialog and waits for finish"""
        new = dialog_class(master=master, **kwargs)
        new.deiconify()
        new.grab_set()
        new.focus_set()
        new.wait_window()
        if (new.cancelled):
            return None
        return new._return_values()

    def _return_values(self):
        """Returns the result of this dialog, if any"""
        return None

class Main(Common, Tk):
    """
    A main application window
    """

class Window(Common, Toplevel):
    """
    A sub window that is not a dialog, unless you want it to be
    """

class CommonFrame(Common, Frame):
    """A nice Frame to use with common setup methods"""
