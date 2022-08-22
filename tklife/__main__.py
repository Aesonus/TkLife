"""Shows an example of a skeleton window"""

from tkinter import BOTH, E, Misc, StringVar, Tk, W, ttk

from tklife.constants import COMMAND, STICKY, TEXT, TEXTVARIABLE
from tklife.controller import ControllerABC
from tklife.skel import SkeletonMixin, SkelWidget


class ExampleController(ControllerABC):
    def button_a_command(self, *__):
        print(self.view.created['entry_a']['textvariable'].get())

    def button_b_command(self, *__):
        print(self.view.created['entry_b']['textvariable'].get())


class ExampleView(SkeletonMixin, ttk.Frame):
    def __init__(self, master: 'Misc', controller: ExampleController, **kwargs) -> None:
        self.controller: ExampleController
        super().__init__(master, controller, **kwargs)
        self.created['entry_b']['textvariable'].set("Default value")

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
        )


if __name__ == "__main__":
    main = Tk()
    main.title("Skeleton Example")
    example_view = ExampleView(main, ExampleController())
    example_view.pack(fill=BOTH)
    main.mainloop()
