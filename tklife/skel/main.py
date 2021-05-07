import logging
import tkinter.ttk as ttk
from abc import abstractmethod
from tkinter import Frame, LabelFrame, Variable, Widget
from tkinter.constants import COMMAND
from typing import (Any, Dict, Iterable, Literal, Mapping, Tuple, Type,
                    TypeVar, Union)

from ..constants import COLUMN, ROW, TEXTVARIABLE, VARIABLE
from ..event import EventsEnum
from .dummy import DummyAttr

_Container = TypeVar('_Container', Frame, ttk.Frame,
                     LabelFrame, ttk.Labelframe, 'Skeleton')
_WRow = TypeVar(
    '_WRow', bound=Iterable[Iterable[Tuple[Type[Widget], Mapping[str, Any]]]])
_LRow = TypeVar('_LRow', bound=Iterable[Iterable[Mapping[str, Any]]])
_LCfg = TypeVar(
    '_LCfg', bound=Tuple[Iterable[Dict[str, Any]], Iterable[Dict[str, Any]]])

__all__ = [
    'tk_vars',
    'widgets',
    'layout',
    'layout_cfg',
    'Skeleton',
]

T_Name = str
T_TkVarDef = Tuple[T_Name, Type[Variable], Mapping[str, str]]
T_TkVarLvlDef = Tuple[T_Name, Iterable[T_TkVarDef]]
T_TkVarCfg = Iterable[Union[T_TkVarDef, T_TkVarLvlDef]]


class TkVarsMap(dict):
    """
    Behaves like a normal dictionary (except in a special case), but has a few extra methods and features
    that are useful for tkinter applications:

    + Set attr and get attr will set and get the underlying Variable
    + Nested TkVars objects will only set/get the TkVars instance
    """

    def __getattr__(self, name):
        try:
            if isinstance(self[name], TkVarsMap):
                ret = self[name]
            else:
                ret = self[name].get()
            return ret
        except KeyError:
            raise AttributeError

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self and isinstance(self[name], Variable):
            self[name].set(value=value)
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError


def tk_vars(master: _Container, var_cfg: T_TkVarCfg):
    logging.getLogger('skel.tk_vars').debug('Creating vars')

    def flatten(var_cfg=var_cfg, var_obj=None):
        var_obj = TkVarsMap() if var_obj is None else var_obj
        for name, *params in var_cfg:
            if len(params) > 1:
                # This is me, go ahead and put me down
                # in the current var_obj
                vartype, kwargs = params
                kw = {
                    'master': master
                }
                kw.update(**kwargs)
                var_obj[name] = vartype(**kw)
                logging.getLogger('skel.tk_vars').debug(
                    'Created %s with name %s', vartype, name
                )
            elif hasattr(var_obj, name):
                cfg, = params
                logging.getLogger('skel.tk_vars').debug(
                    'Ascending to level %s', name
                )
                flatten(cfg, var_obj[name])
            else:
                logging.getLogger('skel.tk_vars').debug(
                    'Ascending to level %s', name
                )
                cfg, = params
                upper_vars = var_obj.__class__()
                var_obj[name] = flatten(cfg, upper_vars)
        return var_obj
    master.vars_ = flatten()


def widgets(frame: _Container, widget_rows: _WRow) -> None:
    for index, row in enumerate(widget_rows):
        for w, kw in row:
            kwargs = frame._widget_kw.copy()
            kwargs.update(kw)
            # Use late binding for variables if needed
            for key in (VARIABLE, TEXTVARIABLE):
                try:
                    value = kwargs.pop(key)
                    if isinstance(value, DummyAttr):
                        kwargs[key] = value.get_real(frame.vars_)
                    else:
                        kwargs[key] = value
                except KeyError:
                    # Do nothing on purpose
                    pass
            created = w(master=frame, **kwargs)
            # Use late binding on event generation if needed
            try:
                event = kwargs.pop(COMMAND)
                if isinstance(event, EventsEnum):
                    created.configure(command=event.generate(created))
            except KeyError:
                # Do nothing on purpose
                pass
        if frame._debug:
            logging.getLogger('skel.widgets').debug(
                "'%s': row %s: %s", frame, index, row)


def layout(frame: _Container, layout_rows: _LRow) -> None:
    mod = 0
    for y, row in enumerate(layout_rows):
        for x, kw in enumerate(row):
            w = frame.winfo_children()[x + y + mod]
            kwargs = {
                COLUMN: x,
                ROW: y,
                **frame._grid_kw
            }
            kwargs.update(kw)
            w.grid(**kwargs)
        mod += len(row) - 1
        if frame._debug:
            logging.getLogger('skel.layout').debug(
                "'%s': row %s: %s", frame, y, row)


def layout_cfg(frame: _Container, configuration: _LCfg) -> None:
    col_cfg, row_cfg = configuration
    for col, cfg in enumerate(col_cfg):
        frame.grid_columnconfigure(col, **cfg)
        if frame._debug:
            logging.getLogger('skel.layout_cfg').debug(
                "'%s': col %s: %s", frame, col, cfg)
    for row, cfg in enumerate(row_cfg):
        frame.grid_rowconfigure(row, **cfg)
        if frame._debug:
            logging.getLogger('skel.layout_cfg').debug(
                "'%s': row %s: %s", frame, row, cfg)


class Skeleton(object):
    """
    Mixin to be used with a container type widget to elegantly configure its
    widgets. This should come BEFORE the tk widget. (eg: class Test(Skeleton, Tk): ...)
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.skeleton_configure()
        self._dummy_vars = DummyAttr()
        self.vars_: TkVarsMap
        for func, input in self.skeleton(self._dummy_vars).items():
            if self._debug:
                logging.getLogger(__name__).debug('Call: %s', func)
            func(self, input)

    @abstractmethod
    def skeleton_configure(self, debug: bool = False, widget_kw: Mapping = None, grid_kw: Mapping = None):
        """
        Configures skeleton configuration settings. Override this in your child class
        and use super().skeleton_configure(**kwargs) to set specific settings. This method must
        be implemented

        Keyword Arguments:
            vars {Type[TkVars]} -- DEPRECATED: Sets the vars to be used in the skeleton method (default: {None})
            debug {bool} -- Logs debug information if set to true (default: {False})
            widget_kw {Mapping} -- kwargs that are used with every widget instantiation. These are updated with each discreet widget's kwargs to allow for overriding of the default value (default: {dict})
            grid_kw {Mapping} -- kwargs that are used with every widget grid method. These are updated with each discreet widget's grid kwargs to allow for overriding of the default value (default: {dict})
        """
        self._debug = debug
        if widget_kw is None:
            widget_kw = {}
        if grid_kw is None:
            grid_kw = {}
        self._widget_kw = widget_kw
        self._grid_kw = grid_kw

    @abstractmethod
    def skeleton(self, vars: DummyAttr) -> Dict:
        """Defines the skeleton for creating widgets and layout and layout configuration"""
