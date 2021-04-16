"""Creates some common widgets"""
from tkinter import Text, Canvas, Tk, Toplevel, Widget, X, VERTICAL, HORIZONTAL, LEFT, BOTTOM, RIGHT, Y, BOTH, END
from tkinter.constants import E, W
from tkinter.ttk import Frame, Button, Scrollbar

from .arrange import Autogrid
from typing import Any, Callable, List, Optional, Sequence, Tuple
from .mixins import Common
from .constants import EXPAND, FILL

__all__ = ['Main', 'Window', 'CommonFrame', 'ModalDialog']

class Main(Common, Tk):
    """
    A main application window
    """
    def __new__(cls) -> Any:
        cls.__doc__ = Frame.__doc__
        return super().__new__(cls)

class Window(Common, Toplevel):
    """
    A sub window that is not a dialog, unless you want it to be
    """

class CommonFrame(Common, Frame):
    """A nice Frame to use with common setup methods"""


class ModalDialog(Common, Toplevel):
    """
    A modal dialog that demands attention
    """
    def __init__(self, master: Widget = None, **kwargs):
        """
        Initializes the dialog, instantiate this directly if you don't care about return values
        """
        super().__init__(**kwargs)
        self.transient(master)
        self.withdraw()
        self.cancelled = False
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind('<Escape>', lambda _: self._on_cancel())

    def _on_cancel(self):
        """Default behavior is to set self.cancelled = True and destroy the dialog"""
        self.cancelled = True
        self.destroy()

    @classmethod
    def show(dialog_class, master: Widget, **kwargs) -> Any:
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



class Table(CommonFrame):
    sort_up = " ▲"
    sort_down = " ▼"
    col_pack_options = {
        FILL: X,
        EXPAND: True
    }

    def __init__(self, master, column_headers, data, **kwargs):
        """
        Creates a table
        """
        self.column_headers = column_headers
        self.data = data
        super().__init__(master, **kwargs)


    def _create_events(self):
        """Create events"""
        self.scrollable_canvas.bind(
            "<Configure>",
            lambda e: self.scrollable_canvas.configure(
                scrollregion=self.scrollable_canvas.bbox("all")
            )
        )

    def _create_vars(self):
        """Create widget variables"""

    def _create_widgets(self):
        """Create widgets"""
        self.table_frame = Frame(self)
        self.scrollable_canvas = Canvas(self.table_frame)
        self.x_scroll = Scrollbar(
            self, orient=HORIZONTAL, command=self.scrollable_canvas.xview)
        self.y_scroll = Scrollbar(
            self.table_frame, orient=VERTICAL, command=self.scrollable_canvas.yview)
        self.scrollable_canvas.configure(yscrollcommand=self.y_scroll.set,
                                         xscrollcommand=self.x_scroll.set)
        self.table = Frame(self.scrollable_canvas)
        for header_text in self.column_headers:
            widget = Frame(self.table)
            button = Button(widget, text=header_text)
            button.configure(
                command=lambda button=button: self._sort_command(button))

        self._create_data_widgets()

    def _create_data_widgets(self):
        for row in self.data:
            for x_index, col_frame in enumerate(self.table.children.values()):
                widget = Text(col_frame, width=20, height=1)
                widget.insert('1.0', row[x_index])

    def _layout_widgets(self):
        """Layout widgets"""
        for col_frame in self.table.children.values():
            for widget in col_frame.children.values():
                widget.pack(**self.col_pack_options)
            col_frame.pack(side=LEFT, fill=X, expand=True)
        self.x_scroll.pack(side=BOTTOM, fill=X)
        self.y_scroll.pack(side=RIGHT, fill=Y)
        self.scrollable_canvas.pack(expand=True, fill=BOTH)
        self.scrollable_canvas.create_window(
            (0, 0), window=self.table, anchor="nw")
        self.table_frame.pack(expand=True, fill=BOTH)

    def _sort_command(self, button):
        """Event that sorts by the element"""
        self.__reset_button_sort_text(except_button=button)
        if self.sort_up in button['text']:
            button.configure(text=button['text'][:-2] + self.sort_down)
        elif self.sort_down in button['text']:
            button.configure(text=button['text'][:-2] + self.sort_up)
        else:
            button.configure(text=button['text'] + self.sort_up)
        column_data = [
            tuple(enumerate(column.pack_slaves())) for column in self.table.children.values()
        ]
        column_to_sort_by = [col for col in column_data if col[0][1] == button][0]
        sort_kwargs = {
            'key': self.__sort_key
        }
        if self.sort_down in button['text']:
            sort_kwargs['reverse'] = True
        sorted_column = sorted(column_to_sort_by[1:], **sort_kwargs)
        self.__apply_sorting(sorted_column, column_data)

    @staticmethod
    def __sort_key(row):
        text = row[1].get(1.0, END)
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return text

    def __apply_sorting(self, sorted_column, column_data):
        for col in self.table.children.values():
            for widget in tuple(col.children.values())[1:]:
                widget.pack_forget()

        index_order = [col[0] for col in sorted_column]
        all_sorted_columns = []
        for col in [data[1:] for data in column_data]:
            all_sorted_columns.append([])
            for index in index_order:
                found = [t for t in col if t[0] == index][0]
                all_sorted_columns[-1].append(found)
                found[1].pack(**self.col_pack_options)
        self.scrollable_canvas.update_idletasks()

    def __reset_button_sort_text(self, except_button=None):
        for col_widget in self.table.children.values():
            button = tuple(col_widget.children.values())[0]
            if button is not except_button:
                button.configure(text=button['text'].replace(
                    self.sort_up, '').replace(self.sort_down, ''))

