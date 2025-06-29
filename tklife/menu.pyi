import tkinter
from typing import Any, Callable, Literal, Optional

MenuCommand = Callable[[tkinter.Menu], None]

class MenuMixin:
    def __init__(self, master: Optional[tkinter.Misc] = ..., **kwargs: Any) -> None: ...
    @property
    def menu_template(self) -> dict: ...

class Menu:
    def __new__(cls) -> None: ...
    @classmethod
    def add(cls, **opts: Any) -> MenuCommand: ...
    @classmethod
    def command(
        cls,
        label: str,
        accelerator: str = ...,
        activebackground: str = ...,
        activeforeground: str = ...,
        background: str = ...,
        bitmap: str = ...,
        columnbreak: int = ...,
        compound: Any = ...,
        font: Any = ...,
        foreground: str = ...,
        hidemargin: bool = ...,
        image: Any = ...,
        state: Literal["normal", "active", "disabled"] = ...,
        underline: int = ...,
    ) -> MenuCommand: ...
    @classmethod
    def cascade(
        cls,
        label: str,
        accelerator: Optional[str] = ...,
        activebackground: Optional[str] = ...,
        activeforeground: Optional[str] = ...,
        background: Optional[str] = ...,
        bitmap: Optional[str] = ...,
        columnbreak: Optional[int] = ...,
        command: Optional[str] = ...,
        compound: Optional[Any] = ...,
        font: Optional[Any] = ...,
        foreground: Optional[str] = ...,
        hidemargin: Optional[bool] = ...,
        image: Optional[Any] = ...,
        state: Optional[str] = ...,
        underline: Optional[int] = ...,
    ) -> MenuCommand: ...
