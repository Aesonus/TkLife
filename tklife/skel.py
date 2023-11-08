"""Defines the SkelWidget, CreatedWidget, CachedWidget, SkeletonMixin, and MenuMixin."""

from __future__ import annotations

import abc
import dataclasses
import tkinter
import typing
from functools import partial, reduce

from .controller import ControllerABC
from .proxy import CallProxyFactory

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

    from .event import BaseEvent

__all__ = [
    "SkelWidget",
    "CreatedWidget",
    "CachedWidget",
    "SkeletonMixin",
    "MenuMixin",
]


class SkelEventDef(typing.TypedDict):
    """Used in conjunction with `SkeletonMixin.events` attribute to define events.

    Attributes:

        event (BaseEvent) -- The event to bind
        action (Callable[[tkinter.Event], Literal['break'] | None]) -- The action to
            bind
        bind_method (Literal['bind', 'bind_tag', 'bind_all']) -- The bind method to use
        widget (tkinter.Misc) -- The widget to bind to. This may be
            ommitted, and will default to self.
        add (Literal['', '+']) -- The add argument to pass to the bind method. This may
            be ommitted, and will default to ''. If you want to add to an existing bind,
            use '+'. If you want to replace an existing bind, use ''.

    """

    event: BaseEvent
    action: typing.Callable[[tkinter.Event], typing.Literal["break"] | None]
    bind_method: typing.Literal["bind", "bind_tag", "bind_all", "bind_class"]
    widget: typing.NotRequired[tkinter.Misc]
    add: typing.NotRequired[typing.Literal["", "+"]]


@dataclasses.dataclass(frozen=True)
class SkelWidget:
    """Represents a widget in a skeleton.

    Args:
        widget (typing.Type[tkinter.Widget]): The widget class
        init_args (dict[str, typing.Any]): The init arguments for the widget
        grid_args (dict[str, typing.Any]): The grid arguments for the widget
        label (typing.Optional[str]): The label of the widget

    Attributes:
        widget (typing.Type[tkinter.Widget]): The widget class
        init_args (dict[str, typing.Any]): The init arguments for the widget
        grid_args (dict[str, typing.Any]): The grid arguments for the widget
        label (typing.Optional[str]): The label of the widget

    """

    widget: typing.Type[tkinter.Widget]
    init_args: dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    grid_args: dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    label: typing.Optional[str] = None

    def __iter__(self):
        return iter((self.widget, self.init_args, self.grid_args, self.label))

    def init(self, **merge_init_args: typing.Any) -> SkelWidget:
        """Creates a new SkelWidget with the same widget and grid_args as the current
        SkelWidget, but with updated init_args.

        Args:
            **merge_init_args: Additional or updated init arguments to merge with the
                current SkelWidget's init_args.

        Returns:
            SkelWidget: The new SkelWidget with the updated init_args.

        """
        return SkelWidget(
            self.widget,
            {**self.init_args, **merge_init_args},
            self.grid_args,
            self.label,
        )

    def grid(self, **merge_grid_args: typing.Any) -> SkelWidget:
        """Creates a new SkelWidget with the same widget and init_args as the current
        SkelWidget, but with updated grid_args.

        Args:
            **merge_grid_args: Additional or updated grid arguments to merge with the
                current SkelWidget's grid_args.

        Returns:
            SkelWidget: The new SkelWidget with the updated grid_args.

        """
        return SkelWidget(
            self.widget,
            self.init_args,
            {**self.grid_args, **merge_grid_args},
            self.label,
        )

    def set_label(self, new_label: str) -> SkelWidget:
        """Sets the label of the widget.

        Args:
            new_label (str): The new label

        Returns:
            SkelWidget -- The new SkelWidget with the new label

        """
        return SkelWidget(self.widget, self.init_args, self.grid_args, new_label)


T_Widget = typing.TypeVar(  # pylint: disable=invalid-name
    "T_Widget",
    tkinter.Widget,
    tkinter.Misc,
)


