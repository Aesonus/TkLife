from tkinter.ttk import Label
from typing import Mapping, Optional, Type
from tkinter import Widget
from ...constants import TEXT

__all__ = [
    'LabelledWidget',
]

class LabelledWidget(object):
    def __init__(self, label_text: str, widget_type: Type[Widget], kw: Optional[Mapping] = None, lbl_kw: Optional[Mapping] = None) -> None:
        """
        ## LabelledWidget

        Defines the skeleton for 2 widgets, the first being a ttk.Label widget and the other being whichever widget you desire.

        ### Usage

        Unpack in the skeleton. Example:

        ```
        {
            widgets: [
                    [*LabelledWidget('Hello:', Spinbox)]
                ],
            ...
        }
        ```
        """
        self.label_text = label_text
        self.widget_type = widget_type
        self.kw = {} if kw is None else kw
        self.lbl_kw = {} if lbl_kw is None else lbl_kw

    def __iter__(self):
        yield (
            Label, {
                **self.lbl_kw,
                TEXT: self.label_text,
            }
        )
        yield (
            self.widget_type, {
                **self.kw
            })
