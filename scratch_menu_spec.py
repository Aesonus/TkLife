"""A placeholder file until this functionality is implemented"""
from functools import wraps
from tkinter import Tk
from types import SimpleNamespace
from typing import Any, Callable
from tklife.controller import ControllerABC
from tklife.skel import SkeletonMixin

class MenuMeta(type):
    def __new__(mcls, name, bases, namespace: dict[str, Any]):
        def separator(func):
            return classmethod(func)
        commands = SimpleNamespace(
            separator=separator,
            radiobutton=classmethod,
            checkbutton=classmethod,
            command=classmethod,
        )

        namespace['add'] = commands
        for name, value in tuple(namespace.items()):
            if not isinstance(value, (mcls, classmethod)) and isinstance(value, Callable):
                namespace[name] = commands.command(value)

        return super().__new__(mcls, name, bases, namespace)

    #@property
    #def add(cls):
    #    def separator(func):
    #        return classmethod(func)
    #    return SimpleNamespace(
    #        separator=separator,
    #        radiobutton=classmethod,
    #        checkbutton=classmethod,
    #        command=classmethod,
    #    )



class Menu(metaclass=MenuMeta):
    pass


class Main(SkeletonMixin, Tk):
    def __init__(self, controller, **kwargs) -> None:
        super().__init__(None, controller, **kwargs)

    @property
    def template(self):
        return []

    class MainMenu(Menu):
        class File(Menu):  # Use classes for submenus
            # Use class attributes for coptions in the add_cascade method
            underline = 0
            label = "File"  # Should default to the class name if not defined
            accelerator = ""

            def open(cls, underline=0, label="Open"):  # Menu items should be decorated with the menu_item decorator.
                                                        # coptions are set in the function signature using kwargs
                                                        # They should return a callable, which is the command associated with the item
                return cls.controller.command

            @Menu.add.separator
            def open_close_separator(cls):  # Naming the menu item func "separator" will put in a separator.
                                 # Return values are ignored
                pass

            def exit(cls, underline=1, label="Exit"):
                return lambda __: cls.controller.view.destroy()

            @Menu.add.separator
            def separator(cls):
                pass

