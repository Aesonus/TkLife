"""Creates some common widgets"""
from tkinter import Event, Grid, Listbox, Misc, Pack, Place, StringVar, Text, Canvas, Tk, Toplevel, Variable, Widget, X, VERTICAL, HORIZONTAL, LEFT, BOTTOM, RIGHT, Y, BOTH, END
from tkinter.constants import ACTIVE, E, GROOVE, INSERT, RIDGE, SINGLE, W
from tkinter.ttk import Entry, Frame, Button, Scrollbar

from .arrange import Autogrid
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple
from .mixins import Common
from .constants import EXPAND, FILL

__all__ = ['Main', 'Window', 'CommonFrame', 'ModalDialog', 'ScrolledListbox', 'AutoSearchCombobox']


class ScrolledListbox(Listbox):
    """
    A scrolled listbox, based on tkinter.scrolledtext.ScrolledText

    Arguments:
        Listbox {[type]} -- [description]
    """
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Listbox.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Listbox
        # methods -- hack!
        text_meths = vars(Listbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class AutoSearchCombobox(Entry):
    def __init__(self, master: Widget, values: Optional[Iterable[str]] = None, height: Optional[int]=None, **kwargs):
        super().__init__(master, **kwargs)
        self._tl = Toplevel(self, takefocus=False, relief=GROOVE, borderwidth=1)
        self._tl.wm_overrideredirect(True)
        self._lb = ScrolledListbox(self._tl, width=kwargs.pop('width', None), height=height, selectmode=SINGLE)
        self.values = values
        self._lb.pack(expand=True, fill=BOTH)
        self._hide_tl()
        self.winfo_toplevel().focus_set()
        self.bind('<KeyRelease>', self._handle_keyrelease)
        self.bind('<FocusOut>', self._handle_focusout)
        self.winfo_toplevel().bind('<Configure>', self._handle_configure)
        self.bind('<KeyPress>', self._handle_keypress)

    @property
    def values(self):
        """
        Gets the values
        """
        try:
            return self.__values
        except AttributeError:
            self.values = ()
            return self.values

    @values.setter
    def values(self, values: Optional[Iterable]):
        """
        Sorts and sets the values
        """
        self.__values = tuple(sorted(values)) if values is not None else tuple()
        self._lb.insert(END, *self.values)
        self._lb.selection_clear(0, END)
        self._lb.selection_set(0)
        self._lb.activate(0)

    @property
    def _lb_current_selection(self) -> str:
        """
        Returns the current selection in the listbox
        """
        try:
            sel = self._lb.curselection()[0]
        except IndexError:
            return None
        return self._lb.get(sel)

    def _set_lb_index(self, index):
        self._lb.selection_clear(0, END)
        self._lb.selection_set(index)
        self._lb.activate(index)
        self._lb.see(index)

    @property
    def text_after_cursor(self) -> str:
        """
        Gets the entry text after the cursor
        """
        contents = self.get()
        return contents[self.index(INSERT):]

    @property
    def dropdown_is_visible(self):
        return self._tl.winfo_ismapped()

    def _handle_keypress(self, event: Event):
        if 'Left' in event.keysym:
            if self.dropdown_is_visible:
                self._hide_tl()
                return 'break'
            else:
                return
        elif (('Right' in event.keysym and self.text_after_cursor == '') or event.keysym in ['Return', 'Tab']) and self.dropdown_is_visible:
            #Completion and block next action
            self.delete(0, END)
            self.insert(0, self._lb_current_selection)
            self._hide_tl()
            return 'break'

    def _handle_keyrelease(self, event: Event):
        if 'Up' in event.keysym and self.dropdown_is_visible:
            previous_index = self._lb.index(ACTIVE)
            new_index = max(0, self._lb.index(ACTIVE) - 1)
            self._set_lb_index(new_index)
            if previous_index == new_index:
                self._hide_tl()
            return
        if 'Down' in event.keysym:
            if self.dropdown_is_visible:
                current_index = self._lb.index(ACTIVE)
                new_index = min(current_index + 1, self._lb.size() - 1)
                self._set_lb_index(new_index)
                return 'break'
            if not self.dropdown_is_visible and self._lb.size() > 0:
                self._show_tl()

        if len(event.keysym) == 1 or ('Right' in event.keysym and self.text_after_cursor == '') or event.keysym in ['BackSpace']:
            if self.get() != '':
                new_values = [value for value in self.values if value.lower(
                ).startswith(self.get().lower())]
            else:
                new_values = self.values
            self._lb.delete(0, END)
            self._lb.insert(END, *new_values)
            self._set_lb_index(0)
            if self._lb.size() < 1 or self.get() == self._lb_current_selection:
                self._hide_tl()
            else:
                self._show_tl()

    def _handle_focusout(self, event: Event):
        def cf():
            if self.focus_get() != self._tl and self.focus_get() != self._lb:
                self._hide_tl()
            else:
                self.focus_set()
        self.after(1, cf)

    def _handle_configure(self, event: Event):
        if self._tl.winfo_ismapped():
            self._update_tl_pos()

    def _show_tl(self) -> None:
        if self._tl.winfo_ismapped() == False:
            self._update_tl_pos()
            self._tl.deiconify()
            self._tl.attributes("-topmost", True)

    def _update_tl_pos(self) -> None:
        self._tl.geometry('+{}+{}'.format(self.winfo_rootx(),
                          self.winfo_rooty() + self.winfo_height() - 1))

    def _hide_tl(self) -> None:
        self._tl.withdraw()


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
        column_to_sort_by = [
            col for col in column_data if col[0][1] == button][0]
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
    def headers(self, headers: Tuple[HeaderRow, ]):
        self.__headers = []
        self.__sort_keys = []
        for label, key in headers:
            self.__headers.append(self._create_header_button(label))
            self.__sort_keys.append(
                lambda widget=self.__headers[-1]: key(widget))

        self._layout_table_widgets()

    @property
    def cell_widgets(self) -> List[Widget]:
        return self.__cell_widgets

    @cell_widgets.setter
    def cell_widgets(self, widgets: Sequence[Widget]):
        self.__cell_widgets = list(widgets)
        self._layout_table_widgets()

    def sort_data(self, column_index: int, sort_by: Optional[Callable] = None):
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
        button.configure(command=lambda index=len(
            self.__headers): self.sort_data(index))
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
        # Configure the grid to expand
        all_widgets = self.headers + self.cell_widgets
        for button, coords in Autogrid((len(self.headers), ), 1).zip_dicts(all_widgets):
            button.grid(**coords, sticky=E+W)