HeaderRow = Tuple[str, Callable[[Widget], Any]]

class NewTable(CommonFrame):
    sort_up = " ▲"
    sort_down = " ▼"
    def __init__(self, master: Widget, headers: Optional[Tuple[HeaderRow, ...]] = None, **kwargs):
        self.__headers = []
        self.__sort_keys = []
        self.__cell_widgets = []
        super().__init__(master=master, **kwargs)
        self.headers = headers

    @property
    def headers(self):
        return self.__headers

    @headers.deleter
    def headers(self):
        for button in self.headers:
            button.destroy()
        self.__headers = []
        self.__sort_keys = []

    @headers.setter
    def headers(self, headers: Tuple[HeaderRow,]):
        self.__headers = []
        self.__sort_keys = []
        for label, key in headers:
            self.__headers.append(self._create_header_button(label))
            self.__sort_keys.append(lambda widget=self.__headers[-1]: key(widget))

        self._layout_table_widgets()

    @property
    def cell_widgets(self) -> List[Widget]:
        return self.__cell_widgets

    @cell_widgets.setter
    def cell_widgets(self, widgets: Sequence[Widget]):
        self.__cell_widgets = list(widgets)
        self._layout_table_widgets()

    def sort_data(self, column_index: int, sort_by:Optional[Callable] = None):
        def chunked(sequence: Sequence, chunk_size: int) -> List[Sequence]:
            return [sequence[i: i + chunk_size] for i in range(0, len(sequence), chunk_size)]
        rows = chunked(self.cell_widgets, len(self.headers))
        def sort_key(row):
            widget = row[column_index]
            return self.__sort_keys[column_index](widget)
        if sort_by is not None:
            sort_key = sort_by
        new_rows = sorted(rows, key=sort_key)
        widgets = []
        for row in new_rows:
            widgets.extend(row)
        self.cell_widgets = widgets

    def _create_header_button(self, text) -> Button:
        button = Button(self.table, text=text)
        button.configure(command=lambda index=len(self.__headers): self.sort_data(index))
        return button

    def _create_widgets(self):
        self.table_frame = Frame(self)
        self.scrollable_canvas = Canvas(self.table_frame)
        self.x_scroll = Scrollbar(
            self, orient=HORIZONTAL, command=self.scrollable_canvas.xview)
        self.y_scroll = Scrollbar(
            self.table_frame, orient=VERTICAL, command=self.scrollable_canvas.yview)
        self.scrollable_canvas.configure(yscrollcommand=self.y_scroll.set,
                                         xscrollcommand=self.x_scroll.set)
        self.table = Frame(self.scrollable_canvas)

    def _layout_widgets(self):
        self.x_scroll.pack(side=BOTTOM, fill=X)
        self.y_scroll.pack(side=RIGHT, fill=Y)
        self.scrollable_canvas.pack(expand=True, fill=BOTH)
        self.scrollable_canvas.create_window(
            (0, 0), window=self.table, anchor="nw")
        self.table_frame.pack(expand=True, fill=BOTH)
        self._layout_table_widgets()

    def _layout_table_widgets(self):
        #Configure the grid to expand
        all_widgets = self.headers + self.cell_widgets
        for button, coords in Autogrid((len(self.headers), ), 1).zip_dicts(all_widgets):
            button.grid(**coords, sticky=E+W)
