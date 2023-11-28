"""This module contains the ControllerABC class, which is an abstract base class for
controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import CreatedWidget
    from .core import SkeletonProtocol


class ControllerABC:
    """Abstract base class for controllers.

    Controllers allow for access to created widgets in the view via attribute access.

    Attributes:
        view (SkeletonProtocol): The view associated with this controller

    """

    view: SkeletonProtocol

    def set_view(self, view: SkeletonProtocol) -> None:
        """Sets the view associated with this controller.

        Arguments:
            view (SkeletonProtocol): An instance that implements SkeletonMixin
                methods

        """
        self.view: SkeletonProtocol = view

    def __getattr__(self, attr: str) -> CreatedWidget:
        """Gets a created widget in this controller's view's created dictionary.

        Arguments:
            attr (str): The label of the created widget

        Returns:
            CreatedWidget: The created widget found

        """
        return self.view.created[attr]