class CreatedWidget(typing.Generic[T_Widget]):
    """Stores a widget and its variables.

    Args:
        widget (T_Widget): The widget
        textvariable (typing.Optional[tkinter.Variable]): The textvariable of the widget
        variable (typing.Optional[tkinter.Variable]): The variable of the widget
        listvariable (typing.Optional[tkinter.Variable]): The listvariable of the widget
        **custom_vars (tkinter.Variable): Any other variables

    Attributes:
        widget (T_Widget): The widget
        textvariable (tkinter.Variable): The textvariable of the widget
        variable (tkinter.Variable): The variable of the widget
        listvariable (tkinter.Variable): The listvariable of the widget

    """

    def __init__(
        self,
        widget: T_Widget,
        textvariable: typing.Optional[tkinter.Variable] = None,
        variable: typing.Optional[tkinter.Variable] = None,
        listvariable: typing.Optional[tkinter.Variable] = None,
        **custom_vars: tkinter.Variable,
    ) -> None:
        self.__widget: T_Widget = widget
        self.__values: dict[str, tkinter.Variable] = {
            **{
                k: v
                for k, v in zip(
                    (
                        "textvariable",
                        "variable",
                        "listvariable",
                    ),
                    (
                        textvariable,
                        variable,
                        listvariable,
                    ),
                )
                if v is not None
            },
            **custom_vars,
        }

    @property
    def widget(self) -> T_Widget:
        """Returns the widget.

        Returns:
            T_Widget -- The widget

        """
        return self.__widget

    @property
    def textvariable(self) -> tkinter.Variable:
        """Returns the textvariable of the widget.

        Returns:
            tkinter.Variable -- The textvariable of the widget

        Raises:
            IndexError: Raised when the widget does not have a textvariable

        """
        return self["textvariable"]

    @property
    def variable(self) -> tkinter.Variable:
        """Returns the variable of the widget.

        Returns:
            tkinter.Variable -- The variable of the widget

        Raises:
            IndexError: Raised when the widget does not have a variable

        """
        return self["variable"]

    @property
    def listvariable(self) -> tkinter.Variable:
        """Returns the listvariable of the widget.

        Returns:
            tkinter.Variable -- The listvariable of the widget

        Raises:
            IndexError: Raised when the widget does not have a listvariable

        """
        return self["listvariable"]

    def __getattr__(self, attr: str) -> tkinter.Variable:
        returned = self.__values.get(attr)
        if returned is None:
            raise AttributeError(f"'{attr}' not found")

        return returned

    def __getitem__(self, attr: str) -> tkinter.Variable:
        returned = self.__values.get(attr)
        if returned is None:
            raise AttributeError(f"'{attr}' not found")

        return returned

    def __setitem__(self, *args):
        setattr(self, *args)

    def __setattr__(self, __name: str, __value: typing.Any) -> None:
        if f"_{self.__class__.__name__}__" in __name:
            object.__setattr__(self, __name, __value)
        else:
            raise AttributeError(
                f"Cannot set '{__name}'; {self.__class__} is read-only"
            )

    def as_dict(self) -> dict[str, typing.Any]:
        """Returns a dict of the widget and its variables.

        Returns:
            dict[str, typing.Any] -- The widget and its variables

        """
        return {**self.__values, "widget": self.widget}


CreatedWidgetDict = dict[str, CreatedWidget]


class CachedWidget(typing.NamedTuple):
    """Stores a widget and its grid arguments."""

    widget: typing.Union[tkinter.Widget, None]
    grid_args: typing.Union[dict[str, typing.Any], None]


class SkeletonProtocol(typing.Protocol):
    """Protocol for SkeletonMixin."""

    @property
    def controller(self) -> ControllerABC | CallProxyFactory:
        """Returns the controller or a call proxy factory that will call controller."""

    created: CreatedWidgetDict


class _SkeletonMeta(abc.ABCMeta):
    def __new__(mcs, name, bases: tuple[type, ...], namespace):
        if typing.Generic not in bases and len(bases) > 1 and bases[0] != SkeletonMixin:
            raise TypeError(f"{SkeletonMixin} should be first base class")
        return super().__new__(mcs, name, bases, namespace)


class _Skel(metaclass=_SkeletonMeta):  # pylint: disable=too-few-public-methods
    pass


