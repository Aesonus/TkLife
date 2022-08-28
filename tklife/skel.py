import abc
from collections import UserDict
import dataclasses
from functools import partial
from re import L
import tkinter
import typing

from .controller import ControllerABC
from .proxy import CallProxyFactory

if typing.TYPE_CHECKING:
    from collections.abc import Iterable


class SkelWidget(typing.NamedTuple):
    widget: typing.Type[tkinter.Widget]
    init_args: dict[str, typing.Any]
    grid_args: dict[str, typing.Any]
    label: typing.Optional[str] = None


class CreatedWidget(object):
    def __init__(self, widget: tkinter.Widget,
                 textvariable: typing.Optional[tkinter.Variable] = None,
                 variable: typing.Optional[tkinter.Variable] = None,
                 listvariable: typing.Optional[tkinter.Variable] = None,
                 **custom_vars: tkinter.Variable) -> None:
        self.__widget = widget
        self.__values: dict[str, tkinter.Variable] = {
            **{
                k: v for k, v in zip(("textvariable",
                                      "variable",
                                      "listvariable",
                                      ), (textvariable,
                                          variable,
                                          listvariable,))
                if v is not None
            },
            **custom_vars
        }

    @property
    def widget(self) -> tkinter.Widget:
        return self.__widget

    @property
    def textvariable(self) -> tkinter.Variable:
        return self['textvariable']

    @property
    def variable(self) -> tkinter.Variable:
        return self['variable']

    @property
    def listvariable(self) -> tkinter.Variable:
        return self['listvariable']

    def __getattr__(self, attr: str) -> tkinter.Variable:
        returned = self.__values.get(attr)
        if returned is None:
            raise AttributeError
        else:
            return returned

    def __getitem__(self, attr: str) -> tkinter.Variable:
        returned = self.__values.get(attr)
        if returned is None:
            raise AttributeError(f"'{attr}' not found")
        else:
            return returned

    def __setitem__(self, *args):
        setattr(self, *args)

    def __setattr__(self, __name: str, __value: typing.Any) -> None:
        if f"_{self.__class__.__name__}__" in __name:
            object.__setattr__(self, __name, __value)
        else:
            raise AttributeError(
                f"Cannot set '{__name}'; {self.__class__} is read-only")

    def as_dict(self):
        return dict(**self.__values, widget=self.widget)


CreatedWidgetDict = dict[str, CreatedWidget]

class CachedWidget(typing.NamedTuple):
    widget: typing.Union[tkinter.Widget, None]
    grid_args: typing.Union[dict[str, typing.Any], None]

