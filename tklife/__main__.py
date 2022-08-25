"""Shows an example of a skeleton window"""

from tkinter import E, NSEW, Misc, StringVar, Tk, W, ttk
from tkinter.messagebox import showinfo
from typing import Optional

from tklife.constants import COLUMNSPAN, COMMAND, PADX, PADY, STICKY, TEXT, TEXTVARIABLE, VALUES
from tklife.controller import ControllerABC
from tklife.event import TkEvent, TkEventMod
from tklife.skel import SkeletonMixin, SkelWidget
from tklife.widgets import AutoSearchCombobox, ModalDialog, ScrolledFrame


class ExampleModal(ModalDialog):
    def __init__(self, master, **kwargs):
        super().__init__(master, global_grid_args={PADX: 3, PADY: 3}, **kwargs)

    @property
    def template(self):
        return (
            [
                SkelWidget(ttk.Label, {TEXT: "Enter data:"}, {}),
                SkelWidget(AutoSearchCombobox, {TEXTVARIABLE: StringVar, VALUES: ['test', 'value']}, {}, 'entry')],
            [
                SkelWidget(ttk.Button, {TEXT: "Okay",
                           COMMAND: self.destroy}, {STICKY: W}),
                SkelWidget(ttk.Button, {TEXT: "Cancel",
                           COMMAND: self.cancel}, {STICKY: E})
            ],
        )

    def set_return_values(self):
        self.return_value = self.created['entry'][TEXTVARIABLE].get()


class ExampleController(ControllerABC):
    def button_a_command(self, *__):
        showinfo(title="Information", message=self.view.created['entry_a']['textvariable'].get(), parent=self.view)

    def button_b_command(self, *__):
        showinfo(title="Information", message=self.view.created['entry_b']['textvariable'].get(), parent=self.view)

    def button_c_command(self, *__):
        d = ExampleModal.show(self.view)
        showinfo(title="Information", message=f"{d}", parent=self.view)


class ExampleView(SkeletonMixin, Tk):
    def __init__(self, master: 'Optional[Misc]'=None, example_controller: Optional[ExampleController]=None, **kwargs) -> None:
        self.controller: ExampleController
        super().__init__(master, example_controller,
                         global_grid_args={PADX: 3, PADY: 3}, **kwargs)
        self.title("TkLife Example")
        self.created['entry_b']['textvariable'].set("Default value")

    def create_events(self):
        # Standard event
        TkEvent.ESCAPE.bind(self, lambda __: self.destroy())

        # Composite event
        (TkEventMod.CONTROL + TkEvent.RETURN).bind(self, lambda __: self.destroy())

    @property
    def template(self):
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
                SkelWidget(ttk.Entry, {TEXTVARIABLE: StringVar}, {
                           STICKY: E + W}, 'entry_b'),
                SkelWidget(ttk.Button, {
                           TEXT: "Print contents", COMMAND: self.controller.button_b_command}, {})
            ],
            [None, SkelWidget(ttk.Button, {
                              TEXT: "Dialog", COMMAND: self.controller.button_c_command}, {}), None],
            [SkelWidget(ScrolledFrame, {}, {COLUMNSPAN: 3, STICKY: NSEW})]
        )


if __name__ == "__main__":
    example_view = ExampleView(None, None)
    example_view.controller = ExampleController()
    example_view.mainloop()
