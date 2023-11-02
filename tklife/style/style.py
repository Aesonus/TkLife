"""This module contains the BaseStyle class, which is the base class for all styles.

It also contains all the styles that are defined by default, and the _StyleMeta class,
which is a metaclass for BaseStyle that automatically registers all classes that inherit
from it. This allows for easy access to the Ttk Style name, and configuration and map
options.

"""

from tkinter.ttk import Style, Widget
from typing import Any, Literal, Optional

# pylint: disable=too-few-public-methods

__all__ = [
    "BaseStyle",
    "TProgressbar",
    "TScrollbar",
    "TButton",
    "TCheckbutton",
    "TCombobox",
    "TEntry",
    "TFrame",
    "TLabel",
    "TLabelFrame",
    "TMenubutton",
    "TNotebook",
    "TPanedwindow",
    "TRadiobutton",
    "TSeparator",
    "TSizegrip",
    "Treeview",
]


class _StyleMeta(type):
    """Meta class for BaseStyle that automatically registers all classes that inherit
    from it. This allows for easy access to the Ttk Style name, and configuration and
    map options.

    *This should never be used directly unless you know what you're doing!*

    """

    defined_styles: dict[str, "BaseStyle"] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if cls.__name__ != "BaseStyle":
            mcs.defined_styles.update({cls.ttk_style: cls})
        return cls

    def _yield_bases_in(cls, base_cls):
        """Yields all base classes of a class, excluding object and BaseStyle.

        This method is used recursively to get all base classes and their base classes,
        etc.

        """
        yield base_cls
        for b in base_cls.__bases__:
            if b is object or b is BaseStyle:
                continue
            for ba in cls._yield_bases_in(b):  # pylint: disable=no-value-for-parameter
                yield ba

    @property
    def ttk_style(cls):
        """Returns the Ttk Style name for the class.

        This is the class name concatenated with the names of all its base classes,
        separated by a period.

        """
        return ".".join(
            (
                b.__name__
                for b in cls._yield_bases_in(  # pylint: disable=no-value-for-parameter
                    cls
                )
            ),
        )

    def __getitem__(cls, stylename):
        filtered_styles = (
            {
                k[0 : -len(cls.ttk_style) - 1]: v
                for k, v in cls.defined_styles.items()
                if k.endswith(f".{cls.ttk_style}")
            }
            if cls != BaseStyle
            else cls.defined_styles
        )
        return filtered_styles[stylename]

    def define_all(cls, style: "Optional[Style]" = None):
        """Defines all styles configured by classes that extend the BaseStyle class.

        Args:
            style {Optional[Style]} -- The Ttk Style object to define the styles on.
                (default: {Style})

        """
        style = Style() if style is None else style
        for stylename, stylecls in cls.defined_styles.items():
            style.configure(stylename, **stylecls.configure)
            style.map(stylename, **stylecls.map)

    def set_style(cls, widget: Widget) -> None:
        """Sets the style of a widget to the Ttk Style represented by this class.

        Args:
            widget (Widget): The widget to set the style of.

        Returns:
            None

        """
        widget["style"] = cls.ttk_style

    def as_dict(cls) -> dict[Literal["style"], str]:
        """Returns a dictionary with the key "style" and the value of the Ttk Style name
        of the class. This is useful for setting the style of a widget using the **
        operator.

        Returns:
            dict[str, str] -- The dictionary with the key "style" and the value of
            the Ttk Style name of the class.

        """
        return {"style": cls.ttk_style}


class BaseStyle(metaclass=_StyleMeta):
    """All the base styles inherit from this class."""

    configure: dict[str, Any] = {}
    map: dict[str, list[tuple[Any, ...]]] = {}


class TProgressbar(BaseStyle):
    """Must define class Vertical(TProgressbar) or Horizontal(TScrollbar) to set
    config."""


class TScrollbar(BaseStyle):
    """Must define class Vertical(TProgressbar) or Horizontal(TScrollbar) to set
    config."""


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