class SkeletonMixin(abc.ABC):
    def __init__(self,
                 master: 'typing.Optional[tkinter.Misc]' = None,
                 controller: 'typing.Optional[ControllerABC]' = None,
                 global_grid_args: 'typing.Optional[dict[str, typing.Any]]' = None,
                 **kwargs) -> None:
        # Set the controller first

        self.controller = controller
        if controller is None:
            self.__proxy_factory = CallProxyFactory(self)

        # Init the frame or whatever
        super().__init__(master, **kwargs)  # type: ignore

        self.created: CreatedWidgetDict = {}
        self.__global_gridargs = global_grid_args if global_grid_args else {}
        self.__w_cache: dict[tuple[int, int], CachedWidget] = {}
        self._create_all()
        self._create_menu()
        self.create_events()

    @property
    @abc.abstractmethod
    def template(self) -> 'Iterable[Iterable[SkelWidget]]':
        """
        - Must be implemented in child class
        - Must be declared as @property
        - Only used for inititalization

        Returns:
            An iterable yielding rows that yield columns of SkelWidgets
        """
        pass

    @property
    def menu_template(self):
        return {}

    @property
    def widget_cache(self):
        return self.__w_cache


    def __widget_create(self, skel_widget, row_index, col_index):
        if skel_widget is None:
            self.__w_cache[(row_index, col_index)] = CachedWidget(None, None)
            return None
        for arg, val in skel_widget.init_args.items():
            if isinstance(val, type(tkinter.Variable)):
                skel_widget.init_args[arg] = val()

        w = skel_widget.widget(self, **skel_widget.init_args)
        if skel_widget.label is not None:
            # And what is the vardict?
            vardict = {
                arg: val for arg, val in skel_widget.init_args.items() if isinstance(val, tkinter.Variable)
            }

            # Widgets!
            self.created[skel_widget.label] = CreatedWidget(
                widget=w, **vardict
            )
        return w

    def _create_all(self):
        """
        Creates all the widgets in template.
        """
        global_grid_args = self.__global_gridargs
        for row_index, row in enumerate(self.template):
            for col_index, skel_widget in enumerate(row):
                w = self.__widget_create(skel_widget, row_index, col_index)
                if w is None:
                    continue
                self._grid_widget(row_index, col_index, w, **global_grid_args, **skel_widget.grid_args)

    def _grid_widget(self, row, column, widget, **grid_args):
        widget.grid(row=row, column=column, **grid_args)
        self.__w_cache[row, column] = CachedWidget(widget, grid_args)

    def _create_menu(self):
        def submenu(template: dict):
            menu = tkinter.Menu(self.winfo_toplevel())  # type: ignore
            for menu_partial, data in template.items():
                if menu_partial.func == tkinter.Menu.add_command:
                    menu_partial(menu, command=data)
                elif menu_partial.func == tkinter.Menu.add_cascade:
                    if not isinstance(data, dict):
                        raise ValueError(
                            f"{menu_partial.func.__name__} must have dict for value")
                    menu_partial(menu, menu=submenu(data))
                elif menu_partial.func == tkinter.Menu.add:
                    menu_partial(menu, data)
            return menu

        template = self.menu_template
        if template:
            self.option_add("*tearOff", 0)
            main_menu = submenu(template)
            self['menu'] = main_menu

    def create_events(self):
        pass

    def append_row(self, widget_row: 'Iterable[SkelWidget]') -> int:
        """
        Appends a row

        Arguments:
            row -- A row of SkelWidgets

        Raises:
            TypeError: Raised when row is not iterable

        Returns:
            The new row index
        """
        # Find last row in cache and add 1 for new row
        max_row = -1
        for (row, col) in self.__w_cache.keys():
            if row > max_row:
                max_row = row
        new_row = max_row + 1

        # Create the widgets in the row
        for col_index, skel_widget in enumerate(widget_row):
            w = self.__widget_create(skel_widget, new_row, col_index)
            if w is not None:
                self._grid_widget(new_row, col_index, w, **self.__global_gridargs, **skel_widget.grid_args)

        return new_row

    def destroy_row(self, row_index: int):
        for (row, col), (widget, grid_args) in tuple(self.__w_cache.items()):
            if row == row_index:
                if widget is not None:
                    widget.destroy()
                del self.__w_cache[row, col]
            elif row > row_index:
                w = self.__w_cache[row, col]
                del self.__w_cache[row, col]
                self.__w_cache[row - 1, col] = w
        for (row, col), (widget, grid_args) in self.__w_cache.items():
            if widget is not None and grid_args is not None:
                widget.grid(row=row, column=col, **grid_args)

    def find_row_of(self, label: str) -> 'typing.Union[int, None]':
        """
        Finds a row of a widget having label as defined in SkelWidget

        Arguments:
            label -- Widget label

        Returns:
            The row index containing the given widget or None if not found
        """
        try:
            widget = self.created[label].widget
        except KeyError:
            return None
        else:
            for (row, __), cached in self.widget_cache.items():
                if widget == cached.widget:
                    return row
        return None


    @property
    def controller(self):
        if not self.__controller:
            return self.__proxy_factory
        else:
            return self.__controller

    @controller.setter
    def controller(self, controller: 'ControllerABC'):
        if not isinstance(controller, ControllerABC) and controller is not None:
            raise TypeError(
                f"Controller must be of type {ControllerABC.__name__}")
        self.__controller = controller
        if controller is not None:
            controller.set_view(self)


class Menu(object):

    @classmethod
    def add(cls, **opts: typing.Any):
        return partial(tkinter.Menu.add, **opts)

    @classmethod
    def command(cls, **opts: typing.Any) -> typing.Callable[[tkinter.Menu], None]:
        nf = partial(tkinter.Menu.add_command, **opts)
        return nf

    @classmethod
    def cascade(cls, **opts: typing.Any) -> typing.Callable[[tkinter.Menu], None]:
        nf = partial(tkinter.Menu.add_cascade, **opts)
        return nf
