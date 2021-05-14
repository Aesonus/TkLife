import tkinter as tk
from tkinter import ttk

from . import Skeleton

__all__ = ['SkelMain', 'SkelFrame', 'SkelLabelFrame', 'SkelToplevel']

class SkelMain(Skeleton, tk.Tk):
    pass

class SkelFrame(Skeleton, ttk.Frame):
    pass

class SkelLabelFrame(Skeleton, ttk.Labelframe):
    pass

class SkelToplevel(Skeleton, tk.Toplevel):
    pass

