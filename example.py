from tkinter.constants import COMMAND, E, N, S, W
from tklife.widgets import AutoSearchCombobox
from tklife.event import EventsEnum
from tklife.skel.shortcuts import LabelledWidget
from typing import Dict, Mapping, Type
from tklife.skel import tk_vars, widgets, layout, layout_cfg, Skeleton
from tkinter import StringVar, Tk
from tkinter.ttk import Label, Entry, Button
from tklife.constants import *
import logging

logging.basicConfig(level=logging.DEBUG)

class Events(EventsEnum):
    TEST_BUTTON = '<<TestButton>>'

class Main(Skeleton, Tk):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        Events.TEST_BUTTON.bind(self, self.test_handler)

    def test_handler(self, event):
        print(event.widget)

    def skeleton_configure(self):
        return super().skeleton_configure(grid_kw={PADX: 6, PADY: 6}, debug=True)

    def skeleton(self, vars) -> Dict:
        return {
            tk_vars: (
                ('entry_vars', [
                    ('line1', StringVar, {'value': 'Line 1'}),
                    ('line2', StringVar, {'value': ''}),
                ]),
            ),
            widgets: [
                [(Label, {TEXT: 'Label 1:'}), (Entry, {TEXTVARIABLE: vars.entry_vars.line1})],
                [*LabelledWidget('Label 2:', AutoSearchCombobox, {
                    TEXTVARIABLE: vars.entry_vars.line2,
                    VALUES: ['Test', 'This', 'Autocomplete', 'Awesomeness']
                })],
                [(Button, {TEXT: 'Button', COMMAND: Events.TEST_BUTTON})]
            ],
            layout: [
                [{STICKY: E}, {STICKY: E+W}],
                [{STICKY: E}, {STICKY: E+W}],
                [{COLUMNSPAN: 2, STICKY: N+E+S+W}],
            ],
            layout_cfg: (
                [{'weight': 1}, {'weight': 5},], # col config
                [{'weight': 1}, {'weight': 1}, {'weight': 2},], # row config
            ),
        }

if __name__ == "__main__":
    m = Main()
    m.mainloop()
