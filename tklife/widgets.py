"""Creates some common widgets."""
from __future__ import annotations

from tkinter import (
    BOTH,
    END,
    HORIZONTAL,
    LEFT,
    RIGHT,
    VERTICAL,
    Canvas,
    Event,
    Grid,
    Listbox,
    Misc,
    Pack,
    Place,
    Toplevel,
    Y,
)
from tkinter.constants import ACTIVE, ALL, GROOVE, INSERT, NW, SE, SINGLE, E, N, S, W
from tkinter.ttk import Entry, Frame, Scrollbar
from typing import Any, Generic, Iterable, Optional, TypeVar

from tklife import SkeletonMixin, SkelEventDef
from tklife.event import BaseEvent, TkEvent

__all__ = ["ScrolledListbox", "AutoSearchCombobox", "ScrolledFrame", "ModalDialog"]

T_ReturnValue = TypeVar("T_ReturnValue")  # pylint: disable=invalid-name


class ModalDialog(Generic[T_ReturnValue], SkeletonMixin, Toplevel):
    """A dialog that demands focus.

    This is a base class for dialogs that demand focus. It is a toplevel widget that
    demands focus and blocks the main window until it is destroyed. It also has a
    return value that is set when the dialog is destroyed, and is None if the dialog
    is cancelled.

    Note:
        This widget binds the <Destroy>, <Return>, and <Escape> events. Add to these
        events in child widgets, otherwise the dialog may not work as expected.

    """

    return_value: T_ReturnValue | None
    cancelled: bool

    def __init__(self, master, **kwargs):
        super().__init__(None, **kwargs)
        self.transient(master)
        self.withdraw()
        self.return_value = None
        self.cancelled = False
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    @property
    def events(self) -> Iterable[SkelEventDef]:
        """Returns the events for the dialog."""
        return [
            {
                "event": TkEvent.ESCAPE,
                "action": self.cancel,
                "bind_method": "bind",
            },
            {
                "event": TkEvent.RETURN,
                "action": lambda __: self.destroy(),
                "bind_method": "bind",
            },
            {
                "event": TkEvent.DESTROY,
                "action": self.__destroy_event_handler,
                "bind_method": "bind",
            },
        ]

    def show(self) -> T_ReturnValue | None:
        """Shows the dialog and returns the return value if not cancelled, otherwise
        None.

        Returns:
            T_ReturnValue | None: The return value if not cancelled, otherwise None.

        """
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.wait_window()
        return self.return_value

    @classmethod
    def create(cls, master: Misc, **kwargs) -> T_ReturnValue | None:
        """Creates and shows the dialog and returns the return value if not cancelled,
        otherwise None.

        Args:
            master (Misc): The master widget.
            **kwargs: The kwargs to pass to the dialog constructor.

        Returns:
            T_ReturnValue | None: The return value if not cancelled, otherwise None.

        """
        dialog = cls(master, **kwargs)
        return dialog.show()

    def __destroy_event_handler(self, event):
        if event.widget == self:
            if not self.cancelled:
                self.set_return_values()

    def set_return_values(self):
        """Sets the return value if dialog not cancelled.

        Called in the <Destroy> event if dialog was not cancelled. You must override
        this method and, set self.return_value to your return value

        """
        raise NotImplementedError

    def cancel(self, *__):
        """Call to cancel the dialog."""
        self.cancelled = True
        self.destroy()


