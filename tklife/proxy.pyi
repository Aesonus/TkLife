from typing import Any
from .controller import ControllerABC as ControllerABC
from .skel import SkeletonMixin as SkeletonMixin
from collections.abc import Mapping as Mapping, Sequence as Sequence

class TklProxyError(RuntimeError): ...

class CallProxyFactory:
    skel: Any
    def __init__(self, skel: SkeletonMixin) -> None: ...
    def __getattr__(self, func: str): ...

class CallProxy:
    skel: SkeletonMixin
    func: str
    def __call__(self, *args, **kwargs): ...
    def __init__(self, skel, func) -> None: ...
