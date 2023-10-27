from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .skel import CreatedWidget, T_SkeletonProtocol


class ControllerABC(object):
    view: "T_SkeletonProtocol"

    def set_view(self, view: "T_SkeletonProtocol") -> None:
        """Sets the view associated with this controller.

        Arguments:
            view {T_SkeletonProtocol} -- An instance that implements SkeletonMixin methods

        """
        self.view: "T_SkeletonProtocol" = view

    def __getattr__(self, attr: "str") -> "CreatedWidget":
        """Gets a created widget in this controller's view's created dictionary.

        Arguments:
            attr {str} -- The label of the created widget

        Returns:
            CreatedWidget -- The created widget found

        """
        return self.view.created[attr]
