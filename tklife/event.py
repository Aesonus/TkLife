from typing import Any, Callable
from tkinter import Widget, Event
from enum import Enum

T_ActionCallable = Callable[[Event], Any]

class EventsEnum(Enum):
    def generate(self, widget: Widget):
        def generator(widget=widget):
            widget.event_generate(self.value)
        return generator

    def bind(self, widget: Widget, action: T_ActionCallable):
        widget.bind(self.value, action)