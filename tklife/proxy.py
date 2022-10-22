from dataclasses import dataclass
from collections.abc import Sequence, Mapping
from typing import TYPE_CHECKING, Any

from .skel import T_SkeletonProtocol

from .controller import ControllerABC

if TYPE_CHECKING:
    from .skel import SkeletonMixin


class TklProxyError(RuntimeError):
    """Represents an error in a proxy call"""
    pass


class CallProxyFactory(object):
    skel: Any
    def __init__(self, skel: 'SkeletonMixin') -> None:
        self.skel = skel

    def __getattr__(self, func: str):
        proxy = CallProxy(self.skel, func)
        return proxy


@dataclass(frozen=True)
class CallProxy(object):
    """Refers to a proxy call on controllers"""
    skel: 'SkeletonMixin'
    func: str

    def __call__(self, *args, **kwargs):
        if not isinstance(self.skel.controller, CallProxyFactory):
            return getattr(self.skel.controller, self.func)(*args, **kwargs)
        else:
            raise TklProxyError(
                "Cannot call. Have you assigned a controller yet?")
