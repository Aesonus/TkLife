from tkinter import StringVar, LEFT, END
from tkinter.ttk import Label, Entry, Button, Frame
from tkinter.messagebox import showwarning
from tklife import ModalDialog

class BaseSimpleDialog(ModalDialog):
    """
    Defines a constructor for the simple dialogs
    """
    def __init__(self, **kwargs):
        """
        Initializes the modal
        """
        title_is = kwargs.pop('title')
        self.prompt = kwargs.pop('prompt')
        super().__init__(**kwargs)

        self.title(title_is)

    def _create_vars(self):
        """
        Creates the entry var
        """
        self.input_var = StringVar()

    def _create_widgets(self):
        """
        Creates a prompt with an entry and an ok and cancel button
        """
        self.button_box = Frame(self)
        self._button_box()
        self.entry_label = Label(self, text=self.prompt)
        self.entry = Entry(self, textvariable=self.input_var)
    
    def _button_box(self):
        """Creates buttons for the modal, override to use your own"""
        self.ok_button = Button(self.button_box, text="OK", command=self._on_okay)
        self.cancel_button = Button(self.button_box, text="Cancel", command=self._on_cancel)

    def _layout_widgets(self):
        """
        Layout of modal widgets
        """
        self.entry_label.pack(expand=True, pady=6)
        self.entry.pack(expand=True)
        self.ok_button.pack(expand=True, side=LEFT, padx=6)
        self.cancel_button.pack(expand=True, side=LEFT, padx=6)
        self.button_box.pack(expand=True, pady=12)
        self.entry.focus_set()

    def _on_okay(self):
        """
        Destroys the dialog
        """
        self.cancelled = False
        self.destroy()

    def _create_events(self):
        """
        Creates the events for this dialog
        """
        self.bind('<Return>', func=lambda event: self._on_okay())
        self.bind('<Escape>', func=lambda event: self._on_cancel())

    def select_all_of(self, widget):
        widget.select_range(0, END)

    def invalid_entry(self, predicate):
        """
        Shows the warning when the entry is invalid and selects all of the entry text
        """
        showwarning('Illegal Value', 'Please enter %s' % predicate, parent=self)
        self.entry.focus_set()
        self.select_all_of(self.entry)

class AskString(BaseSimpleDialog):
    """
    Displays a dialog asking for a string value
    """
    
    def _return_values(self):
        """
        Returns the input string value
        """
        return self.input_var.get()

class AskInteger(BaseSimpleDialog):
    """
    Displays a dialog asking for a string value
    """
    def _on_okay(self):
        """
        Validates input before destroying window
        """
        try:
            int(self.input_var.get())
        except ValueError:
            self.invalid_entry('an integer')
        else:
            super()._on_okay()

    def _return_values(self):
        """
        Returns the input int value
        """
        return int(self.input_var.get())

class AskFloat(BaseSimpleDialog):
    """
    Displays a dialog asking for a string value
    """
    def _on_okay(self):
        """
        Validates input before destroying window
        """
        try:
            float(self.input_var.get())
        except ValueError:
            self.invalid_entry('a number')
        else:
            super()._on_okay()

    def _return_values(self):
        """
        Returns the input string value
        """
        return float(self.input_var.get())