class SkeletonMixin(_Skel):
    """Must use this mixin first.

    Optionally can add a MenuMixin. Then you put the Widget class to use.

    """

    created: CreatedWidgetDict

    def __init__(
        self,
        master: typing.Optional[tkinter.Misc] = None,
        controller: typing.Optional[ControllerABC] = None,
        global_grid_args: typing.Optional[dict[str, typing.Any]] = None,
        proxy_factory: typing.Optional[CallProxyFactory] = None,
        **kwargs,
    ) -> None:
        # Set the controller first
        self.__controller = None
        if controller is None:
            self.__proxy_factory = (
                CallProxyFactory(self) if proxy_factory is None else proxy_factory
            )
        else:
            self.controller = controller

        self.__before_init__()
        # Init the frame or the menu mixin... or not
        super().__init__(master, **kwargs)  # type: ignore
        self.__after_init__()

        self.created: CreatedWidgetDict = {}
        self.__global_gridargs = global_grid_args if global_grid_args else {}
        self.__w_cache: dict[tuple[int, int], CachedWidget] = {}
        self._create_all()
        self._grid_config()
        self.__after_widgets__()
        self._create_events()

    def __before_init__(self):
        """Hook that is called immediately before super().__init__ is called."""

    def __after_init__(self):
        """Hook that is called immediately after super().__init__ is called, but before
        creating child widgets and events."""

    def __after_widgets__(self):
        """Hook that is called immediately after creating child widgets, but before
        creating events."""

    @property
    @abc.abstractmethod
    def template(self) -> Iterable[Iterable[SkelWidget | None]]:
        """
        - Must be implemented in child class
        - Must be declared as @property
        - Only used for inititalization

        Returns:
            An iterable yielding iterables that yield a SkelWidget
        """

    @property
    def grid_config(
        self,
    ) -> tuple[
        typing.Iterable[dict[str, typing.Any]], typing.Iterable[dict[str, typing.Any]]
    ]:
        """Returns the grid configuration for the widget. This can be overridden to
        provide a custom grid configuration.

        Returns:
            tuple[Iterable[dict[str, typing.Any]], Iterable[dict[str, typing.Any]]] --
                Row and column config

        """
        return [], []

    @property
    def widget_cache(self) -> dict[tuple[int, int], CachedWidget]:
        """Stores the widgets created as well as grid cooridates and arguments.

        Returns:
            dict[tuple[int, int], CachedWidget] -- Widget cache

        """
        return self.__w_cache

    def __widget_create(self, skel_widget, row_index, col_index):
        if skel_widget is None:
            self.__w_cache[(row_index, col_index)] = CachedWidget(None, None)
            return None
        for arg, val in skel_widget.init_args.items():
            if isinstance(val, type(tkinter.Variable)):
                skel_widget.init_args[arg] = val()

        w = skel_widget.widget(self, **skel_widget.init_args)
        if skel_widget.label is not None:
            # And what is the vardict?
            vardict = {
                arg: val
                for arg, val in skel_widget.init_args.items()
                if isinstance(val, tkinter.Variable)
            }

            # Widgets!
            self.created[skel_widget.label] = CreatedWidget(widget=w, **vardict)
        return w

    def _create_all(self):
        """Creates all the widgets in template."""
        global_grid_args = self.__global_gridargs
        for row_index, row in enumerate(self.template):
            for col_index, skel_widget in enumerate(row):
                w = self.__widget_create(skel_widget, row_index, col_index)
                if w is None:
                    continue
                self._grid_widget(
                    row_index, col_index, w, **global_grid_args, **skel_widget.grid_args
                )

    def _grid_config(self):
        """Configures the grid."""
        rows, cols = self.grid_config
        for index, col in enumerate(cols):
            if col:
                self.columnconfigure(index, **col)
        for index, row in enumerate(rows):
            if row:
                self.rowconfigure(index, **row)

    def _grid_widget(self, row, column, widget, **grid_args):
        """Grids a widget."""
        widget.grid(row=row, column=column, **grid_args)
        self.__w_cache[row, column] = CachedWidget(widget, grid_args)

    def _create_events(self):
        """Binds events to widgets."""
        for event_def in self.events:
            bind_method = getattr(event_def["event"], event_def["bind_method"])
            widget = event_def.get("widget", self)
            add = event_def.get("add", "")
            bind_method(widget, event_def["action"], add=add)

    @property
    def events(self) -> Iterable[SkelEventDef]:
        """Override this property to define events.

        Must return an iterable of SkelEventDef. The default implementation returns an
        empty iterable.

        Returns:
            Iterable[SkelEventDef] -- An iterable of SkelEventDef

        """
        return ()

    def append_row(self, widget_row: Iterable[typing.Union[SkelWidget, None]]) -> int:
        """Appends a row.

        Arguments:
            row -- A row of SkelWidgets (use None for empty cells)

        Raises:
            TypeError: Raised when row is not iterable

        Returns:
            int -- The new row index

        """
        # Find last row in cache and add 1 for new row
        max_row = -1
        for row, __ in self.__w_cache:
            if row > max_row:
                max_row = row
        new_row = max_row + 1

        # Create the widgets in the row
        for col_index, skel_widget in enumerate(widget_row):
            w = self.__widget_create(skel_widget, new_row, col_index)
            if w is not None:
                self._grid_widget(
                    new_row,
                    col_index,
                    w,
                    **self.__global_gridargs,
                    # Ignore the typing error because we have already checked for None
                    **skel_widget.grid_args,  # type: ignore
                )

        return new_row

    def insert_row_at(
        self, index: int, widget_row: Iterable[typing.Union[SkelWidget, None]]
    ) -> int:
        """Inserts a row at the given index.

        Args:
            index (int): The index to insert the row at
            widget_row (Iterable[typing.Union[SkelWidget, None]]): The row to insert

        Raises:
            TypeError: Raised when widget_row is not iterable
            IndexError: Raised when index is out of range

        Returns:
            int: The new row index

        """
        if index == 1 + reduce(
            lambda carry, value: max(carry, value[0]), self.widget_cache.keys(), 0
        ):
            self.append_row(widget_row)
        else:
            i_row = iter(widget_row)
            for (row, col), (widget, grid_args) in tuple(self.__w_cache.items()):
                if row < index:
                    continue
                if row == index:
                    # Make the insert
                    skel_widget = next(i_row)
                    new_widget = self.__widget_create(skel_widget, row, col)
                    if new_widget is not None:
                        self._grid_widget(
                            row,
                            col,
                            new_widget,
                            **self.__global_gridargs,
                            # Ignore the typing error because we have already checked
                            # for None (This check was done in __widget_create)
                            **skel_widget.grid_args,  # type: ignore
                        )
                    else:
                        self.__w_cache[row, col] = CachedWidget(None, None)
                    if widget is not None:
                        self._grid_widget(
                            row + 1, col, widget, **grid_args if grid_args else {}
                        )
                    else:
                        self.__w_cache[row + 1, col] = CachedWidget(None, None)
                elif row > index:
                    # Shift row
                    if (widget, grid_args) != (None, None):
                        self._grid_widget(
                            row + 1, col, widget, **grid_args
                        )  # type: ignore
                    else:
                        self.__w_cache[row + 1, col] = CachedWidget(None, None)
        return index

    def destroy_row(self, row_index: int) -> None:
        """Destroys the row at given index.

        Arguments:
            row_index {int} -- Index of the row to delete

        """
        for (row, col), (widget, grid_args) in tuple(self.__w_cache.items()):
            if row == row_index:
                if widget in (c.widget for c in self.created.values()):
                    ind = [k for k, v in self.created.items() if v.widget == widget][0]
                    del self.created[ind]
                if widget is not None:
                    widget.destroy()
                del self.__w_cache[row, col]
            elif row > row_index:
                w = self.__w_cache[row, col]
                del self.__w_cache[row, col]
                self.__w_cache[row - 1, col] = w
        for (row, col), (widget, grid_args) in self.__w_cache.items():
            if widget is not None and grid_args is not None:
                widget.grid(row=row, column=col, **grid_args)

    def find_row_of(self, label: str) -> typing.Union[int, None]:
        """Finds a row of a widget having label as defined in SkelWidget.

        Arguments:
            label -- Widget label

        Returns:
            The row index containing the given widget or None if not found

        """
        try:
            widget = self.created[label].widget
        except KeyError:
            return None

        for (row, __), cached in self.widget_cache.items():
            if widget == cached.widget:
                return row
        return None

    @property
    def controller(self) -> typing.Union[CallProxyFactory, ControllerABC]:
        """Returns the controller or a call proxy factory that will call controller
        methods if the controller is not set yet.

        Returns:
            typing.Union[CallProxyFactory, ControllerABC] -- Call proxy or Controller
            instance

        """
        if not self.__controller:
            return self.__proxy_factory

        return self.__controller

    @controller.setter
    def controller(self, controller: ControllerABC):
        """Sets the controller.

        Arguments:
            controller {ControllerABC} -- An instance of a controller

        Raises:
            TypeError: Raised when the controller type is not valid

        """
        if not isinstance(controller, ControllerABC) and controller is not None:
            raise TypeError(f"Controller must be of type {ControllerABC.__name__}")
        self.__controller = controller
        if controller is not None:
            controller.set_view(self)


