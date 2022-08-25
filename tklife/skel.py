import abc
from collections import UserDict
import dataclasses
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
                 master: typing.Optional[tkinter.Misc]=None,
                 controller: 'typing.Optional[ControllerABC]' = None,
                 global_grid_args=None,
                 **kwargs) -> None:
        # Set the controller first

        self.controller = controller
        if controller is None:
            self.__proxy_factory = CallProxyFactory(self)

        # Init the frame or whatever

        super().__init__(master, **kwargs)  # type: ignore

        self.created: CreatedWidgetDict = {}
        self._create_all(global_grid_args if global_grid_args else {})
        self.create_events()

    @property
    @abc.abstractmethod
    def template(self) -> Iterable[Iterable[SkelWidget]]:
        pass

    def _create_all(self, global_grid_args: dict):
        for row_index, row in enumerate(self.template):
            for col_index, skel_widget in enumerate(row):
                if skel_widget is None:
                    continue
                for arg, val in skel_widget.init_args.items():
                    if isinstance(val, type(tkinter.Variable)):
                        skel_widget.init_args[arg] = val()

                w = skel_widget.widget(self, **skel_widget.init_args)
                w.grid(row=row_index, column=col_index,
                       **global_grid_args,
                       **skel_widget.grid_args)
                if skel_widget.label is not None:
                    # And what is the vardict?
                    vardict = {
                        arg: val for arg, val in skel_widget.init_args.items() if isinstance(val, tkinter.Variable)
                    }

                    # Widgets!
                    self.created[skel_widget.label] = CreatedWidget(
                        widget=w, **vardict
                    )

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
