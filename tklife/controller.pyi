from .skel import CreatedWidget as CreatedWidget, T_SkeletonProtocol as T_SkeletonProtocol
from tkinter import BaseWidget as BaseWidget, Misc as Misc

class ControllerABC:
    view: T_SkeletonProtocol
    def set_view(self, view: T_SkeletonProtocol) -> None: ...
    def __getattr__(self, attr: str) -> CreatedWidget: ...
