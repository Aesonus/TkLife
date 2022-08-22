from enum import Enum
from tkinter import Event, Widget
from typing import Any, Callable

T_ActionCallable = Callable[[Event], Any]


class EventsEnum(Enum):
    def generate(self, widget: Widget):
        def generator(*__, widget=widget):
            widget.event_generate(self.value)
        return generator

    def bind(self, widget: Widget, action: T_ActionCallable, **kwargs):
        return widget.bind(self.value, action, **kwargs)

    def bind_all(self, widget: Widget, action: T_ActionCallable, **kwargs):
        return widget.bind_all(self.value, action, **kwargs)

    def bind_class(self, widget: Widget, classname: str, action: T_ActionCallable, **kwargs):
        return widget.bind_class(classname, self.value, action, **kwargs)

    def unbind(self, widget: Widget, funcid: str):
        '''
        See:
            http://stackoverflow.com/questions/6433369/
            deleting-and-changing-a-tkinter-event-binding-in-python
            Modified
        '''
        if not funcid:
            widget.tk.call('bind', widget._w, self.value, '')
            return
        func_callbacks = widget.tk.call(
            'bind', widget._w, self.value, None).split('\n')
        new_callbacks = [
            l for l in func_callbacks if l[6:6 + len(funcid)] != funcid]
        widget.tk.call('bind', widget._w, self.value, '\n'.join(new_callbacks))
        widget.deletecommand(funcid)
