"""A placeholder file until this functionality is implemented"""
from tklife.controller import ControllerABC

class MenuMeta(type):
    pass


class Menu(metaclass=MenuMeta):
    def __init__(self, controller: 'ControllerABC') -> None:
        self.controller = controller

def menu_item(func):
    return func


class MainMenu(Menu):
    class File(Menu):  # Use classes for submenus
        # Use class attributes for coptions in the add_cascade method
        underline = 0
        label = "File"  # Should default to the class name if not defined
        accelerator = ""
        
        @menu_item
        def open(self, underline=0, label="Open"):  # Menu items should be decorated with the menu_item decorator.
                                                    # coptions are set in the function signature using kwargs
                                                    # They should return a callable, which is the command associated with the item
            return self.controller.command

        @menu_item
        def separator(self):  # Naming the menu item func "separator" will put in a separator.
                              # Return values are ignored
            pass

        @menu_item
        def exit(self, underline=1, label="Exit"):
            return lambda __: self.controller.view.destroy()

        @menu_item
        def separator(self):
            pass