MenuCommand = typing.Callable[[tkinter.Menu], None]


class MenuMixin(abc.ABC):
    """Mixin to allow for a menu to be configured.

    Must appear after SkeletonMixin, but before the tkinter Widget. Must impliment the
    menu_template() property method.

    """

    def __init__(
        self, master: typing.Optional[tkinter.Misc] = None, **kwargs: typing.Any
    ) -> None:
        # Init the frame or the menu mixin... or not
        super().__init__(master, **kwargs)  # type: ignore
        self._create_menu()

    @property
    @abc.abstractmethod
    def menu_template(self) -> dict:
        """Returns a dict that is used to create the menu."""

    def _create_menu(self):
        def submenu(template: dict):
            menu = tkinter.Menu(self.winfo_toplevel())  # type: ignore
            for menu_partial, data in template.items():
                if menu_partial.func == tkinter.Menu.add_command:
                    menu_partial(menu, command=data)
                elif menu_partial.func == tkinter.Menu.add_cascade:
                    if not isinstance(data, dict):
                        raise ValueError(
                            f"{menu_partial.func.__name__} must have dict for value"
                        )
                    menu_partial(menu, menu=submenu(data))
                elif menu_partial.func == tkinter.Menu.add:
                    menu_partial(menu, data)
            return menu

        self.option_add("*tearOff", 0)
        main_menu = submenu(self.menu_template)
        self["menu"] = main_menu