class ScrolledFrame(Frame):
    """A scrolling frame inside a canvas.

    Based on code found in tkinter.scrolledtext.ScrolledText.

    Note:
        When created, this widget adds to the toplevel's bindings for <MouseWheel>,
        <Button-4>, <Button-5>, <KeyPress>, and <KeyRelease>. This is to ensure that
        the scrolling works in both horizontal (with shift) and vertical directions
        with the mousewheel.

    """

    container: Frame
    canvas: Canvas
    v_scroll: Scrollbar
    h_scroll: Scrollbar

    def __init__(self, master: Misc, show_hscroll=False, **kwargs):
        self._show_hscroll = show_hscroll
        self.container = Frame(master)
        self.canvas = Canvas(self.container, relief="flat", highlightthickness=0)
        self.v_scroll = Scrollbar(self.container, orient=VERTICAL)
        self.h_scroll = Scrollbar(self.container, orient=HORIZONTAL)
        self._modifier_keydown: str | None = None
        self._canvas_handlers: list[tuple[str, BaseEvent]] = []

        kwargs.update(master=self.canvas)
        Frame.__init__(self, **kwargs)
        self.__layout()
        self.__commands()
        self.__events()
        # Copy geometry methods of self.container without overriding Frame
        # methods -- hack!
        text_meths = vars(Frame).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != "_" and m != "config" and m != "configure":
                setattr(self, m, getattr(self.container, m))

    def __layout(self):
        self.canvas.grid(column=0, row=0, sticky=NW + SE)
        self.v_scroll.grid(column=1, row=0, sticky=N + S + E)
        if self._show_hscroll:
            self.h_scroll.grid(column=0, row=1, sticky=E + W + S)
        self.scrolled_frame = self.canvas.create_window((0, 0), window=self, anchor=NW)

    def __commands(self):
        self.v_scroll.configure(command=self._v_scroll_command)
        self.h_scroll.configure(command=self._h_scroll_command)
        self.canvas.configure(yscrollcommand=self._canvas_yscroll_handler)
        self.canvas.configure(xscrollcommand=self._canvas_xscroll_handler)

    def __events(self):
        TkEvent.CONFIGURE.bind(self.container, self._container_configure_handler)
        TkEvent.CONFIGURE.bind(self, self._self_configure_handler)
        TkEvent.ENTER.bind(self.canvas, self._enter_canvas_handler)
        TkEvent.LEAVE.bind(self.canvas, self._leave_canvas_handler)
        TkEvent.KEYPRESS.bind(
            self.winfo_toplevel(), self._modifier_keydown_handler, add="+"
        )
        TkEvent.KEYRELEASE.bind(
            self.winfo_toplevel(), self._modifier_keyup_handler, add="+"
        )

    def _container_configure_handler(self, event: Event):
        self.canvas.configure(
            width=event.width - self.v_scroll.winfo_width(),
            height=event.height - self.h_scroll.winfo_height() * self._show_hscroll,
        )

    def _canvas_yscroll_handler(self, *args):
        if self._can_v_scroll():
            self.v_scroll.set(*args)
        else:
            # This is a hack to make sure the scrollbar updates its size so it doesn't
            # look like the window can scroll
            self.v_scroll.set(0, 1)

    def _v_scroll_command(self, *args):
        if self._can_v_scroll():
            self.canvas.yview(*args)

    def _canvas_xscroll_handler(self, *args):
        if self._can_h_scroll():
            self.h_scroll.set(*args)
        else:
            # This is a hack to make sure the scrollbar updates its size so it doesn't
            # look like the window can scroll
            self.h_scroll.set(0, 1)

    def _h_scroll_command(self, *args):
        if self._can_h_scroll():
            self.canvas.xview(*args)

    def _self_configure_handler(self, *__):
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))

    def _can_v_scroll(self) -> bool:
        """Returns whether the canvas can scroll vertically."""
        return self.canvas.bbox(ALL)[3] >= self.canvas.winfo_height()

    def _can_h_scroll(self) -> bool:
        """Returns whether the canvas can scroll horizontally."""
        return (
            self.canvas.bbox(ALL)[2] >= self.canvas.winfo_width() and self._show_hscroll
        )

    def _enter_canvas_handler(self, __):
        for tkevent in (
            TkEvent.BUTTON + "<4>",
            TkEvent.BUTTON + "<5>",
            TkEvent.MOUSEWHEEL,
        ):
            self._canvas_handlers.append(
                (
                    tkevent.bind(
                        self.winfo_toplevel(), self._mouse_scroll_handler, add="+"
                    ),
                    tkevent,
                )
            )

    def _leave_canvas_handler(self, __):
        for handler, tkevent in self._canvas_handlers:
            tkevent.unbind(self.winfo_toplevel(), handler)
        self._canvas_handlers = []

    def _modifier_keydown_handler(self, event: Event):
        self._modifier_keydown = event.keysym

    def _modifier_keyup_handler(self, __):
        self._modifier_keydown = None

    def _mouse_scroll_handler(self, event: Event):
        # Hold down shift to scroll horizontally
        if (
            self._modifier_keydown
            and ("Shift" in self._modifier_keydown)
            and self._can_h_scroll()
        ):
            if event.num == 4 or event.delta < 0:
                self.canvas.xview_scroll(-1, "units")
            if event.num == 5 or event.delta > 0:
                self.canvas.xview_scroll(1, "units")
        # Otherwise scroll vertically
        elif self._can_v_scroll():
            if event.num == 4 or event.delta < 0:
                self.canvas.yview_scroll(-1, "units")
            if event.num == 5 or event.delta > 0:
                self.canvas.yview_scroll(1, "units")


