from tkinter.constants import E, N, S, W
from tklife.skel.main import tk_vars
from tklife.skel.shortcuts import LabelledWidget
from typing import Dict, Mapping, Type
from tklife.skel import widgets, layout, layout_cfg, TkVars, Skeleton
from tkinter import StringVar, Tk
from tkinter.ttk import Label, Entry, Button
from tklife.constants import *
import logging

logging.basicConfig(level=logging.DEBUG)

class ExVars(TkVars):
    store_as = 'mapping'
    line1_entry1_var = StringVar
    line1_entry2_var = StringVar

class Main(Skeleton, Tk):
    def skeleton_configure(self):
        return super().skeleton_configure(grid_kw={PADX: 6, PADY: 6}, debug=True)

    def skeleton(self, vars) -> Dict:
        return {
            tk_vars: (
                ('entry_vars', [
                    ('line1', StringVar, {'value': 'Line 1'}),
                    ('line2', StringVar, {'value': 'Line 2'}),
                ]),
            ),
            widgets: [
                [(Label, {TEXT: 'Label 1:'}), (Entry, {TEXTVARIABLE: vars.entry_vars.line1})],
                [*LabelledWidget('Label 2:', Entry, {TEXTVARIABLE: vars.entry_vars.line2})],
                [(Button, {TEXT: 'Button'})]
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
