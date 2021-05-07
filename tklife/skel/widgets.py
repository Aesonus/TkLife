from . import Skeleton
from tkinter import ttk
import tkinter as tk

__all__ = ['SkelMain', 'SkelFrame', 'SkelLabelFrame', 'SkelToplevel']

class SkelMain(Skeleton, tk.Tk):
    pass

class SkelFrame(Skeleton, ttk.Frame):
    pass

class SkelLabelFrame(Skeleton, ttk.Labelframe):
    pass

class SkelToplevel(Skeleton, tk.Toplevel):
    pass