class ScrolledListbox(Listbox):
    """A scrolled listbox, based on tkinter.scrolledtext.ScrolledText."""

    frame: Frame
    vbar: Scrollbar

    def __init__(self, master: Misc, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({"yscrollcommand": self.vbar.set})
        Listbox.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar["command"] = self.yview

        # Copy geometry methods of self.frame without overriding Listbox
        # methods -- hack!
        text_meths = vars(Listbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != "_" and m != "config" and m != "configure":
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class AutoSearchCombobox(Entry):
    """A combobox that automatically searches for the closest match to the current
    contents."""

    def __init__(
        self,
        master: Misc,
        values: Optional[Iterable[str]] = None,
        height: Optional[int] = None,
        **kwargs,
    ):
        Entry.__init__(self, master, **kwargs)
        self._ddtl = Toplevel(self, takefocus=False, relief=GROOVE, borderwidth=1)
        self._ddtl.wm_overrideredirect(True)
        self._lb = ScrolledListbox(
            self._ddtl,
            width=kwargs.pop("width", None),
            height=height,
            selectmode=SINGLE,
        )
        self.__values: tuple = tuple()
        self.configure(values=values)
        self._lb.pack(expand=True, fill=BOTH)
        self._hide_tl()
        self.winfo_toplevel().focus_set()
        TkEvent.KEYRELEASE.bind(self, self._handle_keyrelease)
        TkEvent.FOCUSOUT.bind(self, self._handle_focusout)
        TkEvent.KEYPRESS.bind(self, self._handle_keypress)
        # toplevel bindings
        cfg_handler = TkEvent.CONFIGURE.bind(
            self.winfo_toplevel(), self._handle_configure, add="+"
        )
        TkEvent.DESTROY.bind(
            self,
            lambda __: TkEvent.CONFIGURE.unbind(self.winfo_toplevel(), cfg_handler),
        )
        (TkEvent.BUTTONRELEASE + "<1>").bind(self._lb, self._handle_lb_click)

    def cget(self, key: str) -> Any:
        """Gets the value of the specified option."""
        if key == "values":
            return self._get_values()
        return super().cget(key)

    def configure(self, cnf=None, **kwargs):
        """Configures the widget."""
        if cnf is not None:
            kwargs.update(cnf)
        if "values" in kwargs:
            self._set_values(kwargs.pop("values"))
        super().configure(**kwargs)

    def _get_values(self) -> tuple[str, ...]:
        """Gets the values."""
        try:
            return self.__values
        except AttributeError:
            self.__values = ()
            return self.__values

    def _set_values(self, values: Optional[Iterable[str]]) -> None:
        """Sorts and sets the values."""
        self.__values = tuple(sorted(values)) if values is not None else tuple()
        self._lb.delete(0, END)
        self._lb.insert(END, *self.cget("values"))
        self._lb.selection_clear(0, END)
        self._lb.selection_set(0)
        self._lb.activate(0)

    @property
    def _lb_current_selection(self) -> str:
        """Returns the current selection in the listbox."""
        try:
            sel = self._lb.curselection()[0]
        except IndexError:
            return ""
        return self._lb.get(sel)

    def _set_lb_index(self, index):
        self._lb.selection_clear(0, END)
        self._lb.selection_set(index)
        self._lb.activate(index)
        self._lb.see(index)

    @property
    def text_after_cursor(self) -> str:
        """Gets the entry text after the cursor."""
        contents = self.get()
        return contents[self.index(INSERT) :]

    @property
    def dropdown_is_visible(self) -> bool:
        """Returns whether the dropdown is visible."""
        return self._ddtl.winfo_ismapped()

    def _handle_lb_click(self, __):
        self.delete(0, END)
        self.insert(0, self._lb_current_selection)
        self._hide_tl()

    def _handle_keypress(  # pylint: disable=inconsistent-return-statements
        self, event: Event
    ):
        if "Left" in event.keysym:
            if self.dropdown_is_visible:
                self._hide_tl()
                return "break"
            return
        if (
            ("Right" in event.keysym and self.text_after_cursor == "")
            or event.keysym in ["Return", "Tab"]
        ) and self.dropdown_is_visible:
            # Completion and block next action
            self.delete(0, END)
            self.insert(0, self._lb_current_selection)
            self._hide_tl()
            return "break"

    def _handle_keyrelease(  # pylint: disable=inconsistent-return-statements
        self, event: Event
    ):
        if "Up" in event.keysym and self.dropdown_is_visible:
            previous_index = self._lb.index(ACTIVE)
            new_index = max(0, self._lb.index(ACTIVE) - 1)
            self._set_lb_index(new_index)
            if previous_index == new_index:
                self._hide_tl()
            return
        if "Down" in event.keysym:
            if self.dropdown_is_visible:
                current_index = self._lb.index(ACTIVE)
                new_index = min(current_index + 1, self._lb.size() - 1)
                self._set_lb_index(new_index)
                return "break"
            if not self.dropdown_is_visible and self._lb.size() > 0:
                self._show_tl()

        if (
            len(event.keysym) == 1
            or ("Right" in event.keysym and self.text_after_cursor == "")
            or event.keysym in ["BackSpace"]
        ):
            if self.get() != "":
                new_values = tuple(
                    value
                    for value in self.cget("values")
                    if value.lower().startswith(self.get().lower())
                )
            else:
                new_values = self.cget("values")
            self._lb.delete(0, END)
            self._lb.insert(END, *new_values)
            self._set_lb_index(0)
            if self._lb.size() < 1 or self.get() == self._lb_current_selection:
                self._hide_tl()
            else:
                self._show_tl()

    def _handle_focusout(self, __):
        def cf():
            try:
                if self.focus_get() != self._ddtl and self.focus_get() != self._lb:
                    self._hide_tl()
                else:
                    self.focus_set()
            except KeyError:
                self._hide_tl()

        self.after(1, cf)

    def _handle_configure(self, __):
        if self._ddtl.winfo_ismapped():
            self._update_tl_pos()

    def _show_tl(self) -> None:
        if not self._ddtl.winfo_ismapped():
            self._update_tl_pos()
            self._ddtl.deiconify()
            self._ddtl.attributes("-topmost", True)

    def _update_tl_pos(self) -> None:
        self._ddtl.geometry(
            f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height() - 1}"
        )

    def _hide_tl(self) -> None:
        self._ddtl.withdraw()
