from tkinter import StringVar, Tk
from tkinter.constants import E, N, S, W
from tkinter.ttk import Button, Entry, Label
from tklife.skel.shortcuts.main import LabelledWidget
from tklife.constants import COLUMNSPAN, STICKY, TEXT, TEXTVARIABLE
from tklife.skel.main import Skeleton, TkVars, layout, layout_cfg, widgets
import pytest

@pytest.fixture
def MockVarsMapDeep():
    class ExVars(TkVars):
        store_as = 'mapping'
        line1_entry1_var = StringVar
        line1_entry2_var = StringVar
    return ExVars


@pytest.fixture
def MockMain(MockVarsMapDeep):
    class Main(Skeleton, Tk):
        def skeleton_configure(self):
            super().skeleton_configure(vars=MockVarsMapDeep)

        def skeleton(self, vars):
            return {
                widgets: [
                    [(Label, {TEXT: 'Label 1:'}), (Entry, {TEXTVARIABLE: vars.line1_entry1_var})],
                    [*LabelledWidget('Label 2:', Entry, {TEXTVARIABLE: vars.line1_entry2_var})],
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
                )}
    return Main

def test_var_mappings(MockMain, MockVarsMapDeep):
    test_obj = MockMain()
    assert test_obj.tkvars == {
        'line1': {
            'entry1': MockVarsMapDeep.line1_entry1_var,
            'entry2': MockVarsMapDeep.line1_entry2_var,
        }
    }