def cls_as_skel(cls):
    """Use to convert a class to a skeleton.

    This is useful for creating a skeleton that will have rows added dynamically.

    """

    # pylint: disable=missing-class-docstring
    class SkeletonContainer(SkeletonMixin, cls):
        @property
        def template(self):
            return [[]]

    return SkeletonContainer


class Menu:
    """Class methods are used to define a menu template."""

    def __new__(cls):
        raise ValueError("Cannot instantiate instance, use class methods instead")

    @classmethod
    def add(cls, **opts: typing.Any) -> partial:
        """Use to add a separator, radiobutton, or checkbutton menu item.

        >>> {Menu.add(**opts): 'separator'|'radiobutton'|'checkbutton'}

        Returns:
            partial -- Partial function that will be called to create item

        """
        return partial(tkinter.Menu.add, **opts)

    @classmethod
    def command(cls, **opts: typing.Any) -> MenuCommand:
        """Use to add a command menu item.

        >>> {Menu.command(label='labeltext', **opts): command_function}

        Returns:
            T_MenuCommand -- Partial function that will be called to create item

        """
        nf = partial(tkinter.Menu.add_command, **opts)
        return nf

    @classmethod
    def cascade(cls, **opts: typing.Any) -> MenuCommand:
        """Use to add a submenu to a menu.

        >>> {Menu.cascade(label='labeltext', **opts): {
        >>>     # submenu def
        >>> }}

        Returns:
            T_MenuCommand -- Partial function that will be called to create submenu

        """
        nf = partial(tkinter.Menu.add_cascade, **opts)
        return nf
