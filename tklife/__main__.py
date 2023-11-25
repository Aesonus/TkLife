"""Shows an example of a skeleton window."""
from __future__ import annotations

import tkinter as tk
from random import random
from tkinter import EW, NSEW, E, Misc, StringVar, Tk, Toplevel, W, ttk
from tkinter.messagebox import showinfo
from typing import Any, Iterable, Optional

from tklife import SkeletonMixin, SkelEventDef, SkelWidget, style
from tklife.constants import (
    COLUMNSPAN,
    COMMAND,
    PADX,
    PADY,
    STICKY,
    STYLE,
    TEXT,
    TEXTVARIABLE,
    VALUES,
    WEIGHT,
)
from tklife.controller import ControllerABC
from tklife.dynamic import AppendableMixin
from tklife.event import TkEvent, TkEventMod
from tklife.menu import Menu, MenuMixin
from tklife.widgets import AutoSearchCombobox, ModalDialog, ScrolledFrame

# pylint: disable=all


class GreenLabelStyle(style.TLabel):
    configure = {"foreground": "green"}


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
                SkelWidget(
                    AutoSearchCombobox,
                    {TEXTVARIABLE: StringVar, VALUES: ["test", "value"]},
                    {},
                    label="entry",
                ),
            ],
            [
                SkelWidget(ttk.Button, {TEXT: "Okay", COMMAND: self.destroy}).grid(
                    sticky=W
                ),
                SkelWidget(
                    ttk.Button, {TEXT: "Cancel", COMMAND: self.cancel}, {STICKY: E}
                ),
            ],
        )

    def set_return_values(self):
        self.return_value = self.created["entry"][TEXTVARIABLE].get()


class AppendExampleScrolledFrame(SkeletonMixin, AppendableMixin, ScrolledFrame):
    pass


class ExampleController(ControllerABC):
    view: ExampleView

    def button_a_command(self, *__):
        showinfo(
            title="Information",
            message=self.entry_a["textvariable"].get(),
            parent=self.view,
        )

    def button_b_command(self, *__):
        showinfo(
            title="Information",
            message=self.entry_b["textvariable"].get(),
            parent=self.view,
        )

    def button_c_command(self, *__):
        d = ExampleModal.show(self.view)
        showinfo(title="Information", message=f"{d}", parent=self.view)

    def add_row_command(self, *__):
        add_to = self.appendable_frame.widget
        id = f"{random():.8f}"
        new_row = [
            SkelWidget(ttk.Label, {TEXT: f"Appended Row {id}"}, {STICKY: EW}),
            SkelWidget(ttk.Entry, {}, {STICKY: EW}),
            SkelWidget(
                ttk.Button,
                {TEXT: "x", COMMAND: self.get_delete_this_row_command(id)},
                {STICKY: EW},
                label=id,
            ),
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


class ExampleView(SkeletonMixin, MenuMixin, Toplevel):
    def __init__(
        self,
        master: Optional[Misc] = None,
        example_controller: Optional[ExampleController] = None,
        **kwargs,
    ) -> None:
        self.controller: ExampleController
        super().__init__(
            master, example_controller, global_grid_args={PADX: 3, PADY: 3}, **kwargs
        )

    def __after_init__(self):
        self.title("TkLife Example")

    @property
    def events(self) -> Iterable[SkelEventDef]:
        return [
            {
                "event": TkEvent.ESCAPE,
                "action": lambda __: self.destroy(),
                "bind_method": "bind",
            },
            {
                "event": TkEventMod.CONTROL + TkEvent.RETURN,
                "action": lambda __: self.destroy(),
                "bind_method": "bind",
            },
            {
                "event": TkEvent.MAP,
                "action": lambda event: print("Mapped", event.widget),
                "bind_method": "bind",
                "widget": self.created["entry_a"].widget,
            },
        ]

    @property
    def grid_config(self) -> tuple[Iterable[dict[str, Any]], Iterable[dict[str, Any]]]:
        return [
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
        ], [
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
        ]

    @property
    def template(self):
        return (
            [
                SkelWidget(ttk.Label).init(text="Label A:"),
                SkelWidget(ttk.Entry)
                .init(textvariable=tk.StringVar)
                .grid(sticky=tk.EW)
                .set_label("entry_a"),
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Print contents", COMMAND: self.controller.button_a_command},
                    {},
                ),
            ],
            [
                SkelWidget(
                    ttk.Label, {TEXT: "Label B:", STYLE: GreenLabelStyle.ttk_style}, {}
                ),
                SkelWidget(
                    AutoSearchCombobox,
                    {
                        TEXTVARIABLE: StringVar(value="Default value"),
                        "values": ["Default value", "other", "a thing to test"],
                    },
                    {STICKY: E + W},
                    label="entry_b",
                ),
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Print contents", COMMAND: self.controller.button_b_command},
                    {},
                ),
            ],
            [
                None,
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Dialog", COMMAND: self.controller.button_c_command},
                    {},
                ),
                None,
            ],
            [
                SkelWidget(
                    AppendExampleScrolledFrame,
                    {},
                    {COLUMNSPAN: 3, STICKY: NSEW},
                    label="appendable_frame",
                )
            ],
            [
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Add Row", COMMAND: self.controller.add_row_command},
                    {},
                ),
                None,
                SkelWidget(
                    ttk.Button,
                    {
                        TEXT: "Delete Row",
                        COMMAND: self.controller.delete_last_row_command,
                    },
                    {},
                ),
            ],
        )

    @property
    def menu_template(self):
        return {
            Menu.cascade(label="File", underline=0): {
                Menu.command(
                    label="Show Dialog", underline=0
                ): self.controller.button_c_command,
                Menu.add(): "separator",
                Menu.command(label="Exit", underline=1): self.destroy,
            }
        }


if __name__ == "__main__":
    master = Tk()
    style.BaseStyle.define_all()
    example_view = ExampleView(master)
    example_view.controller = ExampleController()
    master.withdraw()
    example_view.wait_window()
    master.quit()
