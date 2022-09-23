from tkinter.ttk import Style
from typing import Any, Optional


class _StyleMeta(type):
    """*This should never be used directly unless you know what you're doing!*"""

    defined_styles: dict[str, 'BaseStyle'] = {

    }
    def __new__(cls, name, bases, namespace):
        newcls = super().__new__(cls, name, bases, namespace)
        if newcls.__name__ != "BaseStyle":
            cls.defined_styles.update(
                {newcls.ttk_style: newcls}
            )
        return newcls

    def _yield_bases_in(cls, base_cls):
        yield base_cls
        for b in base_cls.__bases__:
            if b is object or b is BaseStyle: continue
            for ba in cls._yield_bases_in(b):
                yield ba
    @property
    def ttk_style(cls):
        return ".".join(b.__name__ for b in cls._yield_bases_in(cls))

    def __getitem__(cls, stylename):
        return cls.defined_styles[stylename]

    def define_all(cls, style: 'Optional[Style]'=None):
        """Defines all the styles that have been defined"""
        style = Style() if style is None else style
        for stylename, stylecls in cls.defined_styles.items():
            style.configure(stylename, **stylecls.configure)
            style.map(stylename, **stylecls.map)


class BaseStyle(metaclass=_StyleMeta):
    """All the base styles inherit from this class"""
    configure: dict[str, Any]= {}
    map: dict[str, list[tuple[Any, ...]]]={}

class TEntry(BaseStyle):
    """This would be the base style. Extending this would add a new style type"""