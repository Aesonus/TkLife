"""Creates some common widgets."""
from abc import abstractmethod
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
from typing import Any, Iterable, Optional

from tklife import SkeletonMixin
from tklife.event import TkEvent

__all__ = ["ScrolledListbox", "AutoSearchCombobox", "ScrolledFrame", "ModalDialog"]


class ModalDialog(SkeletonMixin, Toplevel):
    """A dialog that demands focus."""

    return_value: Any

    def __init__(self, master, **kwargs):
        super().__init__(None, **kwargs)
        self.transient(master)
        self.withdraw()
        self.return_value = None
        self.cancelled = False
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        TkEvent.ESCAPE.bind(self, self.cancel)
        TkEvent.RETURN.bind(self, lambda __: self.destroy())
        TkEvent.DESTROY.bind(self, self.__destroy_event_handler)

    @classmethod
    def show(cls, master: Misc, **kwargs):
        """Shows the dialog.

        Returns the return value if not cancelled, otherwise None.

        """
        dialog = cls(master, **kwargs)
        dialog.deiconify()
        dialog.grab_set()
        dialog.focus_set()
        dialog.wait_window()
        return dialog.return_value

    def __destroy_event_handler(self, __):
        if not self.cancelled:
            self.set_return_values()

    @abstractmethod
    def set_return_values(self):
        """Sets the return value if dialog not cancelled.

        Called in the <Destroy> event if cancelled = True. You must override this method
        and, set self.return_value to your return value

        """

    def cancel(self, *__):
        """Call to cancel the dialog."""
        self.cancelled = True
        self.destroy()


class ScrolledFrame(Frame):
    """A scrolling frame inside a canvas.

    Based on tkinter.scrolledtext.ScrolledText

    """

    container: Frame
    canvas: Canvas
    v_scroll: Scrollbar
    h_scroll: Scrollbar

    def __init__(self, master: Misc, **kwargs):
        self.container = Frame(master)
        self.canvas = Canvas(self.container, relief="flat", highlightthickness=0)
        self.v_scroll = Scrollbar(self.container, orient=VERTICAL)
        self.h_scroll = Scrollbar(self.container, orient=HORIZONTAL)
        kwargs.update({"master": self.canvas})
        Frame.__init__(self, **kwargs)
        self.__layout()
        self.__commands()
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
        self.h_scroll.grid(column=0, row=1, sticky=E + W + S)
        self.scrolled_frame = self.canvas.create_window((0, 0), window=self, anchor=NW)

    def __commands(self):
        self.v_scroll.configure(command=self.canvas.yview)
        self.h_scroll.configure(command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.canvas.configure(xscrollcommand=self.h_scroll.set)
        TkEvent.CONFIGURE.bind(self.container, self._container_configure_handler)
        TkEvent.CONFIGURE.bind(self, self._self_configure_handler)
        TkEvent.ENTER.bind(self.canvas, self._enter_canvas_handler)
        TkEvent.LEAVE.bind(self.canvas, self._leave_canvas_handler)

    def _container_configure_handler(self, event: Event):
        self.canvas.configure(
            width=event.width - self.v_scroll.winfo_width(),
            height=event.height - self.h_scroll.winfo_height(),
        )

    def _self_configure_handler(self, *__):
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))

    def _enter_canvas_handler(self, __):
        (TkEvent.BUTTON + "<4>").bind_all(
            self.winfo_toplevel(), self._mouse_scroll_handler
        )
        (TkEvent.BUTTON + "<5>").bind_all(
            self.winfo_toplevel(), self._mouse_scroll_handler
        )
        (TkEvent.MOUSEWHEEL).bind_all(self.winfo_toplevel(), self._mouse_scroll_handler)

    def _leave_canvas_handler(self, __):
        self.unbind_all((TkEvent.BUTTON + "<4>").value)
        self.unbind_all((TkEvent.BUTTON + "<5>").value)

    def _mouse_scroll_handler(self, event: Event):
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
        self.values = tuple(values) if values else ()
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

    @property
    def values(self) -> tuple[str, ...]:
        """Gets the values."""
        try:
            return self.__values
        except AttributeError:
            self.values = ()
            return self.values

    @values.setter
    def values(self, values: Optional[Iterable[str]]) -> None:
        """Sorts and sets the values."""
        self.__values = tuple(sorted(values)) if values is not None else tuple()
        self._lb.delete(0, END)
        self._lb.insert(END, *self.values)
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
                    for value in self.values
                    if value.lower().startswith(self.get().lower())
                )
            else:
                new_values = self.values
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
