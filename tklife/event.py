from enum import Enum
from tkinter import Event, Widget
from typing import Any, Callable, Optional

T_ActionCallable = Callable[[Event], Any]


class _EventMixin(object):
    def generate(self, widget: Widget) -> T_ActionCallable:
        def generator(*__, widget=widget):
            widget.event_generate(self.value)
        return generator

    def bind(self, widget: Widget, action: T_ActionCallable, **kwargs):
        return widget.bind(self.value, action, **kwargs)

    def bind_all(self, widget: Widget, action: T_ActionCallable, **kwargs):
        return widget.bind_all(self.value, action, **kwargs)

    def bind_class(self, widget: Widget, classname: str, action: T_ActionCallable, **kwargs):
        return widget.bind_class(classname, self.value, action, **kwargs)

    def unbind(self, widget: Widget, funcid: Optional[str] = None):
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

    def __add__(self, arg):
        return CompositeEvent.factory(self, arg)


class EventsEnum(_EventMixin, Enum):
    pass


class CompositeEvent(_EventMixin):
    def __init__(self, value: str) -> None:
        self.value = value

    @classmethod
    def factory(cls, modifier, event) -> 'CompositeEvent':
        return cls(f"{modifier.value[0:-1]}-{event.value[1:]}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class TkEventMod(EventsEnum):
    ALT = "<Alt>"
    ANY = "<Any>"
    CONTROL = "<Control>"
    DOUBLE = "<Double>"
    LOCK = "<Lock>"
    SHIFT = "<Shift>"
    TRIPLE = "<Triple>"


class TkEvent(EventsEnum):

    ACTIVATE = "<Activate>"
    BUTTON = "<Button>"
    BUTTONRELEASE = "<ButtonRelease>"
    CONFIGURE = "<Configure>"
    DEACTIVATE = "<Deactivate>"
    DESTROY = "<Destroy>"
    ENTER = "<Enter>"
    EXPOSE = "<Expose>"
    FOCUSIN = "<FocusIn>"
    FOCUSOUT = "<FocusOut>"
    KEYPRESS = "<KeyPress>"
    KEYRELEASE = "<KeyRelease>"
    LEAVE = "<Leave>"
    MAP = "<Map>"
    MOTION = "<Motion>"
    MOUSEWHEEL = "<MouseWheel>"
    UNMAP = "<Unmap>"
    VISIBILITY = "<Visibility>"
    ALT_L = "<Alt_L>"
    ALT_R = "<Alt_R>"
    BACKSPACE = "<BackSpace>"
    CANCEL = "<Cancel>"
    CAPS_LOCK = "<Caps_Lock>"
    CONTROL_L = "<Control_L>"
    CONTROL_R = "<Control_R>"
    DELETE = "<Delete>"
    DOWN = "<Down>"
    END = "<End>"
    ESCAPE = "<Escape>"
    EXECUTE = "<Execute>"
    F1 = "<F1>"
    F2 = "<F2>"
    FI = "<Fi>"
    F12 = "<F12>"
    HOME = "<Home>"
    INSERT = "<Insert>"
    LEFT = "<Left>"
    LINEFEED = "<Linefeed>"
    KP_0 = "<KP_0>"
    KP_1 = "<KP_1>"
    KP_2 = "<KP_2>"
    KP_3 = "<KP_3>"
    KP_4 = "<KP_4>"
    KP_5 = "<KP_5>"
    KP_6 = "<KP_6>"
    KP_7 = "<KP_7>"
    KP_8 = "<KP_8>"
    KP_9 = "<KP_9>"
    KP_ADD = "<KP_Add>"
    KP_BEGIN = "<KP_Begin>"
    KP_DECIMAL = "<KP_Decimal>"
    KP_DELETE = "<KP_Delete>"
    KP_DIVIDE = "<KP_Divide>"
    KP_DOWN = "<KP_Down>"
    KP_END = "<KP_End>"
    KP_ENTER = "<KP_Enter>"
    KP_HOME = "<KP_Home>"
    KP_INSERT = "<KP_Insert>"
    KP_LEFT = "<KP_Left>"
    KP_MULTIPLY = "<KP_Multiply>"
    KP_NEXT = "<KP_Next>"
    KP_PRIOR = "<KP_Prior>"
    KP_RIGHT = "<KP_Right>"
    KP_SUBTRACT = "<KP_Subtract>"
    KP_UP = "<KP_Up>"
    NEXT = "<Next>"
    NUM_LOCK = "<Num_Lock>"
    PAUSE = "<Pause>"
    PRINT = "<Print>"
    PRIOR = "<Prior>"
    RETURN = "<Return>"
    RIGHT = "<Right>"
    SCROLL_LOCK = "<Scroll_Lock>"
    SHIFT_L = "<Shift_L>"
    SHIFT_R = "<Shift_R>"
    TAB = "<Tab>"
    UP = "<Up>"
