from tkinter.ttk import Style, Widget
from typing import Any, Literal, Optional


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
            if b is object or b is BaseStyle:
                continue
            for ba in cls._yield_bases_in(b):
                yield ba

    @property
    def ttk_style(cls):
        return ".".join(b.__name__ for b in cls._yield_bases_in(cls))

    def __getitem__(cls, stylename):
        filtered_styles = {
            k[0:-len(cls.ttk_style)-1]: v for k, v in cls.defined_styles.items() if k.endswith(f".{cls.ttk_style}")
        } if cls != BaseStyle else cls.defined_styles
        return filtered_styles[stylename]

    def define_all(cls, style: 'Optional[Style]' = None):
        """
        Defines all styles configured by classes that extend the BaseStyle class

        Keyword Arguments:
            style -- A Ttk Style object (default: {Style})
        """
        style = Style() if style is None else style
        for stylename, stylecls in cls.defined_styles.items():
            style.configure(stylename, **stylecls.configure)
            style.map(stylename, **stylecls.map)

    def set_style(cls, widget: Widget):
        widget["style"] = cls.ttk_style

    def as_dict(cls) -> dict[Literal["style"], str]:
        return {
            "style": cls.ttk_style
        }


class BaseStyle(metaclass=_StyleMeta):
    """All the base styles inherit from this class"""
    configure: dict[str, Any] = {}
    map: dict[str, list[tuple[Any, ...]]] = {}


class TProgressbar(BaseStyle):
    """Must define class Vertical(TProgressbar) or Horizontal(TScrollbar) to set config"""


class TScrollbar(BaseStyle):
    """Must define class Vertical(TProgressbar) or Horizontal(TScrollbar) to set config"""


class TButton(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TCheckbutton(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TCombobox(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TEntry(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TFrame(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TLabel(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TLabelFrame(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TMenubutton(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TNotebook(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TPanedwindow(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TRadiobutton(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TSeparator(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class TSizegrip(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"


class Treeview(BaseStyle):
    "Ttk Style name, override using same class name to set configuration"
