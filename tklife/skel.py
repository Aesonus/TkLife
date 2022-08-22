import tkinter
import typing

if typing.TYPE_CHECKING:
    from .controller import ControllerABC


class SkelWidget(typing.NamedTuple):
    widget: tkinter.Misc
    init_args: dict[str, typing.Any]
    grid_args: dict[str, typing.Any]
    label: typing.Optional[str] = None


class SkeletonMixin(object):
    def __init__(self, master: tkinter.Misc, controller: 'ControllerABC', **kwargs) -> None:
        # Set the controller first
        self.controller = controller

        # Init the frame or whatever
        super().__init__(master, **kwargs)

        self.created = {}
        self.create_all()

    def create_all(self):
        for row_index, row in enumerate(self.template):
            for col_index, skel_widget in enumerate(row):
                if skel_widget is None:
                    continue
                for arg, val in skel_widget.init_args.items():
                    if isinstance(val, type(tkinter.Variable)):
                        skel_widget.init_args[arg] = val()

                w = skel_widget.widget(self, **skel_widget.init_args)
                w.grid(row=row_index, column=col_index,
                       **skel_widget.grid_args)
                if skel_widget.label is not None:
                    vardict = {
                        arg: val for arg, val in skel_widget.init_args.items() if isinstance(val, tkinter.Variable)
                    }
                    self.created[skel_widget.label] = {
                        'widget': w,
                        **vardict
                    }

    @property
    def controller(self):
        return self.__controller

    @controller.setter
    def controller(self, controller: 'ControllerABC'):
        self.__controller = controller
        controller.set_view(self)
