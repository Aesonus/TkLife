import abc
from abc import abstractmethod
from tkinter import Canvas, Listbox, Misc, Toplevel
from tkinter.ttk import Entry, Frame, Scrollbar
from tklife.skel import SkeletonMixin
from typing import Any, Iterable, Optional

class ModalDialog(SkeletonMixin, Toplevel, metaclass=abc.ABCMeta):
    return_value: Any
    cancelled: bool
    def __init__(self, master, **kwargs): ...
    @classmethod
    def show(cls, master: Misc, **kwargs): ...
    @abstractmethod
    def set_return_values(self): ...
    def cancel(self, *__) -> None: ...

class ScrolledFrame(Frame):
    container: Frame
    canvas: Canvas
    v_scroll: Scrollbar
    h_scroll: Scrollbar
    def __init__(self, master: Misc, **kwargs) -> None: ...

class ScrolledListbox(Listbox):
    frame: Frame
    vbar: Scrollbar
    def __init__(self, master: Misc, **kw) -> None: ...

class AutoSearchCombobox(Entry):
    def __init__(self, master: Misc, values: Optional[Iterable[str]] = ..., height: Optional[int] = ..., **kwargs): ...
    @property
    def values(self) -> tuple[str, ...]: ...
    @values.setter
    def values(self, values: Optional[Iterable[str]]) -> None: ...
    @property
    def text_after_cursor(self) -> str: ...
    @property
    def dropdown_is_visible(self) -> bool: ...
