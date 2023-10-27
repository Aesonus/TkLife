from enum import Enum
from tkinter import BaseWidget, Tk, Toplevel
from typing import Any, Callable, Optional, Union

__all__ = [
    "EventsEnum",
    "CompositeEvent",
    "TkEventMod",
    "TkEvent",
    "TkVirtualEvents",
    "TtkNotebookEvents",
    "TtkPanedWindowEvents",
    "TtkSpinboxEvents",
    "TtkComboboxEvents",
    "TtkTreeviewEvents",
]

T_ActionCallable = Callable[..., Any]
T_Widget = Union[BaseWidget, Tk, Toplevel]


class _EventMixin(object):
    value: str

    def generate(self, widget: T_Widget, **kwargs) -> T_ActionCallable:
        """Returns a callable that will generate this event on a widget.

        Arguments:
            widget {T_Widget} -- The widget to generate the event on

        Returns:
            T_ActionCallable -- The callable that actually generates the event

        """

        def generator(*__, widget=widget, kwargs=kwargs):
            widget.event_generate(self.value, **kwargs)

        return generator

    def bind(self, widget: T_Widget, action: T_ActionCallable, add="") -> str:
        """Binds a callback to an event on given widget. Kwargs are passed to the bind
        method.

        Arguments:
            widget {T_Widget} -- The widget the bind is on
            action {T_ActionCallable} -- The callable called when the event is triggered

        Returns:
            str -- The event callback id, used to unbind events

        """
        return widget.bind(self.value, action, add=add)

    def bind_tag(
        self, widget: T_Widget, tag: str, action: T_ActionCallable, add=""
    ) -> str:
        return widget._bind(("bind", tag), self.value, action, add=add)  # type: ignore

    def bind_all(self, widget: T_Widget, action: T_ActionCallable, add=""):
        """Binds a callback to an event on all widgets. Kwargs are passed to the bind
        method.

        Arguments:
            widget {T_Widget} -- The widget that will call bind_all
            action {T_ActionCallable} -- The callable called when the event is triggered

        Returns:
            str -- The event callback id, used to unbind

        """
        return widget.bind_all(self.value, action, add=add)

    def bind_class(
        self, widget: T_Widget, classname: str, action: T_ActionCallable, add=""
    ) -> str:
        """Binds a callback to this event on all widgets in the given class. Kwargs are
        passed to the bind method.

        Arguments:
            widget {T_Widget} -- The widget that will call bind_class
            classname {str} -- The widget class to bind on. See: https://tkdocs.com/shipman/binding-levels.html
            action {T_ActionCallable} -- The callable called when the event is triggered

        Returns:
            str -- The event callback id, used to unbind

        """
        return widget.bind_class(classname, self.value, action, add=add)

    def unbind(self, widget: T_Widget, funcid: Optional[str] = None) -> None:
        """Unbinds callback(s) on the event for the given widget.

        Based on code found on Stack Overflow

        See:
            http://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding-in-python
            Modified

        Arguments:
            widget {T_Widget} -- The widget that will call unbind

        Keyword Arguments:
            funcid {Optional[str]} -- The callback id to remove, or None for all (default: {None})

        """
        if not funcid:
            widget.tk.call("bind", widget._w, self.value, "")  # type: ignore
            return
        func_callbacks = widget.tk.call("bind", widget._w, self.value, None).split(  # type: ignore
            "\n"
        )
        new_callbacks = [l for l in func_callbacks if l[6 : 6 + len(funcid)] != funcid]
        widget.tk.call(
            "bind", widget._w, self.value, "\n".join(new_callbacks)  # type: ignore
        )
        widget.deletecommand(funcid)

    def __add__(self, arg):
        return CompositeEvent.factory(self, arg)


class EventsEnum(_EventMixin, Enum):
    """Use to define custom tkinter events."""


