import abc
import tkinter
import typing

from .controller import ControllerABC


class SkelWidget(typing.NamedTuple):
    widget: typing.Type[tkinter.Misc]
    init_args: dict[str, typing.Any]
    grid_args: dict[str, typing.Any]
    label: typing.Optional[str] = None


class CreatedVariables(typing.TypedDict, total=False):
    textvariable: tkinter.Variable
    variable: tkinter.Variable
    listvariable: tkinter.Variable


class CreatedWidget(CreatedVariables):
    widget: tkinter.Misc


class SkeletonMixin(abc.ABC):
    def __init__(self, master: tkinter.Misc, controller: 'ControllerABC', global_grid_args=None, **kwargs) -> None:
        # Set the controller first
        self.controller = controller

        # Init the frame or whatever
        super().__init__(master, **kwargs)

        self.created: dict[str, CreatedWidget] = {}
        self._create_all(global_grid_args if global_grid_args else {})
        self.create_events()

    @property
    @abc.abstractmethod
    def template(self) -> typing.Iterable[typing.Iterable[SkelWidget]]:
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
                    self.created[skel_widget.label] = {
                        'widget': w,
                        **vardict,
                    }

    def create_events(self):
        pass

    @property
    def controller(self):
        return self.__controller

    @controller.setter
    def controller(self, controller: ControllerABC):
        if not isinstance(controller, ControllerABC):
            raise TypeError(
                f"Controller must be of type {ControllerABC.__name__}")
        self.__controller = controller
        controller.set_view(self)
