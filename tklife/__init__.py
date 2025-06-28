"""Make Tkinter life easier."""

from tklife import constants, controller, core, event, menu  # noqa: F401
from tklife.core import *  # noqa: F401

__all__ = ["constants", "controller", "core", "event", "menu"] + core.__all__
