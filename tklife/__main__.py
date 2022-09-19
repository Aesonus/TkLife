"""Shows an example of a skeleton window"""

from functools import cached_property, partial
from random import random
from tkinter import E, EW, NSEW, Misc, StringVar, Tk, W, ttk
import tkinter
from tkinter.messagebox import showinfo
from typing import Optional

from tklife.constants import COLUMNSPAN, COMMAND, PADX, PADY, STICKY, TEXT, TEXTVARIABLE, VALUES
from tklife.controller import ControllerABC
from tklife.event import TkEvent, TkEventMod
from tklife.skel import Menu, MenuMixin, SkeletonMixin, SkelWidget, cls_as_skel
from tklife.widgets import AutoSearchCombobox, ModalDialog, ScrolledFrame


class ExampleModal(ModalDialog):
    def __init__(self, master, **kwargs):
        super().__init__(master, global_grid_args={PADX: 3, PADY: 3}, **kwargs)

    def __after_init__(self):
        self.title("Example Modal")

    @property
    def template(self):
        return (
            [
                SkelWidget(ttk.Label).init(text="Enter Data:"),
                SkelWidget(AutoSearchCombobox, {TEXTVARIABLE: StringVar, VALUES: ['test', 'value']}, {}, 'entry')],
            [
                SkelWidget(ttk.Button, {TEXT: "Okay",
                           COMMAND: self.destroy}).grid(sticky=W),
                SkelWidget(ttk.Button, {TEXT: "Cancel",
                           COMMAND: self.cancel}, {STICKY: E})
            ],
        )

    def set_return_values(self):
        self.return_value = self.created['entry'][TEXTVARIABLE].get()


class AppendExampleScrolledFrame(SkeletonMixin, ScrolledFrame):
    @property
    def template(self):
        return [[]]


class ExampleController(ControllerABC):
    def button_a_command(self, *__):
        showinfo(title="Information",
                 message=self.entry_a['textvariable'].get(), parent=self.view)

    def button_b_command(self, *__):
        showinfo(title="Information",
                 message=self.entry_b['textvariable'].get(), parent=self.view)

    def button_c_command(self, *__):
        d = ExampleModal.show(self.view)
        showinfo(title="Information", message=f"{d}", parent=self.view)

    def add_row_command(self, *__):
        add_to = self.appendable_frame.widget
        id = f"{random():.8f}"
        new_row = [
            SkelWidget(ttk.Label, {TEXT: f"Appended Row {id}"}, {STICKY: EW}),
            SkelWidget(ttk.Entry, {}, {STICKY: EW}),
            SkelWidget(ttk.Button, {TEXT: 'x', COMMAND: self.get_delete_this_row_command(id)}, {STICKY: EW}, id),
        ]
        add_to.append_row(new_row)

    def get_delete_this_row_command(self, last_label):
        def delete_this_row():
            delete_from = self.appendable_frame.widget
            delete_from.destroy_row(delete_from.find_row_of(last_label))

        return delete_this_row

    def delete_last_row_command(self, *__):
        delete_from = self.appendable_frame.widget
        delete_from.destroy_row(int(len(delete_from.widget_cache) / 3) - 1)

class ExampleView(SkeletonMixin, MenuMixin, Tk):
    def __init__(self, master: 'Optional[Misc]' = None, example_controller: Optional[ExampleController] = None, **kwargs) -> None:
        self.controller: ExampleController
        super().__init__(master, example_controller,
                         global_grid_args={PADX: 3, PADY: 3}, **kwargs)

    def __after_init__(self):
        self.title("TkLife Example")

    def create_events(self):
        # Standard event
        TkEvent.ESCAPE.bind(self, lambda __: self.destroy())

        # Composite event
        (TkEventMod.CONTROL + TkEvent.RETURN).bind(self, lambda __: self.destroy())

    @property
    def template(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        return (
            [
                SkelWidget(ttk.Label, {TEXT: "Label A:"}, {}),
                SkelWidget(ttk.Entry, {TEXTVARIABLE: StringVar}, {
                           STICKY: E + W}, 'entry_a'),
                SkelWidget(ttk.Button, {
                           TEXT: "Print contents", COMMAND: self.controller.button_a_command}, {})
            ],
            [
                SkelWidget(ttk.Label, {TEXT: "Label B:"}, {}),
                SkelWidget(AutoSearchCombobox, {TEXTVARIABLE: StringVar(value="Default value"), "values": ["Default value", "other", "a thing to test"]}, {
                           STICKY: E + W}, 'entry_b'),
                SkelWidget(ttk.Button, {
                           TEXT: "Print contents", COMMAND: self.controller.button_b_command}, {})
            ],
            [None, SkelWidget(ttk.Button, {
                              TEXT: "Dialog", COMMAND: self.controller.button_c_command}, {}), None],
            [SkelWidget(cls_as_skel(ScrolledFrame), {}, {COLUMNSPAN: 3, STICKY: NSEW}, 'appendable_frame')],
            [SkelWidget(ttk.Button, {TEXT: "Add Row", COMMAND: self.controller.add_row_command}, {}), None, SkelWidget(ttk.Button, {TEXT: "Delete Row", COMMAND: self.controller.delete_last_row_command}, {})]
        )


    @property
    def menu_template(self):
        return {
            Menu.cascade(label="File", underline=0): {
                Menu.command(label="Show Dialog", underline=0): self.controller.button_c_command,
                Menu.add(): 'separator',
                Menu.command(label="Exit", underline=1): self.destroy
            }
        }


if __name__ == "__main__":
    example_view = ExampleView(None, None)  # None arguments are added for illustration
    example_view.controller = ExampleController()
    example_view.mainloop()
