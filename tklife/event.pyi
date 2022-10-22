from enum import Enum
from tkinter import BaseWidget, Event, Tk, Toplevel
from typing import Any, Callable, Optional, Union

T_ActionCallable = Callable[[Event], Any]
T_Widget = Union[BaseWidget, Tk, Toplevel]

class _EventMixin:
    value: str
    def generate(self, widget: T_Widget, **kwargs) -> T_ActionCallable: ...
    def bind(self, widget: T_Widget, action: T_ActionCallable, add: str = ...) -> str: ...
    def bind_tag(self, widget: T_Widget, tag: str, action: T_ActionCallable, add: str = ...) -> str: ...
    def bind_all(self, widget: T_Widget, action: T_ActionCallable, add: str = ...): ...
    def bind_class(self, widget: T_Widget, classname: str, action: T_ActionCallable, add: str = ...) -> str: ...
    def unbind(self, widget: T_Widget, funcid: Optional[str] = ...) -> None: ...
    def __add__(self, arg): ...

class EventsEnum(_EventMixin, Enum): ...

class CompositeEvent(_EventMixin):
    value: str
    def __init__(self, value: str) -> None: ...
    @classmethod
    def factory(cls, modifier: Union[_EventMixin, str], event: Union[_EventMixin, str]) -> CompositeEvent: ...

class TkEventMod(EventsEnum):
    ALT: str
    ANY: str
    CONTROL: str
    DOUBLE: str
    LOCK: str
    SHIFT: str
    TRIPLE: str

class TkEvent(EventsEnum):
    ACTIVATE: str
    BUTTON: str
    BUTTONRELEASE: str
    CONFIGURE: str
    DEACTIVATE: str
    DESTROY: str
    ENTER: str
    EXPOSE: str
    FOCUSIN: str
    FOCUSOUT: str
    KEYPRESS: str
    KEYRELEASE: str
    LEAVE: str
    MAP: str
    MOTION: str
    MOUSEWHEEL: str
    UNMAP: str
    VISIBILITY: str
    ALT_L: str
    ALT_R: str
    BACKSPACE: str
    CANCEL: str
    CAPS_LOCK: str
    CONTROL_L: str
    CONTROL_R: str
    DELETE: str
    DOWN: str
    END: str
    ESCAPE: str
    EXECUTE: str
    F1: str
    F2: str
    FI: str
    F12: str
    HOME: str
    INSERT: str
    LEFT: str
    LINEFEED: str
    KP_0: str
    KP_1: str
    KP_2: str
    KP_3: str
    KP_4: str
    KP_5: str
    KP_6: str
    KP_7: str
    KP_8: str
    KP_9: str
    KP_ADD: str
    KP_BEGIN: str
    KP_DECIMAL: str
    KP_DELETE: str
    KP_DIVIDE: str
    KP_DOWN: str
    KP_END: str
    KP_ENTER: str
    KP_HOME: str
    KP_INSERT: str
    KP_LEFT: str
    KP_MULTIPLY: str
    KP_NEXT: str
    KP_PRIOR: str
    KP_RIGHT: str
    KP_SUBTRACT: str
    KP_UP: str
    NEXT: str
    NUM_LOCK: str
    PAUSE: str
    PRINT: str
    PRIOR: str
    RETURN: str
    RIGHT: str
    SCROLL_LOCK: str
    SHIFT_L: str
    SHIFT_R: str
    TAB: str
    UP: str

class TkVirtualEvents(EventsEnum):
    ALT_UNDERLINED: str
    INVOKE: str
    LISTBOX_SELECT: str
    MENU_SELECT: str
    MODIFIED: str
    SELECTION: str
    THEME_CHANGED: str
    TK_WORLD_CHANGED: str
    TRAVERSE_IN: str
    TRAVERSE_OUT: str
    UNDO_STACK: str
    WIDGET_VIEW_SYNC: str
    CLEAR: str
    COPY: str
    CUT: str
    LINE_END: str
    LINE_START: str
    NEXT_CHAR: str
    NEXT_LINE: str
    NEXT_PARA: str
    NEXT_WORD: str
    PASTE: str
    PASTE_SELECTION: str
    PREV_CHAR: str
    PREV_LINE: str
    PREV_PARA: str
    PREV_WINDOW: str
    PREV_WORD: str
    REDO: str
    SELECT_ALL: str
    SELECT_LINE_END: str
    SELECT_LINE_START: str
    SELECT_NEXT_CHAR: str
    SELECT_NEXT_LINE: str
    SELECT_NEXT_PARA: str
    SELECT_NEXT_WORD: str
    SELECT_NONE: str
    SELECT_PREV_CHAR: str
    SELECT_PREV_LINE: str
    SELECT_PREV_PARA: str
    SELECT_PREV_WORD: str
    TOGGLE_SELECTION: str
    UNDO: str

class TtkNotebookEvents(EventsEnum):
    NOTEBOOK_TAB_CHANGED: str

class TtkPanedWindowEvents(EventsEnum):
    ENTERED_CHILD: str

class TtkSpinboxEvents(EventsEnum):
    INCREMENT: str
    DECREMENT: str

class TtkComboboxEvents(EventsEnum):
    COMBOBOX_SELECTED: str

class TtkTreeviewEvents(EventsEnum):
    TREEVIEW_SELECT: str
    TREEVIEW_OPEN: str
    TREEVIEW_CLOSE: str
