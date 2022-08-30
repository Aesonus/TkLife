from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import tkinter
    from .skel import SkeletonMixin
    from typing import Union


class ControllerABC(object):
    def set_view(self, view: 'Union[SkeletonMixin, tkinter.Widget]'):
        self.view: 'Union[SkeletonMixin, tkinter.Misc]' = view

    def __getattr__(self, attr: 'str'):
        return self.view.created[attr]
