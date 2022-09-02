from tkinter import BaseWidget, Misc
from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    import tkinter
    from .skel import T_SkeletonProtocol, CreatedWidget
    from typing import Union, Any


class ControllerABC(object):
    def set_view(self, view: 'T_SkeletonProtocol') -> None:
        """
        Sets the view associated with this controller

        Arguments:
            view {T_SkeletonProtocol} -- An instance that implements SkeletonMixin methods
        """
        self.view: 'T_SkeletonProtocol' = view

    def __getattr__(self, attr: 'str') -> 'CreatedWidget':
        """
        Gets a created widget in this controller's view's created dictionary

        Arguments:
            attr {str} -- The label of the created widget

        Returns:
            CreatedWidget -- The created widget found
        """
        return self.view.created[attr]
