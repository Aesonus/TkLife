"""Shows a sample tklife application"""

from tkinter import StringVar, Widget
from tkinter.constants import END
from tkinter.ttk import Button, Entry, Label
from .widgets import NewTable
from .constants import COLUMNSPAN, PADX, PADY
from .mixins import generate_event_for
from . import Main
from .arrange import Autogrid

PADDING = {
    PADX: 6,
    PADY: 6
}

@generate_event_for
def show_dialog_for(widget):
    """Example of event generation decorator for a function"""
    return '<<ShowDialog>>'

class App(Main):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title('Sample Application')

    def _create_vars(self):
        self.entry_var = StringVar(value="Test Value")

    def _create_widgets(self):
        Label(self, text='Example Entry:')
        Entry(self, textvariable=self.entry_var)
        button = Button(self, text='Show Dialog')
        button.configure(command=self.show_dialog_for(button))
        button = Button(self, text='Show For This Button',)
        button.configure(command=show_dialog_for(button))
        def get_widget_text(widget: Entry):
            return widget.get()
        table = NewTable(self, headers=(('Test', get_widget_text), ('The', get_widget_text), ('Table', get_widget_text), ))
        widgets_ = []
        for row in range(4):
            for col in range(3):
                widgets_.append(Entry(table.table))
                widgets_[-1].insert(0, 'Row {}; Col {}'.format(row, col))
        table.cell_widgets = widgets_

    def _layout_widgets(self):
        for widget, grid_coords in Autogrid((2, 1), 1).zip_dicts(self.winfo_children(), grid_kwargs_list=({}, {},), fill_grid_kwargs={COLUMNSPAN: 2}):
            widget.grid(**grid_coords, **PADDING)

    def _create_events(self):
        self.bind('<<ShowDialog>>', lambda e: print(e.widget))

    @generate_event_for
    def show_dialog_for(self, widget):
        """Example of event generation decorator for an instance method"""
        return '<<ShowDialog>>'


App().mainloop()