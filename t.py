from tkinter.ttk import Label, Entry
from tkinter import E, W, StringVar, Tk, Widget
from typing import Any, Mapping, NamedTuple, Optional, Sequence, Type
from tklife.constants import PADX, PADY, STICKY, TEXT, TEXTVARIABLE
from tklife.mixins import Common, GridConfig, Skeleton, WidgetConfig
from tklife.widgets import Main



class App(Skeleton, Tk):
    def __init__(self, master: Optional[Widget] = None, **kwargs):
        self.inj = "world"
        super().__init__(master, **kwargs)
    @property
    def skeleton(self) -> GridConfig:
        return (
            [
                WidgetConfig(Label, {TEXT: 'Hello:'}, {STICKY: E}),
                WidgetConfig(Entry, {TEXTVARIABLE: (StringVar, self.inj)}, {STICKY: W}, 'test_entry')
            ],
        )

    @property
    def all_grid_kwargs(self):
        return {
            PADX: 6,
            PADY: 6,
        }

    def test_var(self):
        print(self.vars['test_entry'].get())


m = App()
#m.test_var()

m.mainloop()
