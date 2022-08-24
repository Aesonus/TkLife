from dataclasses import dataclass
from collections.abc import Sequence, Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .skel import SkeletonMixin

class CallProxyFactory(object):
    def __init__(self, skel: 'SkeletonMixin') -> None:
        self.skel = skel

    def __getattr__(self, func: str):
        proxy = CallProxy(self.skel, func)
        return proxy

@dataclass(frozen=True)
class CallProxy(object):
    """Refers to a proxy on controllers"""
    skel: 'SkeletonMixin'
    func: str

    def __call__(self, *args, **kwargs):
        try:
            return getattr(self.skel.controller, self.func)(*args, **kwargs)
        except RecursionError:
            raise RuntimeError("This will be something soon")