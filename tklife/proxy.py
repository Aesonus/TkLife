"""Contains the CallProxy and CallProxyFactory classes.

These are used to create stand-ins for controller calls that can be used before the
controller has been assigned to the skeleton.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from tklife.controller import ControllerABC
    from tklife.core import SkeletonMixin


T_Controller = TypeVar(  # pylint: disable=invalid-name
    "T_Controller",
    bound="ControllerABC|None",
)


class TklProxyError(RuntimeError):
    """Represents an error in a proxy call."""


class CallProxyFactory(Generic[T_Controller]):
    """Factory for CallProxy objects.

    This is used to create a CallProxy object that will call the controller's function
    when called.

    Args:
        skel (SkeletonMixin): The skeleton that will be used to create the CallProxy
            object.

    Attributes:
        skel (SkeletonMixin): The skeleton that will be used to create the CallProxy
            object.

    """

    skel: SkeletonMixin[T_Controller]

    def __init__(self, skel: SkeletonMixin[T_Controller]) -> None:
        self.skel = skel

    def __getattr__(self, func: str) -> CallProxy:
        """Creates a CallProxy object that will call the controller's function when
        called.

        Args:
            func (str): The name of the function to call.

        Returns:
            CallProxy: The CallProxy object that will call the controller's function

        """
        proxy = CallProxy(self.skel, func)
        return proxy


@dataclass(frozen=True)
class CallProxy(Generic[T_Controller]):
    """Stand-in for a controller call. When called, it will call the controller's method
    or raise an error if the controller has not been assigned yet.

    Args:
        skel (SkeletonMixin): The skeleton that will be used to call the controller's
            method.
        func (str): The name of the function to call.

    Attributes:
        skel (SkeletonMixin): The skeleton that will be used to call the controller's
            method.
        func (str): The name of the function to call.

    """

    skel: SkeletonMixin[T_Controller]
    func: str

    def __call__(self, *args, **kwargs):
        if not isinstance(self.skel.controller, CallProxyFactory):
            return getattr(self.skel.controller, self.func)(*args, **kwargs)

        raise TklProxyError("Cannot call. Have you assigned a controller yet?")
