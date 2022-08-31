from tkinter import BaseWidget, Misc
from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    import tkinter
    from .skel import T_SkeletonProtocol
    from typing import Union, Any



class ControllerABC(object):
    def set_view(self, view: 'T_SkeletonProtocol'):
        self.view: 'T_SkeletonProtocol' = view

    def __getattr__(self, attr: 'str'):
        return self.view.created[attr]