class CompositeEvent(_EventMixin):
    """An event composed of other events/event mods."""

    value: str

    def __init__(self, value: str) -> None:
        """Create a new CompositeEvent instance.

        Arguments:
            value {str} -- The event. Should be formatted like: <event>

        """
        self.value = value

    @classmethod
    def factory(
        cls, modifier: "Union[_EventMixin, str]", event: "Union[_EventMixin, str]"
    ) -> "CompositeEvent":
        """Creates a composite event from two events.

        Arguments:
            modifier {Union[_EventMixin, str]} -- Prepends to the new event. Either should be an event type, or string like: "<Event>"
            event {Union[_EventMixin, str]} -- Appends to the new event. Either should be an event type, or string like: "<Event>"

        Returns:
            CompositeEvent -- The new event, having value like <modifier-event>

        """
        mod_value = modifier.value if not isinstance(modifier, str) else modifier
        event_value = event.value if not isinstance(event, str) else event
        return cls(f"{mod_value[0:-1]}-{event_value[1:]}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class TkEventMod(EventsEnum):
    """Standard tkinter event modifiers."""

    ALT = "<Alt>"
    ANY = "<Any>"
    CONTROL = "<Control>"
    DOUBLE = "<Double>"
    LOCK = "<Lock>"
    SHIFT = "<Shift>"
    TRIPLE = "<Triple>"


class TkEvent(EventsEnum):
    """Standard tkinter events."""

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


class TkVirtualEvents(EventsEnum):
    ALT_UNDERLINED = "<<AltUnderlined>>"
    INVOKE = "<<Invoke>>"
    LISTBOX_SELECT = "<<ListboxSelect>>"
    MENU_SELECT = "<<MenuSelect>>"
    MODIFIED = "<<Modified>>"
    SELECTION = "<<Selection>>"
    THEME_CHANGED = "<<ThemeChanged>>"
    TK_WORLD_CHANGED = "<<TkWorldChanged>>"
    TRAVERSE_IN = "<<TraverseIn>>"
    TRAVERSE_OUT = "<<TraverseOut>>"
    UNDO_STACK = "<<UndoStack>>"
    WIDGET_VIEW_SYNC = "<<WidgetViewSync>>"
    CLEAR = "<<Clear>>"
    COPY = "<<Copy>>"
    CUT = "<<Cut>>"
    LINE_END = "<<LineEnd>>"
    LINE_START = "<<LineStart>>"
    NEXT_CHAR = "<<NextChar>>"
    NEXT_LINE = "<<NextLine>>"
    NEXT_PARA = "<<NextPara>>"
    NEXT_WORD = "<<NextWord>>"
    PASTE = "<<Paste>>"
    PASTE_SELECTION = "<<PasteSelection>>"
    PREV_CHAR = "<<PrevChar>>"
    PREV_LINE = "<<PrevLine>>"
    PREV_PARA = "<<PrevPara>>"
    PREV_WINDOW = "<<PrevWindow>>"
    PREV_WORD = "<<PrevWord>>"
    REDO = "<<Redo>>"
    SELECT_ALL = "<<SelectAll>>"
    SELECT_LINE_END = "<<SelectLineEnd>>"
    SELECT_LINE_START = "<<SelectLineStart>>"
    SELECT_NEXT_CHAR = "<<SelectNextChar>>"
    SELECT_NEXT_LINE = "<<SelectNextLine>>"
    SELECT_NEXT_PARA = "<<SelectNextPara>>"
    SELECT_NEXT_WORD = "<<SelectNextWord>>"
    SELECT_NONE = "<<SelectNone>>"
    SELECT_PREV_CHAR = "<<SelectPrevChar>>"
    SELECT_PREV_LINE = "<<SelectPrevLine>>"
    SELECT_PREV_PARA = "<<SelectPrevPara>>"
    SELECT_PREV_WORD = "<<SelectPrevWord>>"
    TOGGLE_SELECTION = "<<ToggleSelection>>"
    UNDO = "<<Undo>>"


class TtkNotebookEvents(EventsEnum):
    NOTEBOOK_TAB_CHANGED = "<<NotebookTabChanged>>"


class TtkPanedWindowEvents(EventsEnum):
    ENTERED_CHILD = "<<EnteredChild>>"


class TtkSpinboxEvents(EventsEnum):
    INCREMENT = "<<Increment>>"
    DECREMENT = "<<Decrement>>"


class TtkComboboxEvents(EventsEnum):
    COMBOBOX_SELECTED = "<<ComboboxSelected>>"


class TtkTreeviewEvents(EventsEnum):
    TREEVIEW_SELECT = "<<TreeviewSelect>>"
    TREEVIEW_OPEN = "<<TreeviewOpen>>"
    TREEVIEW_CLOSE = "<<TreeviewClose>>"
