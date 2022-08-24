"""Creates some common widgets"""
from tkinter import (BOTH, END, HORIZONTAL, LEFT, RIGHT, VERTICAL, Canvas,
                     Event, Grid, Listbox, Pack, Place, Toplevel, Widget, Y)
from tkinter.constants import (ACTIVE, ALL, GROOVE, INSERT, NW, SE, SINGLE, E,
                               N, S, W)
from tkinter.ttk import Entry, Frame, Scrollbar
from typing import Iterable, Optional
from tklife.event import TkEvent

__all__ = ['ScrolledListbox', 'AutoSearchCombobox', 'ScrolledFrame', 'ModalDialog']


class ModalDialog(Toplevel):
    """A dialog that demands focus"""
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        self.transient(master)
        self.withdraw()
        self.return_value = None
        self.cancelled = False
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        TkEvent.ESCAPE.bind(self, self.cancel)
        TkEvent.RETURN.bind(self, lambda __: self.destroy())
        TkEvent.DESTROY.bind(self, self.set_return_values)

    @classmethod
    def show(cls, master: Widget, **kwargs):
        dialog = cls(master, **kwargs)
        dialog.deiconify()
        dialog.grab_set()
        dialog.focus_set()
        dialog.wait_window()
        return dialog.return_value

    def set_return_values(self, event: Event):
        """
        Sets the return value if dialog not cancelled.
        Called in the <Destroy> event if cancelled = True.
        You must override this method for return value to work
        """
        pass

    def cancel(self, *__):
        self.cancelled = True
        self.destroy()

class ScrolledFrame(Frame):
    """
    A scrolling frame inside a canvas. Based on tkinter.scrolledtext.ScrolledText
    """

    def __init__(self, master: Widget, **kwargs):
        self.container = Frame(master)
        self.canvas = Canvas(self.container, relief=None, highlightthickness=0)
        self.v_scroll = Scrollbar(self.container, orient=VERTICAL)
        self.h_scroll = Scrollbar(self.container, orient=HORIZONTAL)
        kwargs.update({'master': self.canvas})
        Frame.__init__(self, **kwargs)
        self.__layout()
        self.__commands()
        # Copy geometry methods of self.container without overriding Frame
        # methods -- hack!
        text_meths = vars(Frame).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.container, m))

    def __layout(self):
        self.canvas.grid(column=0, row=0, sticky=NW+SE)
        self.v_scroll.grid(column=1, row=0, sticky=N+S+E)
        self.h_scroll.grid(column=0, row=1, sticky=E+W+S)
        self.scrolled_frame = self.canvas.create_window(
            (0, 0), window=self, anchor=NW)

    def __commands(self):
        self.v_scroll.configure(command=self.canvas.yview)
        self.h_scroll.configure(command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.canvas.configure(xscrollcommand=self.h_scroll.set)
        self.container.bind('<Configure>', self._container_configure_handler)
        self.bind('<Configure>', self._self_configure_handler)

    def _container_configure_handler(self, event: Event):
        self.canvas.configure(
            width=event.width - self.v_scroll.winfo_width(),
            height=event.height - self.h_scroll.winfo_height()
        )

    def _self_configure_handler(self, *__):
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))


