import abc
from collections import UserDict
import dataclasses
from functools import partial
import tkinter
import typing
from collections.abc import Iterable

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


class SkeletonMixin(abc.ABC):
    def __init__(self,
                 master: typing.Optional[tkinter.Misc] = None,
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
        self.__cache: dict[str, list[list]] = {
            'widgets': [[]]
        }
        self.__global_gridargs = global_grid_args if global_grid_args else {}
        self.create_all()
        self._create_menu()
        self.create_events()

    @property
    @abc.abstractmethod
    def template(self) -> Iterable[Iterable[SkelWidget]]:
        pass

    @property
    def menu_template(self):
        return {}

    def __get_cache_widget(self, row, col) -> typing.Union[tuple[SkelWidget, tkinter.Widget], None]:
        wdg_cache = self.__cache['widgets']
        return wdg_cache[row][col]

    def __set_cache_widget(self, skel_widget, widget, row, col):
        if row == len(self.__cache['widgets']):
            self.__cache['widgets'].append([])
        if col == len(self.__cache['widgets'][row]):
            self.__cache['widgets'][row].append((skel_widget, widget))
        self.__cache['widgets'][row][col] = (skel_widget, widget)


    def create_all(self):
        """
        Creates all the widgets in template. Calling subsequently will regrid all existing widgets.
        """
        index_error = False
        global_grid_args = self.__global_gridargs
        new_cache = []
        for row_index, row in enumerate(self.template):
            new_cache.append(list())
            for col_index, skel_widget in enumerate(row):
                if skel_widget is None:
                    print(row_index, *new_cache[row_index],sep="\n")
                    new_cache[row_index].append(None)
                    continue
                try:
                    cached_w = self.__get_cache_widget(row_index, col_index)
                    if cached_w is None and skel_widget is None:
                        new_cache[row_index].append(None)
                        continue
                except IndexError:
                    index_error = True
                if index_error: # Or the cache is different
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
                else:
                    w = cached_w
                new_cache[row_index].append((skel_widget, w))
                w.grid(row=row_index, column=col_index,
                       **global_grid_args,
                       **skel_widget.grid_args)
        self.__cache['widgets'] = new_cache

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

    @property
    def controller(self):
        if not self.__controller:
            return self.__proxy_factory
        else:
            return self.__controller

    @controller.setter
    def controller(self, controller: ControllerABC):
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
