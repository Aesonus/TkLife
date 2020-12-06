"""Creates some common widgets"""
from tkinter import Text, Canvas, X, VERTICAL, HORIZONTAL, LEFT, BOTTOM, RIGHT, Y, BOTH, END
from tkinter.ttk import Frame, Button, Scrollbar
from tklife import CommonFrame


class Table(CommonFrame):
    sort_up = " ▲"
    sort_down = " ▼"
    col_pack_options = {
        'fill': X,
        'expand': True
    }

    def __init__(self, column_headers, data, **kwargs):
        """
        Creates a table
        """
        self.column_headers = column_headers
        self.data = data
        super().__init__(**kwargs)

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