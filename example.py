from tkinter.constants import COMMAND, E, N, NW, S, SE, W
from tklife.widgets import AutoSearchCombobox, ScrolledFrame
from tklife.event import EventsEnum
from tklife.skel.shortcuts import LabelledWidget
from typing import Dict, Mapping, Type
from tklife.skel import tk_vars, widgets, layout, layout_cfg, Skeleton
from tkinter import StringVar, Tk
from tkinter.ttk import Frame, Label, Entry, Button
from tklife.constants import *
import logging

logging.basicConfig(level=logging.DEBUG)

class Events(EventsEnum):
    TEST_BUTTON = '<<TestButton>>'

class Main(Skeleton, Tk):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        Events.TEST_BUTTON.bind(self, self.test_handler)
        for i in range(50):
            nl = Label(self.scrolled_frame, text='Label {}'.format(i))
            e = Entry(self.scrolled_frame)
            nl.pack()
            e.pack()

    def test_handler(self, event):
        print(event.widget)

    @property
    def scrolled_frame(self) -> 'ScrolledFrame':
        return self.widget_grid[0, 2]

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
                    VALUES: ['Test', 'This', 'Saws', 'Stew', 'Autocomplete', 'Awesomeness', 'Also', 'Arrows'],
                    HEIGHT: '4'
                })],
                [(ScrolledFrame, {})],
                [(Button, {TEXT: 'Button', COMMAND: Events.TEST_BUTTON})],
            ],
            layout: [
                [{STICKY: E}, {STICKY: E+W}],
                [{STICKY: E}, {STICKY: E+W}],
                [{STICKY: NW + SE, COLUMNSPAN: 2}],
                [{COLUMNSPAN: 2, STICKY: N+E+S+W}],
            ],
            layout_cfg: (
                [{WEIGHT: 1}, {WEIGHT: 5},], # col config
                [{WEIGHT: 1}, {WEIGHT: 1}, {WEIGHT: 2}, {WEIGHT: 1}], # row config
            ),
        }

if __name__ == "__main__":
    m = Main()
    m.mainloop()
