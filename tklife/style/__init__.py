"""This module contains the BaseStyle class, which is the base class for all styles.

It also contains all the styles that are defined by default, and the _StyleMeta class,
which is a metaclass for BaseStyle that automatically registers all classes that inherit
from it. This allows for easy access to the Ttk Style name, and configuration and map
options.

"""
from .style import *  # noqa: F401
