from typing import Any
from collections.abc import Sequence
import abc
from tkinter.ttk import Style

class _StyleMeta(abc.ABCMeta):

    @property
    def ttk_style(cls):
        def iter_bases(__bases):
            for base in __bases:
                if base == BaseStyle:
                    continue
                yield base
                for base2 in iter_bases(base.__bases__):
                    yield base2
        if not hasattr(cls, "__name_cache__"):
            cls.__name_cache__ = ".".join((cls.__name__, *(b.__name__ for b in iter_bases(cls.__bases__))))
        return cls.__name_cache__

class BaseStyle(metaclass=_StyleMeta):
    """All the base styles inherit from this class"""

class TEntry(BaseStyle):
    """This would be the base style. Extending this would add a new style type"""
    bordercolor: str
    darkcolor: str
    fieldbackground: str
    foreground: str
    insertcolor: str
    insertwidth: int
    lightcolor: str
    padding: int
    relief: str
    selectbackground: str
    selectborderwidth: int
    selectforeground: str

class Example(TEntry):
    padding = {
        ("normal", 3),
        ("readonly", 4, 3),
    }