class ScrolledListbox(Listbox):
    """
    A scrolled listbox, based on tkinter.scrolledtext.ScrolledText
    """

    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Listbox.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Listbox
        # methods -- hack!
        text_meths = vars(Listbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class AutoSearchCombobox(Entry):
    def __init__(self, master: Widget, values: Optional[Iterable[str]] = None, height: Optional[int] = None, **kwargs):
        super().__init__(master, **kwargs)
        self._tl = Toplevel(self, takefocus=False,
                            relief=GROOVE, borderwidth=1)
        self._tl.wm_overrideredirect(True)
        self._lb = ScrolledListbox(self._tl, width=kwargs.pop(
            'width', None), height=height, selectmode=SINGLE)
        self.values = values
        self._lb.pack(expand=True, fill=BOTH)
        self._hide_tl()
        self.winfo_toplevel().focus_set()
        self.bind('<KeyRelease>', self._handle_keyrelease)
        self.bind('<FocusOut>', self._handle_focusout)
        self.bind('<KeyPress>', self._handle_keypress)
        # toplevel bindings
        cfg_handler = self.winfo_toplevel().bind(
            '<Configure>', self._handle_configure, add="+")
        self.bind('<Destroy>', lambda __,
                  cfg_handler=cfg_handler: self._unbind_my_configure(cfg_handler))

    def _unbind_my_configure(self, cfg_handler):
        """Internal function. Allows for JUST this widget's associated callback. Getting around tkinter bug"""
        root_tl = self.winfo_toplevel()
        if not cfg_handler:
            root_tl.tk.call('bind', self._w, '<Configure>', '')
            return
        func_callbacks = root_tl.tk.call(
            'bind', root_tl._w, '<Configure>', None).split('\n')
        new_callbacks = [
            l for l in func_callbacks if l[6:6 + len(cfg_handler)] != cfg_handler]
        root_tl.tk.call('bind', root_tl._w, '<Configure>',
                        '\n'.join(new_callbacks))
        root_tl.deletecommand(cfg_handler)

    @property
    def values(self):
        """
        Gets the values
        """
        try:
            return self.__values
        except AttributeError:
            self.values = ()
            return self.values

    @values.setter
    def values(self, values: Optional[Iterable]):
        """
        Sorts and sets the values
        """
        self.__values = tuple(
            sorted(values)) if values is not None else tuple()
        self._lb.insert(END, *self.values)
        self._lb.selection_clear(0, END)
        self._lb.selection_set(0)
        self._lb.activate(0)

    @property
    def _lb_current_selection(self) -> str:
        """
        Returns the current selection in the listbox
        """
        try:
            sel = self._lb.curselection()[0]
        except IndexError:
            return None
        return self._lb.get(sel)

    def _set_lb_index(self, index):
        self._lb.selection_clear(0, END)
        self._lb.selection_set(index)
        self._lb.activate(index)
        self._lb.see(index)

    @property
    def text_after_cursor(self) -> str:
        """
        Gets the entry text after the cursor
        """
        contents = self.get()
        return contents[self.index(INSERT):]

    @property
    def dropdown_is_visible(self):
        return self._tl.winfo_ismapped()

    def _handle_keypress(self, event: Event):
        if 'Left' in event.keysym:
            if self.dropdown_is_visible:
                self._hide_tl()
                return 'break'
            else:
                return
        elif (('Right' in event.keysym and self.text_after_cursor == '') or event.keysym in ['Return', 'Tab']) and self.dropdown_is_visible:
            # Completion and block next action
            self.delete(0, END)
            self.insert(0, self._lb_current_selection)
            self._hide_tl()
            return 'break'

    def _handle_keyrelease(self, event: Event):
        if 'Up' in event.keysym and self.dropdown_is_visible:
            previous_index = self._lb.index(ACTIVE)
            new_index = max(0, self._lb.index(ACTIVE) - 1)
            self._set_lb_index(new_index)
            if previous_index == new_index:
                self._hide_tl()
            return
        if 'Down' in event.keysym:
            if self.dropdown_is_visible:
                current_index = self._lb.index(ACTIVE)
                new_index = min(current_index + 1, self._lb.size() - 1)
                self._set_lb_index(new_index)
                return 'break'
            if not self.dropdown_is_visible and self._lb.size() > 0:
                self._show_tl()

        if len(event.keysym) == 1 or ('Right' in event.keysym and self.text_after_cursor == '') or event.keysym in ['BackSpace']:
            if self.get() != '':
                new_values = [value for value in self.values if value.lower(
                ).startswith(self.get().lower())]
            else:
                new_values = self.values
            self._lb.delete(0, END)
            self._lb.insert(END, *new_values)
            self._set_lb_index(0)
            if self._lb.size() < 1 or self.get() == self._lb_current_selection:
                self._hide_tl()
            else:
                self._show_tl()

    def _handle_focusout(self, event: Event):
        def cf():
            if self.focus_get() != self._tl and self.focus_get() != self._lb:
                self._hide_tl()
            else:
                self.focus_set()
        self.after(1, cf)

    def _handle_configure(self, event: Event):
        if self._tl.winfo_ismapped():
            self._update_tl_pos()

    def _show_tl(self) -> None:
        if self._tl.winfo_ismapped() == False:
            self._update_tl_pos()
            self._tl.deiconify()
            self._tl.attributes("-topmost", True)

    def _update_tl_pos(self) -> None:
        self._tl.geometry('+{}+{}'.format(self.winfo_rootx(),
                          self.winfo_rooty() + self.winfo_height() - 1))

    def _hide_tl(self) -> None:
        self._tl.withdraw()
